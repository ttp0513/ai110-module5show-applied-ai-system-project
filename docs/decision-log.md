# Decision Log

## Decision status

- **Proposed:** documented but not yet explicitly confirmed
- **Accepted:** approved for implementation
- **Superseded:** replaced by a later decision

| ID | Decision | Status | Rationale |
|---|---|---|---|
| D-001 | Build a responsive web application | Accepted | Supports mobile and desktop with one MVP |
| D-002 | Use Python and FastAPI for application services | Accepted | Fits the existing Python recommender |
| D-003 | Use custom HTML, CSS, and JavaScript for the initial UI | Accepted | Enables a distinctive interface without a large client toolchain |
| D-004 | Do not require an account in the MVP | Accepted | Reduces setup and keeps discovery immediate |
| D-005 | Keep user-added songs private | Accepted | Protects ownership and simplifies moderation |
| D-006 | Always delete uploaded audio after analysis | Accepted | Audio is only an analysis input because the app provides no playback |
| D-007 | Provide AI analysis and full manual entry | Accepted | Requested product requirement |
| D-008 | Require review before saving AI-estimated features | Accepted | Prevents uncertain estimates from becoming silent facts |
| D-009 | Use RAG plus deterministic feature scoring | Accepted | Makes retrieval central while retaining explainability |
| D-010 | Provide deterministic fallback and demo mode | Accepted | Required for reliability and reproducibility |
| D-011 | Provide recommendations without streaming, previews, or playback | Accepted | Keeps the product focused and avoids media licensing and storage complexity |
| D-012 | Use VYBE as the working name | Proposed | Brand and trademark review remain future work |
| D-013 | Exclude popularity and familiarity from song features | Accepted | The value changes over time, is not inferable from audio, and cannot be supplied consistently by users |
| D-014 | Use fixed supported genre and mood vocabularies | Accepted | Keeps manual input, AI output, audio estimates, and catalog values interoperable |
| D-015 | Renormalize weights using active preferences only | Accepted | Unselected features must not silently affect a listener's score |
| D-016 | Store private songs only in volatile memory | Superseded | Replaced after the product owner required songs to survive restarts |
| D-017 | Persist private songs and anonymous ownership in SQLite | Accepted | Songs should remain until users remove them without requiring a database server |
| D-018 | Use a catalog-trained KNN model for genre and mood estimates | Accepted | Provides a reproducible specialized model constrained to the app vocabulary |
| D-019 | Keep unapproved audio proposals in process memory | Accepted | No upload bytes persist and abandoned drafts disappear on restart |
| D-020 | Separate measurements, algorithms, AI estimates, and user corrections in provenance | Accepted | Prevents approximate audio analysis from being presented as fact |
| D-021 | Start retrieval with local TF-IDF and controlled semantic cues | Accepted | Keeps Phase 6 reproducible and credential-free while preserving a future embedding adapter boundary |
| D-022 | Rebuild the caller-visible retrieval index per request for the MVP | Accepted | Immediately reflects private-song ownership and deletion without stale index state |
| D-023 | Generate Phase 6 explanations only from structured catalog evidence | Accepted | Unknown requests must return no match instead of hallucinated songs or attributes |
| D-024 | Use Responses API Structured Outputs for configured preference extraction | Accepted | Pydantic-constrained output maps safely into the existing recommendation contract |
| D-025 | Require visible review before interpreted preferences affect ranking | Accepted | Keeps AI advisory and lets listeners correct meaning before use |
| D-026 | Preserve a deterministic local preference interpreter | Accepted | The core journey remains reproducible without a credential or provider availability |
| D-027 | Weight reviewed feature similarity at 65% and retrieval relevance at 35% | Accepted | Explicitly reviewed intent should dominate wording similarity in the initial hybrid policy |
| D-028 | Fall back to feature-only ranking when retrieval finds no match | Accepted | Unknown wording should not disable useful recommendations or cause invented candidates |
| D-029 | Render Phase 8 explanations from validated score evidence | Accepted | Deterministic grounded prose prevents unsupported model claims while preserving transparency |

## Decisions still open

The product owner should confirm or change D-012 before its implementation
phase. Accepted technical decisions may still be superseded by a documented
later decision.
