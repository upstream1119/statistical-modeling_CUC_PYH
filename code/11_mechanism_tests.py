"""Mechanism-path checks for digital finance and carbon intensity.

These checks provide writing evidence for possible pathways. They should not
be described as strict causal mediation tests.
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table11_mechanism_tests.csv"

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
MECHANISMS = [
    ("innovation", "技术创新"),
    ("industrial_structure", "产业结构"),
    ("energy_structure", "能源结构"),
]


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = ["province", "year", DEPENDENT_VAR, CORE_VAR] + CONTROL_VARS
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing panel columns: {missing}")
    return df


def fit_ols(formula: str, df: pd.DataFrame):
    model_df = df.dropna().copy()
    if model_df.empty:
        raise ValueError(f"No complete observations for formula: {formula}")
    return smf.ols(formula=formula, data=model_df).fit(cov_type="HC1")


def significance_label(p_value: float) -> str:
    if p_value < 0.01:
        return "1%水平显著"
    if p_value < 0.05:
        return "5%水平显著"
    if p_value < 0.1:
        return "10%水平边际显著"
    return "未通过常规显著性检验"


def direction_label(coef: float) -> str:
    return "正向" if coef > 0 else "负向" if coef < 0 else "零"


def interpretation_note(mechanism_label: str, path_a_coef: float, path_a_p: float, path_b_coef: float, path_b_p: float) -> str:
    return (
        f"数字普惠金融与{mechanism_label}呈{direction_label(path_a_coef)}关系"
        f"（{significance_label(path_a_p)}）；{mechanism_label}与碳强度呈"
        f"{direction_label(path_b_coef)}关系（{significance_label(path_b_p)}）。"
    )


def run_mechanism_test(df: pd.DataFrame, mechanism: str, mechanism_label: str) -> dict[str, object]:
    controls = [col for col in CONTROL_VARS if col != mechanism]
    model_columns = [DEPENDENT_VAR, CORE_VAR, mechanism, "year"] + controls
    model_df = df.dropna(subset=model_columns).copy()
    if model_df.empty:
        raise ValueError(f"No complete observations for mechanism: {mechanism}")

    path_a_formula = f"{mechanism} ~ {CORE_VAR} + " + " + ".join(controls + ["C(year)"])
    path_b_formula = f"{DEPENDENT_VAR} ~ {CORE_VAR} + {mechanism} + " + " + ".join(controls + ["C(year)"])

    path_a = fit_ols(path_a_formula, model_df[[mechanism, CORE_VAR, "year"] + controls])
    path_b = fit_ols(path_b_formula, model_df[[DEPENDENT_VAR, CORE_VAR, mechanism, "year"] + controls])

    return {
        "mechanism": mechanism,
        "mechanism_label": mechanism_label,
        "path_a_formula": path_a_formula,
        "path_a_digital_finance_coef": float(path_a.params[CORE_VAR]),
        "path_a_digital_finance_p_value": float(path_a.pvalues[CORE_VAR]),
        "path_b_mechanism_coef": float(path_b.params[mechanism]),
        "path_b_mechanism_p_value": float(path_b.pvalues[mechanism]),
        "direct_digital_finance_coef": float(path_b.params[CORE_VAR]),
        "direct_digital_finance_p_value": float(path_b.pvalues[CORE_VAR]),
        "n_obs": int(path_b.nobs),
        "interpretation_note": interpretation_note(
            mechanism_label,
            float(path_a.params[CORE_VAR]),
            float(path_a.pvalues[CORE_VAR]),
            float(path_b.params[mechanism]),
            float(path_b.pvalues[mechanism]),
        ),
        "writing_caution": "仅可写为机制路径线索，不可写为严格因果中介效应。",
    }


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    rows = [run_mechanism_test(df, mechanism, label) for mechanism, label in MECHANISMS]
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported mechanism-path checks: {OUT_PATH}")


if __name__ == "__main__":
    main()
