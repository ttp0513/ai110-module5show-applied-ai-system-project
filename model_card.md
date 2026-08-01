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
or broad audio-classification quality. See the
[Phase 12 evaluation](docs/phase-12-testing-and-ai-evaluation.md).

## Limitations and biases

VYBE has several important limitations:

- The built-in catalog contains only 60 synthetic songs. It cannot represent
  the diversity of real music, artists, cultures, languages, or listening
  communities.
- Natural-language interpretation is primarily designed around English music
  terms. Users who describe music through another language, culture, or
  vocabulary may receive weaker interpretations.
- Genre and mood labels are subjective. A song described as relaxed by one
  listener could feel moody or focused to another.
- The local audio classifier compares uploaded music with a small catalog. It
  may produce confident-looking genre or mood suggestions for music that does
  not resemble its reference data.
- TF-IDF retrieval works well for known words and controlled musical cues but
  has limited understanding of indirect, unfamiliar, or highly creative
  descriptions.
- The fixed evaluation dataset is small and intentionally aligned with the
  supported vocabulary. A 100% result on that set does not demonstrate perfect
  performance for arbitrary users or prompts.
- Live Gemini behavior may change across model versions. Automated tests
  validate its structured contract with mocked responses rather than claiming
  stable live-model accuracy.
- VYBE does not use listening history or popularity. This improves privacy and
  reproducibility, but limits personalization and awareness of current trends.
- Anonymous cookie ownership has no account recovery or cross-device sync.

These limitations may cause some genres, moods, languages, and cultural
descriptions to receive better results than others. The system presents AI
outputs as editable suggestions rather than objective facts.

## Potential misuse and prevention

VYBE could be misused in several ways:

- Someone could upload audio they do not own or have permission to analyze.
- A user could try to overwhelm the server with oversized files or repeated
  requests.
- A malicious prompt could attempt to make Gemini ignore its instructions or
  return unsupported information.
- Someone could present estimated genre, mood, or emotional values as objective
  claims about a song or artist.
- A developer could expose a Gemini API key through source control, logs, or
  client-side code.

The system reduces these risks through:

- A required permission confirmation before audio analysis.
- Immediate deletion of uploaded audio after analysis or failure.
- No playback, streaming, or permanent audio storage.
- File-size, duration, content-type, prompt-length, and request-body limits.
- JSON Schema, Pydantic validation, fixed vocabularies, and numeric bounds.
- Instructions that treat user text as untrusted data.
- Mandatory review before AI-derived preferences affect ranking or analyzed
  song values are saved.
- Deterministic catalog-only ranking and grounded explanation templates.
- Session isolation, same-origin protection, safe errors, security headers,
  sanitized logs, and server-side environment variables for credentials.

These protections reduce misuse but cannot verify legal ownership of audio or
prevent every abusive request. A public deployment would still require rate
limiting, monitoring, abuse reporting, trusted hosts, and clear terms of use.

## Reliability testing reflection

The most surprising lesson was that reliability improved when the AI was given
less authority.

I initially expected the language model to be the most important part of the
recommendation system. Testing showed that the application became more
dependable when Gemini was limited to producing reviewable structured
preferences while retrieval, exclusions, ranking, and explanations remained
deterministic.

Forced-provider-failure tests were especially useful. They showed that a
Gemini timeout or invalid response did not need to break the main journey; the
local rules could still interpret supported terms and let the user continue.

The controlled evaluation reached a 100% metric pass rate, but that result also
demonstrated a testing limitation. A small fixed dataset is valuable for
detecting regressions, but it does not measure every way real users may
describe music. I learned to report evaluation as reproducible evidence, not
as proof that the AI is universally accurate.

## Collaboration with AI

I used AI as a collaborative design and development assistant throughout the
project. It helped me outline the phased architecture, compare storage
options, draft UML and Mermaid diagrams, implement bounded components,
identify test cases, troubleshoot server errors, and review documentation.
I did not accept its suggestions automatically; I compared them with the
requirements, ran tests, inspected outputs, and changed decisions when they
did not fit the application.

### Helpful AI suggestion

A particularly helpful suggestion was to separate AI preference extraction
from deterministic recommendation ranking and preserve a local fallback.

This led to an architecture where Gemini returns only schema-constrained music
preferences. The user reviews those values, and deterministic retrieval and
scoring produce the final recommendations. I verified the suggestion through
provider-failure tests, schema-validation tests, deterministic ranking tests,
and the Phase 12 evaluation.

This suggestion made the application more reliable, explainable, and
reproducible without removing the useful natural-language interface.

### Flawed AI suggestion

An early AI-assisted design included popularity as a recommendation feature.

That suggestion was unsuitable because popularity changes over time, the app
has no reliable popularity data source, uploaded audio cannot reveal
popularity, and users cannot consistently provide a meaningful value. Using
synthetic popularity would have made the recommendations look more informed
than they actually were.

I challenged the suggestion and removed popularity from the domain model,
catalog options, manual song entry, audio analysis, scoring, and explanations.
The final system uses only features that can be consistently stored, measured,
estimated with visible uncertainty, or entered by the user.

This experience taught me that AI suggestions can sound technically plausible
while still conflicting with data quality, product scope, or responsible
design requirements. AI-generated recommendations require the same critical
review as AI-generated code.

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
