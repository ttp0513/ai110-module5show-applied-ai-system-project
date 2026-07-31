# Phase 5: AI-assisted audio analysis

## Outcome

Phase 5 lets a listener upload an audio file temporarily and receive an
editable recommendation-feature proposal. VYBE does not play or retain the
audio. The private catalog receives only values that the listener explicitly
reviews and approves.

## What the AI does

VYBE decodes the waveform with `librosa` and measures duration and estimated
tempo. It derives bounded numeric estimates for energy, positivity,
danceability, acousticness, instrumentalness, and liveness from signal
descriptors. These are useful recommendation inputs, not objective facts.

A specialized K-nearest-neighbors model is trained reproducibly from the 60
validated built-in songs. It maps the numeric feature vector to VYBE's
supported genre and mood vocabularies and returns confidence scores. Its
predictions prefill the review form and meaningfully affect saved songs and
later recommendations.

This phase does not use a general-purpose language model, identify a commercial
recording, transcribe lyrics, or infer popularity. Audio analysis cannot
reliably determine personal or cultural meaning, so review remains mandatory.

## Safety and privacy lifecycle

1. The listener confirms ownership or permission to analyze the audio.
2. The server accepts WAV, FLAC, OGG, MP3, or M4A extensions only when the
   bytes match the format.
3. The upload streams to a randomized non-public path and stops at 25 MiB.
4. Decoded audio must be audible and between 15 and 900 seconds.
5. A `finally` block deletes the temporary file after success or failure.
6. An audio-free proposal is held in memory and bound to the browser session.
7. Approval saves reviewed values and field-level provenance to SQLite.
8. Approval or cancellation removes the proposal.

Restarting the server discards unapproved proposals. Approved song data lasts
until the owning browser deletes it, provided its anonymous-session cookie
remains available.

## Provenance

- `measured`: duration and tempo
- `algorithm_estimated`: numeric acoustic approximations
- `ai_estimated`: genre and mood from `catalog-knn-v1`
- `embedded_metadata`: title, artist, or year read from tags
- `user_entered`: a fallback or manual value

If the listener changes a proposal, `user_corrected` is saved as `true` for
that field.

## API and fallback

- `POST /api/songs/analyze` creates an audio-free review proposal.
- `POST /api/songs/analyzed/{analysis_id}/approve` saves reviewed values.
- `DELETE /api/songs/analyzed/{analysis_id}` discards the proposal.
- `POST /api/songs/private` remains the fully manual fallback.

## Reliability checks

Integration tests generate an original sine-wave WAV and exercise the real
analyzer. They cover session isolation, one-time approval, correction
provenance, upload source, rights confirmation, disguised files, and UI/API
contracts.
