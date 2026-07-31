"""Small specialized classifiers trained on the approved VYBE catalog."""

from dataclasses import dataclass

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.models.song import Genre, Mood, Song

FEATURE_NAMES = (
    "energy",
    "tempo_bpm",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "liveness",
    "duration_seconds",
)
MODEL_VERSION = "catalog-knn-v1"


@dataclass(frozen=True)
class CategoryPrediction:
    """One model prediction with a comparable confidence score."""

    value: str
    confidence: float


class CatalogCategoryClassifier:
    """Estimate supported categories from numeric recommendation features."""

    def __init__(self, songs: tuple[Song, ...]) -> None:
        if len(songs) < 5:
            raise ValueError("At least five catalog songs are required for training.")
        matrix = np.asarray(
            [[float(getattr(song, name)) for name in FEATURE_NAMES] for song in songs]
        )
        neighbors = min(5, len(songs))
        self._genre = make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=neighbors, weights="distance"),
        ).fit(matrix, [song.genre.value for song in songs])
        self._mood = make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=neighbors, weights="distance"),
        ).fit(matrix, [song.mood.value for song in songs])

    @staticmethod
    def _predict(model: object, vector: list[float]) -> CategoryPrediction:
        probabilities = model.predict_proba([vector])[0]
        index = int(np.argmax(probabilities))
        return CategoryPrediction(
            value=str(model.classes_[index]),
            confidence=round(float(probabilities[index]), 3),
        )

    def predict(
        self, features: dict[str, float]
    ) -> tuple[tuple[Genre, float], tuple[Mood, float]]:
        """Return genre and mood estimates constrained to supported categories."""

        vector = [features[name] for name in FEATURE_NAMES]
        genre = self._predict(self._genre, vector)
        mood = self._predict(self._mood, vector)
        return (Genre(genre.value), genre.confidence), (
            Mood(mood.value),
            mood.confidence,
        )
