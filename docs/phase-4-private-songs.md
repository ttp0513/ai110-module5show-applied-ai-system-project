# Phase 4: Private Songs and Manual Entry

## 1. Phase objective

Phase 4 lets an anonymous listener manually add a complete song record, use it
in deterministic recommendations, inspect it, and remove it without exposing
the record to another listener.

Audio upload and automated music analysis are intentionally reserved for
Phase 5.

## 2. Anonymous session model

The server issues a random UUID in a persistent HTTP-only, same-site cookie.
Only IDs registered in SQLite are accepted. A user-provided or unknown ID is
replaced rather than trusted.

Private data is:

- Stored in a local SQLite database
- Indexed by the opaque session ID
- Unavailable to other anonymous sessions
- Preserved across application restarts
- Never written to Git, CSV, browser storage, or logs

The cookie is configured for up to ten years so the same browser can reconnect
until the listener deletes the song. Clearing browser cookies removes the
access key but does not automatically delete the database row.

## 3. Manual song contract

Every field is required:

- Title and artist
- Supported genre and mood
- Energy, tempo, and valence
- Danceability and acousticness
- Instrumentalness and liveness
- Release year and duration

The API rejects unknown fields, including popularity. Normalized features must
remain from zero through one, release year cannot be in the future, and other
numeric limits match the canonical song contract.

## 4. Provenance

Every manual field receives deterministic provenance:

```text
source = user_entered
confidence = null
model_version = null
user_corrected = false
```

Phase 5 can add measured, embedded-metadata, and AI-estimated sources without
changing the canonical song or recommendation response.

## 5. Recommendation integration

For the current session:

```text
eligible songs = 60 built-in songs + private session songs
```

The combined immutable tuple enters the existing deterministic engine. Private
songs receive no special boost and are scored with the same features and
weights as built-in songs.

Another session receives only its own combined catalog.

## 6. API

### `GET /api/songs/private`

Lists complete private records and provenance for the current session.

### `POST /api/songs/private`

Validates and creates a canonical manual song. Returns `201 Created`.

### `DELETE /api/songs/private/{song_id}`

Deletes a record only if it belongs to the current session. Returns `404` for
unknown or differently owned IDs.

### `GET /api/catalog/options`

Now reports built-in, private, and combined counts for the current session.

## 7. Guardrails

- Maximum 100 private songs per anonymous session
- Unpredictable server-issued identifiers
- Persistent HTTP-only, same-site session cookie
- Production cookies marked secure
- Thread-safe SQLite repository with transactions and foreign keys
- Strict schema with unknown fields rejected
- Catalog isolation tested using two independent clients
- Catalog text inserted into the UI using safe text nodes

## 8. Limitations

- There is no account recovery or cross-device synchronization.
- Clearing cookies loses access unless account recovery is added.
- Orphaned anonymous records need a future retention policy.
- Multiple application hosts would need a shared production database.
- Audio upload, file validation, and analysis are not part of this phase.

Accounts remain the recommended future option when cross-device access or
recovery becomes a product requirement.
