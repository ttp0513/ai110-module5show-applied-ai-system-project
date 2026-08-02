# VYBE model card and responsible-AI reflection

## System summary

I built VYBE as an AI-assisted music recommendation application rather than as
one general-purpose AI model. One of my main design decisions was to give each
component a limited responsibility. Gemini can help interpret what a listener
means, but it cannot invent catalog records or directly control the final song
ranking.

| Component                 | Implementation                                  | Role                                         |
| ------------------------- | ----------------------------------------------- | -------------------------------------------- |
| Preference extraction     | Gemini structured output or `rules-v1` fallback | Convert vibe text into supported fields      |
| Catalog retrieval         | Local TF-IDF plus controlled music cues         | Retrieve approved candidate songs            |
| Audio category estimation | Catalog-trained K-nearest-neighbors classifier  | Suggest supported genre and mood             |
| Audio measurement         | librosa, soundfile, and mutagen                 | Estimate measurable signal features          |
| Final ranking             | Deterministic weighted scorer                   | Rank retrieved songs against reviewed intent |
| Explanations              | Deterministic evidence templates                | Describe only validated score evidence       |

## How I understand the workflow

I think about VYBE as a sequence of small decisions instead of one AI doing
everything:

1. The listener describes a vibe, chooses preferences manually, or adds a
   private song.
2. For a written vibe, Gemini tries to convert everyday language into the
   genres, moods, numeric targets, and constraints supported by VYBE.
3. The application validates that proposal. If Gemini is missing, unavailable,
   or invalid, the local `rules-v1` interpreter handles the words it knows.
4. The listener sees the interpretation and can correct, apply, or discard it.
5. Local TF-IDF retrieves real public and session-owned private songs.
6. Deterministic code scores the retrieved songs against the reviewed music
   preferences and applies exclusions.
7. Grounding checks make sure the response refers to real, caller-visible
   catalog records before the UI displays it.

This separation became important while I was building the project. Gemini is
useful for understanding flexible language, but retrieval and ranking remain
local and testable. The human review step connects the two parts.

## Intended use

I designed VYBE to help a listener discover songs from its built-in and private
catalog by describing a mood, moment, genre, or sound. The listener can also set
preferences manually or add a private song. AI-interpreted preferences and
audio-analysis estimates must be reviewed before they affect recommendations or
are saved.

This is an educational project for CodePath AI Foundation course and was built upon the module 1-3 Music Recommender project. I would not present it as an authority on musical genre, emotion, cultural identity, copyright, or professional audio analysis. The app recommends catalog songs but does not play or stream them.

The main intended users are listeners trying the recommendation experience,
students learning how applied-AI components work together, and reviewers who
want to inspect a reproducible example of validation, fallback, retrieval, and
human review.

## Inputs and outputs

For preference interpretation, the user can enter up to 1,000 characters of
untrusted text. I restrict the result to supported genres, moods, exclusions,
bounded numeric targets, a short summary, and ambiguity notes. Pydantic then
validates that structured result before the application can use it.

For audio-assisted song entry, the app accepts a user-authorized file up to 25
MiB and 15 minutes in a supported format. The original file is deleted after
analysis. The proposed features include source and confidence information and
remain editable because I do not assume that a local estimate is automatically
correct.

The final output contains only `Song` records visible to the current caller,
deterministic scores, feature-based reasons, and explanations rendered from
validated catalog evidence.

### Inputs I actually tried

During development, I tried short keyword-based prompts, conversational prompts,
manual preference forms, private-song forms, valid and invalid audio inputs, and
skip-and-refine requests. Examples included:

- `cozy instrumental lofi beats for late-night coding`
- `focused lofi coding beats, low energy`
- `I want to study for exam with soft and classical music`
- a request that skipped `Midnight Coding` and asked the system to rerank

I also tested empty and oversized prompts, forced provider failure, unsupported
structured values, missing reviewed preferences, private-session filtering,
and temporary upload cleanup.

### Outputs I actually observed

The interpretation response included structured preferences, a summary,
ambiguity notes, extracted-field names, provider and model information,
`used_fallback`, and `needs_review`. Recommendation responses included real
catalog songs, retrieval and feature scores, deterministic reasons, exclusions,
and grounded explanations. Audio analysis produced an editable proposal with
feature provenance and warnings rather than saving a song automatically.

The exact reproducible examples are recorded in
[`artifacts/reproducible-execution.md`](artifacts/reproducible-execution.md).

## Data

I trained the local audio category classifier using only the version-controlled
VYBE catalog as its reference feature set. This makes it a small,
project-specific KNN model rather than a broadly trained music classifier. The
local TF-IDF retriever is built from the public catalog and private metadata
visible to the current anonymous session.

I do not control or document the data used to train Gemini. That belongs to
Google, so anyone enabling the provider should review the current Gemini and
free-tier data-use terms rather than assuming this repository describes them.

## Evaluation

I created evaluation dataset version `1.0.0` with representative preference,
retrieval, and hybrid-ranking cases. On this fixed dataset, the deterministic
demo path passes the declared thresholds, including 100% catalog grounding,
100% fallback success, and zero unsupported factual claims.

I am careful not to call that result proof of general AI accuracy. It is a
regression result on a small controlled set and does not establish fairness
across cultures or genres, live Gemini stability, or broad audio-classification
quality. The testing method and thresholds are described in the
[Phase 12 evaluation](docs/phase-12-testing-and-ai-evaluation.md).

## Reliability rules and their trade-offs

Writing tests made me realize that every guardrail can still make the wrong
decision in either direction. These are four rules I relied on and the limits I
see in them:

| Rule                             | What it checks and why it matters                                                                                                                         | Possible false positive                                                                                 | Possible false negative                                                                   |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Structured preference validation | Gemini fields must match supported names, enums, and numeric ranges. This stops malformed or unsupported values from entering the app.                    | A reasonable synonym may be rejected only because it is not in VYBE's fixed vocabulary.                 | A schema-valid value may still misunderstand the listener's subjective meaning.           |
| Catalog grounding                | Recommended IDs and evidence must refer to public or current-session private songs. This prevents invented songs and cross-session leakage.               | A valid new private record could be unavailable if derived retrieval data were not refreshed correctly. | A real catalog song can pass grounding even when it is not a good subjective match.       |
| Review before apply or save      | AI and audio proposals cannot silently affect ranking or persistence. This keeps the listener in control.                                                 | It adds friction when the proposal is already correct.                                                  | A listener may approve an incorrect proposal without reviewing it carefully.              |
| Upload validation and deletion   | Audio type, signature, size, duration, and usable signal are checked, and temporary audio is deleted. This limits unsafe files and unnecessary retention. | An unusual but legitimate audio file may be rejected.                                                   | A technically valid file may contain irrelevant audio that still produces weak estimates. |

## Failure modes I observed

### The deterministic interpreter missed part of an ordinary request

On August 2, 2026, I ran this prompt through local deterministic mode:

```text
I want to study for exam with soft and classical music
```

It returned `classical` and `focused`, but it did not interpret `soft` as a
possible energy or acousticness cue and returned no ambiguity warning. This was
not a crash, the response was valid, but it showed that a keyword system can miss meaning that a person would notice. Manual correction and `needs_review: true` kept the incomplete interpretation from being silently accepted.

### Gemini produced a useful but subjective expansion

For the same prompt, the verified Gemini response proposed `classical`, `chill`,
`focused`, and `relaxed`. It also warned that "soft" suggested lower energy and
higher acousticness without enough information for exact values.

This was more expressive than the local result, but `chill` and `relaxed` were
still Gemini's interpretation rather than facts stated by the listener. I would
not call the response wrong, but it would have felt risky if the application had
applied all three moods automatically. The review screen was necessary because
the listener might want classical study music without wanting a relaxed mood.

### Provider status was initially confusing

I also saw the interface indicate that Gemini was configured even when a request
used local fallback. At first I thought a configured API key proved the request
had used Gemini. I changed the UI to distinguish ready, active, demo, and
unavailable-with-fallback states. This was a real example of technically correct
configuration information giving the user the wrong impression.

## Gemini compared with the deterministic interpreter

I compared both modes using the same study-music prompt rather than assuming
which one was better:

| Observation         | Local `rules-v1` result             | Gemini result                                                                          |
| ------------------- | ----------------------------------- | -------------------------------------------------------------------------------------- |
| Genres              | `classical`                         | `classical`                                                                            |
| Moods               | `focused`                           | `chill`, `focused`, `relaxed`                                                          |
| Treatment of "soft" | No numeric target or ambiguity note | Explained likely lower energy and higher acousticness, but did not invent exact values |
| Repeatability       | Same supported cues each run        | Wording or fields may vary by model response                                           |
| Availability        | Works without a network or API key  | Depends on credentials, quota, network, and provider behavior                          |
| Safety boundary     | Returns a reviewable proposal       | Must pass the same schema and review boundary                                          |
| Ranking authority   | None                                | None                                                                                   |

The local interpreter was narrower but predictable. Gemini understood more of
the conversational wording but made a broader subjective inference. Neither
mode should control ranking without validation and listener review.

## When VYBE should require human review

VYBE should refuse to apply an interpretation when neither Gemini nor the local
fallback produces at least one supported preference. It should also refuse to
save an analyzed private song when required values are missing or the listener
has not approved the proposal.

I would enforce the first condition in the interpretation service and API
contract, then have the UI disable **Apply** while leaving the manual controls
available. The message should say:

> VYBE could not confidently map this description to supported music
> preferences. Please clarify your request or set the preferences manually.

I prefer this to guessing because an extra question is less harmful than a
confident recommendation based on preferences the listener never intended.

## Limitations and biases

One limitation is that Gemini does not actually listen to uploaded music. It
only interprets the user's written description, such as "soft classical music
for studying." Audio analysis is handled separately by local feature-extraction
code and a KNN model.

Recommendation quality is limited by the songs in the application's catalog.
The built-in catalog contains only 60 synthetic songs. If a genre, mood,
artist, cultural style, or language is not represented well, the system cannot
provide strong recommendations for it. This may favor common English music
terms and overlook less represented ways of describing music.

Genre and mood are also subjective. Words such as "chill," "dark," or
"energetic" may mean different things to different people and cultures. Gemini
may interpret an unclear description differently from what the listener meant.
The local fallback is more predictable, but it recognizes a limited vocabulary
and may miss slang, spelling errors, mixed-language requests, or creative
descriptions.

The audio classifier is trained from the small application catalog. Its genre
and mood values are suggestions, not objective facts. That is why VYBE displays
the estimates and their provenance for the listener to review and correct.

My reliability evaluation also uses a small controlled test dataset. A 100%
result means those declared cases passed; it does not prove that the system
will correctly understand every real-world request. Live Gemini output can
also change across requests or model versions. VYBE does not use popularity or
listening history, which improves privacy and reproducibility but limits trend
awareness and personalization. Anonymous sessions also have no account
recovery or cross-device synchronization.

## Potential misuse and prevention

A user could upload audio they do not own or have permission to use. VYBE asks
the user to confirm their rights, validates the file, and deletes it after
analysis. It stores only reviewed metadata. I understand that a confirmation
checkbox cannot fully prove or enforce copyright ownership.

A user could also enter false song information. The application validates the
shape and numeric ranges, but it cannot prove that every manually entered value
is factually correct. Private records are isolated to the anonymous session, so
incorrect private data does not change the built-in public catalog.

Someone could try prompt injection, unsupported instructions, extremely long
input, oversized uploads, or repeated requests. VYBE limits prompt and file
sizes, requests a constrained structured Gemini response, and validates it
against supported genres, moods, and numeric ranges. Invalid output is rejected
and replaced by the local fallback. AI and audio proposals require visible user
review before affecting ranking or storage.

The Gemini key stays in a server-side environment variable and is not returned
to the browser or written to normal logs. Safe errors, session isolation,
same-origin protection, security headers, sanitized logs, catalog-only ranking,
and temporary-file cleanup further reduce risk.

These controls reduce misuse but cannot prevent everything. A public production
deployment would still need stronger authentication, rate limiting, abuse
monitoring and reporting, clearer retention controls, trusted-host settings,
and terms covering copyright and acceptable use.

## Reliability testing reflection

The biggest surprise was that having a valid Gemini API key did not mean every
request was successfully handled by Gemini. At one point, the interface showed
that Gemini was configured, but a request still used deterministic fallback.
This taught me that "AI is configured" and "AI completed this request" are two
different states.

I updated the interface to distinguish Gemini being ready, Gemini successfully
handling the latest request, local demo mode, and Gemini being unavailable with
local fallback. The app does not claim Gemini succeeded until its response
passes schema and music-domain validation.

I was also surprised that a response could sound reasonable while containing a
value that did not fit the application's allowed schema. Natural-sounding text
is not automatically a safe application result. The deterministic fallback was
more important than I expected because it kept the main journey working when a
key was missing, the provider failed, or output was invalid.

Testing improved my confidence but also showed me its limits. The controlled
evaluation cases passed consistently, while live Gemini wording could change.
I learned to test structured fields, grounding, constraints, review status, and
fallback behavior instead of expecting the exact same sentence every time. I
report the 100% fixed-set result as reproducible regression evidence, not proof
that the AI is universally accurate.

## Collaboration with AI

I used AI throughout the project as a design and development assistant. It
helped me divide the work into phases, compare technology choices, draft the
architecture and UML diagrams, implement components, write tests, troubleshoot
server problems, and improve documentation.

I did not understand every suggestion immediately. I repeatedly asked for
plain-language explanations of a modular monolith, deterministic ranking,
retrieval, fallback behavior, FastAPI, SQLite, and browser local storage. This
helped me make decisions rather than accepting technical terms without
understanding them.

I also ran the application and questioned the AI when its explanation did not
match what I saw. For example, the interface continued showing deterministic
mode after I configured Gemini. Investigating it helped me understand the
difference between environment configuration, provider availability, a
validated AI response, and fallback behavior.

The collaboration was useful, but it was not automatic. I clarified the
requirements several times, removed features that did not make sense, restarted
and tested the app after configuration changes, reviewed live output, and made
the final product decisions myself.

### Helpful AI suggestion

One helpful suggestion was to make Gemini return a structured preference
proposal that the listener must review before it affects recommendations. I was
initially focused mainly on adding AI to the application. The suggestion helped
me understand that calling Gemini was not enough; its output needed validation,
visible review, correction, and fallback.

The resulting workflow is: user description, Gemini proposal, schema
validation, user review, approved preferences, and then local retrieval and
ranking. This made the AI useful while keeping the listener in control. It also
made the feature testable through structured genres, moods, numeric values,
fallback status, and review requirements.

### Flawed AI suggestion

An early AI suggestion included popularity as a recommendation feature. It
sounded reasonable because commercial music applications often use popularity.
After thinking about this project, I realized VYBE had no trustworthy source for
current popularity, uploaded audio could not reveal it, and users could not
provide it consistently.

Keeping popularity would have created misleading data and made the scoring look
more informed than it was. I removed it from the domain model, catalog options,
manual entry, audio analysis, ranking, and explanations.

This taught me that an AI suggestion can sound professional and still be wrong
for the actual product. I needed to ask where the data would come from, whether
a user could understand it, and whether I could test the feature honestly. I
now treat AI as a collaborator that offers options, not an authority whose
design decisions should be accepted automatically.

## Safeguards

I added several safeguards because I did not want a reasonable-sounding AI
response to be trusted automatically:

- The user sees and reviews AI interpretations and audio proposals.
- JSON Schema, Pydantic models, fixed enums, and numeric bounds reject invalid
  values.
- Retrieval uses caller-visible catalog records, and final ranking is
  deterministic.
- Provider failure activates deterministic fallback, while manual entry remains
  available.
- Private-song queries are filtered by session, and uploaded audio is deleted
  immediately after analysis or failure.
- Structured logs are sanitized and include request IDs, timings, validation
  outcomes, and fallback status rather than secrets or raw uploads.
- The app does not collect listening history, calculate popularity, play music,
  or permanently store uploaded audio.
- The interface distinguishes Gemini being configured, Gemini successfully
  handling a request, deterministic demo mode, and provider fallback. I do not
  label Gemini as active until the response passes schema and domain validation.

## Next reliability improvement

My next improvement would be a small human-labeled prompt comparison set for
Gemini and `rules-v1`. Each prompt would have acceptable genres, moods,
constraints, and ambiguity behavior instead of requiring one exact sentence.
The evaluator could measure field agreement, unsupported-field rate, fallback
rate, and how often a human correction is needed.

This would be more useful than adding another model immediately. It would test
the part I currently know least about, whether different people agree with the
interpretation, without making the application dramatically more complicated.

## Monitoring and change policy

If I continue developing VYBE, I should run the complete test suite and fixed
evaluation before changing prompts, Gemini models, cue mappings, catalog data,
retrieval logic, classifier behavior, or ranking weights. When an evaluation
case changes meaning, I should version the dataset instead of silently editing
the expected result.

Before any public release, I would also test live Gemini separately with a
larger and more diverse prompt set. I would record the exact model ID, test
date, API tier, success rate, validation failures, and fallback rate so that a
future result can be compared honestly.
