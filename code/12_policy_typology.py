"""Province policy typology based on digital finance and carbon intensity."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
REGION_GROUPS_PATH = ROOT / "data_raw" / "region_groups.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table12_policy_typology.csv"


POLICY_SUGGESTIONS = {
    "示范引领型": "巩固数字金融与绿色创新协同优势，强化跨区域示范和经验扩散。",
    "转型压力型": "优先推动数字金融资源向节能改造、产业升级和高耗能行业治理倾斜。",
    "稳态优化型": "保持低碳优势，补齐数字金融服务深度和绿色项目匹配能力。",
    "重点扶持型": "加强数字基础设施、信用体系和绿色金融供给，提升低碳转型基础能力。",
}


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    if not REGION_GROUPS_PATH.exists():
        raise FileNotFoundError(f"Missing region groups: {REGION_GROUPS_PATH}")
    panel = pd.read_csv(DATA_PATH)
    regions = pd.read_csv(REGION_GROUPS_PATH)
    required_panel = ["province", "year", "digital_finance", "carbon_intensity"]
    missing_panel = [col for col in required_panel if col not in panel.columns]
    if missing_panel:
        raise ValueError(f"Missing panel columns: {missing_panel}")
    if not {"province", "region"}.issubset(regions.columns):
        raise ValueError("region_groups.csv must include province and region columns.")
    return panel, regions[["province", "region"]]


def classify(row: pd.Series, digital_threshold: float, carbon_threshold: float) -> str:
    high_digital = row["digital_finance_mean"] >= digital_threshold
    high_carbon = row["carbon_intensity_mean"] >= carbon_threshold
    if high_digital and not high_carbon:
        return "示范引领型"
    if high_digital and high_carbon:
        return "转型压力型"
    if (not high_digital) and not high_carbon:
        return "稳态优化型"
    return "重点扶持型"


def build_typology(panel: pd.DataFrame, regions: pd.DataFrame) -> pd.DataFrame:
    sorted_panel = panel.sort_values(["province", "year"])
    grouped = sorted_panel.groupby("province", as_index=False).agg(
        start_year=("year", "min"),
        end_year=("year", "max"),
        digital_finance_mean=("digital_finance", "mean"),
        carbon_intensity_mean=("carbon_intensity", "mean"),
        digital_finance_start=("digital_finance", "first"),
        digital_finance_end=("digital_finance", "last"),
        carbon_intensity_start=("carbon_intensity", "first"),
        carbon_intensity_end=("carbon_intensity", "last"),
    )
    grouped["digital_finance_change"] = grouped["digital_finance_end"] - grouped["digital_finance_start"]
    grouped["carbon_intensity_change"] = grouped["carbon_intensity_end"] - grouped["carbon_intensity_start"]

    digital_threshold = float(grouped["digital_finance_mean"].median())
    carbon_threshold = float(grouped["carbon_intensity_mean"].median())

    grouped["digital_level"] = grouped["digital_finance_mean"].apply(lambda value: "高" if value >= digital_threshold else "低")
    grouped["carbon_level"] = grouped["carbon_intensity_mean"].apply(lambda value: "高" if value >= carbon_threshold else "低")
    grouped["policy_type"] = grouped.apply(classify, axis=1, digital_threshold=digital_threshold, carbon_threshold=carbon_threshold)
    grouped["policy_suggestion"] = grouped["policy_type"].map(POLICY_SUGGESTIONS)
    grouped["digital_threshold_median"] = digital_threshold
    grouped["carbon_threshold_median"] = carbon_threshold

    result = grouped.merge(regions, on="province", how="left")
    missing_region = sorted(result.loc[result["region"].isna(), "province"].tolist())
    if missing_region:
        raise ValueError(f"Missing region mapping for provinces: {missing_region}")

    columns = [
        "province",
        "region",
        "start_year",
        "end_year",
        "digital_finance_mean",
        "carbon_intensity_mean",
        "digital_finance_change",
        "carbon_intensity_change",
        "digital_level",
        "carbon_level",
        "policy_type",
        "policy_suggestion",
        "digital_threshold_median",
        "carbon_threshold_median",
    ]
    return result[columns].sort_values(["policy_type", "region", "province"]).reset_index(drop=True)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    panel, regions = load_inputs()
    typology = build_typology(panel, regions)
    if typology["province"].nunique() != 30:
        raise ValueError(f"Expected 30 provinces, got {typology['province'].nunique()}")
    typology.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported policy typology table: {OUT_PATH}")


if __name__ == "__main__":
    main()
