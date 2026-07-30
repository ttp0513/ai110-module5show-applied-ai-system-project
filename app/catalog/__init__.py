"""Validated built-in and private song catalog access."""

from app.catalog.private_repository import (
    PrivateCatalogLimitError,
    SQLitePrivateSongRepository,
)
from app.catalog.repository import CatalogRepository, CatalogValidationError

__all__ = [
    "CatalogRepository",
    "CatalogValidationError",
    "PrivateCatalogLimitError",
    "SQLitePrivateSongRepository",
]
