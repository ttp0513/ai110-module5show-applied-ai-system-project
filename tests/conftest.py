"""Shared dependency isolation for API tests."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from app.api.dependencies import get_analysis_drafts, get_private_catalog
from app.catalog import SQLitePrivateSongRepository
from app.main import app


@pytest.fixture(autouse=True)
def isolated_private_database(
    tmp_path: Path,
) -> Iterator[SQLitePrivateSongRepository]:
    """Prevent tests from reading or mutating the developer's private catalog."""

    repository = SQLitePrivateSongRepository(tmp_path / "private-test.db")
    app.dependency_overrides[get_private_catalog] = lambda: repository
    get_analysis_drafts().clear()
    yield repository
    app.dependency_overrides.pop(get_private_catalog, None)
    get_analysis_drafts().clear()
