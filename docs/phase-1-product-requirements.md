# Phase 1: Product Requirements

## 1. Product summary

VYBE helps listeners find music for a moment, activity, or desired feeling.
A listener can describe a vibe in natural language or select musical
preferences manually. The system retrieves candidate songs, applies
transparent feature-based scoring, and explains why each result fits.

Listeners can also add private songs by uploading audio for assisted analysis
or by entering all features manually.

VYBE is a recommendation application, not a music player. It identifies songs
by title and artist but does not stream, preview, or play audio.

## 2. Problem statement

Traditional music discovery often assumes that listening history fully
represents a person's current intent. A listener may instead need music for a
specific situation, such as studying, exercising, unwinding, or gaining
confidence. VYBE converts that situational intent into inspectable musical
preferences and recommendations.

## 3. Target users

- Primary: listeners approximately 16-28 who discover music by mood or activity
- Secondary: students, creators, gamers, gym users, and focus-music listeners
- Accessibility: the experience must remain usable without motion, color
  perception, precise pointer input, or AI availability

## 4. Product principles

1. **Intent first:** begin with what the listener needs right now.
2. **Transparent AI:** show the AI interpretation before using it.
3. **Catalog grounded:** never recommend a song that is not in an approved
   catalog.
4. **Human control:** every inferred preference and uploaded-song feature is
   reviewable and editable.
5. **Graceful fallback:** manual recommendation remains usable when AI fails.
6. **Private by default:** user audio and private catalog entries are not
   publicly shared.

## 5. MVP capabilities

### 5.1 Discover music

- Accept a natural-language vibe request.
- Extract supported, structured musical preferences.
- Show the interpretation for review and correction.
- Provide complete manual preference controls.
- Retrieve semantically relevant catalog candidates.
- Rank candidates using retrieval relevance, feature similarity, and
  constraints.
- Return five catalog-grounded recommendations.
- Display identifying song information without providing playback.
- Explain recommendations in plain language.
- Expose deterministic score details on request.
- Refine a mix with quick controls or natural-language instructions.

### 5.2 Add a song

- Accept supported audio uploads.
- Validate file type, size, duration, and content signature.
- Read available embedded metadata.
- Measure deterministic audio properties.
- Estimate supported musical characteristics using specialized models.
- Display source and confidence for estimated values.
- Require user review before saving.
- Allow complete manual entry without an audio upload.
- Preserve valid partial results if analysis fails.
- Add an approved song to the user's private catalog and retrieval index.
- Allow a user-added song to appear in later recommendations.

### 5.3 Reliability and operations

- Validate structured AI outputs.
- Verify generated claims against catalog facts.
- Fall back to deterministic explanations.
- Produce structured, privacy-aware logs.
- Include a fixed AI evaluation dataset and executable evaluation workflow.
- Provide a deterministic demonstration mode.

## 6. Primary user journeys

### Journey A: natural-language recommendation

1. The listener describes a situation or desired vibe.
2. AI converts the request into supported preferences and constraints.
3. The listener reviews and optionally edits the interpretation.
4. The system retrieves and ranks catalog songs.
5. The listener receives five recommendations with grounded explanations.
6. The listener may refine, like, keep, or skip results.

### Journey B: manual recommendation

1. The listener opens manual controls.
2. The listener selects at least one preference.
3. The deterministic engine scores and ranks songs.
4. The listener receives recommendations and score explanations.

### Journey C: AI-assisted song addition

1. The listener selects an audio file and confirms upload rights.
2. The system validates and analyzes the file.
3. The listener reviews metadata, measurements, estimates, and confidence.
4. The listener corrects values as needed.
5. The listener approves the song.
6. The system saves its features and indexes it for private retrieval.

### Journey D: manual song addition

1. The listener opens the complete song form.
2. The listener enters identity, metadata, and all recommendation features.
3. The system validates the values.
4. The listener approves the song for the private catalog.

## 7. Out of scope for the MVP

- User accounts and cross-device synchronization
- Public user-song sharing
- Audio streaming, previews, and playback
- Spotify or Apple Music integration
- Payments or subscriptions
- Social feeds and friend graphs
- Collaborative playlists
- Model fine-tuning
- Production cloud deployment

Popularity and familiarity are not supported recommendation features. They are
not reliably inferable from audio, change over time, and cannot reasonably be
provided by listeners adding their own songs.

## 8. UX requirements

- Mobile-first responsive layout with desktop support.
- Dark, high-contrast visual system with restrained gradient accents.
- Minimum 44 by 44 pixel touch targets.
- Keyboard navigation and visible focus states.
- Screen-reader labels and meaningful reading order.
- Reduced-motion support.
- Clear loading, empty, error, and fallback states.
- AI estimates must be labeled as estimates.
- A user must be able to edit AI interpretations before committing them.

## 9. Privacy and ownership requirements

- Require the user to confirm ownership or permission before audio analysis.
- Keep user-added songs private in the MVP.
- Delete uploaded audio when analysis finishes or fails.
- Retain only user-approved metadata, derived features, and provenance.
- Never commit audio, credentials, raw logs, or generated private indexes.
- Do not log raw user prompts by default.
- Provide an explicit removal action for user-added song records.

## 10. Technical direction

- Python application services
- FastAPI backend
- Pydantic input, output, and configuration validation
- Responsive HTML, CSS, and JavaScript interface
- Embedding retrieval over approved song documents
- Configurable language model for preference extraction and explanations
- Specialized music analysis with Essentia and/or librosa
- Pytest unit, integration, guardrail, and evaluation tests
- Structured application logging
- Local deterministic demo mode

The precise persistence mechanism and model providers will be selected in
Phase 2 after compatibility and setup cost are evaluated.
