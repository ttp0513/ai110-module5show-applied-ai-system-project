# Phase 9: Backend API

## Outcome

Phase 9 turns the endpoints delivered incrementally in Phases 3–8 into one
documented public application contract. FastAPI remains the transport layer;
catalog, AI, retrieval, analysis, and ranking logic stay in their existing
domain modules.

Phase 9 introduced API version `0.2.0`; Phase 11 advances the current API to
`0.3.0` with operational guardrails. Interactive documentation is available at
`/docs`, the machine-readable OpenAPI document at `/openapi.json`, and safe
client limits and capabilities at `GET /api/capabilities`.

## Primary user journey

1. `GET /api/catalog/options` loads supported controls.
2. `POST /api/preferences/interpret` converts vibe text into reviewable values.
3. The listener reviews or edits those values in the UI.
4. `POST /api/recommendations` retrieves and ranks grounded catalog songs.
5. `POST /api/recommendations/refine` reranks complete reviewed intent and can
   omit up to 20 songs the listener already skipped.

The server does not retain recommendation history. Each refinement contains
the complete query, reviewed preferences, and skipped song IDs, which keeps
the result reproducible and avoids hidden AI state.

## Supporting routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/health` | Process health and active phase |
| `GET` | `/api/capabilities` | Safe client features and limits |
| `POST` | `/api/recommendations/deterministic` | Manual feature-only ranking |
| `POST` | `/api/retrieval/search` | Grounded catalog candidate search |
| `GET` | `/api/songs/private` | List session-owned songs |
| `POST` | `/api/songs/private` | Save a manually described song |
| `DELETE` | `/api/songs/private/{song_id}` | Delete an owned song |
| `POST` | `/api/songs/analyze` | Temporarily analyze authorized audio |
| `POST` | `/api/songs/analyzed/{analysis_id}/approve` | Save reviewed analysis |
| `DELETE` | `/api/songs/analyzed/{analysis_id}` | Discard an analysis draft |

## API design choices

- Pydantic rejects unsupported or out-of-range values before domain logic.
- Anonymous session cookies isolate private songs without requiring accounts.
- Refined results use the same retrieval, scoring, grounding, and session rules
  as initial results.
- Unknown excluded IDs are ignored and never reveal whether another user owns
  them; `excluded_song_count` counts only records visible to the caller.
- Secrets, storage paths, and raw prompts are absent from capability and health
  responses.

## Why there is no jobs endpoint

The current audio workflow returns one bounded analysis proposal directly and
the existing browser journey consumes that response synchronously. Adding a
job queue now would introduce worker lifecycle, durable job state, polling,
and cleanup without improving the current MVP journey. A jobs endpoint should
be added with a real background worker only if production measurements show
that analysis cannot reliably finish within the HTTP timeout.

## Completion checks

- The OpenAPI schema includes every primary route.
- Capability metadata contains no credential values.
- Refinement excludes only caller-visible songs and is deterministic.
- Limits reject oversized refinement state.
- All earlier unit, integration, and AI reliability tests remain green.
