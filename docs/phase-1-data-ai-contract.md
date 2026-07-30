# Phase 1: Data and AI Contract

## 1. Canonical song record

Every built-in or user-added song must expose the same recommendation fields.

| Field | Type | Required | Valid value |
|---|---|---:|---|
| `id` | string | Yes | Unique, non-empty identifier |
| `title` | string | Yes | Non-empty display text |
| `artist` | string | Yes | Non-empty display text |
| `genre` | string | Yes | Supported normalized category |
| `mood` | string | Yes | Supported normalized category |
| `energy` | float | Yes | 0.0 through 1.0 |
| `tempo_bpm` | float | Yes | Positive BPM within configured limits |
| `valence` | float | Yes | 0.0 through 1.0 |
| `danceability` | float | Yes | 0.0 through 1.0 |
| `acousticness` | float | Yes | 0.0 through 1.0 |
| `instrumentalness` | float | Yes | 0.0 through 1.0 |
| `liveness` | float | Yes | 0.0 through 1.0 |
| `release_year` | integer | Yes | Configured historical through current year |
| `duration_seconds` | integer | Yes | Positive supported duration |
| `source` | enum | Yes | `built_in`, `upload`, or `manual` |
| `owner_scope` | enum | Yes | `public_catalog` or `private_catalog` |

Popularity and familiarity are intentionally excluded. They cannot be
determined from the audio itself, are difficult to maintain accurately, and
would treat built-in and user-added songs inconsistently.

## 2. Feature provenance

Each user-added feature must record:

| Field | Purpose |
|---|---|
| `feature_name` | Canonical feature being described |
| `source` | `measured`, `ai_estimated`, `embedded_metadata`, or `user_entered` |
| `confidence` | Optional 0.0 through 1.0 model confidence |
| `model_version` | Optional analyzer identifier |
| `user_corrected` | Whether the listener replaced the proposed value |

User-confirmed values are authoritative for the private catalog.

## 3. Structured vibe interpretation

Natural-language interpretation may return only supported fields:

- `intent_summary`
- `preferred_genres`
- `preferred_moods`
- numeric targets corresponding to canonical song features
- explicit minimum and maximum constraints
- excluded genres and moods
- `confidence`
- `needs_clarification`
- `clarification_question`

Unknown properties, invalid ranges, and unsupported categories must fail schema
validation rather than silently reaching the ranking engine.

## 4. Retrieval contract

Retrieval must:

1. Search only approved built-in and current-user private documents.
2. Return canonical song IDs and normalized relevance values.
3. Apply hard exclusions before final ranking.
4. Never make another user's private song available.
5. Log identifiers and scores without copying private audio.
6. Return an explicit unavailable state if the index cannot be used.

Retrieved records must materially determine the hybrid candidate set.

## 5. Recommendation contract

Each recommendation contains:

- Canonical song record
- Rank
- Deterministic feature-match score
- Retrieval relevance score
- Constraint-satisfaction score
- Final hybrid score
- Structured supporting feature contributions
- Grounded explanation or deterministic fallback

All scores exposed as normalized values must remain from 0.0 through 1.0.
Ties must be resolved deterministically.

## 6. Explanation contract

Generated explanations may use only:

- Validated listener preferences
- Retrieved catalog records
- Calculated scores and contributions
- Explicit constraint results

Before display, validation must confirm:

- Song ID, title, and artist match the catalog.
- Numeric claims match canonical feature values.
- Claimed supporting features were actually active.
- No lyrical, cultural, or production claim was invented.

An invalid explanation is replaced by a deterministic template.

## 7. Audio-analysis contract

Audio analysis may:

- Measure duration and estimate tempo.
- Read permitted embedded metadata.
- Estimate genre, mood, energy, valence, danceability, acousticness,
  instrumentalness, and liveness.

It must not:

- Claim perfect or objective understanding.
- Save results without user review.
- Make uploaded audio public.
- Treat model confidence as certainty.

Partial success is valid. Measured or validated fields must be preserved while
the user manually completes missing fields.

## 8. Playback contract

VYBE returns recommendation metadata and explanations only. It does not
stream, preview, or play built-in or user-uploaded songs. Audio uploads are
temporary analysis inputs rather than playable library assets. Temporary audio
must be deleted when analysis finishes, fails, or is cancelled.

## 9. Failure contract

| Failure | Required behavior |
|---|---|
| Language model unavailable | Use manual controls and deterministic scoring |
| Invalid AI schema | Retry once if safe, then fall back |
| Retrieval unavailable | Use deterministic full-catalog scoring |
| Explanation fails grounding | Use deterministic explanation |
| Audio analysis partially fails | Preserve valid results and open manual form |
| Audio analysis fully fails | Offer retry or complete manual entry |
| Invalid audio file | Reject safely without indexing |
| Empty catalog | Display a recoverable no-catalog state |
