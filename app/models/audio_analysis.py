"""Review-first contracts for temporary audio analysis."""

from pydantic import BaseModel, Field

from app.models.private_song import FeatureProvenance, ManualSongCreate


class AudioFileInfo(BaseModel):
    """Non-sensitive facts retained after the uploaded bytes are deleted."""

    original_filename: str
    detected_format: str
    size_bytes: int = Field(gt=0)


class AudioAnalysisProposal(BaseModel):
    """Editable recommendation features proposed from one temporary upload."""

    analysis_id: str
    suggested_song: ManualSongCreate
    provenance: list[FeatureProvenance]
    warnings: list[str]
    analyzer_version: str
    file_info: AudioFileInfo


class AudioAnalysisApproval(BaseModel):
    """User-reviewed values that may enter the private catalog."""

    song: ManualSongCreate
