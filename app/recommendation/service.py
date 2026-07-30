"""Filter, score, and deterministically rank catalog songs."""

from app.models import (
    Recommendation,
    RecommendationResponse,
    Song,
    UserPreferences,
)
from app.recommendation.scorer import CatalogRanges, score_song


class DeterministicRecommender:
    """Recommend catalog songs without an AI or retrieval provider."""

    def recommend(
        self,
        preferences: UserPreferences,
        songs: tuple[Song, ...],
        limit: int = 5,
    ) -> RecommendationResponse:
        """Apply exclusions, score candidates, and preserve stable tie ordering."""

        if limit <= 0:
            raise ValueError("Recommendation limit must be positive.")

        eligible_songs = tuple(
            song
            for song in songs
            if song.genre not in preferences.excluded_genres
            and song.mood not in preferences.excluded_moods
        )
        filtered_song_count = len(songs) - len(eligible_songs)
        if not eligible_songs:
            return RecommendationResponse(
                considered_song_count=0,
                filtered_song_count=filtered_song_count,
                recommendations=[],
            )

        ranges = CatalogRanges.from_songs(songs)
        scored = [
            (source_order, song, *score_song(preferences, song, ranges))
            for source_order, song in enumerate(eligible_songs)
        ]
        scored.sort(key=lambda item: (-item[2], item[0]))

        recommendations = [
            Recommendation(
                rank=rank,
                song=song,
                score=score,
                reasons=reasons,
            )
            for rank, (_, song, score, reasons) in enumerate(
                scored[:limit],
                start=1,
            )
        ]
        return RecommendationResponse(
            considered_song_count=len(eligible_songs),
            filtered_song_count=filtered_song_count,
            recommendations=recommendations,
        )
