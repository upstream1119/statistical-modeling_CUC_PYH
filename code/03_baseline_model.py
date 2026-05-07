"""Baseline regression scaffold.

The default model is:
low_carbon = digital_finance + controls + year fixed effects.
Province fixed effects can be added after the final sample size is confirmed.
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"

DEPENDENT_VAR = "low_carbon"
CORE_VAR = "digital_finance"
CONTROL_VARS = [
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
        raise ValueError("panel_data.csv is empty. Fill data before regression.")
    return df


def build_formula(df: pd.DataFrame) -> str:
    controls = [col for col in CONTROL_VARS if col in df.columns]
    rhs = [CORE_VAR] + controls + ["C(year)"]
    return f"{DEPENDENT_VAR} ~ " + " + ".join(rhs)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()

    model_columns = [DEPENDENT_VAR, CORE_VAR, "year"] + [col for col in CONTROL_VARS if col in df.columns]
    model_df = df.dropna(subset=model_columns).copy()
    if model_df.empty:
        raise ValueError("No complete rows available for baseline regression.")

    formula = build_formula(model_df)
    result = smf.ols(formula=formula, data=model_df).fit(cov_type="HC1")

    output = pd.DataFrame(
        {
            "coef": result.params,
            "std_err": result.bse,
            "t_value": result.tvalues,
            "p_value": result.pvalues,
        }
    )
    output.to_csv(TABLES_DIR / "table03_baseline_regression.csv", encoding="utf-8-sig")

    with open(TABLES_DIR / "table03_baseline_regression_summary.txt", "w", encoding="utf-8") as f:
        f.write(result.summary().as_text())

    print("Exported baseline regression results.")
    print(f"Formula: {formula}")


if __name__ == "__main__":
    main()
