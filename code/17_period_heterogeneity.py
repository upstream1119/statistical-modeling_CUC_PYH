"""Period heterogeneity analysis for digital finance and carbon intensity."""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table16_period_heterogeneity.csv"

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

PERIODS = [
    ("2011-2016", 2011, 2016, "数字普惠金融扩张早期"),
    ("2017-2022", 2017, 2022, "数字普惠金融深化阶段"),
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


def build_formula() -> str:
    rhs = [CORE_VAR] + CONTROL_VARS + ["C(year)"]
    return f"{DEPENDENT_VAR} ~ " + " + ".join(rhs)


def fit_period(df: pd.DataFrame, period_name: str, start_year: int, end_year: int, stage_note: str) -> dict[str, object]:
    period_df = df.loc[(df["year"] >= start_year) & (df["year"] <= end_year)].copy()
    model_columns = [DEPENDENT_VAR, CORE_VAR, "year"] + CONTROL_VARS
    period_df = period_df.dropna(subset=model_columns)
    if period_df.empty:
        raise ValueError(f"No complete observations for period: {period_name}")
    result = smf.ols(formula=build_formula(), data=period_df).fit(cov_type="HC1")
    return {
        "period": period_name,
        "start_year": start_year,
        "end_year": end_year,
        "stage_note": stage_note,
        "n_obs": int(result.nobs),
        "n_provinces": int(period_df["province"].nunique()),
        "digital_finance_coef": float(result.params[CORE_VAR]),
        "digital_finance_std_err": float(result.bse[CORE_VAR]),
        "digital_finance_t_value": float(result.tvalues[CORE_VAR]),
        "digital_finance_p_value": float(result.pvalues[CORE_VAR]),
        "r_squared": float(result.rsquared),
        "interpretation_note": "Use as period heterogeneity evidence, not causal proof.",
    }


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    rows = [fit_period(df, *period) for period in PERIODS]
    result = pd.DataFrame(rows)
    if not (result["n_obs"] == 180).all():
        raise ValueError(f"Expected 180 observations per period, got {result[['period', 'n_obs']].to_dict('records')}")
    if not (result["n_provinces"] == 30).all():
        raise ValueError(
            f"Expected 30 provinces per period, got {result[['period', 'n_provinces']].to_dict('records')}"
        )
    result.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported period heterogeneity table: {OUT_PATH}")


if __name__ == "__main__":
    main()
