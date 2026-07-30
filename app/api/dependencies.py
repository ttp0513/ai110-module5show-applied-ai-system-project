"""Application-owned dependency construction."""

from functools import lru_cache
from pathlib import Path

from app.catalog import CatalogRepository
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
