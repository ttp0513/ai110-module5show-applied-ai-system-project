"""Verify Phase 6 retrieval API grounding and private-session isolation."""

import asyncio

import httpx

from app.main import app
from tests.integration.test_private_songs_api import MANUAL_SONG


async def retrieval_scenario() -> None:
    transport = httpx.ASGITransport(app=app)
    async with (
        httpx.AsyncClient(transport=transport, base_url="http://test") as owner,
        httpx.AsyncClient(transport=transport, base_url="http://test") as other,
    ):
        private_song = {
            **MANUAL_SONG,
            "title": "Quasar Velvet Signal",
            "artist": "Session Only",
        }
        created = await owner.post("/api/songs/private", json=private_song)
        assert created.status_code == 201

        owner_results = await owner.post(
            "/api/retrieval/search?limit=5",
            json={"query": "Quasar Velvet Signal"},
        )
        assert owner_results.status_code == 200
        assert owner_results.json()["candidates"][0]["song"]["title"] == (
            "Quasar Velvet Signal"
        )
        assert owner_results.json()["searched_song_count"] == 61

        other_results = await other.post(
            "/api/retrieval/search?limit=5",
            json={"query": "Quasar Velvet Signal"},
        )
        assert other_results.status_code == 200
        assert all(
            candidate["song"]["title"] != "Quasar Velvet Signal"
            for candidate in other_results.json()["candidates"]
        )
        assert other_results.json()["searched_song_count"] == 60


def test_retrieval_uses_only_caller_visible_catalog() -> None:
    asyncio.run(retrieval_scenario())


def test_retrieval_rejects_unbounded_or_empty_input() -> None:
    async def scenario() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            empty = await client.post(
                "/api/retrieval/search",
                json={"query": "  "},
            )
            long = await client.post(
                "/api/retrieval/search",
                json={"query": "x" * 1001},
            )
            return empty, long

    empty, long = asyncio.run(scenario())
    assert empty.status_code == 422
    assert long.status_code == 422
