# Climate & Energy Explorer — Design Specification

**Date:** 2026-09-17  
**Project:** Interactive exploratory dashboard for climate/energy data  
**Target:** GitHub Pages deployment, single HTML file (vanilla JS + Chart.js)  
**Timeline:** Weekend (2-3 days)

---

## 1. Purpose & Success Criteria

**Purpose:** Build a polished, interactive data explorer that lets users investigate CO₂ emissions, energy transitions, and climate equity across countries and time — demonstrating data literacy, domain curiosity, and communication design for top-university applications.

**Success Criteria:**
- Loads in <2s on GitHub Pages (single HTML + embedded data)
- Four working tabs: Emissions, Energy Transition, Correlation Lab, Equity Lens
- Responsive on mobile/desktop
- URL-state sharing works (?countries=USA,CHN&metric=co2_per_capita&year=2000-2022)
- AI Insight Panel generates useful 3-bullet interpretations
- Clean case study (400 words) in README

---

## 2. Data Sources & Preparation

| Dataset | Source | File | Key Fields |
|---------|--------|------|------------|
| CO₂ Emissions (territorial) | Our World in Data / Global Carbon Project | `co2.csv` | country, year, co2, co2_per_capita, co2_per_gdp, coal_co2, oil_co2, gas_co2, cement_co2, flaring_co2 |
| CO₂ Emissions (consumption) | Our World in Data | `co2_consumption.csv` | country, year, consumption_co2, consumption_co2_per_capita |
| Energy Electricity Mix | Ember / OWID | `energy_mix.csv` | country, year, coal, oil, gas, solar, wind, hydro, nuclear, other_renewables |
| GDP & Population | World Bank (via OWID) | `gdp_pop.csv` | country, year, gdp, population, gdp_per_capita |
| Temperature Anomalies | NASA GISTEMP | `temp_anomaly.csv` | year, global_anomaly, nh_anomaly, sh_anomaly |

**Prep Pipeline (Python/Colab):**
1. Download CSVs from OWID GitHub (stable URLs)
2. Merge on (country, year) → single long-form dataframe
3. Filter: years 1990–2023, countries with >1M population
4. Compute derived: energy_per_capita, co2_intensity, renewables_share
5. Output: `data.json` (array of objects, one per country-year) + `meta.json` (country list, year range, variable definitions)

**Embedded Data Strategy:** Inline `data.json` as `const DATA = [...]` in HTML (gzipped ~200KB → acceptable for Pages).

---

## 3. Architecture

### 3.1 File Structure
```
Climate&energy/
├── index.html          # Single-file app (HTML + CSS + JS + embedded data)
├── data/
│   ├── raw/            # Downloaded CSVs (gitignored)
│   ├── prep.ipynb      # Colab notebook for data prep
│   └── data.json       # Generated (committed)
├── docs/
│   └── superpowers/specs/2026-09-17-climate-dashboard-design.md
└── README.md
```

### 3.2 Technical Stack
- **HTML/CSS/JS** — vanilla, no build step (like SAT app)
- **Chart.js v4** — via CDN (single request, cached)
- **No framework** — keeps it portable, auditable, lightweight
- **localStorage** — saves user preferences (theme, last viewed countries)
- **URL State** — `URLSearchParams` for shareable links

### 3.3 State Management
```js
const state = {
  view: 'emissions',           // 'emissions' | 'energy' | 'correlation' | 'equity'
  countries: ['USA', 'CHN', 'IND', 'DEU', 'BRA'],  // ISO3 codes
  metric: 'co2_per_capita',    // varies by view
  yearRange: [1990, 2023],
  chartType: 'line',           // 'line' | 'bar' | 'area'
  scale: 'linear',             // 'linear' | 'log'
  theme: 'dark',               // 'dark' | 'light'
};
```

---

## 4. UI / UX Specification

### 4.1 Layout (Responsive)
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Title + Theme Toggle + Share Button                 │
├─────────────────────────────────────────────────────────────┤
│ Tab Bar: [Emissions] [Energy] [Correlation] [Equity]        │
├─────────────────────────────────────────────────────────────┤
│ Controls Bar (sticky):                                      │
│  [Country Multi-select]  [Metric Select]  [Year Slider]     │
│  [Chart Type] [Scale] [Download PNG] [Download CSV]         │
├─────────────────────────────────────────────────────────────┤
│ Chart Area (Chart.js canvas, full width, 500px min-height)  │
├─────────────────────────────────────────────────────────────┤
│ AI Insight Panel (collapsible):                             │
│  "Explain this pattern" → 3 bullets + sources               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Tab Details

#### **Tab 1: Emissions Explorer**
- **Metrics:** Total CO₂, Per Capita, Per GDP, Consumption-based, By Sector (coal/oil/gas/cement)
- **Chart:** Line (default) / Bar / Area
- **Special:** "Show consumption vs territorial" toggle

#### **Tab 2: Energy Transition**
- **Chart:** Stacked area (absolute TWh) OR 100% stacked (% share)
- **Metrics:** Coal, Oil, Gas, Solar, Wind, Hydro, Nuclear, Other Renewables
- **Special:** "Show renewables only" filter

#### **Tab 3: Correlation Lab**
- **X/Y Axis Selectors:** Any two numeric variables
- **Chart:** Scatter with trend line (OLS), sized by population (optional)
- **Special:** Year animation slider (shows trajectory over time)

#### **Tab 4: Equity Lens**
- **Pre-set Views (radio buttons):**
  1. Historical Cumulative (1850–2023) vs Current Annual
  2. Per Capita vs Total (bubble: population)
  3. Developed (Annex I) vs Developing
  4. Consumption vs Territorial (carbon leakage)
- **Chart:** Bar / Scatter / Butterfly chart

### 4.3 Interactions
- **Country Selector:** Typeahead (debounced), region groups (OECD, G20, LDC, etc.), "Select All Region" button
- **Year Slider:** Dual-handle range (noUiSlider or native `<input type="range">` pair)
- **Keyboard:** ←/→ year step, Enter to add country, Escape to clear
- **Hover Tooltip:** Formatted values, year, country flag emoji

### 4.4 AI Insight Panel
- **Trigger:** Button "🤖 Explain Pattern" (disabled if no chart data)
- **Prompt Engineering:** Pre-written system prompt + context (current view, metrics, countries, visible data points)
- **Output:** 3 bullets: (1) What the chart shows, (2) Key driver/context, (3) Caveat/nuance
- **Caching:** localStorage cache by hash of (view + countries + metric + yearRange)

---

## 5. Data Flow

```
User Action → updateState() → filterData() → transformForChart() → chart.update()
                    ↓
              updateURL() → pushState()
                    ↓
              savePreferences() → localStorage
```

**Filter Logic:** `DATA.filter(d => state.countries.includes(d.iso3) && d.year >= state.yearRange[0] && d.year <= state.yearRange[1])`

**Transform:** Pivot to Chart.js datasets: `{ label: 'USA', data: [{x: 1990, y: 15.2}, ...], borderColor: '#6C5CFF' }`

---

## 6. Color System & Accessibility

| Semantic | Dark | Light | Usage |
|----------|------|-------|-------|
| Background | #0f0f14 | #f8f9fb | Page bg |
| Card | #1a1a22 | #ffffff | Panels |
| Border | #2e2e3e | #e1e4eb | Dividers |
| Primary | #6C5CFF | #5a4ad9 | Accent, primary lines |
| Success | #00D9A5 | #00b88a | Renewables, positive |
| Warning | #FFB800 | #e6a200 | Fossil fuels |
| Danger | #FF6B6B | #e05555 | High emissions |
| Text | #f5f5ff | #1a1a2e | Primary text |
| Muted | #9aa0b5 | #6b7280 | Labels |

- **Colorblind-safe palette** (viridis/category10 derived)
- **Focus states** visible, keyboard navigable
- **Reduced motion** respects `prefers-reduced-motion`

---

## 7. Error Handling & Edge Cases

| Scenario | Handling |
|----------|----------|
| No data for country/year | Show "No data" in tooltip; gap in line chart |
| Single country selected | Disable correlation tab (needs ≥2) |
| Data load fails | Inline fallback: show static message + retry button |
| Mobile viewport <400px | Stack controls vertically; chart full-width |
| Share URL with invalid params | Fall back to defaults; log to console |

---

## 8. Testing Checklist

- [ ] All 4 tabs render without console errors
- [ ] Country selector: typeahead, multi-select, region groups work
- [ ] Year slider updates chart in real-time
- [ ] Chart type/scale toggles persist in URL
- [ ] Share button copies valid URL
- [ ] PNG/CSV download produces correct files
- [ ] AI Insight generates 3 bullets (mock mode for demo)
- [ ] Theme toggle persists + respects system preference
- [ ] Mobile: touch scroll, pinch zoom on chart
- [ ] Lighthouse: Performance >90, Accessibility >95, Best Practices >90

---

## 9. Deployment

- **GitHub Pages:** `main` branch → `/` (root)
- **Custom domain:** Optional (can use `username.github.io/Climate-energy/`)
- **No CI needed** — single HTML file

---

## 10. Case Study Outline (README)

1. **Problem:** Climate data is abundant but hard to explore comparatively
2. **Approach:** Single-file exploratory tool with equity framing
3. **Data:** 5 authoritative sources, merged & derived metrics
4. **Design Decisions:** Why single-file, why Chart.js, why equity lens
5. **Technical Challenge:** Embedding 200KB data + Chart.js <2s load
6. **What I'd Extend:** Scenario modeling, policy simulation, i18n

---

## 11. Out of Scope (v1)

- User accounts / saved dashboards
- Map visualization (choropleth)
- Scenario modeling (SSP pathways)
- Multi-language
- Backend / API

---

**Approval:** Review this spec. If approved, I'll invoke `writing-plans` to create the implementation plan with day-by-day tasks and AI prompts for each step.