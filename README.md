# VYBE

VYBE is an AI-assisted music discovery application that turns a listener's
natural-language description into a transparent, catalog-grounded mix.

The application will also let listeners upload their own audio. Music-analysis
models will estimate supported musical features, and the listener must review
or correct those values before the track enters their private catalog.

## Project status

**Phase 1 complete:** product requirements and system boundaries are defined.
No application code has been implemented yet.

## Phase 1 documents

- [Product requirements](docs/phase-1-product-requirements.md)
- [Data and AI contract](docs/phase-1-data-ai-contract.md)
- [Acceptance criteria](docs/phase-1-acceptance-criteria.md)
- [Decision log](docs/decision-log.md)
- [System context diagram](diagrams/system-context.mmd)
- [Primary user journeys](diagrams/user-journeys.mmd)

## Planned delivery phases

1. Requirements and project definition
2. Project setup and architecture
3. Song catalog and deterministic recommender
4. User song upload and manual entry
5. AI audio analysis
6. Retrieval-augmented generation
7. AI preference extraction
8. Hybrid ranking and grounded explanations
9. Backend API
10. Responsive user interface
11. Logging, security, and guardrails
12. Testing and AI evaluation
13. Documentation and final delivery

## Current assumptions

- The MVP is a responsive web application.
- No account is required for the first version.
- User-added songs are private.
- Uploaded audio is deleted after analysis by default.
- Users can enter or correct every recommendation feature manually.
- Playback integrations and social features are outside the MVP.

These assumptions are recorded as provisional decisions and can be changed
before Phase 2 begins.
