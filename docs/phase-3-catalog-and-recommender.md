# Phase 3: Catalog and Deterministic Recommender

## 1. Phase objective

Phase 3 provides a validated song catalog and a transparent recommendation
baseline that requires no AI provider. Later retrieval and AI phases will
extend this baseline rather than replace it.

## 2. Canonical catalog

The built-in catalog contains 60 fictional songs and 14 columns:

- Identifier, title, and artist
- Genre and mood
- Energy, tempo, valence, and danceability
- Acousticness, instrumentalness, and liveness
- Release year and duration

Popularity is intentionally absent. The repository rejects missing or
unexpected columns, invalid feature ranges, unsupported categories, future
release years, and duplicate identifiers before exposing any records.

## 3. Supported categories

Genres:

```text
ambient, classical, electronic, folk, hip hop, indie pop, jazz,
latin, lofi, pop, rock, synthwave, world
```

Moods:

```text
celebratory, chill, confident, focused, happy, intense, moody,
relaxed, romantic
```

Fixed vocabularies ensure that catalog records, manual controls, AI extraction,
and future audio-analysis estimates use compatible values. Adding a category
requires an intentional schema and evaluation update.

## 4. Scoring policy

| Feature | Base weight |
|---|---:|
| Genre | 20% |
| Mood | 20% |
| Energy | 12% |
| Tempo | 8% |
| Valence | 8% |
| Danceability | 8% |
| Acousticness | 7% |
| Instrumentalness | 7% |
| Liveness | 5% |
| Release year | 3% |
| Duration | 2% |

Genre and mood carry the greatest weight because they express a listener's
most direct categorical intent. Energy is the strongest numeric signal. Tempo,
valence, and danceability provide useful shape, while narrower or less
reliable characteristics have smaller influence.

These are initial product weights, not learned truths. Phase 12 will evaluate
them against fixed cases and document any changes.

## 5. Similarity rules

- Exact genre or mood match: `1.0`
- Explicitly related category: `0.5`
- Unrelated category: `0.0`
- Numeric value: `1 - absolute distance / supported range`, bounded at zero

Related categories are deliberately explicit:

- Pop and indie pop
- Lofi and ambient
- Electronic and synthwave
- Latin and world
- Happy and celebratory
- Chill and relaxed
- Chill and focused
- Intense and confident

Tempo, release year, and duration use observed catalog ranges. Features already
stored from zero through one use a range of one.

## 6. Active-weight normalization

Only selected preferences affect a score. If a listener chooses mood and
energy, the engine renormalizes those two weights to 100% of the calculation.
Unselected features never silently influence the result.

For every active feature:

```text
normalized weight = base weight / total active base weight
contribution = similarity × normalized weight
final score = sum of contributions
```

The API returns each contribution so a user or test can reproduce the score.

## 7. Constraints and ranking

Excluded genres and moods are removed before scoring. At least one positive
ranking preference is required; exclusions alone cannot create a meaningful
ranking.

Songs are ordered by:

1. Final score descending
2. Original catalog order for ties

This produces reproducible results without using hidden popularity signals.

## 8. API

### `GET /api/catalog/options`

Returns catalog size, supported genres and moods, and all recommendation
features. It is the source of truth for future UI controls.

### `POST /api/recommendations/deterministic`

Accepts validated manual preferences and returns:

- Deterministic mode identifier
- Eligible and filtered song counts
- Ranked canonical song records
- Final normalized scores
- Per-feature similarities, weights, summaries, and contributions

The endpoint accepts a result limit from 1 through 20 and returns validation
errors for empty or unsupported preferences.

## 9. Limitations

- Weights are developer-defined and require later evaluation.
- Related categories are a small curated set rather than a learned taxonomy.
- The fictional catalog is intentionally limited.
- Numerical similarity assumes linear distance.
- Exclusions currently cover genre and mood; numeric hard ranges arrive with
  more advanced preference handling.
- This phase does not include semantic retrieval or natural-language input.

## 10. Phase completion checks

- All 60 catalog records validate.
- Popularity does not exist in the schema, catalog, or API feature list.
- Empty preferences fail validation.
- Exact and related matches behave as documented.
- Exclusions run before scoring.
- Scores equal the sum of returned contributions.
- Tie ordering is repeatable.
- Catalog and recommendation endpoints pass integration tests.
