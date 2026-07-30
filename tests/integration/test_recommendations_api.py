"""Verify the Phase 3 catalog and deterministic recommendation API."""

import asyncio

import httpx

from app.main import app


async def request(
    method: str,
    path: str,
    json: dict[str, object] | None = None,
) -> httpx.Response:
    """Issue an in-process API request."""

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.request(method, path, json=json)


def test_catalog_options_describe_canonical_features() -> None:
    response = asyncio.run(request("GET", "/api/catalog/options"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["song_count"] == 60
    assert "popularity" not in payload["recommendation_features"]
    assert "pop" in payload["genres"]
    assert "focused" in payload["moods"]


def test_deterministic_recommendation_endpoint() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/recommendations/deterministic?limit=3",
            json={
                "preferred_genres": ["lofi"],
                "preferred_moods": ["focused"],
                "target_instrumentalness": 0.9,
            },
        )
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "deterministic"
    assert len(payload["recommendations"]) == 3
    assert payload["recommendations"][0]["song"]["title"] == "Focus Flow"


def test_recommendation_endpoint_rejects_empty_preferences() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/recommendations/deterministic",
            json={},
        )
    )

    assert response.status_code == 422
