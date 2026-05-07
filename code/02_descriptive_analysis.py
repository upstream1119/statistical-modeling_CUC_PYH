"""Descriptive statistics and exploratory outputs."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

NUMERIC_COLUMNS = [
    "low_carbon",
    "digital_finance",
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError("panel_data.csv is empty. Fill data before descriptive analysis.")
    return df


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_panel_data()
    available_numeric = [col for col in NUMERIC_COLUMNS if col in df.columns]

    desc = df[available_numeric].describe().T
    desc.to_csv(TABLES_DIR / "table01_descriptive_statistics.csv", encoding="utf-8-sig")

    corr = df[available_numeric].corr()
    corr.to_csv(TABLES_DIR / "table02_correlation_matrix.csv", encoding="utf-8-sig")

    print("Exported descriptive statistics and correlation matrix.")


if __name__ == "__main__":
    main()
