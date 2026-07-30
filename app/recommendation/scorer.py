"""Transparent feature similarity scoring without AI dependencies."""

from dataclasses import dataclass

from app.models import FeatureReason, Song, UserPreferences

FEATURE_WEIGHTS = {
    "genre": 0.20,
    "mood": 0.20,
    "energy": 0.12,
    "tempo_bpm": 0.08,
    "valence": 0.08,
    "danceability": 0.08,
    "acousticness": 0.07,
    "instrumentalness": 0.07,
    "liveness": 0.05,
    "release_year": 0.03,
    "duration_seconds": 0.02,
}

RELATED_GENRE_PAIRS = {
    frozenset(("pop", "indie pop")),
    frozenset(("lofi", "ambient")),
    frozenset(("electronic", "synthwave")),
    frozenset(("latin", "world")),
}

RELATED_MOOD_PAIRS = {
    frozenset(("happy", "celebratory")),
    frozenset(("chill", "relaxed")),
    frozenset(("chill", "focused")),
    frozenset(("intense", "confident")),
}

NUMERIC_TARGETS = (
    ("energy", "target_energy", 1.0),
    ("tempo_bpm", "target_tempo_bpm", None),
    ("valence", "target_valence", 1.0),
    ("danceability", "target_danceability", 1.0),
    ("acousticness", "target_acousticness", 1.0),
    ("instrumentalness", "target_instrumentalness", 1.0),
    ("liveness", "target_liveness", 1.0),
    ("release_year", "preferred_release_year", None),
    ("duration_seconds", "preferred_duration_seconds", None),
)


@dataclass(frozen=True)
class CatalogRanges:
    """Observed ranges needed to compare non-normalized catalog features."""

    tempo_bpm: float
    release_year: float
    duration_seconds: float

    @classmethod
    def from_songs(cls, songs: tuple[Song, ...]) -> "CatalogRanges":
        """Calculate safe, nonzero ranges from the current catalog."""

        if not songs:
            raise ValueError("Cannot calculate feature ranges for an empty catalog.")

        def observed_range(feature: str) -> float:
            values = [float(getattr(song, feature)) for song in songs]
            return max(1.0, max(values) - min(values))

        return cls(
            tempo_bpm=observed_range("tempo_bpm"),
            release_year=observed_range("release_year"),
            duration_seconds=observed_range("duration_seconds"),
        )


@dataclass(frozen=True)
class RawSimilarity:
    """One unnormalized feature comparison."""

    feature: str
    similarity: float
    summary: str


def calculate_category_similarity(
    song_value: str,
    preferred_values: list[str],
    related_pairs: set[frozenset[str]],
) -> tuple[float, str]:
    """Compare one category with exact and explicitly related preferences."""

    if song_value in preferred_values:
        return 1.0, f"Exact {song_value} match"

    for preferred_value in preferred_values:
        if frozenset((song_value, preferred_value)) in related_pairs:
            return 0.5, f"{song_value.title()} is related to {preferred_value.title()}"

    return 0.0, f"{song_value.title()} does not match the selected categories"


def calculate_numeric_similarity(
    target: float,
    song_value: float,
    value_range: float,
) -> float:
    """Return normalized closeness constrained to the zero-to-one interval."""

    return max(0.0, 1.0 - abs(target - song_value) / value_range)


def score_song(
    preferences: UserPreferences,
    song: Song,
    ranges: CatalogRanges,
) -> tuple[float, list[FeatureReason]]:
    """Score a song using active preferences and normalized feature weights."""

    similarities: list[RawSimilarity] = []

    if preferences.preferred_genres:
        similarity, summary = calculate_category_similarity(
            song.genre.value,
            [genre.value for genre in preferences.preferred_genres],
            RELATED_GENRE_PAIRS,
        )
        similarities.append(RawSimilarity("genre", similarity, summary))

    if preferences.preferred_moods:
        similarity, summary = calculate_category_similarity(
            song.mood.value,
            [mood.value for mood in preferences.preferred_moods],
            RELATED_MOOD_PAIRS,
        )
        similarities.append(RawSimilarity("mood", similarity, summary))

    for feature, preference_name, fixed_range in NUMERIC_TARGETS:
        target = getattr(preferences, preference_name)
        if target is None:
            continue
        value_range = fixed_range or getattr(ranges, feature)
        song_value = float(getattr(song, feature))
        similarity = calculate_numeric_similarity(
            float(target),
            song_value,
            value_range,
        )
        similarities.append(
            RawSimilarity(
                feature,
                similarity,
                f"Target {float(target):g}; song value {song_value:g}",
            )
        )

    active_weight = sum(FEATURE_WEIGHTS[item.feature] for item in similarities)
    weighted_score = sum(
        FEATURE_WEIGHTS[item.feature] * item.similarity for item in similarities
    )
    score = weighted_score / active_weight

    reasons = [
        FeatureReason(
            feature=item.feature,
            summary=item.summary,
            similarity=item.similarity,
            normalized_weight=FEATURE_WEIGHTS[item.feature] / active_weight,
            contribution=(
                FEATURE_WEIGHTS[item.feature] / active_weight * item.similarity
            ),
        )
        for item in similarities
    ]
    return score, reasons
