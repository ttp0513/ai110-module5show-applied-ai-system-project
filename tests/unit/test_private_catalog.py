"""Verify anonymous private-song storage and provenance."""

import pytest
from pydantic import ValidationError

from app.catalog import SQLitePrivateSongRepository
from app.models import ManualSongCreate, SongOwnerScope, SongSource


def submission(**overrides: object) -> ManualSongCreate:
    """Build a complete valid manual song."""

    values = {
        "title": "User Signal",
        "artist": "Private Artist",
        "genre": "synthwave",
        "mood": "happy",
        "energy": 0.72,
        "tempo_bpm": 112,
        "valence": 0.81,
        "danceability": 0.74,
        "acousticness": 0.18,
        "release_year": 2025,
        "duration_seconds": 214,
        "instrumentalness": 0.68,
        "liveness": 0.12,
    }
    values.update(overrides)
    return ManualSongCreate.model_validate(values)


def test_manual_song_is_private_and_tracks_every_field_source(
    tmp_path,
) -> None:
    repository = SQLitePrivateSongRepository(tmp_path / "private.db")
    session_id = repository.resolve_session(None)

    record = repository.create(session_id, submission())

    assert record.song.source is SongSource.MANUAL
    assert record.song.owner_scope is SongOwnerScope.PRIVATE_CATALOG
    assert len(record.provenance) == 13
    assert {item.source.value for item in record.provenance} == {"user_entered"}


def test_private_repository_isolates_sessions(tmp_path) -> None:
    repository = SQLitePrivateSongRepository(tmp_path / "private.db")
    session_a = repository.resolve_session(None)
    session_b = repository.resolve_session(None)
    repository.create(session_a, submission())

    assert len(repository.list_songs(session_a)) == 1
    assert repository.list_songs(session_b) == ()


def test_manual_song_rejects_unknown_popularity() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        submission(popularity=99)


def test_delete_requires_owning_session(tmp_path) -> None:
    repository = SQLitePrivateSongRepository(tmp_path / "private.db")
    session_a = repository.resolve_session(None)
    session_b = repository.resolve_session(None)
    record = repository.create(session_a, submission())

    assert repository.delete(session_b, record.song.id) is False
    assert repository.delete(session_a, record.song.id) is True
    assert repository.list_songs(session_a) == ()


def test_private_songs_survive_repository_recreation(tmp_path) -> None:
    database_path = tmp_path / "private.db"
    first_repository = SQLitePrivateSongRepository(database_path)
    session_id = first_repository.resolve_session(None)
    created = first_repository.create(session_id, submission())

    restarted_repository = SQLitePrivateSongRepository(database_path)

    records = restarted_repository.list_records(session_id)
    assert len(records) == 1
    assert records[0].song.id == created.song.id
    assert restarted_repository.resolve_session(session_id) == session_id
