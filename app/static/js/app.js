const state = {
  options: null,
  selectedGenres: new Set(),
  selectedMoods: new Set(),
  analysisId: null,
};

const elements = {
  form: document.querySelector("#recommendation-form"),
  genres: document.querySelector("#genre-options"),
  moods: document.querySelector("#mood-options"),
  excludedGenre: document.querySelector("#excluded-genre"),
  excludedMood: document.querySelector("#excluded-mood"),
  summary: document.querySelector("#selected-summary"),
  signalSummary: document.querySelector("#signal-summary"),
  catalogSummary: document.querySelector("#catalog-summary"),
  songCount: document.querySelector("#song-count"),
  error: document.querySelector("#form-error"),
  submit: document.querySelector("#submit-button"),
  resultsSection: document.querySelector("#results-section"),
  resultsSummary: document.querySelector("#results-summary"),
  resultsList: document.querySelector("#results-list"),
  songGenre: document.querySelector("#song-genre"),
  songMood: document.querySelector("#song-mood"),
  songForm: document.querySelector("#manual-song-form"),
  songFormMessage: document.querySelector("#song-form-message"),
  saveSongButton: document.querySelector("#save-song-button"),
  privateSongCount: document.querySelector("#private-song-count"),
  privateSongList: document.querySelector("#private-song-list"),
  analysisForm: document.querySelector("#audio-analysis-form"),
  analysisMessage: document.querySelector("#analysis-message"),
  analyzeButton: document.querySelector("#analyze-button"),
  analysisReview: document.querySelector("#analysis-review"),
  analysisFileSummary: document.querySelector("#analysis-file-summary"),
  analysisWarnings: document.querySelector("#analysis-warnings"),
  analysisConfidence: document.querySelector("#analysis-confidence"),
  cancelAnalysis: document.querySelector("#cancel-analysis-button"),
  manualSongPanel: document.querySelector("#manual-song-panel"),
  saveSongLabel: document.querySelector("#save-song-label"),
};

function titleCase(value) {
  return value.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function createChoiceChip(type, value) {
  const label = document.createElement("label");
  label.className = "choice-chip";
  label.innerHTML = `
    <input type="checkbox" name="${type}" value="${value}">
    <span>${titleCase(value)}</span>
  `;

  const input = label.querySelector("input");
  input.addEventListener("change", () => {
    const selected = type === "genre" ? state.selectedGenres : state.selectedMoods;
    input.checked ? selected.add(value) : selected.delete(value);
    updateSummary();
  });
  return label;
}

function populateSelect(select, values) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = titleCase(value);
    select.append(option);
  });
}

function renderOptions(options) {
  elements.genres.replaceChildren(
    ...options.genres.map((genre) => createChoiceChip("genre", genre)),
  );
  elements.moods.replaceChildren(
    ...options.moods.map((mood) => createChoiceChip("mood", mood)),
  );
  populateSelect(elements.excludedGenre, options.genres);
  populateSelect(elements.excludedMood, options.moods);
  populateSelect(elements.songGenre, options.genres);
  populateSelect(elements.songMood, options.moods);
  elements.songCount.textContent = options.song_count;
  elements.catalogSummary.textContent = `${options.song_count} songs ready to rank`;
}

function activeSliderPreferences() {
  return [...document.querySelectorAll(".slider-control")]
    .filter((control) => control.querySelector(".feature-toggle").checked)
    .map((control) => {
      const input = control.querySelector('input[type="range"]');
      const label = control.querySelector(".slider-heading > label").textContent;
      const output = control.querySelector("output").textContent;
      return {
        key: control.dataset.preference,
        value: Number(input.value),
        label: `${label}: ${output}`,
      };
    });
}

function updateSummary() {
  const selections = [
    ...[...state.selectedGenres].map((value) => titleCase(value)),
    ...[...state.selectedMoods].map((value) => titleCase(value)),
    ...activeSliderPreferences().map((item) => item.label),
  ];

  if (elements.excludedGenre.value) {
    selections.push(`No ${titleCase(elements.excludedGenre.value)}`);
  }
  if (elements.excludedMood.value) {
    selections.push(`No ${titleCase(elements.excludedMood.value)}`);
  }

  const tags = selections.length ? selections : ["Nothing selected yet"];
  elements.summary.replaceChildren(
    ...tags.map((text) => {
      const tag = document.createElement("span");
      tag.textContent = text;
      return tag;
    }),
  );

  const positiveSignals = [
    ...state.selectedGenres,
    ...state.selectedMoods,
    ...activeSliderPreferences().map((item) => item.label),
  ];
  elements.signalSummary.textContent = positiveSignals.length
    ? positiveSignals.slice(0, 3).map(titleCase).join(" / ")
    : "Waiting for your vibe";
}

function buildPayload() {
  const payload = {
    preferred_genres: [...state.selectedGenres],
    preferred_moods: [...state.selectedMoods],
    excluded_genres: elements.excludedGenre.value
      ? [elements.excludedGenre.value]
      : [],
    excluded_moods: elements.excludedMood.value
      ? [elements.excludedMood.value]
      : [],
  };

  activeSliderPreferences().forEach((preference) => {
    payload[preference.key] = preference.key === "target_tempo_bpm"
      ? preference.value
      : preference.value / 100;
  });
  return payload;
}

function reasonRow(reason) {
  const row = document.createElement("div");
  row.className = "reason-row";
  const feature = document.createElement("span");
  feature.className = "reason-feature";
  feature.textContent = titleCase(reason.feature.replaceAll("_", " "));
  const summary = document.createElement("span");
  summary.className = "reason-summary";
  summary.textContent = reason.summary;
  const points = document.createElement("span");
  points.className = "reason-points";
  points.textContent = `+${(reason.contribution * 100).toFixed(1)} pts`;
  row.append(feature, summary, points);
  return row;
}

function resultCard(recommendation) {
  const article = document.createElement("article");
  article.className = "result-card";
  const rank = document.createElement("span");
  rank.className = "result-rank";
  rank.textContent = String(recommendation.rank).padStart(2, "0");

  const main = document.createElement("div");
  main.className = "result-main";
  const title = document.createElement("h3");
  title.textContent = recommendation.song.title;
  const artist = document.createElement("span");
  artist.className = "result-artist";
  artist.textContent = recommendation.song.artist;
  const meta = document.createElement("span");
  meta.className = "result-meta";
  meta.textContent =
    `${recommendation.song.genre} · ${recommendation.song.mood} · ` +
    `${Math.round(recommendation.song.tempo_bpm)} BPM · ` +
    `${recommendation.song.release_year}`;
  main.append(title, artist, meta);

  const score = document.createElement("div");
  score.className = "result-score";
  const scoreValue = document.createElement("strong");
  scoreValue.textContent = `${(recommendation.score * 100).toFixed(1)}%`;
  const scoreLabel = document.createElement("span");
  scoreLabel.textContent = "Match";
  score.append(scoreValue, scoreLabel);
  article.append(rank, main, score);

  const details = document.createElement("details");
  details.className = "result-details";
  const detailsSummary = document.createElement("summary");
  detailsSummary.textContent = "See exactly why this matched";
  details.append(detailsSummary);
  const reasons = document.createElement("div");
  reasons.className = "reason-list";
  reasons.append(...recommendation.reasons.map(reasonRow));
  details.append(reasons);
  article.append(details);
  return article;
}

function renderResults(payload) {
  elements.resultsList.replaceChildren(
    ...payload.recommendations.map(resultCard),
  );
  elements.resultsSummary.textContent =
    `${payload.considered_song_count} songs considered · ` +
    `${payload.filtered_song_count} filtered out`;
  elements.resultsSection.hidden = false;
  elements.resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function privateSongRow(record) {
  const row = document.createElement("div");
  row.className = "private-song-row";
  const identity = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = record.song.title;
  const metadata = document.createElement("small");
  metadata.textContent =
    `${record.song.artist} · ${record.song.genre} · ${record.song.mood}`;
  identity.append(title, metadata);

  const remove = document.createElement("button");
  remove.className = "delete-song-button";
  remove.type = "button";
  remove.textContent = "Remove";
  remove.setAttribute("aria-label", `Remove ${record.song.title}`);
  remove.addEventListener("click", async () => {
    remove.disabled = true;
    const response = await fetch(`/api/songs/private/${record.song.id}`, {
      method: "DELETE",
    });
    if (response.ok) {
      await loadPrivateSongs();
      await refreshCatalogCounts();
    } else {
      remove.disabled = false;
      elements.songFormMessage.textContent = "This private song could not be removed.";
      elements.songFormMessage.hidden = false;
    }
  });
  row.append(identity, remove);
  return row;
}

function renderPrivateSongs(payload) {
  elements.privateSongCount.textContent = payload.count;
  if (!payload.records.length) {
    const empty = document.createElement("p");
    empty.className = "empty-private-state";
    empty.textContent =
      "No private songs yet. Add one to include it in your next ranking.";
    elements.privateSongList.replaceChildren(empty);
    return;
  }
  elements.privateSongList.replaceChildren(
    ...payload.records.map(privateSongRow),
  );
}

async function loadPrivateSongs() {
  const response = await fetch("/api/songs/private");
  if (!response.ok) throw new Error("Private songs are unavailable.");
  renderPrivateSongs(await response.json());
}

async function refreshCatalogCounts() {
  const response = await fetch("/api/catalog/options");
  if (!response.ok) return;
  const options = await response.json();
  state.options.song_count = options.song_count;
  state.options.private_song_count = options.private_song_count;
  elements.songCount.textContent = options.song_count;
  elements.catalogSummary.textContent = `${options.song_count} songs ready to rank`;
}

async function loadOptions() {
  try {
    const response = await fetch("/api/catalog/options");
    if (!response.ok) throw new Error("Catalog options are unavailable.");
    state.options = await response.json();
    renderOptions(state.options);
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
    elements.submit.disabled = true;
  }
}

function buildManualSongPayload(form) {
  const data = new FormData(form);
  const normalizedFeatures = [
    "energy",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "liveness",
  ];
  const payload = Object.fromEntries(data.entries());
  normalizedFeatures.forEach((feature) => {
    payload[feature] = Number(payload[feature]) / 100;
  });
  payload.tempo_bpm = Number(payload.tempo_bpm);
  payload.release_year = Number(payload.release_year);
  payload.duration_seconds = Number(payload.duration_seconds);
  return payload;
}

function populateReviewForm(song) {
  Object.entries(song).forEach(([name, value]) => {
    const input = elements.songForm.elements[name];
    if (!input) return;
    const normalized = [
      "energy",
      "valence",
      "danceability",
      "acousticness",
      "instrumentalness",
      "liveness",
    ].includes(name);
    input.value = normalized ? Math.round(Number(value) * 100) : value;
    if (input.type === "range") input.dispatchEvent(new Event("input"));
  });
}

function showAnalysisProposal(proposal) {
  state.analysisId = proposal.analysis_id;
  populateReviewForm(proposal.suggested_song);
  elements.analysisFileSummary.textContent =
    `${proposal.file_info.original_filename} · ` +
    `${proposal.file_info.detected_format.toUpperCase()} · audio already deleted`;
  elements.analysisWarnings.replaceChildren(
    ...proposal.warnings.map((warning) => {
      const paragraph = document.createElement("p");
      paragraph.textContent = `! ${warning}`;
      return paragraph;
    }),
  );
  const predictions = proposal.provenance.filter(
    (item) => item.source === "ai_estimated",
  );
  elements.analysisConfidence.replaceChildren(
    ...predictions.map((item) => {
      const badge = document.createElement("span");
      const confidence = Math.round((item.confidence || 0) * 100);
      badge.textContent =
        `${titleCase(item.feature_name)} estimate · ${confidence}% confidence`;
      return badge;
    }),
  );
  elements.analysisReview.hidden = false;
  elements.manualSongPanel.open = true;
  elements.saveSongLabel.textContent = "Approve reviewed values";
  elements.manualSongPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function discardAnalysis() {
  if (state.analysisId) {
    await fetch(`/api/songs/analyzed/${state.analysisId}`, { method: "DELETE" });
  }
  state.analysisId = null;
  elements.analysisReview.hidden = true;
  elements.saveSongLabel.textContent = "Save private song";
}

elements.analysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.analysisMessage.hidden = true;
  elements.analyzeButton.disabled = true;
  elements.analyzeButton.querySelector("span").textContent = "Analyzing safely…";
  if (state.analysisId) await discardAnalysis();

  try {
    const response = await fetch("/api/songs/analyze", {
      method: "POST",
      body: new FormData(elements.analysisForm),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Audio could not be analyzed.");
    }
    showAnalysisProposal(await response.json());
    elements.analysisForm.reset();
  } catch (error) {
    elements.analysisMessage.textContent = error.message;
    elements.analysisMessage.hidden = false;
  } finally {
    elements.analyzeButton.disabled = false;
    elements.analyzeButton.querySelector("span").textContent = "Analyze temporarily";
  }
});

elements.cancelAnalysis.addEventListener("click", async () => {
  await discardAnalysis();
  elements.songForm.reset();
  releaseYearInput.value = String(currentYear);
});

document.querySelectorAll(".slider-control").forEach((control) => {
  const slider = control.querySelector('input[type="range"]');
  const toggle = control.querySelector(".feature-toggle");
  const output = control.querySelector("output");

  const showValue = () => {
    output.textContent = control.dataset.preference === "target_tempo_bpm"
      ? `${slider.value} BPM`
      : `${slider.value}%`;
    updateSummary();
  };

  slider.addEventListener("input", showValue);
  toggle.addEventListener("change", updateSummary);
});

elements.excludedGenre.addEventListener("change", updateSummary);
elements.excludedMood.addEventListener("change", updateSummary);

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.error.hidden = true;
  const payload = buildPayload();
  const hasPositiveSignal =
    payload.preferred_genres.length ||
    payload.preferred_moods.length ||
    activeSliderPreferences().length;

  if (!hasPositiveSignal) {
    elements.error.textContent = "Choose a genre, mood, or sound detail first.";
    elements.error.hidden = false;
    return;
  }

  elements.submit.disabled = true;
  elements.submit.querySelector("span").textContent = "Ranking the catalog…";

  try {
    const response = await fetch("/api/recommendations/deterministic?limit=5", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.[0]?.msg || "Recommendations are unavailable.");
    }
    renderResults(await response.json());
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
  } finally {
    elements.submit.disabled = false;
    elements.submit.querySelector("span").textContent = "Generate recommendations";
  }
});

document.querySelectorAll(".manual-feature-grid input[type='range']").forEach(
  (input) => {
    const output = input.closest("label").querySelector("output");
    input.addEventListener("input", () => {
      output.textContent = `${input.value}%`;
    });
  },
);

const releaseYearInput = elements.songForm.elements.release_year;
const currentYear = new Date().getFullYear();
releaseYearInput.max = String(currentYear);
releaseYearInput.value = String(currentYear);

elements.songForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.songFormMessage.hidden = true;
  elements.saveSongButton.disabled = true;
  elements.saveSongButton.querySelector("span").textContent = "Saving…";

  try {
    const endpoint = state.analysisId
      ? `/api/songs/analyzed/${state.analysisId}/approve`
      : "/api/songs/private";
    const song = buildManualSongPayload(elements.songForm);
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.analysisId ? { song } : song),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.[0]?.msg || error.detail || "Song could not be saved.");
    }
    elements.songForm.reset();
    state.analysisId = null;
    elements.analysisReview.hidden = true;
    elements.saveSongLabel.textContent = "Save private song";
    releaseYearInput.value = String(currentYear);
    document.querySelectorAll(".manual-feature-grid input[type='range']").forEach(
      (input) => {
        input.dispatchEvent(new Event("input"));
      },
    );
    elements.songFormMessage.textContent =
      "Song saved. It will be considered in your next recommendation.";
    elements.songFormMessage.classList.add("success-message");
    elements.songFormMessage.hidden = false;
    await loadPrivateSongs();
    await refreshCatalogCounts();
  } catch (error) {
    elements.songFormMessage.textContent = error.message;
    elements.songFormMessage.classList.remove("success-message");
    elements.songFormMessage.hidden = false;
  } finally {
    elements.saveSongButton.disabled = false;
    elements.saveSongButton.querySelector("span").textContent = "Save private song";
  }
});

async function initialize() {
  await loadOptions();
  try {
    await loadPrivateSongs();
  } catch (error) {
    elements.songFormMessage.textContent = error.message;
    elements.songFormMessage.hidden = false;
  }
}

initialize();
