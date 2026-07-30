"""Validated listener preferences for deterministic recommendation."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.song import Genre, Mood


class UserPreferences(BaseModel):
    """Optional targets and exclusions used by the deterministic engine."""

    model_config = ConfigDict(extra="forbid")

    preferred_genres: list[Genre] = Field(default_factory=list)
    preferred_moods: list[Mood] = Field(default_factory=list)
    target_energy: float | None = Field(default=None, ge=0.0, le=1.0)
    target_tempo_bpm: float | None = Field(default=None, ge=20.0, le=300.0)
    target_valence: float | None = Field(default=None, ge=0.0, le=1.0)
    target_danceability: float | None = Field(default=None, ge=0.0, le=1.0)
    target_acousticness: float | None = Field(default=None, ge=0.0, le=1.0)
    target_instrumentalness: float | None = Field(default=None, ge=0.0, le=1.0)
    target_liveness: float | None = Field(default=None, ge=0.0, le=1.0)
    preferred_release_year: int | None = Field(default=None, ge=1900)
    preferred_duration_seconds: int | None = Field(
        default=None,
        ge=15,
        le=7200,
    )
    excluded_genres: list[Genre] = Field(default_factory=list)
    excluded_moods: list[Mood] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_an_active_preference(self) -> "UserPreferences":
        """Reject requests that provide only exclusions or no ranking signal."""

        active_targets = (
            self.preferred_genres,
            self.preferred_moods,
            self.target_energy,
            self.target_tempo_bpm,
            self.target_valence,
            self.target_danceability,
            self.target_acousticness,
            self.target_instrumentalness,
            self.target_liveness,
            self.preferred_release_year,
            self.preferred_duration_seconds,
        )
        if not any(value is not None and value != [] for value in active_targets):
            raise ValueError("At least one ranking preference is required.")
        return self
