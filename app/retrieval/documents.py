"""Construct searchable text only from canonical approved song fields."""

from app.models.song import Song

GENRE_CONTEXT = {
    "ambient": "atmospheric spacious meditation background calm",
    "classical": "orchestral piano strings timeless study elegant",
    "electronic": "digital synth club futuristic dance",
    "folk": "organic storytelling acoustic earthy",
    "hip hop": "rap beats rhythmic confident bars",
    "indie pop": "alternative catchy bedroom pop youthful",
    "jazz": "improvised sophisticated swing lounge",
    "latin": "rhythmic warm dance celebration",
    "lofi": "study coding homework beats cozy late night",
    "pop": "catchy melodic accessible singalong",
    "rock": "guitar drums anthem energetic",
    "synthwave": "retro neon cyberpunk futuristic night drive",
    "world": "global traditional cultural organic",
}

MOOD_CONTEXT = {
    "celebratory": "party victory festive joyful",
    "chill": "calm cozy easygoing laid back late night",
    "confident": "bold empowered swagger motivation",
    "focused": "study work coding concentration productive",
    "happy": "bright upbeat joyful positive sunny",
    "intense": "powerful dramatic workout adrenaline",
    "moody": "dark introspective rainy emotional",
    "relaxed": "peaceful restful gentle unwind",
    "romantic": "love dreamy intimate date night",
}


def _level(value: float, low: str, medium: str, high: str) -> str:
    if value < 0.34:
        return low
    if value > 0.66:
        return high
    return medium


def build_song_document(song: Song) -> str:
    """Create a reproducible retrieval document with semantic cue words."""

    tempo_label = (
        "slow tempo"
        if song.tempo_bpm < 90
        else "fast tempo"
        if song.tempo_bpm > 130
        else "medium tempo"
    )
    descriptors = (
        _level(song.energy, "low energy calm", "medium energy", "high energy"),
        _level(song.valence, "dark low positivity", "balanced", "bright positive"),
        _level(
            song.danceability,
            "low movement",
            "moderate groove",
            "danceable movement",
        ),
        _level(
            song.acousticness,
            "electronic production",
            "mixed production",
            "acoustic organic",
        ),
        _level(
            song.instrumentalness,
            "vocal song",
            "mixed vocals",
            "instrumental no vocals",
        ),
        tempo_label,
    )
    return " ".join(
        (
            song.title,
            song.artist,
            song.genre.value,
            GENRE_CONTEXT[song.genre.value],
            song.mood.value,
            MOOD_CONTEXT[song.mood.value],
            *descriptors,
            str(song.release_year),
        )
    ).lower()
