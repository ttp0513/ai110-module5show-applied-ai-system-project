# VYBE

VYBE is an AI-assisted music discovery application that turns a listener's
natural-language description into a transparent, catalog-grounded mix.

The application will also let listeners upload their own audio. Music-analysis
models will estimate supported musical features, and the listener must review
or correct those values before the track enters their private catalog.

## Project status

- **Phase 1 complete:** product requirements and system boundaries
- **Phase 2 complete:** runnable scaffold, configuration, and architecture
- **Phase 3 complete:** canonical catalog and deterministic recommendation
- **Phase 3 prototype complete:** responsive deterministic interface
- **Phase 4 complete:** anonymous private songs and manual entry
- **Phase 5 complete:** temporary audio analysis and mandatory review
- **Phase 6 in review:** grounded natural-language catalog retrieval

Semantic retrieval, AI preference extraction, and grounded explanations are
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

## Phase 1–3 interface

The current browser interface includes:

- Product positioning and transparency principles
- Catalog-backed genre and mood options
- Optional energy, positivity, danceability, instrumentalness, acousticness,
  and tempo controls
- Genre and mood exclusions
- Five deterministic recommendations
- Expandable per-feature score contributions
- Responsive mobile and desktop layouts
- Keyboard focus, semantic form controls, reduced motion, and safe text
  rendering

This Phase 3 checkpoint intentionally excluded natural-language AI, RAG,
user-added songs, audio analysis, and playback. Phase 4 now extends the same
interface with private manual song entry.

## Phase 4 documents

- [Private songs and manual entry](docs/phase-4-private-songs.md)
- [Private song lifecycle](diagrams/private-song-lifecycle.mmd)

Phase 4 lets a listener add complete song metadata and recommendation features
without uploading audio. The song remains isolated to an opaque anonymous
session, participates in deterministic ranking, and can be removed by its
owner. SQLite preserves the song across application restarts, while a
persistent HTTP-only cookie reconnects the same browser to its records.

## Phase 5 documents

- [AI-assisted audio analysis](docs/phase-5-audio-analysis.md)
- [Audio analysis sequence](diagrams/audio-analysis-sequence.mmd)

Phase 5 accepts a permitted WAV, FLAC, OGG, MP3, or M4A file for temporary
analysis. Signal measurements and a specialized catalog-trained classifier
prefill an editable review form. The upload is deleted before review; only
approved feature values and provenance are stored.

## Phase 6 documents

- [Grounded catalog retrieval](docs/phase-6-grounded-retrieval.md)
- [Grounded retrieval sequence](diagrams/grounded-retrieval-sequence.mmd)

Phase 6 lets listeners search the caller-visible catalog with phrases such as
“late-night coding beats.” A local TF-IDF retriever uses controlled music cues
to return relevant approved records. Every explanation is generated from
structured catalog evidence, private songs remain session-isolated, and
unknown requests produce no invented candidates.

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
3. Song catalog and deterministic recommender — complete
4. Private songs and manual feature entry — complete
5. AI audio analysis — complete
6. Retrieval and grounding foundation — in review
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
