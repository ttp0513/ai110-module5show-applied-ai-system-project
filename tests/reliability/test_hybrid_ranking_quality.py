"""Fixed Phase 8 cases for hybrid relevance and ranking stability."""

from pathlib import Path

import pytest

from app.catalog import CatalogRepository
from app.models import UserPreferences
from app.retrieval import CatalogRetrievalService
from app.services import HybridRecommendationService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _songs():
    return CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()


@pytest.mark.parametrize(
    ("query", "preferences", "expected_genre"),
    [
        (
            "late-night coding lofi beats",
            UserPreferences(
                preferred_genres=["lofi"],
                preferred_moods=["focused"],
            ),
            "lofi",
        ),
        (
            "romantic neon night drive",
            UserPreferences(
                preferred_genres=["synthwave"],
                preferred_moods=["romantic"],
            ),
            "synthwave",
        ),
        (
            "intense guitar workout anthem",
            UserPreferences(
                preferred_genres=["rock"],
                preferred_moods=["intense"],
            ),
            "rock",
        ),
    ],
)
def test_fixed_hybrid_requests_rank_expected_genre_first(
    query: str,
    preferences: UserPreferences,
    expected_genre: str,
) -> None:
    response = HybridRecommendationService(CatalogRetrievalService()).recommend(
        query=query,
        preferences=preferences,
        songs=_songs(),
        candidate_limit=15,
        result_limit=5,
    )

    assert response.recommendations[0].song.genre.value == expected_genre


def test_identical_hybrid_request_has_identical_order_and_scores() -> None:
    service = HybridRecommendationService(CatalogRetrievalService())
    preferences = UserPreferences(
        preferred_genres=["jazz"],
        preferred_moods=["relaxed"],
    )
    arguments = {
        "query": "relaxed jazz lounge",
        "preferences": preferences,
        "songs": _songs(),
        "candidate_limit": 15,
        "result_limit": 5,
    }

    first = service.recommend(**arguments)
    second = service.recommend(**arguments)

    assert [(item.song.id, item.score) for item in first.recommendations] == [
        (item.song.id, item.score) for item in second.recommendations
    ]
