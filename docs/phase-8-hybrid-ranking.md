# Phase 8: Hybrid ranking and grounded explanations

## Outcome

Phase 8 unifies the previous capabilities into the primary recommendation
journey:

1. A listener describes a vibe.
2. Phase 7 extracts supported preferences.
3. The listener reviews, applies, and may correct those preferences.
4. Phase 6 retrieves caller-visible candidate songs using the original text.
5. Phase 8 scores those candidates against the reviewed preferences.
6. VYBE returns one ranked list with reproducible score evidence and grounded
   explanations.

Manual-only recommendations remain available through the deterministic Phase 3
endpoint.

## Hybrid score

For a successful retrieval:

```text
normalized retrieval = raw retrieval score / largest candidate retrieval score
final score = 0.35 × normalized retrieval + 0.65 × feature score
```

The retrieval component captures how well a song document matches the
listener's wording. The feature component uses the existing auditable genre,
mood, energy, tempo, positivity, danceability, acousticness,
instrumentalness, liveness, year, and duration scorer.

Feature similarity receives the larger weight because the listener has
reviewed those values explicitly. The 35/65 split is an initial product policy,
not a learned truth, and is protected by fixed regression tests.

Exclusions run before retrieval and ranking. Popularity and listening history
remain absent.

## Retrieval fallback

If the text query has no positive match, VYBE does not return an empty final
recommendation set. It ranks the full eligible catalog using reviewed feature
preferences only and reports:

```text
used_retrieval_fallback = true
retrieval_weight = 0
feature_weight = 1
```

This preserves a useful, reproducible journey when retrieval vocabulary is
insufficient.

## Grounded explanations

Phase 8 deliberately generates explanation prose from validated score evidence
rather than asking a language model to invent prose. Each explanation can
claim only:

- whether retrieval or retrieval fallback was used;
- exact feature-match summaries already returned by the scorer;
- the approved song attached to that evidence.

The UI displays the hybrid score, retrieval contribution, feature
contribution, and the original per-feature reasons. This is a reliability
choice: a future prose model can replace the renderer only if every claim is
validated against the same evidence contract.

## Privacy

The hybrid service receives the built-in catalog plus private songs owned by
the current anonymous session. Retrieval and ranking never query another
session's records. Tests add a uniquely named private song and verify that it
can rank first for its owner but never appears for another client.

## API

`POST /api/recommendations?limit=5`

```json
{
  "query": "romantic neon night drive",
  "preferences": {
    "preferred_genres": ["synthwave"],
    "preferred_moods": ["romantic"],
    "target_energy": 0.55
  }
}
```

The nested preferences must pass the same `UserPreferences` validation used by
the deterministic endpoint. Missing reviewed preferences are rejected.

## Reliability checks

- Hybrid scores equal the returned weighted components.
- Rankings are stable for identical requests.
- Exclusions happen before retrieval.
- Unknown queries use explicit feature fallback.
- Grounded prose contains only known evidence templates.
- Private songs remain session-isolated.
- Existing deterministic recommendations continue passing unchanged.
