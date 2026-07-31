"""Signal measurements and reviewable feature estimates for uploaded audio."""

from datetime import UTC, datetime
from pathlib import Path

import librosa
import numpy as np
from mutagen import File as MutagenFile

from app.audio.classifier import MODEL_VERSION, CatalogCategoryClassifier
from app.models.audio_analysis import AudioAnalysisProposal, AudioFileInfo
from app.models.private_song import (
    FeatureProvenance,
    FeatureSource,
    ManualSongCreate,
)

ANALYZER_VERSION = "vybe-audio-v1"


class AudioAnalysisError(ValueError):
    """Raised when safe, useful audio features cannot be extracted."""


def _bounded(value: float) -> float:
    return round(float(np.clip(value, 0.0, 1.0)), 3)


def _first_tag(tags: object, names: tuple[str, ...]) -> str | None:
    if not tags:
        return None
    for name in names:
        value = tags.get(name)
        if value:
            candidate = value[0] if isinstance(value, list) else value
            text = str(candidate).strip()
            if text:
                return text
    return None


class AudioAnalyzer:
    """Analyze audio without retaining its waveform or file."""

    def __init__(
        self,
        classifier: CatalogCategoryClassifier,
        max_duration_seconds: int,
    ) -> None:
        self.classifier = classifier
        self.max_duration_seconds = max_duration_seconds

    def analyze(
        self,
        path: Path,
        original_filename: str,
        detected_format: str,
        size_bytes: int,
        analysis_id: str,
    ) -> AudioAnalysisProposal:
        """Create a transparent, editable proposal from one local temporary file."""

        try:
            metadata = MutagenFile(path, easy=True)
            tags = metadata.tags if metadata else None
            y, sample_rate = librosa.load(
                path,
                sr=22050,
                mono=True,
                duration=self.max_duration_seconds + 1,
            )
        except Exception as error:
            raise AudioAnalysisError(
                "The audio could not be decoded. Try another supported file."
            ) from error

        duration = float(librosa.get_duration(y=y, sr=sample_rate))
        if duration < 15:
            raise AudioAnalysisError("Audio must be at least 15 seconds long.")
        if duration > self.max_duration_seconds:
            raise AudioAnalysisError(
                f"Audio must be {self.max_duration_seconds} seconds or shorter."
            )
        if y.size == 0 or float(np.max(np.abs(y))) < 0.001:
            raise AudioAnalysisError("The audio is silent or too quiet to analyze.")

        rms = librosa.feature.rms(y=y)[0]
        onset = librosa.onset.onset_strength(y=y, sr=sample_rate)
        tempo_value, _ = librosa.beat.beat_track(
            onset_envelope=onset,
            sr=sample_rate,
        )
        tempo = float(np.asarray(tempo_value).reshape(-1)[0])
        if not np.isfinite(tempo) or tempo < 20:
            tempo = 90.0
        tempo = round(float(np.clip(tempo, 20.0, 300.0)), 1)

        centroid = librosa.feature.spectral_centroid(y=y, sr=sample_rate)[0]
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        zero_crossing = librosa.feature.zero_crossing_rate(y)[0]
        contrast = librosa.feature.spectral_contrast(y=y, sr=sample_rate)
        chroma = librosa.feature.chroma_stft(y=y, sr=sample_rate)

        energy = _bounded(np.mean(rms) * 5.0)
        brightness = _bounded(np.mean(centroid) / 5000.0)
        percussiveness = _bounded(np.std(onset) / (np.mean(onset) + 1e-6))
        tonal_strength = _bounded(np.max(np.mean(chroma, axis=1)) * 2.0)
        features = {
            "energy": energy,
            "tempo_bpm": tempo,
            "valence": _bounded(
                0.2 + 0.35 * brightness + 0.25 * energy + 0.2 * tonal_strength
            ),
            "danceability": _bounded(
                0.35 * (tempo / 180.0)
                + 0.4 * percussiveness
                + 0.25 * (1.0 - np.std(onset) / (np.mean(onset) + 1e-6))
            ),
            "acousticness": _bounded(
                0.7 * (1.0 - brightness) + 0.3 * (1.0 - np.mean(flatness) * 5.0)
            ),
            "instrumentalness": _bounded(
                0.55 * tonal_strength + 0.45 * (1.0 - np.mean(zero_crossing) * 8.0)
            ),
            "liveness": _bounded(
                0.5 * np.std(rms) * 10.0 + 0.5 * np.mean(contrast) / 40.0
            ),
            "duration_seconds": float(round(duration)),
        }
        (genre, genre_confidence), (mood, mood_confidence) = self.classifier.predict(
            features
        )

        title = _first_tag(tags, ("title",)) or Path(original_filename).stem
        artist = _first_tag(tags, ("artist", "albumartist")) or "Unknown Artist"
        date_text = _first_tag(tags, ("date", "year"))
        current_year = datetime.now(UTC).year
        try:
            release_year = int((date_text or "").strip()[:4])
            if not 1900 <= release_year <= current_year:
                raise ValueError
            year_source = FeatureSource.EMBEDDED_METADATA
        except ValueError:
            release_year = current_year
            year_source = FeatureSource.USER_ENTERED

        suggested = ManualSongCreate(
            title=title[:200],
            artist=artist[:200],
            genre=genre,
            mood=mood,
            release_year=release_year,
            **features,
        )
        metadata_source = {
            "title": (
                FeatureSource.EMBEDDED_METADATA
                if _first_tag(tags, ("title",))
                else FeatureSource.USER_ENTERED
            ),
            "artist": (
                FeatureSource.EMBEDDED_METADATA
                if _first_tag(tags, ("artist", "albumartist"))
                else FeatureSource.USER_ENTERED
            ),
            "release_year": year_source,
        }
        provenance = [
            FeatureProvenance(feature_name=name, source=source)
            for name, source in metadata_source.items()
        ]
        provenance.extend(
            [
                FeatureProvenance(
                    feature_name="genre",
                    source=FeatureSource.AI_ESTIMATED,
                    confidence=genre_confidence,
                    model_version=MODEL_VERSION,
                ),
                FeatureProvenance(
                    feature_name="mood",
                    source=FeatureSource.AI_ESTIMATED,
                    confidence=mood_confidence,
                    model_version=MODEL_VERSION,
                ),
                FeatureProvenance(
                    feature_name="tempo_bpm",
                    source=FeatureSource.MEASURED,
                    model_version=ANALYZER_VERSION,
                ),
                FeatureProvenance(
                    feature_name="duration_seconds",
                    source=FeatureSource.MEASURED,
                    model_version=ANALYZER_VERSION,
                ),
            ]
        )
        provenance.extend(
            FeatureProvenance(
                feature_name=name,
                source=FeatureSource.ALGORITHM_ESTIMATED,
                model_version=ANALYZER_VERSION,
            )
            for name in (
                "energy",
                "valence",
                "danceability",
                "acousticness",
                "instrumentalness",
                "liveness",
            )
        )
        warnings = [
            "Genre and mood are specialized-model estimates, not facts.",
            "All acoustic feature values are approximations and must be reviewed.",
        ]
        if genre_confidence < 0.6 or mood_confidence < 0.6:
            warnings.append(
                "At least one category has low confidence; please correct it."
            )
        if artist == "Unknown Artist":
            warnings.append("No embedded artist was found.")

        return AudioAnalysisProposal(
            analysis_id=analysis_id,
            suggested_song=suggested,
            provenance=provenance,
            warnings=warnings,
            analyzer_version=ANALYZER_VERSION,
            file_info=AudioFileInfo(
                original_filename=Path(original_filename).name,
                detected_format=detected_format,
                size_bytes=size_bytes,
            ),
        )
