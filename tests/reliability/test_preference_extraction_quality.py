"""Fixed Phase 7 interpretation cases for measurable regression checks."""

import asyncio

import pytest

from app.ai.providers import DemoPreferenceProvider


@pytest.mark.parametrize(
    ("prompt", "genre", "mood"),
    [
        ("cozy lofi beats for coding", "lofi", "focused"),
        ("romantic neon night drive", "synthwave", "romantic"),
        ("intense rock guitar workout", "rock", "intense"),
        ("peaceful orchestral strings", "classical", "relaxed"),
        ("happy latin celebration", "latin", "happy"),
    ],
)
def test_fixed_prompts_extract_expected_categories(
    prompt: str,
    genre: str,
    mood: str,
) -> None:
    extraction = asyncio.run(DemoPreferenceProvider().extract(prompt))

    assert genre in [item.value for item in extraction.preferred_genres]
    assert mood in [item.value for item in extraction.preferred_moods]


def test_interpreter_is_deterministic_for_identical_text() -> None:
    provider = DemoPreferenceProvider()
    first = asyncio.run(provider.extract("medium energy romantic synthwave"))
    second = asyncio.run(provider.extract("medium energy romantic synthwave"))

    assert first == second
