"""Verify the unified Phase 8 recommendation journey and session isolation."""

import asyncio

import httpx

from app.main import app
from tests.integration.test_private_songs_api import MANUAL_SONG


async def hybrid_scenario() -> None:
    transport = httpx.ASGITransport(app=app)
    async with (
        httpx.AsyncClient(transport=transport, base_url="http://test") as owner,
        httpx.AsyncClient(transport=transport, base_url="http://test") as other,
    ):
        private_song = {
            **MANUAL_SONG,
            "title": "Velvet Quasar Hybrid",
            "artist": "Private Orbit",
        }
        created = await owner.post("/api/songs/private", json=private_song)
        assert created.status_code == 201

        request = {
            "query": "Velvet Quasar Hybrid",
            "preferences": {
                "preferred_genres": ["synthwave"],
                "preferred_moods": ["happy"],
            },
        }
        owner_results = await owner.post(
            "/api/recommendations?limit=5",
            json=request,
        )
        assert owner_results.status_code == 200
        assert owner_results.json()["recommendations"][0]["song"]["title"] == (
            "Velvet Quasar Hybrid"
        )

        other_results = await other.post(
            "/api/recommendations?limit=5",
            json=request,
        )
        assert other_results.status_code == 200
        assert all(
            item["song"]["title"] != "Velvet Quasar Hybrid"
            for item in other_results.json()["recommendations"]
        )


def test_hybrid_api_uses_only_caller_visible_songs() -> None:
    asyncio.run(hybrid_scenario())


def test_hybrid_api_rejects_missing_reviewed_preferences() -> None:
    async def scenario() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            return await client.post(
                "/api/recommendations",
                json={"query": "late night coding"},
            )

    assert asyncio.run(scenario()).status_code == 422
