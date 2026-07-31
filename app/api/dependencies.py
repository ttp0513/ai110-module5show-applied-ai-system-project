"""Application-owned dependency construction."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, Response

from app.ai import (
    DemoPreferenceProvider,
    OpenAIPreferenceProvider,
    PreferenceInterpretationService,
)
from app.audio import AnalysisDraftRepository, AudioAnalysisService, AudioAnalyzer
from app.audio.classifier import CatalogCategoryClassifier
from app.catalog import CatalogRepository, SQLitePrivateSongRepository
from app.config import get_settings
from app.recommendation import DeterministicRecommender
from app.retrieval import CatalogRetrievalService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache
def get_catalog() -> CatalogRepository:
    """Load and validate the built-in catalog once per process."""

    return CatalogRepository.from_csv(PROJECT_ROOT / "data" / "songs.csv")


@lru_cache
def get_recommender() -> DeterministicRecommender:
    """Return the stateless deterministic recommendation service."""

    return DeterministicRecommender()


@lru_cache
def get_retrieval_service() -> CatalogRetrievalService:
    """Return the stateless catalog-grounded retrieval service."""

    return CatalogRetrievalService()


@lru_cache
def get_preference_interpreter() -> PreferenceInterpretationService:
    """Select configured structured extraction with a deterministic fallback."""

    settings = get_settings()
    fallback = DemoPreferenceProvider()
    if settings.demo_mode or settings.ai_provider == "demo":
        return PreferenceInterpretationService(fallback, fallback)
    if not settings.ai_api_key:
        return PreferenceInterpretationService(
            fallback,
            fallback,
            initial_fallback_reason=(
                "OpenAI is configured without an API key; local rules used."
            ),
        )
    primary = OpenAIPreferenceProvider(
        api_key=settings.ai_api_key,
        model=settings.ai_model,
        timeout_seconds=settings.request_timeout_seconds,
    )
    return PreferenceInterpretationService(primary, fallback)


@lru_cache
def get_private_catalog() -> SQLitePrivateSongRepository:
    """Return durable private storage shared within the application process."""

    configured_path = get_settings().private_database_path
    database_path = (
        configured_path
        if configured_path.is_absolute()
        else PROJECT_ROOT / configured_path
    )
    return SQLitePrivateSongRepository(database_path)


@lru_cache
def get_analysis_drafts() -> AnalysisDraftRepository:
    """Return non-persistent, audio-free proposals awaiting review."""

    return AnalysisDraftRepository()


@lru_cache
def get_audio_analysis_service() -> AudioAnalysisService:
    """Build the bounded Phase 5 audio analysis workflow."""

    settings = get_settings()
    classifier = CatalogCategoryClassifier(get_catalog().list_all())
    analyzer = AudioAnalyzer(classifier, settings.max_audio_duration_seconds)
    return AudioAnalysisService(
        analyzer=analyzer,
        drafts=get_analysis_drafts(),
        upload_directory=PROJECT_ROOT / "data" / "uploads",
        max_upload_bytes=settings.max_audio_upload_bytes,
    )


def get_session_id(
    response: Response,
    private_catalog: Annotated[
        SQLitePrivateSongRepository,
        Depends(get_private_catalog),
    ],
    proposed_id: Annotated[
        str | None,
        Cookie(alias="vybe_session"),
    ] = None,
) -> str:
    """Resolve an issued anonymous session and refresh its secure cookie."""

    settings = get_settings()
    session_id = private_catalog.resolve_session(proposed_id)
    response.set_cookie(
        key="vybe_session",
        value=session_id,
        httponly=True,
        secure=settings.environment == "production",
        samesite="strict",
        path="/",
        max_age=settings.session_cookie_max_age_days * 24 * 60 * 60,
    )
    return session_id
