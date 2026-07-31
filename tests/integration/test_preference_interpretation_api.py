"""Verify the Phase 7 review-first preference interpretation endpoint."""

import asyncio

import httpx

from app.main import app


async def post(prompt: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.post(
            "/api/preferences/interpret",
            json={"prompt": prompt},
        )


def test_demo_endpoint_returns_reviewable_structured_preferences() -> None:
    response = asyncio.run(post("cozy instrumental lofi beats for late-night coding"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "demo"
    assert payload["needs_review"] is True
    assert payload["preferences"]["preferred_genres"] == ["lofi"]
    assert "focused" in payload["preferences"]["preferred_moods"]
    assert payload["preferences"]["target_instrumentalness"] == 0.9
    assert "prompt" not in payload


def test_endpoint_rejects_empty_and_oversized_prompts() -> None:
    empty = asyncio.run(post("  "))
    oversized = asyncio.run(post("x" * 1001))

    assert empty.status_code == 422
    assert oversized.status_code == 422


def test_interpreted_preferences_drive_existing_recommender() -> None:
    async def scenario() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            interpretation = await client.post(
                "/api/preferences/interpret",
                json={"prompt": "focused lofi coding beats, low energy"},
            )
            recommendations = await client.post(
                "/api/recommendations/deterministic?limit=3",
                json=interpretation.json()["preferences"],
            )
            return interpretation, recommendations

    interpretation, recommendations = asyncio.run(scenario())

    assert interpretation.status_code == 200
    assert recommendations.status_code == 200
    assert recommendations.json()["recommendations"][0]["song"]["genre"] == "lofi"
