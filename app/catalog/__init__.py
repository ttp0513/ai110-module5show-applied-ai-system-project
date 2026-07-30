"""Validated built-in and private song catalog access."""

from app.catalog.repository import CatalogRepository, CatalogValidationError

__all__ = ["CatalogRepository", "CatalogValidationError"]
