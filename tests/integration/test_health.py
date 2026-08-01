"""Verify that the Phase 2 application skeleton is runnable."""

import asyncio

import httpx

from app.main import app


async def get(path: str) -> httpx.Response:
    """Issue an in-process request without starting a network server."""

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        return await client.get(path)


def test_health_check() -> None:
    response = asyncio.run(get("/api/health"))

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "VYBE",
        "environment": "development",
        "demo_mode": True,
        "phase": 13,
    }


def test_api_describes_current_phase() -> None:
    response = asyncio.run(get("/api"))

    assert response.status_code == 200
    assert response.json()["status"] == "Phase 13 MVP complete"
