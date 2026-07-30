# Phase 1: Acceptance Criteria

## 1. MVP functional acceptance

- A listener can submit a natural-language vibe.
- The interpretation is schema-valid and reviewable before recommendation.
- A listener can instead set all supported preferences manually.
- Retrieval provides candidates that affect the final recommendation set.
- Five or fewer valid catalog songs are ranked and returned.
- Every result includes a grounded or deterministic explanation.
- A listener can refine the active mix.
- A listener can add a song through audio analysis or complete manual entry.
- An analyzed song is not saved until the listener confirms its features.
- An approved private song is eligible for later retrieval and ranking.
- AI and retrieval failure do not disable manual recommendation.

## 2. Reliability targets

| Metric | MVP target |
|---|---:|
| Catalog-grounded recommendations | 100% |
| Structured AI output validity | At least 99% |
| Unsupported factual song claims | 0 in the fixed evaluation set |
| Preference extraction accuracy | At least 90% |
| Hard-constraint satisfaction | At least 95% |
| Deterministic fallback success | 100% |
| Saved-song retrieval grounding | 100% |
| Valid feature ranges | 100% |
| Overall fixed-evaluation pass rate | At least 90% |

## 3. Audio-analysis targets

| Metric | MVP target |
|---|---:|
| Duration error | Less than 1 second |
| Tempo error on evaluation songs | Within 5 BPM |
| Invalid upload rejection | 100% |
| Manual completion after analysis failure | 100% |
| User approval before indexing | 100% |

Genre, mood, and subjective audio descriptors will be benchmarked during model
selection in Phase 5. They must display source and confidence and remain
editable regardless of measured accuracy.

## 4. Security and privacy acceptance

- API keys and secrets are absent from source control.
- Uploaded filenames cannot control storage paths.
- File content is validated independently of its extension.
- Audio is private and deleted when analysis finishes, fails, or is cancelled.
- Raw prompts and audio are not written to standard logs.
- Another session cannot retrieve a user's private songs.
- Public error responses do not contain stack traces or secrets.

## 5. Accessibility acceptance

- All core workflows are keyboard operable.
- Interactive controls have visible focus states.
- Touch targets are at least 44 by 44 pixels.
- Text and essential controls meet accessible contrast requirements.
- Screen readers receive labels, status updates, and result ordering.
- Reduced-motion preferences disable nonessential animation.
- Color is not the only indicator of confidence, error, or selection.

## 6. Reproducibility acceptance

- Dependencies are version-pinned.
- `.env.example` documents every configuration value.
- Setup, index, run, test, and evaluation commands are documented.
- Demo mode works without an external AI credential.
- A clean-environment rehearsal succeeds using only the README.
- Fixed evaluation cases are version controlled.

## 7. Definition of done

The complete MVP is done only when:

1. All required journeys work on mobile and desktop.
2. Unit, integration, guardrail, and reliability tests pass.
3. Reliability thresholds are met or explicitly documented as limitations.
4. Clean setup succeeds from the README.
5. The model card and architecture documentation reflect the delivered system.
6. No unresolved critical security, privacy, or grounding defect remains.

## 8. Phase 1 completion

Phase 1 is complete when the product requirements, data and AI contract,
acceptance criteria, diagrams, and provisional decisions are present and
internally consistent. Application implementation begins in Phase 2.
