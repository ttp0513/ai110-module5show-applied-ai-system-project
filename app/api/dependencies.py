"""Application-owned dependency construction."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, Response

from app.catalog import CatalogRepository, SQLitePrivateSongRepository
from app.config import get_settings
from app.recommendation import DeterministicRecommender

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
def get_private_catalog() -> SQLitePrivateSongRepository:
    """Return durable private storage shared within the application process."""

    configured_path = get_settings().private_database_path
    database_path = (
        configured_path
        if configured_path.is_absolute()
        else PROJECT_ROOT / configured_path
    )
    return SQLitePrivateSongRepository(database_path)


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
