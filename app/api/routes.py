"""Phase 2 application and health routes."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.api.dependencies import (
    get_catalog,
    get_private_catalog,
    get_recommender,
    get_session_id,
)
from app.catalog import (
    CatalogRepository,
    PrivateCatalogLimitError,
    SQLitePrivateSongRepository,
)
from app.config import get_settings
from app.models import (
    Genre,
    ManualSongCreate,
    Mood,
    PrivateSongRecord,
    RecommendationResponse,
    UserPreferences,
)
from app.recommendation import DeterministicRecommender

router = APIRouter()
CatalogDependency = Annotated[CatalogRepository, Depends(get_catalog)]
PrivateCatalogDependency = Annotated[
    SQLitePrivateSongRepository,
    Depends(get_private_catalog),
]
RecommenderDependency = Annotated[
    DeterministicRecommender,
    Depends(get_recommender),
]
SessionDependency = Annotated[str, Depends(get_session_id)]


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
    built_in_song_count: int
    private_song_count: int
    genres: list[Genre]
    moods: list[Mood]
    recommendation_features: list[str]


class PrivateSongListResponse(BaseModel):
    """Private songs visible to the current anonymous session."""

    count: int
    records: list[PrivateSongRecord]


@router.get("/api", tags=["application"])
def application_summary() -> dict[str, str]:
    """Identify the API while the product UI is developed in a later phase."""

    return {
        "name": get_settings().app_name,
        "status": "Phase 4 private song catalog",
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
        phase=4,
    )


@router.get(
    "/api/catalog/options",
    response_model=CatalogOptionsResponse,
    tags=["catalog"],
)
def catalog_options(
    catalog: CatalogDependency,
    private_catalog: PrivateCatalogDependency,
    session_id: SessionDependency,
) -> CatalogOptionsResponse:
    """Return canonical category choices without exposing implementation details."""

    songs = catalog.list_all()
    private_songs = private_catalog.list_songs(session_id)
    return CatalogOptionsResponse(
        song_count=len(songs) + len(private_songs),
        built_in_song_count=len(songs),
        private_song_count=len(private_songs),
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
    private_catalog: PrivateCatalogDependency,
    recommender: RecommenderDependency,
    session_id: SessionDependency,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecommendationResponse:
    """Return transparent recommendations using only validated catalog features."""

    return recommender.recommend(
        preferences=preferences,
        songs=catalog.list_all() + private_catalog.list_songs(session_id),
        limit=limit,
    )


@router.get(
    "/api/songs/private",
    response_model=PrivateSongListResponse,
    tags=["private songs"],
)
def list_private_songs(
    private_catalog: PrivateCatalogDependency,
    session_id: SessionDependency,
) -> PrivateSongListResponse:
    """List private songs owned by the current anonymous session."""

    records = list(private_catalog.list_records(session_id))
    return PrivateSongListResponse(count=len(records), records=records)


@router.post(
    "/api/songs/private",
    response_model=PrivateSongRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["private songs"],
)
def create_private_song(
    submission: ManualSongCreate,
    private_catalog: PrivateCatalogDependency,
    session_id: SessionDependency,
) -> PrivateSongRecord:
    """Add a manually described song to the current session's private catalog."""

    try:
        return private_catalog.create(session_id, submission)
    except PrivateCatalogLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/api/songs/private/{song_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["private songs"],
)
def delete_private_song(
    song_id: str,
    private_catalog: PrivateCatalogDependency,
    session_id: SessionDependency,
) -> Response:
    """Delete a private song only from its owning anonymous session."""

    if not private_catalog.delete(session_id, song_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Private song not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
