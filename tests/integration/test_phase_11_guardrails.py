"""Verify Phase 11 tracing, security headers, logs, and request guardrails."""

import asyncio
import logging
from uuid import UUID

import httpx

from app.api.dependencies import get_catalog
from app.main import app


async def request(
    method: str,
    path: str,
    **kwargs: object,
) -> httpx.Response:
    """Issue an in-process request while allowing safe 500 responses."""

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.request(method, path, **kwargs)


def test_responses_include_request_id_and_browser_security_headers() -> None:
    response = asyncio.run(request("GET", "/api/health"))

    assert response.status_code == 200
    UUID(response.headers["x-request-id"])
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "microphone=()" in response.headers["permissions-policy"]


def test_each_request_receives_a_new_server_generated_identifier() -> None:
    first = asyncio.run(request("GET", "/api/health"))
    second = asyncio.run(request("GET", "/api/health"))

    assert first.headers["x-request-id"] != second.headers["x-request-id"]


def test_cross_origin_mutation_is_rejected() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/preferences/interpret",
            headers={"Origin": "https://attacker.example"},
            json={"prompt": "focused lofi"},
        )
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Cross-origin state changes are not allowed."}
    assert "x-request-id" in response.headers


def test_oversized_declared_body_is_rejected_before_parsing() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/preferences/interpret",
            headers={"Content-Length": str(27 * 1024 * 1024)},
            content=b"{}",
        )
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "The request body is too large."}


def test_raw_prompt_is_absent_from_standard_logs(caplog: object) -> None:
    secret_prompt = "private-vibe-phrase-92841 focused lofi"
    with caplog.at_level(logging.INFO):  # type: ignore[attr-defined]
        response = asyncio.run(
            request(
                "POST",
                "/api/preferences/interpret",
                json={"prompt": secret_prompt},
            )
        )

    assert response.status_code == 200
    assert secret_prompt not in caplog.text  # type: ignore[attr-defined]
    assert "path=/api/preferences/interpret" in caplog.text  # type: ignore[attr-defined]


def test_unexpected_errors_return_safe_traceable_response() -> None:
    def fail_catalog() -> None:
        raise RuntimeError("database-password=do-not-expose")

    app.dependency_overrides[get_catalog] = fail_catalog
    try:
        response = asyncio.run(request("GET", "/api/catalog/options"))
    finally:
        app.dependency_overrides.pop(get_catalog, None)

    assert response.status_code == 500
    payload = response.json()
    assert payload["detail"] == "An unexpected error occurred."
    assert payload["request_id"] == response.headers["x-request-id"]
    assert "database-password" not in response.text
