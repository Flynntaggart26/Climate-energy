# Climate & Energy Explorer

> An interactive, single-file dashboard for exploring CO₂ emissions, energy transitions, and climate equity across 50 countries (1990–2023).

[![CI](https://github.com/Flynntaggart26/Climate-energy/actions/workflows/ci.yml/badge.svg)](https://github.com/Flynntaggart26/Climate-energy/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/Flynntaggart26/Climate-energy)](https://github.com/Flynntaggart26/Climate-energy/releases)
[![Live demo](https://img.shields.io/badge/demo-GitHub_Pages-7c6cff)](https://flynntaggart26.github.io/Climate-energy/)

## Live demo

**https://flynntaggart26.github.io/Climate-energy/**

Try these entry points:

- [Emissions view](https://flynntaggart26.github.io/Climate-energy/?view=emissions) — totals, per-capita, per-GDP and consumption-based CO₂
- [Equity lens](https://flynntaggart26.github.io/Climate-energy/?view=equity) — cumulative vs annual, per-capita vs total, High-income vs Rest
- [Correlation lab](https://flynntaggart26.github.io/Climate-energy/?view=correlation) — GDP vs CO₂ scatter with OLS trend
- [Self-test report](https://flynntaggart26.github.io/Climate-energy/?selftest=1) — built-in checks that verify every view renders

## Contents

- [Features](#features)
- [Themes](#themes)
- [Keyboard shortcuts](#keyboard-shortcuts)
- [Tech](#tech)
- [Project structure](#project-structure)
- [Data & methodology](#data--methodology)
- [Case study](#case-study)
- [Run locally](#run-locally)
- [Testing & CI](#testing--ci)
- [Releases](#releases)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Acknowledgments](#acknowledgments)

## Features

| Tab | What you can investigate |
|-----|--------------------------|
| **Emissions** | Total, per-capita, per-GDP, and consumption-based CO₂ — with a territorial-vs-consumption overlay that reveals carbon leakage |
| **Energy** | Fossil & industry CO₂ mix per country as a stacked chart, absolute (Mt) or 100% share |
| **Correlation Lab** | Any two indicators (GDP, CO₂, energy, population, intensity) as a population-weighted scatter with OLS trend and Pearson r — step through years |
| **Equity Lens** | Four presets: cumulative vs annual, per-capita vs total bubbles, High-income vs Rest, consumption vs territorial with a y=x reference |
| **Table** | Sortable, searchable, paginated data grid of the current selection |

Highlights:

- **KPI dashboard** — selection total, population-weighted per-capita, change since start year, and the NASA GISTEMP temperature anomaly
- **Top-10 ranking board** — bar-scaled leaderboard for the current metric and year; click a country to isolate it
- **Temperature overlay** — global anomaly series on a dual axis over emissions trends
- **Timeline animation** — press ▶ to play the end-year forward through history
- **2030 forecast** — per-country OLS projection drawn as dashed series
- **Region filter chips** — narrow any view by world region
- **Shareable URLs** — every view, country set, metric, year range, theme, overlay, and region filter encodes into a link
- **Exports** — PNG (with background fill), CSV, JSON, iframe embed code, plus copyable insight bullets
- **Insight panel** — every chart gets a computed 3-bullet interpretation with caveats (no black box; all bullets trace to visible data)
- **Guided tour & help modal** — onboarding steps and a shortcut reference built in

## Themes

Six hand-tuned themes with matching chart colors (ticks, grids, legends, and tooltips re-tint with the theme):

| Theme | Character |
|-------|-----------|
| Dark | Deep-space indigo default |
| Light | High-contrast paper |
| Ocean | Cyan/teal abyss |
| Forest | Green canopy |
| Sunset | Rose/amber dusk |
| Auto | Follows the OS color scheme |

Glassmorphism header and control bar, gradient brand mark, custom sliders, and ambient background glows adapt to each theme.

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `1`–`5` | Switch tabs |
| `←` / `→` | Step end year |
| `?` | Open/close help |
| `Esc` | Close panels |

## Tech

Vanilla HTML/CSS/JS + Chart.js 4 via CDN. No framework, no build step, no backend — one auditable `index.html` (~1.3MB with data inlined) that loads in under 2 seconds on GitHub Pages.

- ES2020 client code in a single `<script>` block (strict mode, single state object, pure data transforms)
- CSS custom-property theme engine (`data-theme` + `themeColors()` bridge into Chart.js)
- `?selftest=1` runs 13 in-browser assertions across all five views and renders the report on the page

## Project structure

```
index.html                  # the whole app (markup + styles + logic + inlined data)
data/
  prep.py                   # raw CSVs → data.json + meta.json (159 countries)
  create_embedded.py        # top-50-by-population cut for the web bundle
  inline_data.py            # inlines data into index.html as window.DATA
  data_embedded.json        # web bundle data (regenerable)
  meta_embedded.json        # countries, metrics, presets (regenerable)
  raw/                      # source CSVs (gitignored, re-downloaded by prep.py)
.github/workflows/ci.yml   # data validation + JS syntax + feature + smoke tests
```

## Data & methodology

Sources: **Our World in Data / Global Carbon Project** (`owid-co2-data`) and **NASA GISTEMP** global temperature anomalies.

Pipeline (`data/`):

```
raw CSVs → prep.py → data.json + meta.json (159 countries, strict JSON)
         → create_embedded.py → data_embedded.json (top 50 by population)
         → inline_data.py → window.DATA inside index.html
```

Cleaning decisions: aggregates and bunker fuels dropped (no ISO code), 1990–2023 window, >1M population filter, full region/income mapping with no silent fallbacks, `NaN → null` with strict round-trip checks, CO₂ intensity fixed to kg/$.

## Case study

**Problem.** Climate data is abundant but hard to explore comparatively. Headlines report totals (China first) but rarely per-capita, cumulative, or consumption-based figures — so one dataset supports opposite narratives, and none show historical responsibility.

**Approach.** A single-file explorer with an explicit equity lens, putting totals, per-capita, cumulative, and consumption views one click apart so they challenge each other.

**Design decisions.** One HTML file for instant loads and auditability; Chart.js over heavier viz libraries; template-computed insights instead of an LLM call, so every claim is traceable; honest gaps (missing consumption data is shown as missing, not interpolated).

**Technical challenge.** The full JSON (~13MB) would kill load time — cutting to essential columns × top-50 countries brought the inline payload to ~1.2MB with a reproducible, idempotent build script.

## Run locally

```bash
python3 data/prep.py            # raw CSVs → data.json + meta.json
python3 data/create_embedded.py # top-50 cut
python3 data/inline_data.py     # inline into index.html
python3 -m http.server          # → http://localhost:8000
```

Raw CSVs (`data/raw/`, gitignored) re-download automatically from the URLs in `prep.py`.

## Testing & CI

Every push runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. Embedded JSON validation (row counts, year window)
2. `node --check` on the extracted app script
3. Feature-marker check (all views, themes, and feature hooks present)
4. HTTP smoke test serving `index.html` exactly as Pages does

You can also verify the deployed site in your browser via the [self-test report](https://flynntaggart26.github.io/Climate-energy/?selftest=1).

## Releases

Versioned snapshots live under [**Releases**](https://github.com/Flynntaggart26/Climate-energy/releases) — start with `v2.0.0` (10 features + theme overhaul).

## Roadmap

- Electricity-mix-by-source data
- SSP scenario pathways
- Choropleth map view

## Limitations

- Consumption-based CO₂ is ~18% missing; territorial totals are more complete
- `other_industry_co2` is 70% missing and excluded from the Energy stack
- No electricity-generation mix in this dataset — Energy shows CO₂ by source instead
- "High income" is a World Bank proxy, not UNFCCC Annex I

## Acknowledgments

- Our World in Data & the Global Carbon Project for `owid-co2-data`
- NASA GISTEMP for the global temperature anomaly series
- Chart.js for the charting engine
