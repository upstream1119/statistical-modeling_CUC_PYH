"""Build the province-year panel dataset for the statistical modeling project.

The raw files are kept under ``其他文件/原始数据_待清洗`` because they are
working files and are ignored by Git. This script converts the downloaded wide
tables into long province-year tables, merges them, computes model variables,
and writes ``data_processed/panel_data.csv``.
"""

from __future__ import annotations

import sys
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEPS = ROOT / "其他文件" / "python_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import pandas as pd

RAW_WORK_DIR = ROOT / "其他文件" / "原始数据_待清洗"
PROCESSED_DIR = ROOT / "data_processed"
PANEL_PATH = PROCESSED_DIR / "panel_data.csv"
PANEL_WITH_TIBET_PATH = PROCESSED_DIR / "panel_data_with_tibet_audit.csv"

YEARS = list(range(2011, 2023))

REQUIRED_COLUMNS = [
    "province",
    "year",
    "carbon_intensity",
    "digital_finance",
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]

PROVINCES = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
]

ENGLISH_PROVINCE_MAP = {
    "Beijing": "北京",
    "Tianjin": "天津",
    "Hebei": "河北",
    "Shanxi": "山西",
    "Inner mongolia": "内蒙古",
    "Inner Mongolia": "内蒙古",
    "Liaoning": "辽宁",
    "Jilin": "吉林",
    "Heilongjiang": "黑龙江",
    "Shanghai": "上海",
    "Jiangsu": "江苏",
    "Zhejiang": "浙江",
    "Anhui": "安徽",
    "Fujian": "福建",
    "Jiangxi": "江西",
    "Shandong": "山东",
    "Henan": "河南",
    "Hubei": "湖北",
    "Hunan": "湖南",
    "Guangdong": "广东",
    "Guangxi": "广西",
    "Hainan": "海南",
    "Chongqing": "重庆",
    "Sichuan": "四川",
    "Guizhou": "贵州",
    "Yunnan": "云南",
    "Tibet": "西藏",
    "Shaanxi": "陕西",
    "Gansu": "甘肃",
    "Qinghai": "青海",
    "Ningxia": "宁夏",
    "Xinjiang": "新疆",
}


def normalize_province(value: object) -> str:
    """Normalize province names to short Chinese names used by the model."""
    if pd.isna(value):
        return ""
    name = str(value).strip()
    if name in ENGLISH_PROVINCE_MAP:
        return ENGLISH_PROVINCE_MAP[name]

    suffixes = [
        "维吾尔自治区",
        "壮族自治区",
        "回族自治区",
        "自治区",
        "省",
        "市",
    ]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def require_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Missing raw file: {path}")
    return path


def filter_years(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["year"].between(YEARS[0], YEARS[-1])].copy()


def load_nbs_wide_csv(filename: str, value_name: str) -> pd.DataFrame:
    """Load National Bureau of Statistics wide CSV exports."""
    path = require_file(RAW_WORK_DIR / filename)
    df = pd.read_csv(path, skiprows=2, encoding="utf-8-sig")
    df.columns = [str(col).strip() for col in df.columns]
    df = df.rename(columns={df.columns[0]: "province"})
    df["province"] = df["province"].map(normalize_province)
    df = df[df["province"].isin(PROVINCES)].copy()

    year_columns = [col for col in df.columns if col.endswith("年")]
    long_df = df.melt(
        id_vars=["province"],
        value_vars=year_columns,
        var_name="year",
        value_name=value_name,
    )
    long_df["year"] = long_df["year"].str.extract(r"(\d{4})").astype(int)
    long_df[value_name] = pd.to_numeric(long_df[value_name], errors="coerce")
    return filter_years(long_df)


def load_digital_finance() -> pd.DataFrame:
    path = require_file(RAW_WORK_DIR / "北京大学数字普惠金融指数（PKU-DFIIC）2011-2023.xlsx")
    df = pd.read_excel(path, sheet_name="Provinces", engine="openpyxl")
    df = df.rename(
        columns={
            "prov_name": "province",
            "index_aggregate": "digital_finance",
        }
    )
    df["province"] = df["province"].map(normalize_province)
    df = df[df["province"].isin(PROVINCES)].copy()
    return filter_years(df[["province", "year", "digital_finance"]])


def load_patents() -> pd.DataFrame:
    path = require_file(RAW_WORK_DIR / "分地区国内发明专利授权量_2011-2022.xlsx")
    df = pd.read_excel(path, header=2, engine="openpyxl")
    df = df.rename(columns={df.columns[0]: "province"})
    df["province"] = df["province"].map(normalize_province)
    df = df[df["province"].isin(PROVINCES)].copy()

    year_columns = [col for col in df.columns if str(col).endswith("年")]
    long_df = df.melt(
        id_vars=["province"],
        value_vars=year_columns,
        var_name="year",
        value_name="innovation",
    )
    long_df["year"] = long_df["year"].astype(str).str.extract(r"(\d{4})").astype(int)
    long_df["innovation"] = pd.to_numeric(long_df["innovation"], errors="coerce")
    return filter_years(long_df)


def load_carbon_and_energy_proxy() -> pd.DataFrame:
    """Load CEADs apparent CO2 accounts.

    ``carbon_emissions_mt`` is from the row "Total apparent CO2 emissions (mt)".
    ``energy_structure`` uses the share of raw-coal-related CO2 emissions in
    total apparent CO2 emissions as a first-pass coal structure proxy. This is
    preferable to summing the energy inventory workbook's physical units without
    standard-coal conversion factors.
    """
    path = require_file(RAW_WORK_DIR / "表观碳排放清单_1997-2022.xlsx")
    frames: list[pd.DataFrame] = []

    for year in YEARS:
        sheet = pd.read_excel(path, sheet_name=str(year), header=None, engine="openpyxl")
        header = sheet.iloc[0]
        total_row = sheet[sheet.iloc[:, 0] == "Total apparent CO2 emissions (mt)"]
        coal_row = sheet[sheet.iloc[:, 1] == "Raw coal total"]
        if total_row.empty or coal_row.empty:
            raise ValueError(f"Missing carbon rows in sheet {year}")

        records = []
        for col_idx in range(2, len(header)):
            province = normalize_province(header.iloc[col_idx])
            if province not in PROVINCES:
                continue
            carbon_emissions_mt = pd.to_numeric(total_row.iloc[0, col_idx], errors="coerce")
            raw_coal_emissions = pd.to_numeric(coal_row.iloc[0, col_idx], errors="coerce")
            records.append(
                {
                    "province": province,
                    "year": year,
                    "carbon_emissions_mt": carbon_emissions_mt,
                    "raw_coal_emissions_mt": raw_coal_emissions,
                }
            )
        frames.append(pd.DataFrame(records))

    df = pd.concat(frames, ignore_index=True)
    df["energy_structure"] = df["raw_coal_emissions_mt"] / df["carbon_emissions_mt"]
    return df


def merge_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    return reduce(
        lambda left, right: left.merge(right, on=["province", "year"], how="outer"),
        frames,
    )


def validate_panel_data(df: pd.DataFrame) -> None:
    """Validate required columns and basic province-year uniqueness."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    duplicated = df.duplicated(subset=["province", "year"]).sum()
    if duplicated:
        raise ValueError(f"Found duplicated province-year rows: {duplicated}")


def build_panel() -> pd.DataFrame:
    gdp = load_nbs_wide_csv("NBS_地区生产总值_GDP_省级_2011-2022.csv", "gdp")
    population = load_nbs_wide_csv("NBS_年末常住人口_省级_2011-2022.csv", "population")
    urban_population = load_nbs_wide_csv("NBS_年末城镇人口_省级_2011-2022.csv", "urban_population")
    secondary_industry = load_nbs_wide_csv(
        "NBS_第二产业增加值_省级_2011-2022.csv",
        "secondary_industry",
    )
    fiscal_expenditure = load_nbs_wide_csv(
        "NBS_地方一般公共预算支出_省级_2011-2022.csv",
        "fiscal_expenditure",
    )
    digital_finance = load_digital_finance()
    patents = load_patents()
    carbon = load_carbon_and_energy_proxy()

    panel = merge_frames(
        [
            gdp,
            population,
            urban_population,
            secondary_industry,
            fiscal_expenditure,
            digital_finance,
            patents,
            carbon,
        ]
    )

    panel["gdp_per_capita"] = panel["gdp"] / panel["population"]
    panel["industrial_structure"] = panel["secondary_industry"] / panel["gdp"]
    panel["urbanization"] = panel["urban_population"] / panel["population"]
    panel["government_intervention"] = panel["fiscal_expenditure"] / panel["gdp"]
    # CEADs uses million tonnes. GDP is 100 million yuan. This gives 10k tonnes
    # per 100 million yuan, a common readable carbon-intensity unit.
    panel["carbon_intensity"] = panel["carbon_emissions_mt"] * 100 / panel["gdp"]

    ordered_columns = [
        "province",
        "year",
        "carbon_intensity",
        "digital_finance",
        "gdp_per_capita",
        "industrial_structure",
        "urbanization",
        "government_intervention",
        "innovation",
        "energy_structure",
        "gdp",
        "population",
        "urban_population",
        "secondary_industry",
        "fiscal_expenditure",
        "carbon_emissions_mt",
        "raw_coal_emissions_mt",
    ]
    panel = panel[ordered_columns]
    panel["province"] = pd.Categorical(panel["province"], categories=PROVINCES, ordered=True)
    panel = panel.sort_values(["province", "year"]).reset_index(drop=True)
    panel["province"] = panel["province"].astype(str)
    return panel


def keep_complete_model_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Keep rows with all required model variables available.

    CEADs apparent carbon accounts do not include Tibet in the downloaded file.
    The audit file keeps Tibet for traceability, while panel_data.csv is the
    complete modeling sample used by downstream scripts.
    """
    return panel.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    try:
        panel = build_panel()
    except ImportError as exc:
        raise SystemExit(
            "Missing Excel dependency. Run `python -m pip install openpyxl` "
            "or keep `其他文件/python_deps` available."
        ) from exc

    validate_panel_data(panel)
    panel.to_csv(PANEL_WITH_TIBET_PATH, index=False, encoding="utf-8-sig")

    model_panel = keep_complete_model_sample(panel)
    validate_panel_data(model_panel)
    model_panel.to_csv(PANEL_PATH, index=False, encoding="utf-8-sig")

    missing_required = model_panel[REQUIRED_COLUMNS].isna().sum()

    print(f"Exported panel data: {PANEL_PATH}")
    print(f"Rows: {len(model_panel)}, provinces: {model_panel['province'].nunique()}, years: {model_panel['year'].nunique()}")
    print(f"Audit file with Tibet retained: {PANEL_WITH_TIBET_PATH}")
    print("Missing values in required variables:")
    print(missing_required.to_string())


if __name__ == "__main__":
    main()
