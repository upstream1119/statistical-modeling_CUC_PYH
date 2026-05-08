"""Regional heterogeneity analysis for digital finance and carbon intensity."""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
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

REGION_MAP = {
    "北京": "东部",
    "天津": "东部",
    "河北": "东部",
    "上海": "东部",
    "江苏": "东部",
    "浙江": "东部",
    "福建": "东部",
    "山东": "东部",
    "广东": "东部",
    "海南": "东部",
    "山西": "中部",
    "安徽": "中部",
    "江西": "中部",
    "河南": "中部",
    "湖北": "中部",
    "湖南": "中部",
    "内蒙古": "西部",
    "广西": "西部",
    "重庆": "西部",
    "四川": "西部",
    "贵州": "西部",
    "云南": "西部",
    "陕西": "西部",
    "甘肃": "西部",
    "青海": "西部",
    "宁夏": "西部",
    "新疆": "西部",
    "辽宁": "东北",
    "吉林": "东北",
    "黑龙江": "东北",
}

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
    df = df.copy()
    df["region"] = df["province"].map(REGION_MAP)
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
