const state = {
  options: null,
  selectedGenres: new Set(),
  selectedMoods: new Set(),
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

loadOptions();
