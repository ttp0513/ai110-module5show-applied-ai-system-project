# UI Checkpoint: Phases 1–3

## Purpose

This checkpoint makes the completed product contract, architecture, catalog,
and deterministic recommendation engine usable from a browser before Phase 4
adds private songs.

## User flow

1. Open VYBE and read the recommendation-only product promise.
2. Choose one or more genres and moods.
3. Optionally activate precise sound controls.
4. Optionally exclude one genre or mood.
5. Review the current mix blueprint.
6. Generate five deterministic recommendations.
7. Expand any recommendation to inspect its feature contributions.

## Visual direction

The interface uses a dark editorial layout, high-contrast lime actions, violet
signal accents, circular music-inspired geometry, compact monospace metadata,
and restrained motion. It does not depend on album art or external media.

## Reliability and accessibility

- Catalog options come from `GET /api/catalog/options`.
- Recommendations come from `POST /api/recommendations/deterministic`.
- At least one positive signal is required before submission.
- API errors are displayed without discarding the current form.
- Catalog text is inserted using `textContent` to prevent markup injection.
- Native fieldsets, labels, checkboxes, sliders, selects, details, and buttons
  preserve keyboard and assistive-technology behavior.
- Visible focus and a skip link support keyboard navigation.
- Reduced-motion preferences disable nonessential transitions.
- Popularity, playback, and listening history are absent.

## Scope boundary

The natural-language composer, AI interpretation review, semantic retrieval,
audio analysis, and private-song workflows will be added only when their
owning phases are implemented and tested.
