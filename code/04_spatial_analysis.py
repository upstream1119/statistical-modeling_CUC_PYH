"""Spatial analysis scaffold.

This script provides placeholders for spatial weight construction, Moran's I,
and spatial econometric models. Install libpysal/esda/spreg only after the team
confirms the Python environment and data format.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError("panel_data.csv is empty. Fill data before spatial analysis.")
    return df


def row_standardize(weights: np.ndarray) -> np.ndarray:
    """Row-standardize a spatial weight matrix."""
    row_sums = weights.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return weights / row_sums


def placeholder_moran_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a minimal province-year coverage summary before spatial packages are added."""
    return (
        df.groupby("year")
        .agg(
            n_provinces=("province", "nunique"),
            carbon_intensity_mean=("carbon_intensity", "mean"),
            digital_finance_mean=("digital_finance", "mean"),
        )
        .reset_index()
    )


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()

    summary = placeholder_moran_summary(df)
    summary.to_csv(TABLES_DIR / "table04_spatial_coverage_summary.csv", index=False, encoding="utf-8-sig")

    print("Exported spatial coverage summary.")
    print("Next step: add province adjacency or distance matrix, then compute Moran's I.")
    print("Recommended packages after approval: libpysal, esda, spreg.")


if __name__ == "__main__":
    main()
