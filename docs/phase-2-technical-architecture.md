# Phase 2: Technical Architecture

## 1. Phase objective

Phase 2 establishes a runnable application boundary and a documented target
architecture without prematurely implementing recommendation, retrieval,
language-model, audio-analysis, or final user-interface behavior.

## 2. Architecture style

VYBE uses a modular monolith for the MVP. One deployable FastAPI process owns
HTTP routing and application orchestration while domain capabilities remain
separated by package.

This structure is simpler to run and evaluate than distributed services while
preserving boundaries that can be extracted later if scale requires it.

## 3. Package responsibilities

| Package | Responsibility | Primary phase |
|---|---|---:|
| `app.api` | HTTP transport, request validation, public responses | 2 and 9 |
| `app.catalog` | Validated public and private song access | 3 and 4 |
| `app.models` | Canonical domain and transport schemas | 3 and 4 |
| `app.recommendation` | Deterministic scoring and hybrid ranking | 3 and 8 |
| `app.retrieval` | Document construction and grounded catalog search | Implemented in 6 |
| `app.ai` | Model adapters, prompts, extraction, explanation | 7 and 8 |
| `app.services` | End-to-end use-case orchestration | 8 and 9 |
| `app.validation` | Grounding, constraints, and output guardrails | 8 and 11 |
| `app.static` | Browser CSS, JavaScript, and approved visual assets | 10 |
| `app.templates` | Server-delivered application shell | 10 |

Dependencies should point inward: transport and providers may depend on domain
contracts, but scoring and domain models must not depend on FastAPI or a
specific AI provider.

## 4. Runtime boundaries

### Browser

- Renders the responsive interface.
- Maintains temporary anonymous session state.
- Displays recommendation metadata without streaming or playing songs.
- Never receives AI credentials or private storage paths.
- Uploads audio only through validated API endpoints.

### FastAPI application

- Validates all external input.
- Assigns request and session identifiers.
- Coordinates retrieval, scoring, AI, audio analysis, and fallback.
- Returns public error representations without internal stack traces.

### Local data

- Built-in catalog: approved, version-controlled song records.
- Private catalog: session-scoped SQLite records, with the database excluded
  from Git.
- Retrieval artifacts: derived indexes that can be rebuilt from approved data.
- Upload workspace: temporary, non-public, and cleaned according to policy.

Uploaded audio is used only as temporary analysis input. The architecture does
not require a media server, playback endpoint, streaming storage, or audio
delivery controls.

### External or specialized providers

- Language-model adapter: structured preference extraction and grounded prose.
- Embedding adapter: searchable representations of approved song documents.
- Music analyzer: deterministic audio features and specialized predictions.

Every provider is accessed through an application-owned interface and must
have a deterministic or manual fallback.

## 5. Configuration

Configuration is read from environment variables with a `VYBE_` prefix and
validated once per process.

Safe defaults:

- Demo mode enabled
- Demo AI provider
- Empty API credential
- Five recommendations
- Fifteen retrieval candidates
- Thirty-second provider timeout

Uploaded audio deletion is an unconditional lifecycle rule rather than a
configurable option.

Secrets are never returned by health endpoints or written to normal logs.

## 6. API surface

Phase 2 implements:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Identify the scaffold |
| `GET` | `/api/health` | Verify process and safe configuration |
| `GET` | `/docs` | Generated development API documentation |

Planned routes are documented but not implemented until their owning phases:

| Method | Route | Owning phase |
|---|---|---:|
| `GET` | `/api/catalog/options` | Implemented in 3 |
| `POST` | `/api/recommendations/deterministic` | Implemented in 3 |
| `POST` | `/api/preferences/interpret` | 7 and 9 |
| `POST` | `/api/recommendations` | 8 and 9 |
| `POST` | `/api/recommendations/refine` | 8 and 9 |
| `GET` | `/api/songs/private` | Implemented in 4 |
| `POST` | `/api/songs/private` | Implemented in 4 |
| `POST` | `/api/songs/analyze` | 5 and 9 |
| `POST` | `/api/retrieval/search` | Implemented in 6 |
| `GET` | `/api/jobs/{job_id}` | 5 and 9 |
| `DELETE` | `/api/songs/private/{song_id}` | Implemented in 4 |

## 7. Request lifecycle

1. Transport validates size, shape, and supported content.
2. Orchestrator assigns a request ID and selects demo or configured providers.
3. Domain services retrieve and score approved records.
4. Generated output passes catalog and factual validation.
5. Invalid generated output uses deterministic fallback.
6. Response includes safe status information but no internal provider details.
7. Structured logs capture identifiers, timings, and outcome categories.

## 8. Error strategy

Errors are classified as:

- `validation_error`: caller can correct the request
- `not_found`: approved record does not exist in the caller's scope
- `provider_unavailable`: AI, embedding, or analysis provider failed
- `analysis_failed`: uploaded audio could not be fully analyzed
- `index_unavailable`: semantic index cannot be queried
- `internal_error`: unexpected failure with a public request ID

Recoverable provider errors route to deterministic or manual workflows.

## 9. Dependency policy

Phase 2 pins direct runtime and development dependencies. A fully resolved lock
or hash-pinned dependency export will be produced once Python is available and
audio-platform compatibility is evaluated.

The minimum supported runtime is Python 3.12. The configured range also permits
3.13 and 3.14, subject to future audio-analysis dependency compatibility.

## 10. Testing strategy

- Unit tests validate isolated configuration and domain behavior.
- Integration tests validate API and cross-component flows.
- Reliability tests validate AI schema, grounding, constraints, and fallback.
- Fixed evaluation cases measure retrieval and recommendation quality.

Phase 2 provides configuration and health-contract tests. They are verified
with Python 3.14 in an isolated project environment.

## 11. Phase 2 completion criteria

- Package boundaries and future ownership are documented.
- Configuration is validated and safe by default.
- Minimal application and health endpoints are implemented.
- Development dependencies and commands are documented.
- Component, domain, sequence, reliability, and deployment diagrams exist.
- Repository formatting and file structure are statically inspected.
- Lint, formatting, configuration, and health-contract tests pass.
