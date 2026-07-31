"""Verify reproducible catalog retrieval and grounded explanations."""

from pathlib import Path

from app.catalog import CatalogRepository
from app.retrieval import CatalogRetrievalService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_vibe_words_retrieve_supported_catalog_semantics() -> None:
    songs = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()

    response = CatalogRetrievalService().search(
        "late night coding study beats",
        songs,
        limit=5,
    )

    assert response.candidates
    assert any(
        candidate.song.genre.value == "lofi" or candidate.song.mood.value == "focused"
        for candidate in response.candidates
    )
    assert response.retrieval_method == "catalog-tfidf-cosine"


def test_explanations_contain_only_candidate_catalog_values() -> None:
    songs = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()

    response = CatalogRetrievalService().search(
        "romantic dreamy date night",
        songs,
        limit=3,
    )

    for candidate in response.candidates:
        song = candidate.song
        assert song.genre.value in candidate.grounded_explanation
        assert song.mood.value in candidate.grounded_explanation
        assert f"{round(song.tempo_bpm)} BPM" in candidate.grounded_explanation
        assert {item.feature for item in candidate.evidence} == {
            "genre",
            "mood",
            "energy",
            "tempo_bpm",
        }


def test_unknown_terms_return_no_invented_candidates() -> None:
    songs = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv").list_all()

    response = CatalogRetrievalService().search(
        "qzxwvu blorptastic",
        songs,
        limit=5,
    )

    assert response.candidates == []
    assert response.searched_song_count == 60
