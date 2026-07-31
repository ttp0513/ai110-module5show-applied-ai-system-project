# Phase 6: Grounded catalog retrieval

## Outcome

Phase 6 introduces VYBE's retrieval layer. A listener can describe a sound,
moment, mood, genre, or artist in natural language and receive relevant
candidates from the approved catalog visible to that browser.

This is the retrieval and grounding foundation for the complete RAG workflow.
Phase 7 will extract structured preferences with a language-model adapter.
Phase 8 will combine retrieval relevance with deterministic feature scoring
and produce final grounded recommendations.

## Retrieval design

Each approved song becomes a derived text document containing:

- title and artist
- canonical genre and mood
- controlled cue words for supported genres and moods
- bounded descriptions of energy, positivity, danceability, acousticness,
  instrumentalness, and tempo
- release year

The service builds TF-IDF vectors with unigrams and bigrams and ranks songs by
cosine similarity to the listener's request. The implementation is local,
deterministic, reproducible, and requires no API key. It is intentionally
described as lexical retrieval with semantic cue enrichment—not as a neural
embedding model.

## Grounded generation

Every result includes a generated explanation assembled only from its
canonical song record. The corresponding genre, mood, energy, and tempo facts
are returned as structured evidence. Unknown queries return no candidates
instead of invented songs.

These evidence-bound templates are the Phase 6 generation layer. A future
language model may improve the prose only after its claims pass the same
catalog grounding checks.

## Privacy and indexing

The retrieval service receives built-in songs plus private songs belonging to
the current anonymous session. It builds an ephemeral in-memory index for that
request. Consequently:

- approved private songs are immediately searchable;
- deleted private songs disappear from subsequent searches;
- another browser cannot index or retrieve those private records;
- the listener's raw request is not stored or written to logs;
- only query length, searched count, and result count are logged.

At MVP catalog size, request-time indexing keeps ownership rules simple and
avoids stale derived data. A persistent vector index can replace this adapter
later without changing the API contract.

## API

`POST /api/retrieval/search?limit=5`

```json
{
  "query": "late-night coding with cozy instrumental beats"
}
```

The response identifies the retrieval method and document version, reports the
number of caller-visible songs searched, and returns up to the requested limit
with catalog evidence and retrieval scores.

Requests must contain 3 to 1,000 characters. The configured
`VYBE_MAX_PROMPT_LENGTH` can impose a stricter operational limit.

## Reliability criteria

Automated tests verify:

- expected cue words retrieve relevant supported genres or moods;
- grounded explanations contain the returned song's actual values;
- unknown terms do not invent candidates;
- private songs are searchable by their owner only;
- empty and oversized requests are rejected;
- deterministic recommendations remain available independently.

Retrieval score measures text relevance only. It is not yet the final music
recommendation score and is labeled accordingly in the UI.
