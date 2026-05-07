"""Pre-model validation, descriptive statistics, and exploratory outputs."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

NUMERIC_COLUMNS = [
    "carbon_intensity",
    "digital_finance",
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]

ID_COLUMNS = ["province", "year"]


def calculate_vif(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Calculate variance inflation factors without extra dependencies."""
    clean = df[columns].dropna().copy()
    if clean.empty:
        raise ValueError("No complete rows available for VIF calculation.")

    standardized = (clean - clean.mean()) / clean.std(ddof=0)
    records = []
    for col in columns:
        y = standardized[col].to_numpy(dtype=float)
        x_cols = [other for other in columns if other != col]
        x = standardized[x_cols].to_numpy(dtype=float)
        x = np.column_stack([np.ones(len(x)), x])

        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        fitted = x @ beta
        ss_res = np.sum((y - fitted) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot else np.nan
        vif = 1 / (1 - r_squared) if r_squared < 1 else np.inf
        records.append({"variable": col, "r_squared": r_squared, "vif": vif})
    return pd.DataFrame(records).sort_values("vif", ascending=False)


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError("panel_data.csv is empty. Fill data before descriptive analysis.")
    return df


def build_quality_report(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    duplicated_rows = int(df.duplicated(subset=ID_COLUMNS).sum())
    expected_rows = int(df["province"].nunique() * df["year"].nunique())
    rows = [
        {"metric": "n_rows", "value": len(df), "note": "Total province-year rows"},
        {"metric": "n_provinces", "value": df["province"].nunique(), "note": "Unique provinces"},
        {"metric": "min_year", "value": int(df["year"].min()), "note": "First sample year"},
        {"metric": "max_year", "value": int(df["year"].max()), "note": "Last sample year"},
        {"metric": "expected_balanced_rows", "value": expected_rows, "note": "Provinces multiplied by years"},
        {"metric": "duplicated_province_year", "value": duplicated_rows, "note": "Duplicated province-year keys"},
    ]
    for col in ID_COLUMNS + numeric_columns:
        rows.append({"metric": f"missing_{col}", "value": int(df[col].isna().sum()), "note": "Missing values"})
    return pd.DataFrame(rows)


def build_high_correlation_pairs(corr: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
    records = []
    columns = list(corr.columns)
    for i, left in enumerate(columns):
        for right in columns[i + 1 :]:
            value = corr.loc[left, right]
            if abs(value) >= threshold:
                records.append(
                    {
                        "variable_1": left,
                        "variable_2": right,
                        "correlation": value,
                        "abs_correlation": abs(value),
                    }
                )
    return pd.DataFrame(records).sort_values("abs_correlation", ascending=False)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_panel_data()
    available_numeric = [col for col in NUMERIC_COLUMNS if col in df.columns]

    quality = build_quality_report(df, available_numeric)
    quality.to_csv(TABLES_DIR / "table00_data_quality_report.csv", index=False, encoding="utf-8-sig")

    desc = df[available_numeric].describe().T
    desc.to_csv(TABLES_DIR / "table01_descriptive_statistics.csv", encoding="utf-8-sig")

    corr = df[available_numeric].corr()
    corr.to_csv(TABLES_DIR / "table02_correlation_matrix.csv", encoding="utf-8-sig")

    high_corr = build_high_correlation_pairs(corr)
    high_corr.to_csv(TABLES_DIR / "table02a_high_correlation_pairs.csv", index=False, encoding="utf-8-sig")

    vif_columns = [col for col in available_numeric if col != "carbon_intensity"]
    vif = calculate_vif(df, vif_columns)
    vif.to_csv(TABLES_DIR / "table02b_vif_diagnostics.csv", index=False, encoding="utf-8-sig")

    print("Exported data quality, descriptive, correlation, and VIF diagnostics.")


if __name__ == "__main__":
    main()
