"""Structured contracts for natural-language preference interpretation."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.preferences import UserPreferences
from app.models.song import Genre, Mood


class ExtractedPreferences(BaseModel):
    """Provider-facing schema whose values are constrained to VYBE fields."""

    model_config = ConfigDict(extra="forbid")

    preferred_genres: list[Genre]
    preferred_moods: list[Mood]
    target_energy: float | None = Field(ge=0.0, le=1.0)
    target_tempo_bpm: float | None = Field(ge=20.0, le=300.0)
    target_valence: float | None = Field(ge=0.0, le=1.0)
    target_danceability: float | None = Field(ge=0.0, le=1.0)
    target_acousticness: float | None = Field(ge=0.0, le=1.0)
    target_instrumentalness: float | None = Field(ge=0.0, le=1.0)
    target_liveness: float | None = Field(ge=0.0, le=1.0)
    preferred_release_year: int | None = Field(ge=1900)
    preferred_duration_seconds: int | None = Field(ge=15, le=7200)
    excluded_genres: list[Genre]
    excluded_moods: list[Mood]
    interpretation_summary: str
    ambiguities: list[str]

    def to_user_preferences(self) -> UserPreferences:
        """Validate extracted fields through the deterministic domain contract."""

        values = self.model_dump(
            exclude={"interpretation_summary", "ambiguities"},
        )
        return UserPreferences.model_validate(values)


class PreferenceInterpretationResponse(BaseModel):
    """Reviewable extraction plus transparent provider and fallback status."""

    preferences: UserPreferences | None
    interpretation_summary: str
    ambiguities: list[str]
    extracted_fields: list[str]
    provider: str
    model: str
    used_fallback: bool
    needs_review: bool = True
    fallback_reason: str | None = None


class PreferenceInterpretationRequest(BaseModel):
    """Bounded raw text accepted by the interpretation endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    prompt: str = Field(min_length=3, max_length=1000)
