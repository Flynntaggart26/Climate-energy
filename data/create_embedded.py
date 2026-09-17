# Build the embeddable dashboard subset (rewritten from scratch).
# Usage:  python create_embedded.py   (run after prep.py)
# Inputs: data.json, meta.json (strict JSON, NaN-free)
# Outputs: data_embedded.json  (top-N countries by population, essential cols)
#          meta_embedded.json  (meta + embedded_countries list)
#
# Goal: keep the inline <script> payload small enough for fast GitHub Pages
# loads (<2s). Full data.json is ~10-16MB; the embedded cut targets ~1MB.

import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON = BASE_DIR / "data.json"
META_JSON = BASE_DIR / "meta.json"
DATA_EMB = BASE_DIR / "data_embedded.json"
META_EMB = BASE_DIR / "meta_embedded.json"

TOP_N = 50

ESSENTIAL_COLS = [
    "country", "year", "iso_code", "population", "gdp",
    "co2_total", "co2_per_capita", "co2_per_gdp",
    "co2_coal", "co2_oil", "co2_gas", "co2_cement", "co2_flaring",
    "co2_other_industry",
    "co2_consumption_total", "co2_consumption_per_capita",
    "co2_cumulative_total", "co2_cumulative_coal", "co2_cumulative_oil",
    "co2_cumulative_gas",
    "energy_total", "energy_per_capita", "energy_per_gdp",
    "gdp_per_capita", "co2_intensity",
    "co2_consumption_diff", "co2_consumption_diff_per_capita",
    "region", "income_group", "temp_anomaly_global",
]


def main() -> None:
    if not DATA_JSON.exists():
        raise FileNotFoundError(f"Run prep.py first — missing {DATA_JSON}")
    df = pd.read_json(DATA_JSON)  # strict JSON: proves no NaN literals survived
    print(f"Full data: {len(df)} rows, {df['iso_code'].nunique()} countries")

    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year].dropna(subset=["population"])
    top = latest.nlargest(TOP_N, "population")["iso_code"].tolist()
    print(f"Top {TOP_N} by {latest_year} population: {', '.join(top[:10])} ...")

    cols = [c for c in ESSENTIAL_COLS if c in df.columns]
    sub = df[df["iso_code"].isin(top)][cols].copy()
    for c in sub.select_dtypes(include=["float64", "int64"]).columns:
        sub[c] = sub[c].round(3)
    sub = sub.sort_values(["iso_code", "year"]).reset_index(drop=True)
    print(f"Filtered: {len(sub)} rows x {len(sub.columns)} cols")

    records = sub.replace([float("inf"), float("-inf")], None).astype(object)
    records = records.where(pd.notnull(records), None).to_dict(orient="records")
    with open(DATA_EMB, "w", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"), allow_nan=False)
    print(f"Wrote {DATA_EMB} ({DATA_EMB.stat().st_size / 1024:.0f} KB)")

    meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    meta["embedded_countries"] = top
    meta["embedded_top_n"] = TOP_N
    with open(META_EMB, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, allow_nan=False)
    print(f"Wrote {META_EMB}")

    json.loads(DATA_EMB.read_text(encoding="utf-8"))  # strict round-trip check
    print("Strict JSON round-trip OK — Phase 0 (embedded) complete")


if __name__ == "__main__":
    main()
