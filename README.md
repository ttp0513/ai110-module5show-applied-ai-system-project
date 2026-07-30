# VYBE

VYBE is an AI-assisted music discovery application that turns a listener's
natural-language description into a transparent, catalog-grounded mix.

The application will also let listeners upload their own audio. Music-analysis
models will estimate supported musical features, and the listener must review
or correct those values before the track enters their private catalog.

## Project status

- **Phase 1 complete:** product requirements and system boundaries
- **Phase 2 complete:** runnable scaffold, configuration, and architecture
- **Phase 3 in review:** canonical catalog and deterministic recommendation

Semantic retrieval, AI, audio analysis, user-added songs, and the final UI are
intentionally reserved for later phases.

## Phase 1 documents

- [Product requirements](docs/phase-1-product-requirements.md)
- [Data and AI contract](docs/phase-1-data-ai-contract.md)
- [Acceptance criteria](docs/phase-1-acceptance-criteria.md)
- [Decision log](docs/decision-log.md)
- [System context diagram](diagrams/system-context.mmd)
- [Primary user journeys](diagrams/user-journeys.mmd)

## Phase 2 documents

- [Technical architecture](docs/phase-2-technical-architecture.md)
- [Component diagram](diagrams/component-architecture.mmd)
- [Domain model](diagrams/domain-model.mmd)
- [Recommendation sequence](diagrams/recommendation-sequence.mmd)
- [Audio-analysis sequence](diagrams/audio-analysis-sequence.mmd)
- [Deployment diagram](diagrams/deployment.mmd)
- [AI reliability flow](diagrams/ai-reliability-flow.mmd)

## Phase 3 documents

- [Catalog and scoring design](docs/phase-3-catalog-and-recommender.md)
- [Deterministic recommendation flow](diagrams/deterministic-recommendation-flow.mmd)

## Local setup

Install Python 3.12, 3.13, or 3.14 before running these commands. Phase 2 was
verified with Python 3.14.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation.

### Deterministic recommendation example

```powershell
$body = @{
    preferred_genres = @("lofi")
    preferred_moods = @("focused")
    target_instrumentalness = 0.90
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/recommendations/deterministic?limit=5" `
    -ContentType "application/json" `
    -Body $body
```

Use `GET /api/catalog/options` to retrieve supported genres, moods, and
recommendation features.

### Verification

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

The current tests verify configuration defaults and the application health
contract.

## Configuration

Application environment variables use the `VYBE_` prefix. Copy
`.env.example` to `.env` for local development. Demo mode is enabled by
default, no AI credential is required for the Phase 2 scaffold, and `.env` is
excluded from version control.

## Planned delivery phases

1. Requirements and project definition
2. Project setup and architecture — complete
3. Song catalog and deterministic recommender — in review
4. User song upload and manual entry
5. AI audio analysis
6. Retrieval-augmented generation
7. AI preference extraction
8. Hybrid ranking and grounded explanations
9. Backend API
10. Responsive user interface
11. Logging, security, and guardrails
12. Testing and AI evaluation
13. Documentation and final delivery

## Current assumptions

- The MVP is a responsive web application.
- No account is required for the first version.
- User-added songs are private.
- Uploaded audio is always deleted when analysis finishes or fails.
- Users can enter or correct every recommendation feature manually.
- VYBE recommends songs but does not stream, preview, or play audio.
- Popularity is not collected or used as a recommendation feature.
- Social features are outside the MVP.

These assumptions are recorded as provisional decisions and can be changed
before Phase 2 begins.
