"""Combine catalog retrieval with transparent deterministic feature scoring."""

from dataclasses import dataclass

from app.models.hybrid import (
    HybridRecommendation,
    HybridRecommendationResponse,
    HybridScoreEvidence,
)
from app.models.preferences import UserPreferences
from app.models.recommendation import FeatureReason
from app.models.song import Song
from app.recommendation.scorer import CatalogRanges, score_song
from app.retrieval import CatalogRetrievalService

RETRIEVAL_WEIGHT = 0.35
FEATURE_WEIGHT = 0.65


@dataclass(frozen=True)
class ScoredCandidate:
    """Internal candidate before stable final ranking."""

    source_order: int
    song: Song
    retrieval_score: float
    normalized_retrieval_score: float
    feature_score: float
    final_score: float
    reasons: list[FeatureReason]


def _explain(candidate: ScoredCandidate, used_fallback: bool) -> str:
    strongest = sorted(
        candidate.reasons,
        key=lambda reason: reason.contribution,
        reverse=True,
    )[:2]
    feature_text = "; ".join(reason.summary for reason in strongest)
    if used_fallback:
        return (
            "Ranked by reviewed music preferences because retrieval found no "
            f"text match. Strongest evidence: {feature_text}."
        )
    return (
        "Retrieved from the approved catalog and ranked by reviewed preferences. "
        f"Strongest evidence: {feature_text}."
    )


class HybridRecommendationService:
    """Retrieve candidates, score features, and generate evidence-only prose."""

    def __init__(self, retrieval: CatalogRetrievalService) -> None:
        self.retrieval = retrieval

    def recommend(
        self,
        query: str,
        preferences: UserPreferences,
        songs: tuple[Song, ...],
        candidate_limit: int,
        result_limit: int,
    ) -> HybridRecommendationResponse:
        eligible = tuple(
            song
            for song in songs
            if song.genre not in preferences.excluded_genres
            and song.mood not in preferences.excluded_moods
        )
        filtered_count = len(songs) - len(eligible)
        if not eligible:
            return HybridRecommendationResponse(
                considered_song_count=0,
                filtered_song_count=filtered_count,
                retrieved_candidate_count=0,
                used_retrieval_fallback=False,
                recommendations=[],
            )

        retrieval_response = self.retrieval.search(query, eligible, candidate_limit)
        used_fallback = not retrieval_response.candidates
        retrieval_scores = {
            candidate.song.id: candidate.retrieval_score
            for candidate in retrieval_response.candidates
        }
        candidates = (
            eligible
            if used_fallback
            else tuple(candidate.song for candidate in retrieval_response.candidates)
        )
        maximum_retrieval = max(retrieval_scores.values(), default=1.0)
        ranges = CatalogRanges.from_songs(eligible)
        order_by_id = {song.id: index for index, song in enumerate(eligible)}

        scored: list[ScoredCandidate] = []
        for song in candidates:
            feature_score, reasons = score_song(preferences, song, ranges)
            raw_retrieval = retrieval_scores.get(song.id, 0.0)
            normalized_retrieval = (
                raw_retrieval / maximum_retrieval if maximum_retrieval else 0.0
            )
            final_score = (
                feature_score
                if used_fallback
                else FEATURE_WEIGHT * feature_score
                + RETRIEVAL_WEIGHT * normalized_retrieval
            )
            scored.append(
                ScoredCandidate(
                    source_order=order_by_id[song.id],
                    song=song,
                    retrieval_score=raw_retrieval,
                    normalized_retrieval_score=normalized_retrieval,
                    feature_score=feature_score,
                    final_score=final_score,
                    reasons=reasons,
                )
            )
        scored.sort(key=lambda item: (-item.final_score, item.source_order))

        recommendations = [
            HybridRecommendation(
                rank=rank,
                song=item.song,
                score=round(item.final_score, 6),
                reasons=item.reasons,
                score_evidence=HybridScoreEvidence(
                    retrieval_score=item.retrieval_score,
                    normalized_retrieval_score=item.normalized_retrieval_score,
                    feature_score=item.feature_score,
                    retrieval_weight=0.0 if used_fallback else RETRIEVAL_WEIGHT,
                    feature_weight=1.0 if used_fallback else FEATURE_WEIGHT,
                ),
                grounded_explanation=_explain(item, used_fallback),
            )
            for rank, item in enumerate(scored[:result_limit], start=1)
        ]
        return HybridRecommendationResponse(
            considered_song_count=len(candidates),
            filtered_song_count=filtered_count,
            retrieved_candidate_count=len(retrieval_response.candidates),
            used_retrieval_fallback=used_fallback,
            recommendations=recommendations,
        )
