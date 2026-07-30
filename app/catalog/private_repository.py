"""SQLite-backed private song and anonymous-session persistence."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from uuid import UUID, uuid4

from app.models.private_song import (
    FeatureProvenance,
    FeatureSource,
    ManualSongCreate,
    PrivateSongRecord,
)
from app.models.song import Song, SongOwnerScope, SongSource

MAX_PRIVATE_SONGS_PER_SESSION = 100


class PrivateCatalogLimitError(ValueError):
    """Raised when an anonymous session reaches its private-song limit."""


class SQLitePrivateSongRepository:
    """Persist private songs and anonymous ownership in one local SQLite file."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS anonymous_sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS private_songs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    energy REAL NOT NULL,
                    tempo_bpm REAL NOT NULL,
                    valence REAL NOT NULL,
                    danceability REAL NOT NULL,
                    acousticness REAL NOT NULL,
                    release_year INTEGER NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    instrumentalness REAL NOT NULL,
                    liveness REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id)
                        REFERENCES anonymous_sessions(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_private_songs_session
                    ON private_songs(session_id);

                CREATE TABLE IF NOT EXISTS feature_provenance (
                    song_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    confidence REAL,
                    model_version TEXT,
                    user_corrected INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (song_id, feature_name),
                    FOREIGN KEY (song_id)
                        REFERENCES private_songs(id)
                        ON DELETE CASCADE
                );
                """
            )

    def resolve_session(self, proposed_id: str | None) -> str:
        """Reuse a persisted valid session or issue and persist a new UUID."""

        with self._lock, self._connect() as connection:
            if proposed_id and self._is_valid_uuid(proposed_id):
                existing = connection.execute(
                    "SELECT 1 FROM anonymous_sessions WHERE id = ?",
                    (proposed_id,),
                ).fetchone()
                if existing:
                    return proposed_id

            session_id = str(uuid4())
            connection.execute(
                "INSERT INTO anonymous_sessions (id) VALUES (?)",
                (session_id,),
            )
            return session_id

    @staticmethod
    def _is_valid_uuid(value: str) -> bool:
        try:
            return str(UUID(value)) == value
        except ValueError:
            return False

    def create(
        self,
        session_id: str,
        submission: ManualSongCreate,
    ) -> PrivateSongRecord:
        """Create a durable private song with user-entered provenance."""

        with self._lock, self._connect() as connection:
            session_exists = connection.execute(
                "SELECT 1 FROM anonymous_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if not session_exists:
                raise ValueError("The anonymous session is not registered.")

            count = connection.execute(
                "SELECT COUNT(*) FROM private_songs WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]
            if count >= MAX_PRIVATE_SONGS_PER_SESSION:
                raise PrivateCatalogLimitError(
                    "The private catalog limit has been reached for this session."
                )

            song_id = f"user-{uuid4().hex}"
            values = submission.model_dump()
            connection.execute(
                """
                INSERT INTO private_songs (
                    id, session_id, title, artist, genre, mood, energy,
                    tempo_bpm, valence, danceability, acousticness,
                    release_year, duration_seconds, instrumentalness, liveness
                ) VALUES (
                    :id, :session_id, :title, :artist, :genre, :mood, :energy,
                    :tempo_bpm, :valence, :danceability, :acousticness,
                    :release_year, :duration_seconds, :instrumentalness, :liveness
                )
                """,
                {
                    "id": song_id,
                    "session_id": session_id,
                    **values,
                },
            )
            connection.executemany(
                """
                INSERT INTO feature_provenance (
                    song_id, feature_name, source, user_corrected
                ) VALUES (?, ?, ?, 0)
                """,
                [
                    (song_id, feature_name, FeatureSource.USER_ENTERED.value)
                    for feature_name in values
                ],
            )
            return self._record_from_values(song_id, values)

    @staticmethod
    def _record_from_values(
        song_id: str,
        values: dict[str, object],
    ) -> PrivateSongRecord:
        song = Song(
            id=song_id,
            **values,
            source=SongSource.MANUAL,
            owner_scope=SongOwnerScope.PRIVATE_CATALOG,
        )
        provenance = [
            FeatureProvenance(
                feature_name=feature_name,
                source=FeatureSource.USER_ENTERED,
            )
            for feature_name in values
        ]
        return PrivateSongRecord(song=song, provenance=provenance)

    def list_records(self, session_id: str) -> tuple[PrivateSongRecord, ...]:
        """Return durable records owned by the supplied anonymous session."""

        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, artist, genre, mood, energy, tempo_bpm,
                       valence, danceability, acousticness, release_year,
                       duration_seconds, instrumentalness, liveness
                FROM private_songs
                WHERE session_id = ?
                ORDER BY created_at, id
                """,
                (session_id,),
            ).fetchall()

            records: list[PrivateSongRecord] = []
            for row in rows:
                row_values = dict(row)
                values = {
                    key: value for key, value in row_values.items() if key != "id"
                }
                provenance_rows = connection.execute(
                    """
                    SELECT feature_name, source, confidence, model_version,
                           user_corrected
                    FROM feature_provenance
                    WHERE song_id = ?
                    ORDER BY rowid
                    """,
                    (row["id"],),
                ).fetchall()
                song = Song(
                    id=row["id"],
                    **values,
                    source=SongSource.MANUAL,
                    owner_scope=SongOwnerScope.PRIVATE_CATALOG,
                )
                provenance = [
                    FeatureProvenance(
                        feature_name=item["feature_name"],
                        source=item["source"],
                        confidence=item["confidence"],
                        model_version=item["model_version"],
                        user_corrected=bool(item["user_corrected"]),
                    )
                    for item in provenance_rows
                ]
                records.append(PrivateSongRecord(song=song, provenance=provenance))
            return tuple(records)

    def list_songs(self, session_id: str) -> tuple[Song, ...]:
        """Return canonical private songs for recommendation."""

        return tuple(record.song for record in self.list_records(session_id))

    def delete(self, session_id: str, song_id: str) -> bool:
        """Delete a song only when it belongs to the supplied session."""

        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM private_songs WHERE id = ? AND session_id = ?",
                (song_id, session_id),
            )
            return cursor.rowcount == 1

    def clear(self) -> None:
        """Clear persisted test state while preserving the schema."""

        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM anonymous_sessions")
