"""Robustness checks for the baseline carbon intensity model."""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table07_robustness_checks.csv"

DEPENDENT_VAR = "carbon_intensity"
CORE_VAR = "digital_finance"
BASE_CONTROLS = [
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
        raise ValueError("panel_data.csv is empty.")
    return df.sort_values(["province", "year"]).reset_index(drop=True)


def fit_spec(df: pd.DataFrame, spec_name: str, core_var: str, controls: list[str]) -> dict[str, object]:
    columns = [DEPENDENT_VAR, core_var, "year"] + controls
    model_df = df.dropna(subset=columns).copy()
    if model_df.empty:
        raise ValueError(f"No complete observations for {spec_name}.")
    formula = f"{DEPENDENT_VAR} ~ {core_var} + " + " + ".join(controls + ["C(year)"])
    result = smf.ols(formula=formula, data=model_df).fit(cov_type="HC1")
    return {
        "spec": spec_name,
        "core_variable": core_var,
        "coef": float(result.params[core_var]),
        "std_err": float(result.bse[core_var]),
        "t_value": float(result.tvalues[core_var]),
        "p_value": float(result.pvalues[core_var]),
        "n_obs": int(result.nobs),
        "r_squared": float(result.rsquared),
        "formula": formula,
    }


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    df["digital_finance_lag1"] = df.groupby("province")[CORE_VAR].shift(1)
    df["log1p_innovation"] = np.log1p(df["innovation"])
    df["log_gdp_per_capita"] = np.log(df["gdp_per_capita"])

    specs = [
        ("baseline", CORE_VAR, BASE_CONTROLS),
        ("lagged_digital_finance", "digital_finance_lag1", BASE_CONTROLS),
        (
            "log1p_innovation",
            CORE_VAR,
            [
                "gdp_per_capita",
                "industrial_structure",
                "urbanization",
                "government_intervention",
                "log1p_innovation",
                "energy_structure",
            ],
        ),
        ("remove_urbanization", CORE_VAR, [var for var in BASE_CONTROLS if var != "urbanization"]),
        ("log_gdp_per_capita", CORE_VAR, ["log_gdp_per_capita"] + BASE_CONTROLS[1:]),
    ]

    rows = [fit_spec(df, name, core, controls) for name, core, controls in specs]
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported robustness checks: {OUT_PATH}")


if __name__ == "__main__":
    main()
