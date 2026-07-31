"""Validated contracts for grounded catalog retrieval."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.song import Song


class RetrievalQuery(BaseModel):
    """A bounded, untrusted natural-language discovery request."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=3, max_length=1000)


class RetrievalEvidence(BaseModel):
    """One catalog fact used in a grounded candidate explanation."""

    feature: str
    value: str


class RetrievalCandidate(BaseModel):
    """An approved song retrieved from the caller-visible catalog."""

    rank: int = Field(ge=1)
    song: Song
    retrieval_score: float = Field(ge=0.0, le=1.0)
    grounded_explanation: str
    evidence: list[RetrievalEvidence]


class RetrievalResponse(BaseModel):
    """Phase 6 retrieval result with explicit system limitations."""

    candidates: list[RetrievalCandidate]
    searched_song_count: int = Field(ge=0)
    retrieval_method: str
    index_version: str
    limitations: list[str]
