"""Orchestrate temporary upload, analysis, review, and persistence."""

import logging
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.audio.analyzer import AudioAnalyzer
from app.audio.drafts import AnalysisDraftRepository
from app.audio.validator import store_validated_upload
from app.catalog.private_repository import SQLitePrivateSongRepository
from app.models.audio_analysis import AudioAnalysisProposal
from app.models.private_song import (
    FeatureProvenance,
    ManualSongCreate,
    PrivateSongRecord,
)
from app.models.song import SongSource

logger = logging.getLogger(__name__)


class AudioAnalysisService:
    """Enforce deletion and user approval around audio-derived values."""

    def __init__(
        self,
        analyzer: AudioAnalyzer,
        drafts: AnalysisDraftRepository,
        upload_directory: Path,
        max_upload_bytes: int,
    ) -> None:
        self.analyzer = analyzer
        self.drafts = drafts
        self.upload_directory = upload_directory
        self.max_upload_bytes = max_upload_bytes

    async def propose(
        self,
        session_id: str,
        upload: UploadFile,
    ) -> AudioAnalysisProposal:
        analysis_id = uuid4().hex
        stored = None
        try:
            stored = await store_validated_upload(
                upload,
                self.upload_directory,
                self.max_upload_bytes,
            )
            proposal = await run_in_threadpool(
                self.analyzer.analyze,
                stored.path,
                Path(upload.filename or "untitled").name,
                stored.detected_format,
                stored.size_bytes,
                analysis_id,
            )
            self.drafts.put(session_id, proposal)
            logger.info(
                "audio_analysis_completed analysis_id=%s format=%s bytes=%s",
                analysis_id,
                stored.detected_format,
                stored.size_bytes,
            )
            return proposal
        finally:
            if stored is not None:
                stored.path.unlink(missing_ok=True)
                logger.info(
                    "temporary_audio_deleted analysis_id=%s",
                    analysis_id,
                )

    def approve(
        self,
        session_id: str,
        analysis_id: str,
        reviewed: ManualSongCreate,
        private_catalog: SQLitePrivateSongRepository,
    ) -> PrivateSongRecord:
        proposal = self.drafts.get(session_id, analysis_id)
        suggested = proposal.suggested_song.model_dump()
        provenance_by_name = {
            item.feature_name: item.model_copy(
                update={
                    "user_corrected": reviewed.model_dump()[item.feature_name]
                    != suggested[item.feature_name]
                }
            )
            for item in proposal.provenance
        }
        provenance: list[FeatureProvenance] = [
            provenance_by_name[name] for name in reviewed.model_dump()
        ]
        record = private_catalog.create(
            session_id,
            reviewed,
            provenance=provenance,
            source=SongSource.UPLOAD,
        )
        self.drafts.pop(session_id, analysis_id)
        logger.info(
            "audio_analysis_approved analysis_id=%s song_id=%s",
            analysis_id,
            record.song.id,
        )
        return record

    def cancel(self, session_id: str, analysis_id: str) -> None:
        self.drafts.pop(session_id, analysis_id)
        logger.info("audio_analysis_cancelled analysis_id=%s", analysis_id)
