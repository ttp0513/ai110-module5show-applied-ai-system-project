"""Load canonical songs from a validated CSV catalog."""

import csv
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError

from app.models.song import Song, SongOwnerScope, SongSource

EXPECTED_COLUMNS = {
    "id",
    "title",
    "artist",
    "genre",
    "mood",
    "energy",
    "tempo_bpm",
    "valence",
    "danceability",
    "acousticness",
    "release_year",
    "duration_seconds",
    "instrumentalness",
    "liveness",
}


class CatalogValidationError(ValueError):
    """Raised when a catalog cannot be represented by canonical song records."""


class CatalogRepository:
    """Provide deterministic read access to an immutable built-in catalog."""

    def __init__(self, songs: Iterable[Song]) -> None:
        loaded_songs = tuple(songs)
        self._validate_unique_ids(loaded_songs)
        self._songs = loaded_songs

    @classmethod
    def from_csv(cls, path: Path) -> "CatalogRepository":
        """Load and validate every record before exposing the catalog."""

        if not path.is_file():
            raise CatalogValidationError(f"Catalog file does not exist: {path}")

        songs: list[Song] = []
        try:
            with path.open(encoding="utf-8", newline="") as catalog_file:
                reader = csv.DictReader(catalog_file)
                columns = set(reader.fieldnames or ())
                if columns != EXPECTED_COLUMNS:
                    missing = sorted(EXPECTED_COLUMNS - columns)
                    unexpected = sorted(columns - EXPECTED_COLUMNS)
                    raise CatalogValidationError(
                        "Catalog columns are invalid. "
                        f"Missing: {missing}; unexpected: {unexpected}"
                    )

                for line_number, row in enumerate(reader, start=2):
                    try:
                        songs.append(
                            Song.model_validate(
                                {
                                    **row,
                                    "source": SongSource.BUILT_IN,
                                    "owner_scope": SongOwnerScope.PUBLIC_CATALOG,
                                }
                            )
                        )
                    except ValidationError as error:
                        raise CatalogValidationError(
                            f"Invalid song at CSV line {line_number}: {error}"
                        ) from error
        except OSError as error:
            raise CatalogValidationError(f"Unable to read catalog: {error}") from error

        return cls(songs)

    @staticmethod
    def _validate_unique_ids(songs: tuple[Song, ...]) -> None:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for song in songs:
            if song.id in seen:
                duplicates.add(song.id)
            seen.add(song.id)
        if duplicates:
            raise CatalogValidationError(
                f"Catalog contains duplicate song IDs: {sorted(duplicates)}"
            )

    def list_all(self) -> tuple[Song, ...]:
        """Return immutable catalog records in source order."""

        return self._songs

    def get(self, song_id: str) -> Song | None:
        """Return one song by canonical identifier."""

        return next((song for song in self._songs if song.id == song_id), None)
