"""Phase 2 application and health routes."""

from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel

from app.ai import PreferenceInterpretationService
from app.api.dependencies import (
    get_audio_analysis_service,
    get_catalog,
    get_hybrid_recommender,
    get_preference_interpreter,
    get_private_catalog,
    get_recommender,
    get_retrieval_service,
    get_session_id,
)
from app.audio import (
    AnalysisDraftNotFound,
    AudioAnalysisError,
    AudioAnalysisService,
    AudioValidationError,
)
from app.catalog import (
    CatalogRepository,
    PrivateCatalogLimitError,
    SQLitePrivateSongRepository,
)
from app.config import get_settings
from app.models import (
    Genre,
    HybridRecommendationRequest,
    HybridRecommendationResponse,
    ManualSongCreate,
    Mood,
    PreferenceInterpretationRequest,
    PreferenceInterpretationResponse,
    PrivateSongRecord,
    RecommendationRefinementRequest,
    RecommendationRefinementResponse,
    RecommendationResponse,
    RetrievalQuery,
    RetrievalResponse,
    UserPreferences,
)
from app.models.audio_analysis import AudioAnalysisApproval, AudioAnalysisProposal
from app.recommendation import DeterministicRecommender
from app.retrieval import CatalogRetrievalService
from app.services import HybridRecommendationService

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
RetrievalDependency = Annotated[
    CatalogRetrievalService,
    Depends(get_retrieval_service),
]
PreferenceInterpreterDependency = Annotated[
    PreferenceInterpretationService,
    Depends(get_preference_interpreter),
]
HybridRecommenderDependency = Annotated[
    HybridRecommendationService,
    Depends(get_hybrid_recommender),
]
SessionDependency = Annotated[str, Depends(get_session_id)]
AudioAnalysisDependency = Annotated[
    AudioAnalysisService,
    Depends(get_audio_analysis_service),
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
    built_in_song_count: int
    private_song_count: int
    genres: list[Genre]
    moods: list[Mood]
    recommendation_features: list[str]


class PrivateSongListResponse(BaseModel):
    """Private songs visible to the current anonymous session."""

    count: int
    records: list[PrivateSongRecord]


class ApiCapabilitiesResponse(BaseModel):
    """Public feature and limit discovery for first-party or future clients."""

    api_version: str
    phase: int
    capabilities: list[str]
    default_recommendation_count: int
    maximum_recommendation_count: int
    maximum_prompt_length: int
    maximum_audio_upload_bytes: int
    preference_interpreter_mode: Literal["gemini", "local_demo"]
    preference_interpreter_model: str


@router.get("/api", tags=["application"])
def application_summary() -> dict[str, str]:
    """Identify the API while the product UI is developed in a later phase."""

    return {
        "name": get_settings().app_name,
        "status": "Phase 13 MVP complete",
        "version": "1.0.0",
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
        phase=13,
    )


@router.get(
    "/api/capabilities",
    response_model=ApiCapabilitiesResponse,
    tags=["application"],
)
def api_capabilities() -> ApiCapabilitiesResponse:
    """Expose safe client configuration without credentials or internal paths."""

    settings = get_settings()
    gemini_ready = (
        not settings.demo_mode
        and settings.ai_provider == "gemini"
        and bool(settings.gemini_api_key)
    )
    return ApiCapabilitiesResponse(
        api_version="1.0.0",
        phase=13,
        capabilities=[
            "deterministic_recommendations",
            "hybrid_grounded_recommendations",
            "recommendation_refinement",
            "private_song_catalog",
            "temporary_audio_analysis",
            "ai_preference_interpretation",
            "catalog_retrieval",
            "operational_guardrails",
        ],
        default_recommendation_count=settings.recommendation_count,
        maximum_recommendation_count=20,
        maximum_prompt_length=settings.max_prompt_length,
        maximum_audio_upload_bytes=settings.max_audio_upload_bytes,
        preference_interpreter_mode="gemini" if gemini_ready else "local_demo",
        preference_interpreter_model=(
            settings.ai_model if gemini_ready else "rules-v1"
        ),
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


@router.post(
    "/api/retrieval/search",
    response_model=RetrievalResponse,
    tags=["retrieval"],
)
def retrieve_catalog_candidates(
    request: RetrievalQuery,
    catalog: CatalogDependency,
    private_catalog: PrivateCatalogDependency,
    retrieval: RetrievalDependency,
    session_id: SessionDependency,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RetrievalResponse:
    """Retrieve caller-visible songs and ground output in canonical fields."""

    settings = get_settings()
    if len(request.query) > settings.max_prompt_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The discovery request exceeds the configured "
                f"{settings.max_prompt_length}-character limit."
            ),
        )
    songs = catalog.list_all() + private_catalog.list_songs(session_id)
    return retrieval.search(request.query, songs, limit)


@router.post(
    "/api/preferences/interpret",
    response_model=PreferenceInterpretationResponse,
    tags=["AI preferences"],
)
async def interpret_preferences(
    request: PreferenceInterpretationRequest,
    interpreter: PreferenceInterpreterDependency,
) -> PreferenceInterpretationResponse:
    """Extract reviewable preferences without logging or storing raw text."""

    settings = get_settings()
    if len(request.prompt) > settings.max_prompt_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The prompt exceeds the configured "
                f"{settings.max_prompt_length}-character limit."
            ),
        )
    return await interpreter.interpret(request.prompt)


@router.post(
    "/api/recommendations",
    response_model=HybridRecommendationResponse,
    tags=["recommendations"],
)
def hybrid_recommendations(
    request: HybridRecommendationRequest,
    catalog: CatalogDependency,
    private_catalog: PrivateCatalogDependency,
    hybrid: HybridRecommenderDependency,
    session_id: SessionDependency,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> HybridRecommendationResponse:
    """Combine retrieval relevance with reviewed deterministic preferences."""

    settings = get_settings()
    if len(request.query) > settings.max_prompt_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The query exceeds the configured "
                f"{settings.max_prompt_length}-character limit."
            ),
        )
    songs = catalog.list_all() + private_catalog.list_songs(session_id)
    return hybrid.recommend(
        query=request.query,
        preferences=request.preferences,
        songs=songs,
        candidate_limit=settings.retrieval_candidate_count,
        result_limit=limit,
    )


@router.post(
    "/api/recommendations/refine",
    response_model=RecommendationRefinementResponse,
    tags=["recommendations"],
)
def refine_recommendations(
    request: RecommendationRefinementRequest,
    catalog: CatalogDependency,
    private_catalog: PrivateCatalogDependency,
    hybrid: HybridRecommenderDependency,
    session_id: SessionDependency,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> RecommendationRefinementResponse:
    """Rerank reviewed intent while excluding songs the listener skipped."""

    settings = get_settings()
    if len(request.query) > settings.max_prompt_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The query exceeds the configured "
                f"{settings.max_prompt_length}-character limit."
            ),
        )
    visible_songs = catalog.list_all() + private_catalog.list_songs(session_id)
    songs = tuple(
        song for song in visible_songs if song.id not in request.excluded_song_ids
    )
    excluded_count = len(visible_songs) - len(songs)
    result = hybrid.recommend(
        query=request.query,
        preferences=request.preferences,
        songs=songs,
        candidate_limit=settings.retrieval_candidate_count,
        result_limit=limit,
    )
    return RecommendationRefinementResponse(
        **result.model_dump(),
        excluded_song_count=excluded_count,
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


@router.post(
    "/api/songs/analyze",
    response_model=AudioAnalysisProposal,
    tags=["audio analysis"],
)
async def analyze_audio(
    analysis_service: AudioAnalysisDependency,
    session_id: SessionDependency,
    file: Annotated[UploadFile, File(description="Temporary audio upload")],
    rights_confirmed: Annotated[bool, Form()],
) -> AudioAnalysisProposal:
    """Analyze authorized audio temporarily and return editable suggestions."""

    if not rights_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirm that you have permission to analyze this audio.",
        )
    try:
        return await analysis_service.propose(session_id, file)
    except (AudioValidationError, AudioAnalysisError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post(
    "/api/songs/analyzed/{analysis_id}/approve",
    response_model=PrivateSongRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["audio analysis"],
)
def approve_audio_analysis(
    analysis_id: str,
    approval: AudioAnalysisApproval,
    analysis_service: AudioAnalysisDependency,
    private_catalog: PrivateCatalogDependency,
    session_id: SessionDependency,
) -> PrivateSongRecord:
    """Save only user-reviewed values; uploaded audio is already deleted."""

    try:
        return analysis_service.approve(
            session_id,
            analysis_id,
            approval.song,
            private_catalog,
        )
    except AnalysisDraftNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis draft not found.",
        ) from error
    except PrivateCatalogLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete(
    "/api/songs/analyzed/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["audio analysis"],
)
def cancel_audio_analysis(
    analysis_id: str,
    analysis_service: AudioAnalysisDependency,
    session_id: SessionDependency,
) -> Response:
    """Discard an unapproved analysis proposal."""

    try:
        analysis_service.cancel(session_id, analysis_id)
    except AnalysisDraftNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis draft not found.",
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
