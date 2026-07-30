"""Verify canonical catalog loading and validation."""

from pathlib import Path

import pytest

from app.catalog import CatalogRepository, CatalogValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_built_in_catalog_loads_all_songs_without_popularity() -> None:
    catalog = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv")

    songs = catalog.list_all()

    assert len(songs) == 60
    assert len({song.id for song in songs}) == 60
    assert not hasattr(songs[0], "popularity")


def test_catalog_rejects_unexpected_columns(tmp_path: Path) -> None:
    invalid_catalog = tmp_path / "invalid.csv"
    invalid_catalog.write_text("id,title,popularity\n1,Example,99\n", encoding="utf-8")

    with pytest.raises(CatalogValidationError, match="unexpected"):
        CatalogRepository.from_csv(invalid_catalog)


def test_catalog_returns_song_by_string_identifier() -> None:
    catalog = CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv")

    song = catalog.get("1")

    assert song is not None
    assert song.title == "Sunrise City"
