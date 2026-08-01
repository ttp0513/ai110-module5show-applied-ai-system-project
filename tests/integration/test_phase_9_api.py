"""Verify the completed Phase 9 public API contract."""

import asyncio

import httpx

from app.main import app


async def request(
    method: str,
    path: str,
    json: dict[str, object] | None = None,
) -> httpx.Response:
    """Issue an in-process request against the public application."""

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.request(method, path, json=json)


def test_capability_manifest_exposes_safe_client_limits() -> None:
    response = asyncio.run(request("GET", "/api/capabilities"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["api_version"] == "1.0.0"
    assert payload["phase"] == 13
    assert "recommendation_refinement" in payload["capabilities"]
    assert "operational_guardrails" in payload["capabilities"]
    assert payload["maximum_recommendation_count"] == 20
    assert "gemini_api_key" not in response.text


def test_openapi_lists_the_complete_primary_api() -> None:
    response = asyncio.run(request("GET", "/openapi.json"))

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/preferences/interpret" in paths
    assert "/api/recommendations" in paths
    assert "/api/recommendations/refine" in paths
    assert "/api/songs/private" in paths
    assert "/api/songs/analyze" in paths


def test_refinement_excludes_skipped_song_and_is_reproducible() -> None:
    initial_request = {
        "query": "focused lofi study music",
        "preferences": {
            "preferred_genres": ["lofi"],
            "preferred_moods": ["focused"],
        },
    }
    initial = asyncio.run(
        request("POST", "/api/recommendations?limit=3", initial_request)
    )
    assert initial.status_code == 200
    skipped_id = initial.json()["recommendations"][0]["song"]["id"]

    refinement_request = {
        **initial_request,
        "excluded_song_ids": [skipped_id, "not-visible-or-unknown"],
    }
    first = asyncio.run(
        request("POST", "/api/recommendations/refine?limit=3", refinement_request)
    )
    second = asyncio.run(
        request("POST", "/api/recommendations/refine?limit=3", refinement_request)
    )

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["excluded_song_count"] == 1
    result_ids = {item["song"]["id"] for item in first.json()["recommendations"]}
    assert skipped_id not in result_ids


def test_refinement_rejects_more_than_twenty_exclusions() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/recommendations/refine",
            {
                "query": "focused lofi study music",
                "preferences": {"preferred_genres": ["lofi"]},
                "excluded_song_ids": [f"song-{index}" for index in range(21)],
            },
        )
    )

    assert response.status_code == 422
