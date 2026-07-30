"""Canonical song categories and validated catalog record."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Genre(StrEnum):
    """Supported genre vocabulary for catalog and preference consistency."""

    AMBIENT = "ambient"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    FOLK = "folk"
    HIP_HOP = "hip hop"
    INDIE_POP = "indie pop"
    JAZZ = "jazz"
    LATIN = "latin"
    LOFI = "lofi"
    POP = "pop"
    ROCK = "rock"
    SYNTHWAVE = "synthwave"
    WORLD = "world"


class Mood(StrEnum):
    """Supported mood vocabulary for catalog and preference consistency."""

    CELEBRATORY = "celebratory"
    CHILL = "chill"
    CONFIDENT = "confident"
    FOCUSED = "focused"
    HAPPY = "happy"
    INTENSE = "intense"
    MOODY = "moody"
    RELAXED = "relaxed"
    ROMANTIC = "romantic"


class SongSource(StrEnum):
    """How a canonical song entered VYBE."""

    BUILT_IN = "built_in"
    UPLOAD = "upload"
    MANUAL = "manual"


class SongOwnerScope(StrEnum):
    """Who may retrieve a canonical song."""

    PUBLIC_CATALOG = "public_catalog"
    PRIVATE_CATALOG = "private_catalog"


class Song(BaseModel):
    """A normalized song record containing only recommendation features."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    artist: str = Field(min_length=1, max_length=200)
    genre: Genre
    mood: Mood
    energy: float = Field(ge=0.0, le=1.0)
    tempo_bpm: float = Field(ge=20.0, le=300.0)
    valence: float = Field(ge=0.0, le=1.0)
    danceability: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)
    release_year: int = Field(ge=1900)
    duration_seconds: int = Field(ge=15, le=7200)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    liveness: float = Field(ge=0.0, le=1.0)
    source: SongSource
    owner_scope: SongOwnerScope

    @field_validator("release_year")
    @classmethod
    def release_year_cannot_be_in_the_future(cls, value: int) -> int:
        """Reject future catalog metadata."""

        if value > datetime.now(UTC).year:
            raise ValueError("release_year cannot be in the future")
        return value
