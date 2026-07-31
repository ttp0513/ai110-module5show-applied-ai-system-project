"""Validated domain and transport models."""

from app.models.audio_analysis import (
    AudioAnalysisApproval,
    AudioAnalysisProposal,
    AudioFileInfo,
)
from app.models.hybrid import (
    HybridRecommendation,
    HybridRecommendationRequest,
    HybridRecommendationResponse,
    HybridScoreEvidence,
    RecommendationRefinementRequest,
    RecommendationRefinementResponse,
)
from app.models.preference_interpretation import (
    ExtractedPreferences,
    PreferenceInterpretationRequest,
    PreferenceInterpretationResponse,
)
from app.models.preferences import UserPreferences
from app.models.private_song import (
    FeatureProvenance,
    FeatureSource,
    ManualSongCreate,
    PrivateSongRecord,
)
from app.models.recommendation import (
    FeatureReason,
    Recommendation,
    RecommendationResponse,
)
from app.models.retrieval import (
    RetrievalCandidate,
    RetrievalEvidence,
    RetrievalQuery,
    RetrievalResponse,
)
from app.models.song import Genre, Mood, Song, SongOwnerScope, SongSource

__all__ = [
    "AudioAnalysisApproval",
    "AudioAnalysisProposal",
    "AudioFileInfo",
    "FeatureReason",
    "FeatureProvenance",
    "FeatureSource",
    "Genre",
    "HybridRecommendation",
    "HybridRecommendationRequest",
    "HybridRecommendationResponse",
    "HybridScoreEvidence",
    "RecommendationRefinementRequest",
    "RecommendationRefinementResponse",
    "Mood",
    "ManualSongCreate",
    "PrivateSongRecord",
    "PreferenceInterpretationRequest",
    "PreferenceInterpretationResponse",
    "ExtractedPreferences",
    "Recommendation",
    "RecommendationResponse",
    "RetrievalCandidate",
    "RetrievalEvidence",
    "RetrievalQuery",
    "RetrievalResponse",
    "Song",
    "SongOwnerScope",
    "SongSource",
    "UserPreferences",
]
