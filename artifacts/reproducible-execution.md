# VYBE reproducible execution evidence

This log records a local deterministic-demo verification run conducted on
July 31, 2026 from the repository root on Windows. It contains no API key,
cookie, uploaded audio, private song, or raw request header.

## Environment and dependencies

Commands:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip check
node --version
```

Output:

```text
Python 3.14.5
No broken requirements found.
v22.18.0
```

## Static verification

Commands:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
node --check app/static/js/app.js
```

Output:

```text
All checks passed!
68 files already formatted
JavaScript syntax check exited successfully with no output.
```

## Automated tests

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Output:

```text
........................................................................ [ 94%]
....                                                                     [100%]
76 tests passed.
```

The run emitted three dependency deprecation warnings: one from Google GenAI
on Python 3.14 and two from audioread compatibility modules. They did not fail
the suite or change application behavior.

## AI and retrieval evaluation

Command:

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate `
  --output artifacts/evaluation-report.json
```

Output:

```text
Evaluation report: artifacts\evaluation-report.json
Overall metric pass rate: 100.00%
preference_extraction_accuracy: 100.0% (threshold 90.0%) - passed=True
structured_output_validity: 100.0% (threshold 99.0%) - passed=True
retrieval_recall_at_5: 100.0% (threshold 90.0%) - passed=True
hybrid_top_1_accuracy: 100.0% (threshold 90.0%) - passed=True
catalog_grounding: 100.0% (threshold 100.0%) - passed=True
hard_constraint_satisfaction: 100.0% (threshold 95.0%) - passed=True
deterministic_fallback_success: 100.0% (threshold 100.0%) - passed=True
saved_song_retrieval_grounding: 100.0% (threshold 100.0%) - passed=True
valid_feature_ranges: 100.0% (threshold 100.0%) - passed=True
unsupported_factual_claims: 0 - passed=True
overall_metric_pass_rate: 100.0% - passed=True
```

These results apply to evaluation dataset version 1.0.0 in deterministic demo
mode. They are regression evidence, not a claim of universal or live-Gemini
accuracy.

## Live application metadata

Commands:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/capabilities
```

Selected output:

```json
{
  "health": {
    "status": "ok",
    "application": "VYBE",
    "environment": "development",
    "demo_mode": true,
    "phase": 13
  },
  "capabilities": {
    "api_version": "1.0.0",
    "phase": 13,
    "maximum_prompt_length": 1000,
    "maximum_audio_upload_bytes": 26214400,
    "features": [
      "deterministic_recommendations",
      "hybrid_grounded_recommendations",
      "recommendation_refinement",
      "private_song_catalog",
      "temporary_audio_analysis",
      "ai_preference_interpretation",
      "catalog_retrieval",
      "operational_guardrails"
    ]
  }
}
```

## Interaction 1: focused lo-fi discovery

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

## Interaction 2: romantic night-drive interpretation

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

## Interaction 3: skip and refine

```text
Starting first result:
Midnight Coding — LoRoom

User action:
Select "Not this one"

Refinement output:
excluded_song_count: 1
new_first_result: Focus Flow — LoRoom
```

## Reproduction notes

1. Follow the root README setup instructions.
2. Keep `VYBE_DEMO_MODE=true` and `VYBE_AI_PROVIDER=demo`.
3. Start Uvicorn on `127.0.0.1:8000`.
4. Run the commands above from the repository root.
5. Expect the deterministic interaction values and evaluation metrics to match.

Timing, UUID request IDs, and the generated report timestamp will differ by run.
