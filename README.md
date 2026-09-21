# Climate & Energy Explorer

> An interactive, single-file dashboard for exploring CO₂ emissions, energy transitions, and climate equity across 50 countries (1990–2023).

**[Live demo](https://flynntaggart26.github.io/Climate-energy/)** · [Data & methodology](#data--methodology) · [Case study](#case-study) · [Run locally](#run-locally)

## Features

| Tab | What you can investigate |
|-----|--------------------------|
| **Emissions** | Total, per-capita, per-GDP, and consumption-based CO₂ — with a territorial-vs-consumption overlay that reveals carbon leakage |
| **Energy** | Fossil & industry CO₂ mix per country as stacked area, absolute (Mt) or 100% share |
| **Correlation Lab** | Any two indicators (GDP, CO₂, energy, population, intensity) as a population-weighted scatter with OLS trend and Pearson r — step through years |
| **Equity Lens** | Four presets: cumulative vs annual, per-capita vs total bubbles, High-income vs Rest, consumption vs territorial with a y=x reference |

- 🔗 **Shareable URLs** — every view, country set, metric, and year range encodes into a link
- 📥 **PNG & CSV export** of any view
- 🌗 **Dark/light themes**, fully responsive down to phones, keyboard navigable
- 💡 **Insight panel** — every chart gets a computed 3-bullet interpretation with caveats (no black box; all bullets trace to visible data)

## Tech

Vanilla HTML/CSS/JS + Chart.js 4 via CDN. No framework, no build step, no backend — one auditable `index.html` (~1.3MB with data inlined) that loads in under 2 seconds on GitHub Pages.

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

**Next:** electricity-mix-by-source data, SSP scenario pathways, choropleth map.

## Run locally

```bash
python3 data/prep.py            # raw CSVs → data.json + meta.json
python3 data/create_embedded.py # top-50 cut
python3 data/inline_data.py     # inline into index.html
python3 -m http.server          # → http://localhost:8000
```

Raw CSVs (`data/raw/`, gitignored) re-download automatically from the URLs in `prep.py`.

## Limitations

- Consumption-based CO₂ is ~18% missing; territorial totals are more complete
- `other_industry_co2` is 70% missing and excluded from the Energy stack
- No electricity-generation mix in this dataset — Energy shows CO₂ by source instead
- "High income" is a World Bank proxy, not UNFCCC Annex I
