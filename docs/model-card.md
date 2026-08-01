# VYBE AI system card

## System summary

VYBE is an AI-assisted recommendation system, not one general-purpose model.
It combines bounded components so that external AI can influence preference
interpretation but cannot invent catalog records or directly control ranking.

| Component | Implementation | Role |
|---|---|---|
| Preference extraction | Gemini structured output or `rules-v1` fallback | Convert vibe text into supported fields |
| Catalog retrieval | Local TF-IDF plus controlled music cues | Retrieve approved candidate songs |
| Audio category estimation | Catalog-trained K-nearest-neighbors classifier | Suggest supported genre and mood |
| Audio measurement | librosa, soundfile, and mutagen | Estimate measurable signal features |
| Final ranking | Deterministic weighted scorer | Rank retrieved songs against reviewed intent |
| Explanations | Deterministic evidence templates | Describe only validated score evidence |

## Intended use

VYBE helps a listener discover songs from its built-in and private catalog by
describing a desired mood or sound. Users must review AI-interpreted preferences
and audio-analysis suggestions before those values affect recommendations or
are saved.

It is intended for entertainment and educational demonstration. It is not an
authority on musical genre, emotion, identity, cultural origin, copyright, or
professional audio analysis.

## Inputs and outputs

Preference extraction accepts at most 1,000 characters of untrusted text and
can return only canonical genres, moods, exclusions, bounded numeric targets,
a short summary, and ambiguity notes. Pydantic validates the structured result.

Audio analysis accepts a user-authorized file up to 25 MiB and 15 minutes in a
supported format. The original bytes are deleted after analysis. Outputs
include source and confidence information and remain editable.

Final results contain only caller-visible `Song` records, deterministic scores,
feature reasons, and grounded explanation templates.

## Data

The local audio category classifier uses only the version-controlled VYBE
catalog as its reference feature set. It is a small product-specific model, not
a broadly trained music classifier. TF-IDF retrieval is rebuilt from the
caller-visible built-in and private metadata for each request.

Gemini training data is controlled by Google and is not documented by this
repository. Free-tier data-use terms must be reviewed before enabling it.

## Evaluation

Evaluation dataset version `1.0.0` contains representative preference,
retrieval, and hybrid-ranking cases. The deterministic demo path currently
passes all declared fixed-set thresholds, including 100% catalog grounding,
100% fallback success, and zero unsupported factual claims.

These are regression results on a small controlled set. They do not establish
general accuracy, fairness across cultures or genres, live Gemini stability,
or broad audio-classification quality. See
[Phase 12 evaluation](phase-12-testing-and-ai-evaluation.md).

## Limitations and risks

- Natural-language cues are English-focused and cover a fixed vocabulary.
- Genre and mood are subjective, overlapping, and culturally dependent.
- The small catalog can make recommendations repetitive.
- TF-IDF does not deeply understand novel language.
- The specialized audio classifier can be overconfident outside its catalog.
- Gemini responses can change with model revisions or provider behavior.
- Anonymous cookie ownership has no account recovery or cross-device sync.
- The system does not determine upload copyright or permission.

## Safeguards

- Visible review gates for AI interpretation and audio proposals.
- JSON Schema, Pydantic, canonical enums, and numeric bounds.
- Catalog-only retrieval and deterministic final ranking.
- Deterministic provider fallback and manual completion.
- Private-session filtering and immediate upload deletion.
- Sanitized structured logs, request IDs, safe errors, and HTTP guardrails.
- No popularity profiling, playback, or listening-history collection.

## Monitoring and change policy

Run the full test suite and fixed evaluation before changing prompts, Gemini
models, cue mappings, catalog data, retrieval logic, classifier behavior, or
ranking weights. Version evaluation cases when their meaning changes. Evaluate
live Gemini separately with labeled prompts before a public release, and record
the exact model ID, date, tier, and observed failure rate.
