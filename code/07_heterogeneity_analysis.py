"""Regional heterogeneity analysis for digital finance and carbon intensity."""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
REGION_GROUPS_PATH = ROOT / "data_raw" / "region_groups.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table08_heterogeneity_by_region.csv"

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

REGION_ORDER = ["东部", "中部", "西部", "东北"]


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = ["province", "year", DEPENDENT_VAR, CORE_VAR] + CONTROL_VARS
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing panel columns: {missing}")
    return df


def add_region(df: pd.DataFrame) -> pd.DataFrame:
    if not REGION_GROUPS_PATH.exists():
        raise FileNotFoundError(f"Missing region groups: {REGION_GROUPS_PATH}")
    region_groups = pd.read_csv(REGION_GROUPS_PATH)
    expected_columns = {"province", "region"}
    if not expected_columns.issubset(region_groups.columns):
        raise ValueError(f"Region groups must include columns: {sorted(expected_columns)}")

    df = df.merge(region_groups[["province", "region"]], on="province", how="left")
    missing = sorted(df.loc[df["region"].isna(), "province"].unique().tolist())
    if missing:
        raise ValueError(f"Missing region mapping for provinces: {missing}")
    return df


def build_formula() -> str:
    rhs = [CORE_VAR] + CONTROL_VARS + ["C(year)"]
    return f"{DEPENDENT_VAR} ~ " + " + ".join(rhs)


def fit_region_model(df: pd.DataFrame, region: str) -> dict[str, object]:
    region_df = df.loc[df["region"] == region].dropna(subset=[DEPENDENT_VAR, CORE_VAR, "year"] + CONTROL_VARS)
    if region_df.empty:
        raise ValueError(f"No complete observations for region: {region}")

    result = smf.ols(formula=build_formula(), data=region_df).fit(cov_type="HC1")
    note = "Interpret cautiously: Northeast has only 3 provinces." if region == "东北" else ""
    return {
        "region": region,
        "n_provinces": int(region_df["province"].nunique()),
        "n_obs": int(result.nobs),
        "digital_finance_coef": float(result.params[CORE_VAR]),
        "digital_finance_std_err": float(result.bse[CORE_VAR]),
        "digital_finance_t_value": float(result.tvalues[CORE_VAR]),
        "digital_finance_p_value": float(result.pvalues[CORE_VAR]),
        "r_squared": float(result.rsquared),
        "interpretation_note": note,
    }


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = add_region(load_panel_data())
    rows = [fit_region_model(df, region) for region in REGION_ORDER]
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported regional heterogeneity table: {OUT_PATH}")


if __name__ == "__main__":
    main()
