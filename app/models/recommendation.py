"""Structured deterministic recommendation results."""

from pydantic import BaseModel, Field

from app.models.song import Song


class FeatureReason(BaseModel):
    """Auditable contribution of one active preference."""

    feature: str
    summary: str
    similarity: float = Field(ge=0.0, le=1.0)
    normalized_weight: float = Field(ge=0.0, le=1.0)
    contribution: float = Field(ge=0.0, le=1.0)


class Recommendation(BaseModel):
    """One ranked song with deterministic evidence."""

    rank: int = Field(ge=1)
    song: Song
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[FeatureReason]


class RecommendationResponse(BaseModel):
    """Deterministic recommendation response returned by Phase 3."""

    mode: str = "deterministic"
    considered_song_count: int = Field(ge=0)
    filtered_song_count: int = Field(ge=0)
    recommendations: list[Recommendation]
