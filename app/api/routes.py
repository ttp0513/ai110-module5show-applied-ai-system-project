"""Phase 2 application and health routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.dependencies import get_catalog, get_recommender
from app.catalog import CatalogRepository
from app.config import get_settings
from app.models import Genre, Mood, RecommendationResponse, UserPreferences
from app.recommendation import DeterministicRecommender

router = APIRouter()
CatalogDependency = Annotated[CatalogRepository, Depends(get_catalog)]
RecommenderDependency = Annotated[
    DeterministicRecommender,
    Depends(get_recommender),
]


class HealthResponse(BaseModel):
    """Public health response without credentials or internal paths."""

    status: Literal["ok"]
    application: str
    environment: str
    demo_mode: bool
    phase: int


class CatalogOptionsResponse(BaseModel):
    """Supported categories and built-in catalog summary."""

    song_count: int
    genres: list[Genre]
    moods: list[Mood]
    recommendation_features: list[str]


@router.get("/api", tags=["application"])
def application_summary() -> dict[str, str]:
    """Identify the API while the product UI is developed in a later phase."""

    return {
        "name": get_settings().app_name,
        "status": "Phase 3 deterministic recommender",
        "documentation": "/docs",
    }


@router.get("/api/health", response_model=HealthResponse, tags=["operations"])
def health_check() -> HealthResponse:
    """Report that the Phase 2 process and configuration loaded successfully."""

    settings = get_settings()
    return HealthResponse(
        status="ok",
        application=settings.app_name,
        environment=settings.environment,
        demo_mode=settings.demo_mode,
        phase=3,
    )


@router.get(
    "/api/catalog/options",
    response_model=CatalogOptionsResponse,
    tags=["catalog"],
)
def catalog_options(
    catalog: CatalogDependency,
) -> CatalogOptionsResponse:
    """Return canonical category choices without exposing implementation details."""

    songs = catalog.list_all()
    return CatalogOptionsResponse(
        song_count=len(songs),
        genres=list(Genre),
        moods=list(Mood),
        recommendation_features=[
            "genre",
            "mood",
            "energy",
            "tempo_bpm",
            "valence",
            "danceability",
            "acousticness",
            "instrumentalness",
            "liveness",
            "release_year",
            "duration_seconds",
        ],
    )


@router.post(
    "/api/recommendations/deterministic",
    response_model=RecommendationResponse,
    tags=["recommendations"],
)
def deterministic_recommendations(
    preferences: UserPreferences,
    catalog: CatalogDependency,
    recommender: RecommenderDependency,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecommendationResponse:
    """Return transparent recommendations using only validated catalog features."""

    return recommender.recommend(
        preferences=preferences,
        songs=catalog.list_all(),
        limit=limit,
    )
