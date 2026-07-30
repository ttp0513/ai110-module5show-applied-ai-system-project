"""Verify session isolation and private-song recommendation integration."""

import asyncio

import httpx

from app.main import app

MANUAL_SONG = {
    "title": "User Signal",
    "artist": "Private Artist",
    "genre": "synthwave",
    "mood": "happy",
    "energy": 0.72,
    "tempo_bpm": 112,
    "valence": 0.81,
    "danceability": 0.74,
    "acousticness": 0.18,
    "release_year": 2025,
    "duration_seconds": 214,
    "instrumentalness": 0.68,
    "liveness": 0.12,
}


async def private_song_scenario() -> None:
    """Run a complete two-session private catalog scenario."""

    transport = httpx.ASGITransport(app=app)
    async with (
        httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as owner,
        httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as other_listener,
    ):
        created = await owner.post("/api/songs/private", json=MANUAL_SONG)
        assert created.status_code == 201
        song_id = created.json()["song"]["id"]
        assert created.json()["song"]["owner_scope"] == "private_catalog"
        assert created.json()["song"]["source"] == "manual"

        owner_records = await owner.get("/api/songs/private")
        other_records = await other_listener.get("/api/songs/private")
        assert owner_records.json()["count"] == 1
        assert other_records.json()["count"] == 0

        recommendations = await owner.post(
            "/api/recommendations/deterministic?limit=3",
            json={
                "preferred_genres": ["synthwave"],
                "preferred_moods": ["happy"],
            },
        )
        assert recommendations.status_code == 200
        assert recommendations.json()["recommendations"][0]["song"]["id"] == song_id

        other_options = await other_listener.get("/api/catalog/options")
        owner_options = await owner.get("/api/catalog/options")
        assert other_options.json()["song_count"] == 60
        assert owner_options.json()["song_count"] == 61

        deleted = await owner.delete(f"/api/songs/private/{song_id}")
        assert deleted.status_code == 204
        final_records = await owner.get("/api/songs/private")
        assert final_records.json()["count"] == 0


def test_private_song_lifecycle_and_isolation() -> None:
    asyncio.run(private_song_scenario())


def test_manual_song_endpoint_rejects_popularity() -> None:
    async def scenario() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            return await client.post(
                "/api/songs/private",
                json={**MANUAL_SONG, "popularity": 99},
            )

    response = asyncio.run(scenario())

    assert response.status_code == 422
