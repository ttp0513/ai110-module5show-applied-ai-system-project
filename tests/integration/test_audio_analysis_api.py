"""Verify temporary audio analysis, review, and persistence boundaries."""

import asyncio
import io
import math
import struct
import wave

import httpx

from app.main import app


def sine_wave(seconds: int = 16) -> bytes:
    """Create a small original WAV fixture without shipping copyrighted audio."""

    sample_rate = 8000
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        samples = (
            struct.pack(
                "<h",
                int(12000 * math.sin(2 * math.pi * 220 * index / sample_rate)),
            )
            for index in range(sample_rate * seconds)
        )
        output.writeframes(b"".join(samples))
    return buffer.getvalue()


async def analysis_scenario() -> None:
    transport = httpx.ASGITransport(app=app)
    async with (
        httpx.AsyncClient(transport=transport, base_url="http://test") as owner,
        httpx.AsyncClient(transport=transport, base_url="http://test") as other,
    ):
        analyzed = await owner.post(
            "/api/songs/analyze",
            data={"rights_confirmed": "true"},
            files={"file": ("Original Signal.wav", sine_wave(), "audio/wav")},
        )
        assert analyzed.status_code == 200
        proposal = analyzed.json()
        assert proposal["suggested_song"]["title"] == "Original Signal"
        assert proposal["file_info"]["detected_format"] == "wav"
        assert proposal["warnings"]
        analysis_id = proposal["analysis_id"]

        inaccessible = await other.post(
            f"/api/songs/analyzed/{analysis_id}/approve",
            json={"song": proposal["suggested_song"]},
        )
        assert inaccessible.status_code == 404

        reviewed = {
            **proposal["suggested_song"],
            "artist": "Reviewed Artist",
        }
        approved = await owner.post(
            f"/api/songs/analyzed/{analysis_id}/approve",
            json={"song": reviewed},
        )
        assert approved.status_code == 201
        record = approved.json()
        assert record["song"]["source"] == "upload"
        assert record["song"]["artist"] == "Reviewed Artist"
        artist_provenance = next(
            item for item in record["provenance"] if item["feature_name"] == "artist"
        )
        assert artist_provenance["user_corrected"] is True

        reused = await owner.post(
            f"/api/songs/analyzed/{analysis_id}/approve",
            json={"song": reviewed},
        )
        assert reused.status_code == 404


def test_audio_analysis_requires_review_and_preserves_provenance() -> None:
    asyncio.run(analysis_scenario())


def test_audio_upload_rejects_permission_and_false_format() -> None:
    async def scenario() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            denied = await client.post(
                "/api/songs/analyze",
                data={"rights_confirmed": "false"},
                files={"file": ("fake.wav", b"not audio", "audio/wav")},
            )
            disguised = await client.post(
                "/api/songs/analyze",
                data={"rights_confirmed": "true"},
                files={"file": ("fake.wav", b"not audio", "audio/wav")},
            )
            return denied, disguised

    denied, disguised = asyncio.run(scenario())
    assert denied.status_code == 400
    assert disguised.status_code == 422
    assert "contents" in disguised.json()["detail"]
