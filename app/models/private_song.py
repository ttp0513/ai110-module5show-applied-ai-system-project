"""Validated manual song input and feature provenance."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.song import Genre, Mood, Song


class FeatureSource(StrEnum):
    """Origin of a canonical feature value."""

    MEASURED = "measured"
    AI_ESTIMATED = "ai_estimated"
    EMBEDDED_METADATA = "embedded_metadata"
    USER_ENTERED = "user_entered"


class FeatureProvenance(BaseModel):
    """Trace how a private song feature entered the catalog."""

    feature_name: str
    source: FeatureSource
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    model_version: str | None = None
    user_corrected: bool = False


class ManualSongCreate(BaseModel):
    """All fields required to add a song without audio analysis."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

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

    @field_validator("release_year")
    @classmethod
    def release_year_cannot_be_in_the_future(cls, value: int) -> int:
        """Reject future manual metadata."""

        if value > datetime.now(UTC).year:
            raise ValueError("release_year cannot be in the future")
        return value


class PrivateSongRecord(BaseModel):
    """A private canonical song and the origin of its values."""

    song: Song
    provenance: list[FeatureProvenance]
