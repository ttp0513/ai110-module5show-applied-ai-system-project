# Phase 7: AI preference interpretation

## Outcome

Phase 7 converts a listener's natural-language vibe into VYBE's validated
`UserPreferences` schema. The interpretation is displayed for review before
the listener applies it to the deterministic recommendation builder.

The same natural-language submission now performs two distinct operations:

1. Phase 6 retrieves caller-visible catalog candidates.
2. Phase 7 extracts supported recommendation preferences.

Applying the reviewed interpretation preselects the manual builder. The
existing deterministic scorer—not the model—still produces the final ranking
at this stage.

## Provider design

`PreferenceExtractionProvider` is an application-owned interface with two
implementations:

- `OpenAIPreferenceProvider` uses the Responses API and Pydantic Structured
  Outputs.
- `DemoPreferenceProvider` uses deterministic, versioned local rules.

OpenAI's current Structured Outputs documentation recommends schema-constrained
responses and demonstrates `client.responses.parse` with a Pydantic model:
<https://developers.openai.com/api/docs/guides/structured-outputs>.

The OpenAI request sets `store=False`. Raw prompts are not persisted by VYBE or
written to standard logs. Normal logs contain prompt length, provider name,
fallback status, and extracted-field count only.

## Structured contract

The provider can return only:

- supported genre and mood enums;
- normalized energy, positivity, danceability, acousticness,
  instrumentalness, and liveness;
- tempo from 20 to 300 BPM;
- supported exclusions;
- a short interpretation summary and ambiguity list.

Popularity, familiarity, song claims, arbitrary instructions, and unsupported
fields cannot enter the domain model. Provider output passes through Pydantic
and then through the existing `UserPreferences` validator.

## Review flow

1. The listener describes a vibe.
2. VYBE displays extracted fields, provider/model status, ambiguity warnings,
   and fallback status.
3. If no active supported preference was recognized, Apply is disabled.
4. The listener can discard the interpretation or apply it.
5. Apply updates the visible manual builder.
6. The listener can change any applied control before requesting rankings.

This keeps the model advisory. It cannot silently modify a recommendation.

## Fallback and configuration

The default configuration remains credential-free:

```text
VYBE_DEMO_MODE=true
VYBE_AI_PROVIDER=demo
VYBE_AI_MODEL=gpt-5.6
VYBE_AI_API_KEY=
```

To use OpenAI Structured Outputs:

```text
VYBE_DEMO_MODE=false
VYBE_AI_PROVIDER=openai
VYBE_AI_MODEL=gpt-5.6
VYBE_AI_API_KEY=<secret>
```

The API key belongs only in the ignored `.env` file or deployment secret
store. If the key is absent, the provider times out, refuses, or returns an
invalid result, VYBE uses the local interpreter and identifies the fallback in
the response.

## API

`POST /api/preferences/interpret`

```json
{
  "prompt": "romantic neon night drive, medium energy, no rock"
}
```

The response does not echo the raw prompt. It contains reviewable preferences,
ambiguities, provider/model identity, fallback status, and extracted field
names.

## Reliability

Tests verify fixed extraction cases, determinism, prompt-injection resistance,
unsupported-field exclusion, schema bounds, provider fallback, non-storage in
the OpenAI adapter, API limits, UI integration, and the complete path from
interpreted preferences to deterministic recommendations.
