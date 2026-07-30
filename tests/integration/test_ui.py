"""Verify that the Phase 1-3 browser interface is served locally."""

import asyncio

import httpx

from app.main import app


async def get(path: str) -> httpx.Response:
    """Issue an in-process request for a UI resource."""

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.get(path)


def test_root_serves_preference_builder() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert "What should this mix feel like?" in response.text
    assert 'id="recommendation-form"' in response.text
    assert 'id="results-section"' in response.text
    assert 'id="manual-song-form"' in response.text
    assert 'id="private-song-list"' in response.text
    assert "play audio" not in response.text.lower()


def test_static_assets_are_available() -> None:
    stylesheet = asyncio.run(get("/static/css/app.css"))
    script = asyncio.run(get("/static/js/app.js"))

    assert stylesheet.status_code == 200
    assert "--lime: #d7ff64" in stylesheet.text
    assert script.status_code == 200
    assert "/api/recommendations/deterministic" in script.text
    assert "/api/songs/private" in script.text
