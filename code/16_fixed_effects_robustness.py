"""Fixed-effects robustness checks for the baseline relationship."""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table15_fixed_effects_robustness.csv"

DEPENDENT_VAR = "carbon_intensity"
CORE_VAR = "digital_finance"
CONTROL_VARS = [
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]
COMPACT_CONTROL_VARS = [
    "gdp_per_capita",
    "industrial_structure",
    "innovation",
    "energy_structure",
]


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = ["province", "year", DEPENDENT_VAR, CORE_VAR] + CONTROL_VARS
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing panel columns: {missing}")
    return df


def fit_model(df: pd.DataFrame, model_name: str, controls: list[str], fixed_effect_terms: list[str], note: str) -> dict[str, object]:
    model_columns = [DEPENDENT_VAR, CORE_VAR, "province", "year"] + controls
    model_df = df.dropna(subset=model_columns).copy()
    if model_df.empty:
        raise ValueError(f"No complete observations for model: {model_name}")
    rhs = [CORE_VAR] + controls + fixed_effect_terms
    formula = f"{DEPENDENT_VAR} ~ " + " + ".join(rhs)
    result = smf.ols(formula=formula, data=model_df).fit(cov_type="HC1")
    return {
        "model_name": model_name,
        "formula": formula,
        "fixed_effects": " + ".join(fixed_effect_terms),
        "controls": "; ".join(controls),
        "n_obs": int(result.nobs),
        "n_provinces": int(model_df["province"].nunique()),
        "digital_finance_coef": float(result.params[CORE_VAR]),
        "digital_finance_std_err": float(result.bse[CORE_VAR]),
        "digital_finance_t_value": float(result.tvalues[CORE_VAR]),
        "digital_finance_p_value": float(result.pvalues[CORE_VAR]),
        "r_squared": float(result.rsquared),
        "interpretation_note": note,
    }


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    rows = [
        fit_model(
            df,
            "year_fe_full_controls",
            CONTROL_VARS,
            ["C(year)"],
            "Baseline-like model with year fixed effects and HC1 robust standard errors.",
        ),
        fit_model(
            df,
            "two_way_fe_full_controls",
            CONTROL_VARS,
            ["C(province)", "C(year)"],
            "Supplementary robustness model controlling province and year fixed effects.",
        ),
        fit_model(
            df,
            "two_way_fe_compact_controls",
            COMPACT_CONTROL_VARS,
            ["C(province)", "C(year)"],
            "Compact two-way fixed-effects model excluding urbanization and government intervention.",
        ),
    ]
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported fixed-effects robustness table: {OUT_PATH}")


if __name__ == "__main__":
    main()
