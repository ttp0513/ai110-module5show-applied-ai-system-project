"""Verify transparent, deterministic scoring and ranking behavior."""

import pytest
from pydantic import ValidationError

from app.api.dependencies import get_catalog
from app.models import Genre, Mood, UserPreferences
from app.recommendation import DeterministicRecommender
from app.recommendation.scorer import calculate_category_similarity


def test_exact_pop_profile_ranks_matching_song_first() -> None:
    preferences = UserPreferences(
        preferred_genres=[Genre.POP],
        preferred_moods=[Mood.HAPPY],
        target_energy=0.82,
    )

    response = DeterministicRecommender().recommend(
        preferences,
        get_catalog().list_all(),
        limit=5,
    )

    assert response.recommendations[0].song.title == "Sunrise City"
    assert response.recommendations[0].score == pytest.approx(1.0)
    assert sum(
        reason.contribution for reason in response.recommendations[0].reasons
    ) == pytest.approx(response.recommendations[0].score)


def test_related_categories_receive_partial_credit() -> None:
    similarity, summary = calculate_category_similarity(
        "indie pop",
        ["pop"],
        {frozenset(("pop", "indie pop"))},
    )

    assert similarity == 0.5
    assert "related" in summary


def test_exclusions_remove_songs_before_scoring() -> None:
    preferences = UserPreferences(
        preferred_moods=[Mood.INTENSE],
        excluded_genres=[Genre.ROCK],
    )

    response = DeterministicRecommender().recommend(
        preferences,
        get_catalog().list_all(),
        limit=20,
    )

    assert response.filtered_song_count > 0
    assert all(
        recommendation.song.genre is not Genre.ROCK
        for recommendation in response.recommendations
    )


def test_empty_preferences_are_rejected() -> None:
    with pytest.raises(ValidationError, match="At least one ranking preference"):
        UserPreferences()


def test_equal_scores_preserve_catalog_order() -> None:
    preferences = UserPreferences(preferred_moods=[Mood.INTENSE])

    first_response = DeterministicRecommender().recommend(
        preferences,
        get_catalog().list_all(),
        limit=20,
    )
    second_response = DeterministicRecommender().recommend(
        preferences,
        get_catalog().list_all(),
        limit=20,
    )

    assert [item.song.id for item in first_response.recommendations] == [
        item.song.id for item in second_response.recommendations
    ]
