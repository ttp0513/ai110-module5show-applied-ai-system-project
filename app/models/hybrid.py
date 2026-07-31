"""Contracts for retrieval-augmented hybrid recommendations."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.preferences import UserPreferences
from app.models.recommendation import FeatureReason
from app.models.song import Song


class HybridRecommendationRequest(BaseModel):
    """Reviewed preferences plus the discovery text used for retrieval."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=3, max_length=1000)
    preferences: UserPreferences


class HybridScoreEvidence(BaseModel):
    """Auditable components used to calculate a hybrid score."""

    retrieval_score: float = Field(ge=0.0, le=1.0)
    normalized_retrieval_score: float = Field(ge=0.0, le=1.0)
    feature_score: float = Field(ge=0.0, le=1.0)
    retrieval_weight: float = Field(ge=0.0, le=1.0)
    feature_weight: float = Field(ge=0.0, le=1.0)


class HybridRecommendation(BaseModel):
    """One hybrid-ranked approved song with grounded evidence."""

    rank: int = Field(ge=1)
    song: Song
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[FeatureReason]
    score_evidence: HybridScoreEvidence
    grounded_explanation: str


class HybridRecommendationResponse(BaseModel):
    """Phase 8 result that identifies retrieval fallback explicitly."""

    mode: str = "hybrid"
    considered_song_count: int = Field(ge=0)
    filtered_song_count: int = Field(ge=0)
    retrieved_candidate_count: int = Field(ge=0)
    used_retrieval_fallback: bool
    explanation_mode: str = "deterministic_grounded"
    recommendations: list[HybridRecommendation]


class RecommendationRefinementRequest(HybridRecommendationRequest):
    """Complete reviewed state for reranking while skipping prior results."""

    excluded_song_ids: set[str] = Field(default_factory=set, max_length=20)


class RecommendationRefinementResponse(HybridRecommendationResponse):
    """Hybrid results plus the number of caller-visible songs skipped."""

    excluded_song_count: int = Field(ge=0)
