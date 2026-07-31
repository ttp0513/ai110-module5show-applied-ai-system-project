"""Verify Phase 8 score composition, fallback, and grounding."""

from pathlib import Path

import pytest

from app.catalog import CatalogRepository
from app.models import UserPreferences
from app.retrieval import CatalogRetrievalService
from app.services import HybridRecommendationService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def catalog_songs():
    return CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()


def test_hybrid_score_is_reproducible_weighted_sum() -> None:
    response = HybridRecommendationService(CatalogRetrievalService()).recommend(
        query="late-night coding lofi beats",
        preferences=UserPreferences(
            preferred_genres=["lofi"],
            preferred_moods=["focused"],
            target_energy=0.35,
        ),
        songs=catalog_songs(),
        candidate_limit=15,
        result_limit=5,
    )

    assert response.used_retrieval_fallback is False
    assert response.recommendations
    for item in response.recommendations:
        evidence = item.score_evidence
        expected = (
            evidence.feature_score * evidence.feature_weight
            + evidence.normalized_retrieval_score * evidence.retrieval_weight
        )
        assert item.score == pytest.approx(expected, abs=1e-6)
        assert item.song.genre.value in {"lofi", "ambient"}
        assert item.grounded_explanation


def test_unknown_query_falls_back_to_feature_ranking() -> None:
    response = HybridRecommendationService(CatalogRetrievalService()).recommend(
        query="qzxwvu blorptastic",
        preferences=UserPreferences(
            preferred_genres=["jazz"],
            preferred_moods=["relaxed"],
        ),
        songs=catalog_songs(),
        candidate_limit=15,
        result_limit=3,
    )

    assert response.used_retrieval_fallback is True
    assert response.retrieved_candidate_count == 0
    assert response.recommendations
    for item in response.recommendations:
        assert item.score == item.score_evidence.feature_score
        assert item.score_evidence.retrieval_weight == 0
        assert "retrieval found no text match" in item.grounded_explanation


def test_exclusions_apply_before_retrieval_and_scoring() -> None:
    response = HybridRecommendationService(CatalogRetrievalService()).recommend(
        query="rock guitar workout",
        preferences=UserPreferences(
            preferred_genres=["rock"],
            excluded_moods=["intense"],
        ),
        songs=catalog_songs(),
        candidate_limit=15,
        result_limit=10,
    )

    assert all(item.song.mood.value != "intense" for item in response.recommendations)
    assert response.filtered_song_count > 0
