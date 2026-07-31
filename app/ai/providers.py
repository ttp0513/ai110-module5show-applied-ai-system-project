"""Preference extraction providers with a reproducible local fallback."""

import re
from typing import Protocol

from openai import AsyncOpenAI

from app.ai.prompts import preference_extraction_instructions
from app.models.preference_interpretation import ExtractedPreferences
from app.models.song import Genre, Mood


class PreferenceProviderError(RuntimeError):
    """Raised when a configured model cannot return validated preferences."""


class PreferenceExtractionProvider(Protocol):
    name: str
    model: str

    async def extract(self, prompt: str) -> ExtractedPreferences:
        """Extract supported preferences from untrusted listener text."""


GENRE_CUES = {
    Genre.AMBIENT: ("ambient", "atmospheric", "spacious", "meditation"),
    Genre.CLASSICAL: ("classical", "orchestral", "piano", "strings"),
    Genre.ELECTRONIC: ("electronic", "edm", "digital", "club"),
    Genre.FOLK: ("folk", "storytelling", "earthy"),
    Genre.HIP_HOP: ("hip hop", "hip-hop", "rap", "bars"),
    Genre.INDIE_POP: ("indie pop", "bedroom pop", "alternative pop"),
    Genre.JAZZ: ("jazz", "swing", "improvised"),
    Genre.LATIN: ("latin", "salsa", "reggaeton"),
    Genre.LOFI: ("lofi", "lo-fi", "study beats", "coding beats"),
    Genre.POP: ("pop", "catchy", "singalong"),
    Genre.ROCK: ("rock", "guitar anthem", "guitar"),
    Genre.SYNTHWAVE: ("synthwave", "cyberpunk", "neon", "night drive"),
    Genre.WORLD: ("world music", "global", "traditional"),
}
MOOD_CUES = {
    Mood.CELEBRATORY: ("celebratory", "party", "victory", "festive"),
    Mood.CHILL: ("chill", "cozy", "laid back", "laid-back"),
    Mood.CONFIDENT: ("confident", "bold", "empowered", "swagger"),
    Mood.FOCUSED: ("focused", "focus", "coding", "study", "productive"),
    Mood.HAPPY: ("happy", "joyful", "sunny", "upbeat"),
    Mood.INTENSE: ("intense", "workout", "adrenaline", "powerful"),
    Mood.MOODY: ("moody", "dark", "rainy", "introspective"),
    Mood.RELAXED: ("relaxed", "peaceful", "restful", "unwind"),
    Mood.ROMANTIC: ("romantic", "date night", "love", "intimate", "dreamy"),
}


def _mentioned(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


def _excluded(text: str, value: str) -> bool:
    escaped = re.escape(value)
    return bool(
        re.search(rf"\b(?:avoid|without|no|exclude)\s+(?:any\s+)?{escaped}\b", text)
    )


def _normalized_feature(text: str, name: str) -> float | None:
    percentage = re.search(rf"\b{name}\s*(?:at|around|=|:)?\s*(\d{{1,3}})\s*%", text)
    if percentage:
        return min(1.0, max(0.0, int(percentage.group(1)) / 100))
    levels = (
        (rf"\b(?:low|calm|gentle)\s+{name}\b", 0.25),
        (rf"\b(?:medium|moderate|balanced)\s+{name}\b", 0.55),
        (rf"\b(?:high|strong)\s+{name}\b", 0.85),
    )
    return next((value for pattern, value in levels if re.search(pattern, text)), None)


class DemoPreferenceProvider:
    """Deterministic interpreter used for setup, testing, and provider failure."""

    name = "demo"
    model = "rules-v1"

    async def extract(self, prompt: str) -> ExtractedPreferences:
        text = prompt.casefold()
        excluded_genres = [genre for genre in Genre if _excluded(text, genre.value)]
        excluded_moods = [mood for mood in Mood if _excluded(text, mood.value)]
        genres = [
            genre
            for genre, cues in GENRE_CUES.items()
            if genre not in excluded_genres and _mentioned(text, cues)
        ]
        moods = [
            mood
            for mood, cues in MOOD_CUES.items()
            if mood not in excluded_moods and _mentioned(text, cues)
        ]

        tempo_match = re.search(r"\b(\d{2,3})\s*bpm\b", text)
        tempo = (
            float(tempo_match.group(1))
            if tempo_match and 20 <= int(tempo_match.group(1)) <= 300
            else None
        )
        instrumentalness = _normalized_feature(text, "instrumentalness")
        if instrumentalness is None and ("instrumental" in text or "no vocals" in text):
            instrumentalness = 0.9

        ambiguities: list[str] = []
        if not genres and not moods:
            ambiguities.append(
                "No supported genre or mood was recognized; add a clearer music cue."
            )
        return ExtractedPreferences(
            preferred_genres=genres,
            preferred_moods=moods,
            target_energy=_normalized_feature(text, "energy"),
            target_tempo_bpm=tempo,
            target_valence=_normalized_feature(text, "positivity"),
            target_danceability=_normalized_feature(text, "danceability"),
            target_acousticness=_normalized_feature(text, "acousticness"),
            target_instrumentalness=instrumentalness,
            target_liveness=_normalized_feature(text, "liveness"),
            preferred_release_year=None,
            preferred_duration_seconds=None,
            excluded_genres=excluded_genres,
            excluded_moods=excluded_moods,
            interpretation_summary=(
                "Recognized supported music cues using the local deterministic "
                "interpreter."
            ),
            ambiguities=ambiguities,
        )


class OpenAIPreferenceProvider:
    """Use Responses API Structured Outputs for validated extraction."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: int,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=float(timeout_seconds),
            max_retries=1,
        )

    async def extract(self, prompt: str) -> ExtractedPreferences:
        try:
            response = await self.client.responses.parse(
                model=self.model,
                instructions=preference_extraction_instructions(),
                input=prompt,
                text_format=ExtractedPreferences,
                store=False,
            )
        except Exception as error:
            raise PreferenceProviderError(
                "The configured AI provider is unavailable."
            ) from error
        if response.output_parsed is None:
            raise PreferenceProviderError(
                "The configured AI provider returned no usable interpretation."
            )
        return response.output_parsed
