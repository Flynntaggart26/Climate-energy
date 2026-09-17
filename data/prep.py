# Climate & Energy Dashboard — Data Preparation (v2, rewritten from scratch)
# Usage:  python prep.py        (run from the data/ directory, or anywhere)
# Inputs: raw/co2_full.csv  (OWID / Global Carbon Project)
#         raw/temp.csv      (NASA GISTEMP via OWID grapher)
# Outputs: data.json  (one record per country-year, strict JSON, NaN -> null)
#          meta.json  (year range, country list, metric config for the UI)
#
# Design decisions:
# - Drop every row without an ISO code (aggregates like World/EU/OECD, bunker
#   fuels, Kosovo). They break Chart.js joins and produced invalid `NaN` JSON.
# - Strict JSON output (allow_nan=False) so a failure is loud, not silent.
# - Paths are anchored to this file's directory, so cwd does not matter.

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
CO2_CSV = RAW_DIR / "co2_full.csv"
TEMP_CSV = RAW_DIR / "temp.csv"
DATA_JSON = BASE_DIR / "data.json"
META_JSON = BASE_DIR / "meta.json"

YEAR_MIN, YEAR_MAX = 1990, 2023
MIN_POPULATION = 1_000_000

# ----------------------------------------------------------------------------
# Region / income lookup. Curated for the countries that survive the
# population filter; anything unmapped falls back to "Other"/"Unclassified"
# (honest) instead of a misleading "Low".
# Regions follow a compact UN-geoscheme style grouping.
# Income groups follow the World Bank FY2024 classification.
# ----------------------------------------------------------------------------
REGION_MAP = {
    # North America
    "USA": "North America", "CAN": "North America", "MEX": "North America",
    # Latin America & Caribbean
    "BRA": "Latin America", "ARG": "Latin America", "CHL": "Latin America",
    "COL": "Latin America", "PER": "Latin America", "VEN": "Latin America",
    "ECU": "Latin America", "BOL": "Latin America", "PRY": "Latin America",
    "URY": "Latin America", "PAN": "Latin America", "CRI": "Latin America",
    "NIC": "Latin America", "HND": "Latin America", "SLV": "Latin America",
    "GTM": "Latin America", "CUB": "Latin America", "DOM": "Latin America",
    "HTI": "Latin America", "JAM": "Latin America", "TTO": "Latin America",
    # Europe
    "DEU": "Europe", "FRA": "Europe", "GBR": "Europe", "ITA": "Europe",
    "ESP": "Europe", "POL": "Europe", "NLD": "Europe", "BEL": "Europe",
    "SWE": "Europe", "NOR": "Europe", "CHE": "Europe", "AUT": "Europe",
    "DNK": "Europe", "FIN": "Europe", "IRL": "Europe", "PRT": "Europe",
    "GRC": "Europe", "CZE": "Europe", "SVK": "Europe", "SVN": "Europe",
    "HUN": "Europe", "ROU": "Europe", "BGR": "Europe", "HRV": "Europe",
    "SRB": "Europe", "BIH": "Europe", "ALB": "Europe", "MKD": "Europe",
    "UKR": "Europe", "BLR": "Europe", "MDA": "Europe", "RUS": "Europe",
    "TUR": "Europe", "GEO": "Europe", "ARM": "Europe", "AZE": "Europe",
    "EST": "Europe", "LVA": "Europe", "LTU": "Europe", "CYP": "Europe",
    # Middle East
    "SAU": "Middle East", "IRN": "Middle East", "IRQ": "Middle East",
    "ISR": "Middle East", "ARE": "Middle East", "QAT": "Middle East",
    "KWT": "Middle East", "OMN": "Middle East", "BHR": "Middle East",
    "JOR": "Middle East", "LBN": "Middle East", "SYR": "Middle East",
    "YEM": "Middle East", "PSE": "Middle East",
    # Africa
    "ZAF": "Africa", "NGA": "Africa", "EGY": "Africa", "DZA": "Africa",
    "MAR": "Africa", "TUN": "Africa", "LBY": "Africa", "SDN": "Africa",
    "ETH": "Africa", "KEN": "Africa", "TZA": "Africa", "UGA": "Africa",
    "GHA": "Africa", "CIV": "Africa", "SEN": "Africa", "CMR": "Africa",
    "AGO": "Africa", "COD": "Africa", "COG": "Africa", "GAB": "Africa",
    "TCD": "Africa", "NER": "Africa", "MLI": "Africa", "BFA": "Africa",
    "MOZ": "Africa", "ZMB": "Africa", "ZWE": "Africa", "MWI": "Africa",
    "MDG": "Africa", "RWA": "Africa", "BDI": "Africa", "SOM": "Africa",
    "MRT": "Africa", "NAM": "Africa", "BWA": "Africa", "MUS": "Africa",
    "BEN": "Africa", "TGO": "Africa", "SLE": "Africa", "LBR": "Africa",
    "GIN": "Africa", "GNB": "Africa", "CAF": "Africa", "SSD": "Africa",
    "ERI": "Africa", "DJI": "Africa", "GMB": "Africa", "LSO": "Africa",
    "SWZ": "Africa", "GNQ": "Africa",
    # Central Asia
    "KAZ": "Central Asia", "UZB": "Central Asia", "TKM": "Central Asia",
    "KGZ": "Central Asia", "TJK": "Central Asia",
    # South Asia
    "IND": "South Asia", "PAK": "South Asia", "BGD": "South Asia",
    "LKA": "South Asia", "NPL": "South Asia", "AFG": "South Asia",
    # East Asia
    "CHN": "East Asia", "JPN": "East Asia", "KOR": "East Asia",
    "PRK": "East Asia", "TWN": "East Asia", "HKG": "East Asia",
    "MNG": "East Asia",
    # Southeast Asia
    "IDN": "Southeast Asia", "THA": "Southeast Asia", "VNM": "Southeast Asia",
    "MYS": "Southeast Asia", "PHL": "Southeast Asia", "SGP": "Southeast Asia",
    "MMR": "Southeast Asia", "KHM": "Southeast Asia", "LAO": "Southeast Asia",
    "TLS": "Southeast Asia",
    # Oceania
    "AUS": "Oceania", "NZL": "Oceania", "PNG": "Oceania",
}

INCOME_MAP = {
    # High income (World Bank FY2024)
    "USA": "High", "CAN": "High", "DEU": "High", "FRA": "High",
    "GBR": "High", "ITA": "High", "ESP": "High", "NLD": "High",
    "BEL": "High", "SWE": "High", "NOR": "High", "CHE": "High",
    "AUT": "High", "DNK": "High", "FIN": "High", "IRL": "High",
    "PRT": "High", "GRC": "High", "CZE": "High", "SVK": "High",
    "SVN": "High", "EST": "High", "LVA": "High", "LTU": "High",
    "HRV": "High", "HUN": "High", "POL": "High", "ROU": "High",
    "CYP": "High", "JPN": "High", "KOR": "High", "TWN": "High",
    "HKG": "High", "SGP": "High", "AUS": "High", "NZL": "High",
    "ISR": "High", "ARE": "High", "QAT": "High", "KWT": "High",
    "SAU": "High", "BHR": "High", "OMN": "High", "CHL": "High",
    "URY": "High", "PAN": "High", "TTO": "High",
    # Upper middle income
    "CHN": "Upper Middle", "RUS": "Upper Middle", "BRA": "Upper Middle",
    "MEX": "Upper Middle", "TUR": "Upper Middle", "THA": "Upper Middle",
    "MYS": "Upper Middle", "ARG": "Upper Middle", "ZAF": "Upper Middle",
    "KAZ": "Upper Middle", "BGR": "Upper Middle", "SRB": "Upper Middle",
    "MKD": "Upper Middle", "BIH": "Upper Middle", "ALB": "Upper Middle",
    "GEO": "Upper Middle", "ARM": "Upper Middle", "AZE": "Upper Middle",
    "CUB": "Upper Middle", "DOM": "Upper Middle", "JAM": "Upper Middle",
    "PER": "Upper Middle", "COL": "Upper Middle", "ECU": "Upper Middle",
    "PRY": "Upper Middle", "VEN": "Upper Middle", "GAB": "Upper Middle",
    "GNQ": "Upper Middle", "BWA": "Upper Middle", "NAM": "Upper Middle",
    "MUS": "Upper Middle", "JOR": "Upper Middle", "LBN": "Upper Middle",
    "IRQ": "Upper Middle", "IRN": "Upper Middle", "TKM": "Upper Middle",
    "IDN": "Upper Middle",
    "BLR": "Upper Middle", "CRI": "Upper Middle", "LBY": "Upper Middle",
    "DJI": "Lower Middle", "SWZ": "Lower Middle", "MNG": "Lower Middle",
    "TJK": "Lower Middle",
    # Lower middle income
    "IND": "Lower Middle", "VNM": "Lower Middle", "PHL": "Lower Middle",
    "EGY": "Lower Middle", "NGA": "Lower Middle", "PAK": "Lower Middle",
    "BGD": "Lower Middle", "KEN": "Lower Middle", "GHA": "Lower Middle",
    "MAR": "Lower Middle", "TUN": "Lower Middle", "DZA": "Lower Middle",
    "BOL": "Lower Middle", "HND": "Lower Middle", "NIC": "Lower Middle",
    "SLV": "Lower Middle", "GTM": "Lower Middle", "UKR": "Lower Middle",
    "MDA": "Lower Middle", "UZB": "Lower Middle", "KGZ": "Lower Middle",
    "LKA": "Lower Middle", "NPL": "Lower Middle", "KHM": "Lower Middle",
    "LAO": "Lower Middle", "MMR": "Lower Middle", "MRT": "Lower Middle",
    "SEN": "Lower Middle", "CIV": "Lower Middle", "CMR": "Lower Middle",
    "COG": "Lower Middle", "AGO": "Lower Middle", "ZMB": "Lower Middle",
    "ZWE": "Lower Middle", "PNG": "Lower Middle", "PSE": "Lower Middle",
    # Low income
    "AFG": "Low", "ETH": "Low", "COD": "Low", "TZA": "Low",
    "UGA": "Low", "MOZ": "Low", "MWI": "Low", "MDG": "Low",
    "RWA": "Low", "BDI": "Low", "SOM": "Low", "TCD": "Low",
    "NER": "Low", "MLI": "Low", "BFA": "Low", "BEN": "Low",
    "TGO": "Low", "SLE": "Low", "LBR": "Low", "GIN": "Low",
    "GNB": "Low", "CAF": "Low", "SSD": "Low", "ERI": "Low",
    "SDN": "Low", "YEM": "Low", "SYR": "Low", "PRK": "Low",
    "HTI": "Low", "GMB": "Low", "LSO": "Low", "TLS": "Low",
}

# OWID source columns -> dashboard column names.
# co2 is in million tonnes (Mt); gdp is in international-$.
RENAME_MAP = {
    "co2": "co2_total",
    "coal_co2": "co2_coal",
    "oil_co2": "co2_oil",
    "gas_co2": "co2_gas",
    "cement_co2": "co2_cement",
    "flaring_co2": "co2_flaring",
    "other_industry_co2": "co2_other_industry",
    "consumption_co2": "co2_consumption_total",
    "consumption_co2_per_capita": "co2_consumption_per_capita",
    "consumption_co2_per_gdp": "co2_consumption_per_gdp",
    "cumulative_co2": "co2_cumulative_total",
    "cumulative_coal_co2": "co2_cumulative_coal",
    "cumulative_oil_co2": "co2_cumulative_oil",
    "cumulative_gas_co2": "co2_cumulative_gas",
    "primary_energy_consumption": "energy_total",
}


def load_co2() -> pd.DataFrame:
    print(f"Loading {CO2_CSV} ...")
    df = pd.read_csv(CO2_CSV, low_memory=False)
    print(f"  raw: {df.shape[0]} rows, {df.shape[1]} cols, "
          f"years {int(df['year'].min())}-{int(df['year'].max())}")
    return df


def load_temp_global() -> pd.DataFrame:
    print(f"Loading {TEMP_CSV} ...")
    t = pd.read_csv(TEMP_CSV)
    world = t[t["Entity"] == "World"][["Year", "Average"]].copy()
    world = world.rename(columns={"Year": "year", "Average": "temp_anomaly_global"})
    print(f"  global temp rows: {len(world)} "
          f"({int(world['year'].min())}-{int(world['year'].max())})")
    return world


def clean_co2(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Drop aggregates / bunker fuels / entities without ISO codes.
    n0 = len(df)
    df = df[df["iso_code"].notna()].copy()
    print(f"Dropped {n0 - len(df)} rows without ISO code (aggregates, bunkers)")

    # 2. Year window.
    df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)].copy()

    # 3. Population filter on the latest available year in-window.
    latest_year = int(df["year"].max())
    pop = df[df["year"] == latest_year][["iso_code", "population"]].dropna()
    valid = set(pop[pop["population"] > MIN_POPULATION]["iso_code"])
    n1 = len(df)
    df = df[df["iso_code"].isin(valid)].copy()
    print(f"Year window {YEAR_MIN}-{latest_year}, pop>{MIN_POPULATION/1e6:.0f}M: "
          f"{n1} -> {len(df)} rows, {df['iso_code'].nunique()} countries")
    return df


def derive(df: pd.DataFrame, temp_global: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns})

    # GDP per capita ($/person).
    df["gdp_per_capita"] = df["gdp"] / df["population"]

    # CO2 intensity: co2_total is Mt (1e9 kg) / GDP ($) -> kg per $.
    # (Previous version used 1e6, underestimating by 1000x.)
    df["co2_intensity"] = df["co2_total"] * 1e9 / df["gdp"]

    # Consumption vs territorial gap (positive = net importer of emissions).
    df["co2_consumption_diff"] = df["co2_consumption_total"] - df["co2_total"]
    df["co2_consumption_diff_per_capita"] = (
        df["co2_consumption_per_capita"] - df["co2_per_capita"]
    )

    df["region"] = df["iso_code"].map(REGION_MAP).fillna("Other")
    df["income_group"] = df["iso_code"].map(INCOME_MAP).fillna("Unclassified")

    df = df.merge(temp_global, on="year", how="left")

    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].round(4)
    return df.sort_values(["iso_code", "year"]).reset_index(drop=True)


def to_strict_records(df: pd.DataFrame) -> list:
    """DataFrame -> JSON-safe records: NaN/+-Inf become None."""
    df = df.replace([np.inf, -np.inf], np.nan).astype(object)
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


def build_meta(df: pd.DataFrame) -> dict:
    countries = (
        df[["iso_code", "country", "region", "income_group"]]
        .drop_duplicates()
        .sort_values("country")
        .to_dict(orient="records")
    )
    have = set(df.columns)
    emission_keys = ["co2_total", "co2_per_capita", "co2_per_gdp",
                     "co2_consumption_total", "co2_consumption_per_capita",
                     "co2_coal", "co2_oil", "co2_gas", "co2_cumulative_total"]
    energy_keys = ["energy_total", "energy_per_capita", "energy_per_gdp"]
    corr_keys = ["gdp_per_capita", "co2_per_capita", "energy_per_capita",
                 "population", "co2_intensity"]

    def opt(keys):
        return [{"key": k, "label": k.replace("_", " ").title(), "unit": ""}
                for k in keys if k in have]

    defaults = ["USA", "CHN", "IND", "DEU", "BRA",
                "GBR", "JPN", "CAN", "AUS", "SAU"]
    isos = {c["iso_code"] for c in countries}
    return {
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
        "n_rows": int(len(df)),
        "n_countries": len(countries),
        "sources": [
            "OWID / Global Carbon Project (owid-co2-data)",
            "NASA GISTEMP global temperature anomaly via OWID grapher",
        ],
        "notes": [
            "Aggregates and bunker fuels (no ISO code) excluded.",
            f"Years {YEAR_MIN}-{YEAR_MAX}; countries with population > 1M.",
            "co2_total in million tonnes (Mt); co2_intensity in kg CO2 per $ GDP.",
            "No electricity-mix-by-source in this dataset; energy tab uses primary energy + fossil CO2 split.",
        ],
        "countries": countries,
        "metrics": {
            "emissions": opt(emission_keys),
            "energy": opt(energy_keys),
            "correlation_x": opt(corr_keys),
            "correlation_y": opt(corr_keys),
        },
        "equity_views": [
            {"id": "cumulative_vs_annual",
             "label": "Historical Cumulative vs Current Annual"},
            {"id": "percapita_vs_total",
             "label": "Per Capita vs Total (bubble = population)"},
            {"id": "developed_vs_developing",
             "label": "High Income vs Rest"},
            {"id": "consumption_vs_territorial",
             "label": "Consumption vs Territorial (Carbon Leakage)"},
        ],
        "default_countries": [c for c in defaults if c in isos],
    }


def main() -> None:
    if not CO2_CSV.exists():
        raise FileNotFoundError(f"Missing input: {CO2_CSV}")
    if not TEMP_CSV.exists():
        raise FileNotFoundError(f"Missing input: {TEMP_CSV}")

    df = derive(clean_co2(load_co2()), load_temp_global())
    print(f"Final: {len(df)} rows, {df['iso_code'].nunique()} countries, "
          f"{len(df.columns)} cols")

    records = to_strict_records(df)
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"), allow_nan=False)
    print(f"Wrote {DATA_JSON} ({DATA_JSON.stat().st_size / 1024:.0f} KB)")

    meta = build_meta(df)
    with open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, allow_nan=False)
    print(f"Wrote {META_JSON}")

    # Loud self-check: strict JSON round-trip (no NaN literals allowed).
    json.loads(DATA_JSON.read_text(encoding="utf-8"))
    json.loads(META_JSON.read_text(encoding="utf-8"))
    print("Strict JSON round-trip OK")
    print("Phase 0 (full data) complete. Next: create_embedded.py")


if __name__ == "__main__":
    main()
