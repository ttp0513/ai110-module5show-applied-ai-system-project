# VYBE

VYBE is a transparent, AI-assisted music recommender. A listener describes a
moment, reviews the interpreted music preferences, and receives ranked songs
from an approved catalog with visible score evidence. VYBE recommends music;
it does not stream, preview, or play audio.

The project matters because it demonstrates how generative AI can improve a
recommendation experience without silently controlling the result. Model output
is bounded, reviewable, and backed by deterministic retrieval, ranking,
fallback, and evaluation systems.

## From Music Recommender Simulation to VYBE

This application evolved from my Modules 1-3 project, **Music Recommender
Simulation**. The original Python command-line project used content-based
filtering to compare manually entered listener preferences with a synthetic
60-song catalog, calculate deterministic weighted scores, and return
explainable top-five recommendations.

VYBE expands that foundation into a responsive FastAPI application with
Gemini-assisted preference extraction, catalog retrieval, user-owned private
songs, temporary audio analysis, hybrid ranking, security guardrails, and
measurable AI evaluation.

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

Requirements: Python 3.12-3.14 and a modern browser.

1. Open PowerShell in the repository root.
2. Create and activate an isolated environment.
3. Install the pinned application and development dependencies.
4. Copy the example configuration to the ignored local `.env` file.
5. Start the FastAPI development server.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

6. Open one of these local URLs:

- Application: <http://127.0.0.1:8000>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/api/health>

7. Keep demo mode for credential-free use, or follow the Gemini configuration
   below and restart the server.
8. Run the verification and evaluation commands before changing the system.

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

## Sample interactions

The following outputs were regenerated from VYBE 1.0.0 in deterministic demo
mode. They are intentionally concise excerpts of the structured API responses.

### Example 1: Focused lo-fi discovery

```text
Input:
cozy lofi beats for coding

AI interpretation:
preferred_genres: [lofi]
preferred_moods: [chill, focused]
provider: demo
model: rules-v1
needs_review: true

Recommendation output:
mode: hybrid
used_retrieval_fallback: false
first_result: Midnight Coding — LoRoom
genre: lofi
mood: chill
explanation_mode: deterministic_grounded
```

### Example 2: Romantic night-drive interpretation

```text
Input:
romantic neon night drive

AI interpretation:
preferred_genres: [synthwave]
preferred_moods: [romantic]
provider: demo
model: rules-v1
needs_review: true
```

The listener reviews these fields before they can affect ranking.

### Example 3: Skip and refine

```text
VYPE recommends first result:
Midnight Coding — LoRoom

User action:
Select "Not this one"

Refinement output:
excluded_song_count: 1
new_first_result: Focus Flow — LoRoom
```

VYBE keeps the same approved vibe, skips that song, and reranks the remaining
options. No hidden chat history affects the result.

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

## Testing summary

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
See the committed
[reproducible execution evidence](artifacts/reproducible-execution.md) for the
exact release commands, outputs, metrics, and interaction log.

What worked:

- 76 unit, integration, security, privacy, UI-contract, and reliability tests
  pass.
- The fixed evaluation passes every declared threshold, with 100% catalog
  grounding, 100% forced-provider fallback success, and zero unsupported
  factual claims in the controlled set.
- Repeated deterministic requests produce identical rankings and scores.

What remains limited or unverified:

- Automated tests mock Gemini's structured response instead of spending quota
  on a changing live model.
- The evaluation set is small, synthetic, and English-focused; 100% on this set
  does not mean universal accuracy.
- Genre and mood are subjective, and the catalog-trained audio classifier is
  not a broad music-understanding model.
- The refinement UI still needs a final manual desktop/mobile visual pass.

The main testing lesson was that AI quality cannot be represented by a single
“works” result. VYBE tests schema validity, grounding, constraints, privacy,
fallback, repeatability, and ranking quality separately so a regression is
visible and actionable.

## Architecture

VYBE is a FastAPI modular monolith: one deployable process with separate
packages for API transport, AI providers, audio analysis, catalog storage,
retrieval, recommendation, and orchestration. SQLite stores private metadata;
the built-in catalog is version controlled; uploaded audio uses a temporary
workspace; Gemini is an optional external preference-extraction provider.

The primary [System Architecture Diagram](diagrams/component-architecture.mmd)
shows the module boundaries. At runtime, the main flow is:

```text
Listener enters a vibe
        ↓
FastAPI validates the request and resolves the private session
        ↓
Gemini or the deterministic fallback extracts bounded preferences
        ↓
Listener reviews and corrects the interpretation
        ↓
Local TF-IDF retrieves caller-visible catalog songs
        ↓
Deterministic hybrid scoring ranks the candidates
        ↓
VYBE returns grounded recommendations and score evidence
```

SQLite stores only approved private song metadata. Uploaded audio enters a
temporary workspace, is analyzed locally, and is deleted before the listener
reviews the proposed values.

Start with:

- [Technical architecture](docs/phase-2-technical-architecture.md)
- [Component architecture](diagrams/component-architecture.mmd)
- [Domain model](diagrams/domain-model.mmd)
- [Deployment model](diagrams/deployment.mmd)
- [User journeys](diagrams/user-journeys.mmd)
- [Model card](model_card.md)
- [Decision log](docs/decision-log.md)

## Design decisions and trade-offs

| Decision | Why it was selected | Trade-off |
|---|---|---|
| FastAPI modular monolith | One process is easy to run while packages preserve clear boundaries | Components cannot scale independently |
| SQLite private catalog | Durable local storage without a database server | Not designed for multiple application hosts |
| Gemini structured output | Handles flexible vibe language within a strict schema | Adds provider, quota, privacy, and model-version dependencies |
| Local deterministic fallback | Keeps the core journey available without credentials | Understands fewer language variations than a large model |
| Local TF-IDF retrieval | Reproducible, private, fast, and credential-free | Has limited understanding of novel or indirect language |
| Deterministic final ranking | Scores and explanations are auditable and testable | Does not learn from behavioral history |
| Mandatory user review | Prevents uncertain AI output from silently changing results | Adds one step to the journey |
| SQLite metadata but no audio retention | Private songs survive restarts without storing media | The app cannot provide playback or reanalyze a deleted upload |
| No popularity feature | Avoids changing, unverifiable, and user-inaccessible data | Cannot recommend based on current trends |

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

## Reflection

This project taught me that calling an AI API is only a small part of building
an AI system. The more difficult work was deciding what the model should
control, validating its output, creating useful fallback behavior, protecting
user data, and making uncertainty visible. Combining bounded AI assistance
with deterministic components and human review produced a system that is more
reliable and easier to explain than an unconstrained model-only workflow.

The graded responsible-AI reflection—including how I collaborated with AI and
evaluated helpful and flawed suggestions—belongs in `model_card.md` and is kept
separate from this general project reflection.
