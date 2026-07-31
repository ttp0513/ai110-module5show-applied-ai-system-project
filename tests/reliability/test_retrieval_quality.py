"""Fixed evaluation cases for Phase 6 retrieval quality and consistency."""

from pathlib import Path

import pytest

from app.catalog import CatalogRepository
from app.retrieval import CatalogRetrievalService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("query", "expected_genre", "expected_mood"),
    [
        ("late-night coding study beats", "lofi", "focused"),
        ("retro neon cyberpunk night drive", "synthwave", "moody"),
        ("orchestral piano study music", "classical", None),
        ("guitar drums workout anthem", "rock", "intense"),
        ("dreamy intimate date night", None, "romantic"),
    ],
)
def test_fixed_queries_recall_expected_category_in_top_five(
    query: str,
    expected_genre: str | None,
    expected_mood: str | None,
) -> None:
    songs = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()

    candidates = CatalogRetrievalService().search(query, songs, limit=5).candidates

    assert any(
        (expected_genre is None or item.song.genre.value == expected_genre)
        and (expected_mood is None or item.song.mood.value == expected_mood)
        for item in candidates
    )


def test_identical_input_has_identical_rank_and_score() -> None:
    songs = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()
    service = CatalogRetrievalService()

    first = service.search("bright acoustic morning", songs, limit=5)
    second = service.search("bright acoustic morning", songs, limit=5)

    assert [(item.song.id, item.retrieval_score) for item in first.candidates] == [
        (item.song.id, item.retrieval_score) for item in second.candidates
    ]
