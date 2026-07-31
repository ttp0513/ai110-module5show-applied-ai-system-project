"""Session-safe lexical retrieval with catalog-grounded output."""

import logging

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.models.retrieval import (
    RetrievalCandidate,
    RetrievalEvidence,
    RetrievalResponse,
)
from app.models.song import Song
from app.retrieval.documents import build_song_document

logger = logging.getLogger(__name__)

RETRIEVAL_METHOD = "catalog-tfidf-cosine"
INDEX_VERSION = "catalog-doc-v1"


def _percentage(value: float) -> str:
    return f"{round(value * 100)}%"


def _ground(song: Song) -> tuple[str, list[RetrievalEvidence]]:
    evidence = [
        RetrievalEvidence(feature="genre", value=song.genre.value),
        RetrievalEvidence(feature="mood", value=song.mood.value),
        RetrievalEvidence(feature="energy", value=_percentage(song.energy)),
        RetrievalEvidence(feature="tempo_bpm", value=f"{round(song.tempo_bpm)} BPM"),
    ]
    explanation = (
        f"Retrieved from the approved catalog: {song.genre.value}, "
        f"{song.mood.value}, {_percentage(song.energy)} energy, and "
        f"{round(song.tempo_bpm)} BPM."
    )
    return explanation, evidence


class CatalogRetrievalService:
    """Retrieve only approved songs supplied for the current request."""

    def search(
        self,
        query: str,
        songs: tuple[Song, ...],
        limit: int,
    ) -> RetrievalResponse:
        """Build an ephemeral index and return grounded catalog candidates."""

        if not songs:
            return RetrievalResponse(
                candidates=[],
                searched_song_count=0,
                retrieval_method=RETRIEVAL_METHOD,
                index_version=INDEX_VERSION,
                limitations=self._limitations(),
            )

        documents = [build_song_document(song) for song in songs]
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents="unicode",
        )
        matrix = vectorizer.fit_transform([*documents, query])
        scores = (matrix[:-1] @ matrix[-1].T).toarray().ravel()
        ranked_indices = np.argsort(-scores, kind="stable")

        candidates: list[RetrievalCandidate] = []
        for index in ranked_indices:
            score = float(scores[index])
            if score <= 0:
                continue
            song = songs[int(index)]
            explanation, evidence = _ground(song)
            candidates.append(
                RetrievalCandidate(
                    rank=len(candidates) + 1,
                    song=song,
                    retrieval_score=round(score, 4),
                    grounded_explanation=explanation,
                    evidence=evidence,
                )
            )
            if len(candidates) == limit:
                break

        logger.info(
            "catalog_retrieval_completed query_length=%s searched=%s hits=%s",
            len(query),
            len(songs),
            len(candidates),
        )
        return RetrievalResponse(
            candidates=candidates,
            searched_song_count=len(songs),
            retrieval_method=RETRIEVAL_METHOD,
            index_version=INDEX_VERSION,
            limitations=self._limitations(),
        )

    @staticmethod
    def _limitations() -> list[str]:
        return [
            "Phase 6 retrieves candidates; Phase 8 will add hybrid ranking.",
            "Descriptions are catalog templates, not language-model claims.",
            "A request with no matching catalog terms may return no candidates.",
        ]
