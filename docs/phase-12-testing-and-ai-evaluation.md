# Phase 12: Testing and AI evaluation

## Outcome

Phase 12 turns VYBE's acceptance targets into reproducible release evidence.
The normal Pytest suite verifies individual behaviors. The separate evaluation
runner executes versioned representative cases, calculates metrics, compares
them with thresholds, and writes a machine-readable JSON report.

Run it from the repository root:

```powershell
python -m scripts.evaluate
```

The default report is written to `artifacts/evaluation-report.json`. Generated
reports are excluded from Git because they include a run timestamp; the cases,
thresholds, calculation code, and regression assertions are version controlled.

## Fixed evaluation metrics

| Metric | Target | Current fixed-set result |
|---|---:|---:|
| Preference extraction accuracy | At least 90% | 100% |
| Structured output validity | At least 99% | 100% |
| Retrieval recall at 5 | At least 90% | 100% |
| Hybrid top-1 category accuracy | At least 90% | 100% |
| Catalog grounding | 100% | 100% |
| Hard-constraint satisfaction | At least 95% | 100% |
| Deterministic fallback success | 100% | 100% |
| Saved-song retrieval grounding | 100% | 100% |
| Valid feature ranges | 100% | 100% |
| Unsupported factual claims | 0 | 0 |
| Overall metric pass rate | At least 90% | 100% |

## What is measured

- The local preference interpreter recognizes expected genre and mood slots.
- Retrieval places an expected supported category in the first five results.
- Hybrid ranking places the expected genre first for representative journeys.
- Every evaluated result points to an approved catalog record and uses the
  deterministic grounded explanation template.
- Excluded genres and moods never enter the result set.
- Forced provider failure successfully routes to the local interpreter.
- A private song with a unique approved title can be retrieved from the
  caller-visible catalog.
- Every built-in numeric feature remains within its canonical range.

## Honest limitations

The current dataset is deliberately small and tests the reproducible demo
path. A 100% fixed-set result means the declared regression examples pass; it
does not prove 100% accuracy for arbitrary listener language or music.

Gemini is contract-tested with mocked structured responses and fallback tests,
but is not scored through a live free-tier API during CI. Live-provider
evaluation would introduce credentials, quotas, cost, data-use considerations,
and nondeterminism. Before a public launch, evaluate a larger human-labeled
prompt set separately for every selected Gemini model version.

Audio validation, temporary-file deletion, review-before-save, and API
guardrails remain covered by integration tests. A larger licensed audio
benchmark is still required to make broad genre or mood accuracy claims.

## Release rule

The evaluation command exits with a nonzero status if any metric falls below
its threshold. Pytest also runs the evaluator and fails if thresholds regress
or two runs differ apart from their timestamps.
