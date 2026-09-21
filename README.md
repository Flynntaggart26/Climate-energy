# Climate-Energy · Single-File Web Apps

> Two dependency-free, single-file web apps — an **Advanced Calorie Tracker** and a **Climate & Energy Explorer**.
> Open either `.html` file in a browser. No framework, no build step, no backend.

| App | File | What it does |
|-----|------|--------------|
| 🔥 **Advanced Calorie Tracker** | [`calorie-tracker.html`](calorie-tracker.html) | 120+ food database, macros, vitamins & minerals, BMR/TDEE targets, hydration, weekly analytics |
| 🌍 **Climate & Energy Explorer** | [`index.html`](index.html) | CO₂ emissions, energy transitions & climate equity across 50 countries (1990–2023) |

**[Live demo — Climate & Energy Explorer](https://flynntaggart26.github.io/Climate-energy/)**

---

## 🔥 Advanced Calorie Tracker

An advanced, offline-friendly calorie and nutrient tracker in a single HTML file. Log meals by weight, hit
protein/carb/fat targets derived from your body metrics, and cover vitamins, minerals and hydration — with
charts, history and CSV export.

### Features

| Area | Details |
|------|---------|
| 🍎 **Food database (120+ items)** | 13 categories — fruits, vegetables, grains, legumes, nuts & seeds, dairy & eggs, meat, fish & seafood, fats & oils, snacks & sweets, fast food, beverages, homemade. Every item carries **12 nutrients per 100 g**: calories, protein, carbs, fat, fiber, sugar, sodium, potassium, calcium, iron, vitamin C, vitamin A |
| 🔍 **Smart logging** | Live search, category filter, sort by name / calories / protein, portion presets (50/100/150/250 g) or exact grams, 4 meals (Breakfast, Lunch, Dinner, Snacks), per-item macro breakdown, one-click delete |
| 🎯 **Personal targets** | BMR via **Mifflin-St Jeor**, TDEE via activity multiplier, goal adjustment (cut → bulk). Auto macro split: protein ~1.7–2.0 g/kg, fat 25 % of kcal, remainder carbs. Water target 35 ml/kg |
| 🧬 **Vital nutrients vs Daily Value** | Fiber 30 g · sugar < 50 g · sodium < 2300 mg · potassium 3500 mg · calcium 1000 mg · iron 18 mg · vitamin C 90 mg · vitamin A 900 mcg — live % bars plus a totals table with ✅ Hit / 🟡 Half / ⚠️ Over status |
| 📊 **Analytics** | Macro donut (energy split), calories-by-meal bar, 7-day calorie history vs target, weight log, hydration progress |
| ➕ **Custom foods** | Add your own dishes (per 100 g) — saved in the browser and loggable like built-ins |
| 💾 **Persistence & export** | Everything in `localStorage` (daily log, water, profile, weights, history). One-click **CSV export** of the day's log |

### How targets are calculated

- **BMR (Mifflin-St Jeor):** men `10·w + 6.25·h − 5·a + 5`, women `10·w + 6.25·h − 5·a − 161`
  (w = kg, h = cm, a = years)
- **TDEE:** BMR × activity (1.2 sedentary → 1.9 athlete)
- **Target kcal:** TDEE + goal (−500 cut … +500 bulk)
- **Protein:** 2.0 g/kg on a cut, 1.8 g/kg maintain, 1.7 g/kg gain · **Fat:** 25 % of kcal ÷ 9 ·
  **Carbs:** remaining kcal ÷ 4

### Data & methodology

Nutrient values are USDA-based approximations per 100 g edible portion, embedded directly in the file —
the app works fully offline (except the Chart.js CDN). Packaged and restaurant items vary by brand and
preparation; mixed/fast-food micronutrients are estimates. For medical-precision needs, check the label.

### Run it

Just open [`calorie-tracker.html`](calorie-tracker.html) in any modern browser — or serve the folder:

```bash
python -m http.server  # → http://localhost:8000/calorie-tracker.html
```

### Limitations

- Estimates, not medical advice — consult a professional for clinical goals
- Vitamin D, B12, magnesium and zinc are not yet tracked per food
- History/weights live in browser `localStorage` (per device, per browser)

---

## 🌍 Climate & Energy Explorer

> An interactive, single-file dashboard for exploring CO₂ emissions, energy transitions, and climate equity
> across 50 countries (1990–2023).

**[Live demo](https://flynntaggart26.github.io/Climate-energy/)** · [Data & methodology](#data--methodology-climate) · [Case study](#case-study) · [Run locally](#run-locally)

### Features

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

### Tech

Vanilla HTML/CSS/JS + Chart.js 4 via CDN. No framework, no build step, no backend — one auditable
`index.html` (~1.3MB with data inlined) that loads in under 2 seconds on GitHub Pages.

### Data & methodology (climate)

Sources: **Our World in Data / Global Carbon Project** (`owid-co2-data`) and **NASA GISTEMP** global
temperature anomalies.

Pipeline (`data/`):

```
raw CSVs → prep.py → data.json + meta.json (159 countries, strict JSON)
         → create_embedded.py → data_embedded.json (top 50 by population)
         → inline_data.py → window.DATA inside index.html
```

Cleaning decisions: aggregates and bunker fuels dropped (no ISO code), 1990–2023 window, >1M population
filter, full region/income mapping with no silent fallbacks, `NaN → null` with strict round-trip checks,
CO₂ intensity fixed to kg/$.

### Case study

**Problem.** Climate data is abundant but hard to explore comparatively. Headlines report totals (China first)
but rarely per-capita, cumulative, or consumption-based figures — so one dataset supports opposite narratives,
and none show historical responsibility.

**Approach.** A single-file explorer with an explicit equity lens, putting totals, per-capita, cumulative, and
consumption views one click apart so they challenge each other.

**Design decisions.** One HTML file for instant loads and auditability; Chart.js over heavier viz libraries;
template-computed insights instead of an LLM call, so every claim is traceable; honest gaps (missing
consumption data is shown as missing, not interpolated).

**Technical challenge.** The full JSON (~13MB) would kill load time — cutting to essential columns × top-50
countries brought the inline payload to ~1.2MB with a reproducible, idempotent build script.

**Next:** electricity-mix-by-source data, SSP scenario pathways, choropleth map.

### Run locally

```bash
python data/prep.py            # raw CSVs → data.json + meta.json
python data/create_embedded.py # top-50 cut
python data/inline_data.py     # inline into index.html
python -m http.server          # → http://localhost:8000
```

Raw CSVs (`data/raw/`, gitignored) re-download automatically from the URLs in `prep.py`.

### Limitations (climate)

- Consumption-based CO₂ is ~18% missing; territorial totals are more complete
- `other_industry_co2` is 70% missing and excluded from the Energy stack
- No electricity-generation mix in this dataset — Energy shows CO₂ by source instead
- "High income" is a World Bank proxy, not UNFCCC Annex I
