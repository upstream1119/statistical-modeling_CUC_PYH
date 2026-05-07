"""Spatial autocorrelation analysis for carbon intensity.

This script uses the province-level adjacency matrix to calculate yearly
Moran's I for carbon intensity. It is intentionally dependency-light so the
first spatial autocorrelation table can be reproduced without PySAL.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
WEIGHTS_PATH = ROOT / "data_raw" / "spatial_weights.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table04_moran_i_by_year.csv"
SEED = 20260507
N_PERMUTATIONS = 999


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError("panel_data.csv is empty. Fill data before spatial analysis.")
    return df


def load_spatial_weights() -> pd.DataFrame:
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Missing spatial weights: {WEIGHTS_PATH}")
    weights = pd.read_csv(WEIGHTS_PATH)
    required = ["province_i", "province_j", "weight"]
    missing = [col for col in required if col not in weights.columns]
    if missing:
        raise ValueError(f"Missing spatial weight columns: {missing}")
    if weights.empty:
        raise ValueError("spatial_weights.csv is empty.")
    return weights


def row_standardize(weights: np.ndarray) -> np.ndarray:
    """Row-standardize a spatial weight matrix."""
    row_sums = weights.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return weights / row_sums


def build_weight_matrix(weights: pd.DataFrame, provinces: list[str]) -> np.ndarray:
    """Build a row-standardized weight matrix using the panel province order."""
    index = {province: idx for idx, province in enumerate(provinces)}
    matrix = np.zeros((len(provinces), len(provinces)), dtype=float)

    for _, row in weights.iterrows():
        i = index.get(str(row["province_i"]))
        j = index.get(str(row["province_j"]))
        if i is not None and j is not None:
            matrix[i, j] = float(row["weight"])

    return row_standardize(matrix)


def moran_i(values: np.ndarray, weights: np.ndarray) -> float:
    """Calculate global Moran's I for one cross-section."""
    centered = values - values.mean()
    denominator = centered @ centered
    if denominator == 0:
        return float("nan")
    s0 = weights.sum()
    return float((len(values) / s0) * (centered @ weights @ centered) / denominator)


def build_moran_table(df: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    provinces = sorted(df["province"].unique().tolist())
    matrix = build_weight_matrix(weights, provinces)
    expected_i = -1 / (len(provinces) - 1)
    rng = np.random.default_rng(SEED)
    records = []

    for year, group in df.groupby("year"):
        group = group.set_index("province").loc[provinces]
        values = group["carbon_intensity"].to_numpy(dtype=float)
        observed = moran_i(values, matrix)
        permuted = np.array([moran_i(rng.permutation(values), matrix) for _ in range(N_PERMUTATIONS)])
        p_greater = (np.sum(permuted >= observed) + 1) / (N_PERMUTATIONS + 1)
        p_two_sided = (np.sum(np.abs(permuted - expected_i) >= abs(observed - expected_i)) + 1) / (
            N_PERMUTATIONS + 1
        )
        records.append(
            {
                "year": int(year),
                "moran_i": observed,
                "expected_i": expected_i,
                "p_greater": p_greater,
                "p_two_sided": p_two_sided,
                "n_provinces": len(provinces),
                "n_permutations": N_PERMUTATIONS,
                "seed": SEED,
            }
        )

    return pd.DataFrame(records).sort_values("year")


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    weights = load_spatial_weights()

    moran = build_moran_table(df, weights)
    moran.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Exported Moran's I table: {OUT_PATH}")
    print("Recommended packages after approval: libpysal, esda, spreg.")


if __name__ == "__main__":
    main()
