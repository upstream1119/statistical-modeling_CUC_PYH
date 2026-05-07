"""Data cleaning script for the statistical modeling project.

This script prepares the province-year panel dataset used by later analysis.
Raw data formats are not fixed yet, so the current version provides a safe
scaffold and validates the expected final columns once panel_data.csv exists.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data_raw"
PROCESSED_DIR = ROOT / "data_processed"
PANEL_PATH = PROCESSED_DIR / "panel_data.csv"

REQUIRED_COLUMNS = [
    "province",
    "year",
    "carbon_intensity",
    "digital_finance",
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]


def validate_panel_data(df: pd.DataFrame) -> None:
    """Validate required columns and basic province-year uniqueness."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    duplicated = df.duplicated(subset=["province", "year"]).sum()
    if duplicated:
        raise ValueError(f"Found duplicated province-year rows: {duplicated}")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not PANEL_PATH.exists():
        template = pd.DataFrame(columns=REQUIRED_COLUMNS)
        template.to_csv(PANEL_PATH, index=False, encoding="utf-8-sig")
        print(f"Created empty template: {PANEL_PATH}")
        print("Fill this file after raw data are collected, then rerun validation.")
        return

    df = pd.read_csv(PANEL_PATH)
    validate_panel_data(df)
    df = df.sort_values(["province", "year"])
    df.to_csv(PANEL_PATH, index=False, encoding="utf-8-sig")
    print(f"Validated panel data: {PANEL_PATH}")
    print(f"Rows: {len(df)}, provinces: {df['province'].nunique()}, years: {df['year'].nunique()}")


if __name__ == "__main__":
    main()
