"""Short-lived, session-owned analysis proposals containing no audio."""

from dataclasses import dataclass
from threading import RLock

from app.models.audio_analysis import AudioAnalysisProposal


class AnalysisDraftNotFound(KeyError):
    """Raised when a draft is missing or belongs to another session."""


@dataclass(frozen=True)
class AnalysisDraft:
    session_id: str
    proposal: AudioAnalysisProposal


class AnalysisDraftRepository:
    """Keep review drafts in process memory until approved or cancelled."""

    def __init__(self) -> None:
        self._drafts: dict[str, AnalysisDraft] = {}
        self._lock = RLock()

    def put(self, session_id: str, proposal: AudioAnalysisProposal) -> None:
        with self._lock:
            self._drafts[proposal.analysis_id] = AnalysisDraft(session_id, proposal)

    def get(self, session_id: str, analysis_id: str) -> AudioAnalysisProposal:
        with self._lock:
            draft = self._drafts.get(analysis_id)
            if draft is None or draft.session_id != session_id:
                raise AnalysisDraftNotFound(analysis_id)
            return draft.proposal

    def pop(self, session_id: str, analysis_id: str) -> AudioAnalysisProposal:
        proposal = self.get(session_id, analysis_id)
        with self._lock:
            del self._drafts[analysis_id]
        return proposal

    def clear(self) -> None:
        with self._lock:
            self._drafts.clear()
