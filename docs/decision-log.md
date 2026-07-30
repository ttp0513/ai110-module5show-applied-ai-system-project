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

## Decisions still open

The product owner should confirm or change D-012 before its implementation
phase. Accepted technical decisions may still be superseded by a documented
later decision.
