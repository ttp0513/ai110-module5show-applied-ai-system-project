# VYBE

VYBE is a transparent, AI-assisted music recommender. A listener describes a
moment, reviews the interpreted music preferences, and receives ranked songs
from an approved catalog with visible score evidence. VYBE recommends music;
it does not stream, preview, or play audio.

## What the MVP does

- Interprets natural-language vibes with Gemini structured output or a local
  deterministic fallback.
- Retrieves real, caller-visible catalog songs with local TF-IDF retrieval.
- Ranks candidates using 35% text relevance and 65% reviewed feature fit.
- Explains every result using validated score evidence.
- Lets listeners skip results and reproducibly refine the set.
- Accepts private songs through complete manual entry or temporary audio
  analysis followed by mandatory user review.
- Persists approved private song data in SQLite until the listener deletes it.
- Deletes uploaded audio immediately after analysis and never offers playback.
- Excludes popularity and listening history from recommendation decisions.

## Quick start on Windows

Requirements: Python 3.12–3.14 and a modern browser.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Application: <http://127.0.0.1:8000>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/api/health>

If Windows reports `WinError 10013`, the port is unavailable or restricted.
Use another local port:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Then open <http://127.0.0.1:8010>.

## Gemini configuration

The default `.env` runs reproducibly without credentials:

```text
VYBE_DEMO_MODE=true
VYBE_AI_PROVIDER=demo
```

To enable Gemini preference extraction, obtain a key from Google AI Studio and
set the ignored local `.env` file:

```text
VYBE_DEMO_MODE=false
VYBE_AI_PROVIDER=gemini
VYBE_AI_MODEL=gemini-3.5-flash
VYBE_GEMINI_API_KEY=<your-key>
```

Restart the server after changing configuration. Never commit or paste the key
into logs or issue reports. Google states that content submitted through the
Gemini free tier may be used to improve its products; do not submit confidential
or personally identifying prompts on that tier. Review Google's current
[Gemini API pricing and data-use terms](https://ai.google.dev/gemini-api/docs/pricing).

Gemini is used only to extract reviewable preferences. Audio features are
measured locally, genre and mood estimates use the local specialized model,
retrieval is local TF-IDF, and final ranking is deterministic.

## Primary user journey

1. Describe a vibe such as “romantic futuristic night drive.”
2. Review and optionally correct the extracted genres, moods, and sound values.
3. Generate five catalog-grounded recommendations.
4. Expand a result to inspect retrieval and feature-score evidence.
5. Select **Not this one** to exclude a result and rerank the remaining songs.
6. Optionally add a private song manually or analyze permitted audio, review
   every proposed value, and save only the approved metadata.

Private songs are associated with an anonymous `HttpOnly` browser cookie and
stored in `data/vybe.db`. They survive server restarts and remain available to
that browser until deleted. Clearing the cookie breaks the browser's link to
the records because the MVP has no account-recovery system.

## Privacy and safety

- Uploaded audio is temporary and is deleted on success or failure.
- Raw prompts, request bodies, audio, cookies, and credentials are not logged.
- Private songs are isolated by anonymous session.
- AI output must pass JSON Schema, Pydantic, and domain validation.
- AI interpretations require visible review before ranking.
- Provider failure automatically uses the deterministic local interpreter.
- Request IDs, safe errors, request limits, same-origin checks, and browser
  security headers protect the application boundary.

For a public deployment, add HTTPS, trusted-host enforcement, rate limiting,
monitoring, backups, log retention, and secret rotation at the hosting layer.

## Verification and evaluation

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest
python -m scripts.evaluate
```

The evaluation report is written to `artifacts/evaluation-report.json`. The
fixed versioned dataset measures preference extraction, retrieval, hybrid
ranking, grounding, constraints, fallback, private-song retrieval, and feature
ranges. The current controlled set passes all thresholds, but it is not a claim
of perfect accuracy for arbitrary prompts, live Gemini versions, or all music.

## Architecture

VYBE is a FastAPI modular monolith: one deployable process with separate
packages for API transport, AI providers, audio analysis, catalog storage,
retrieval, recommendation, and orchestration. SQLite stores private metadata;
the built-in catalog is version controlled; uploaded audio uses a temporary
workspace; Gemini is an optional external preference-extraction provider.

Start with:

- [Technical architecture](docs/phase-2-technical-architecture.md)
- [Component architecture](diagrams/component-architecture.mmd)
- [Domain model](diagrams/domain-model.mmd)
- [Deployment model](diagrams/deployment.mmd)
- [User journeys](diagrams/user-journeys.mmd)
- [Model card](docs/model-card.md)
- [Decision log](docs/decision-log.md)

## Delivery documentation

- [Requirements](docs/phase-1-product-requirements.md)
- [Data and AI contract](docs/phase-1-data-ai-contract.md)
- [Acceptance criteria](docs/phase-1-acceptance-criteria.md)
- [Catalog and deterministic ranking](docs/phase-3-catalog-and-recommender.md)
- [Private songs](docs/phase-4-private-songs.md)
- [Audio analysis](docs/phase-5-audio-analysis.md)
- [Grounded retrieval](docs/phase-6-grounded-retrieval.md)
- [AI preference interpretation](docs/phase-7-ai-preference-interpretation.md)
- [Hybrid ranking](docs/phase-8-hybrid-ranking.md)
- [Backend API](docs/phase-9-backend-api.md)
- [Responsive UI](docs/phase-10-responsive-ui.md)
- [Operational guardrails](docs/phase-11-logging-security-guardrails.md)
- [Testing and AI evaluation](docs/phase-12-testing-and-ai-evaluation.md)
- [Final delivery](docs/phase-13-final-delivery.md)

## MVP boundaries

- No playback, streaming, previews, or audio retention.
- No user accounts, social features, or collaborative playlists.
- No popularity, listening-history, or behavioral tracking.
- No claim that AI-estimated genre or mood is objective fact.
- No production hosting configuration is included.
