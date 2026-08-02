# VYBE diagram guide

This folder explains VYBE in seven diagrams, ordered for readers with no prior
knowledge of the project. Each Mermaid source begins with a plain-language
comment block that explains its purpose, reading direction, and main takeaway.
Lines beginning with `%%` are documentation comments and do not affect rendering.

## Recommended reading path

1. [User journey](01-user-journey.mmd) — begin here to see what listeners can do
   and where they remain in control.
2. [System architecture](02-system-architecture.mmd) — see the complete browser,
   FastAPI, Gemini, local recommendation, storage, and audio-analysis design.
3. [AI preference workflow](03-ai-preference-workflow.mmd) — understand exactly
   how Gemini interprets a request, how output is validated, and when fallback runs.
4. [Recommendation workflow](04-recommendation-workflow.mmd) — follow reviewed
   preferences through local retrieval, deterministic scoring, and grounded output.
5. [Private-song workflow](05-private-song-workflow.mmd) — see audio-assisted and
   manual entry, human review, SQLite persistence, recommendation use, and deletion.
6. [AI reliability and guardrails](06-ai-reliability.mmd) — understand validation,
   grounding, safe degradation, fallback, and sanitized observability.
7. [Domain model UML](07-domain-model-uml.mmd) — optional technical appendix showing
   the typed objects that make catalog evidence and provenance auditable.

## Five ideas to remember

- VYBE recommends songs; it does not play or stream them.
- Gemini converts natural-language requests into reviewable preferences.
- Gemini does not choose, invent, or rank songs.
- Local TF-IDF retrieval and deterministic feature scoring rank real catalog songs.
- Uploaded audio is deleted; only listener-approved metadata may persist in SQLite.

## Visual conventions

- Blue represents browser interaction or API boundaries.
- Purple represents AI interpretation.
- Green represents local application processing.
- Orange represents validation or safety controls.
- Gray represents storage or infrastructure.
- Yellow notes call out important design constraints.
- Solid arrows show normal flow; dotted arrows show optional or fallback paths.

The Mermaid files are the source of truth. GitHub, VS Code Mermaid extensions,
and Mermaid-compatible tools can render them without requiring exported images.
