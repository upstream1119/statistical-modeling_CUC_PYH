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
import numpy as np

RAW_WORK_DIR = ROOT / "data_raw"
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

ENERGY_PROVINCE_SHEET_MAP = {
    "Shanghai": "上海",
    "Yunnan": "云南",
    "InnerMongolia": "内蒙古",
    "Beijing": "北京",
    "Jilin": "吉林",
    "Sichuan": "四川",
    "Tianjin": "天津",
    "Ningxia": "宁夏",
    "Anhui": "安徽",
    "Shandong": "山东",
    "Shanxi": "山西",
    "Guangdong": "广东",
    "Guangxi": "广西",
    "Xinjiang": "新疆",
    "Jiangsu": "江苏",
    "Jiangxi": "江西",
    "Hebei": "河北",
    "Henan": "河南",
    "Zhejiang": "浙江",
    "Hainan": "海南",
    "Hubei": "湖北",
    "Hunan": "湖南",
    "Gansu": "甘肃",
    "Fujian": "福建",
    "Guizhou": "贵州",
    "Liaoning": "辽宁",
    "Chongqing": "重庆",
    "Shaanxi": "陕西",
    "Qinghai": "青海",
    "Heilongjiang": "黑龙江",
}

# Coefficients are from China Energy Statistical Yearbook 2022 Appendix IV,
# "Conversion Factors from Physical Units to Coal Equivalent". Values convert
# CEADs physical units into 10k tonnes coal equivalent.
ENERGY_TCE_FACTORS = {
    # 10k tonnes * kgce/kg -> 10k tce
    "Raw_Coal": 0.7143,
    "Cleaned_Coal": 0.9000,
    # CEADs gives one Other_Washed_Coal column. Appendix IV splits it into
    # middlings and slimes; use their midpoint where the source has no split.
    "Other_Washed_Coal": (0.2857 + 0.4286) / 2,
    "Briquettes": 0.7143,
    "Coke": 0.9714,
    "Other_Coking_Products": 1.1429,
    "Crude_Oil": 1.4286,
    "Gasoline": 1.4714,
    "Kerosene": 1.4714,
    "Diesel_Oil": 1.4571,
    "Fuel_Oil": 1.4286,
    "LPG": 1.7143,
    "Refinery_Gas": 1.5714,
    "Other_Petroleum_Products": 1.4286,
    # 10^8 m3 * kgce/m3 -> 10k tce. Range values use midpoints.
    "Coke_Oven_Gas": ((0.5714 + 0.6143) / 2) * 10,
    "Other_Gas": 0.3571 * 10,
    "Natural_Gas": ((1.1000 + 1.3300) / 2) * 10,
    # 10^10 kJ heat = 10^7 MJ; kgce/MJ -> 10k tce.
    "Heat": 0.03412,
    # 10^8 kWh * kgce/kWh -> 10k tce.
    "Electricity": 0.1229 * 10,
    # Already 10k tce in CEADs.
    "Other_Energy": 1.0,
}

COAL_RELATED_ENERGY_COLUMNS = [
    "Raw_Coal",
    "Cleaned_Coal",
    "Other_Washed_Coal",
    "Briquettes",
    "Coke",
    "Coke_Oven_Gas",
    "Other_Coking_Products",
]


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


def calculate_real_gdp(gdp: pd.DataFrame, gdp_index: pd.DataFrame) -> pd.DataFrame:
    """Chain GDP volume index into real GDP with 2011 as base year."""
    merged = gdp.merge(gdp_index, on=["province", "year"], how="left")
    records = []
    for province, group in merged.sort_values("year").groupby("province", sort=False):
        base_rows = group[group["year"] == YEARS[0]]
        if base_rows.empty:
            continue
        real_gdp = float(base_rows.iloc[0]["gdp_nominal"])
        for _, row in group.iterrows():
            year = int(row["year"])
            if year == YEARS[0]:
                real_gdp = float(row["gdp_nominal"])
            else:
                index_value = row["gdp_index_previous_year_100"]
                if pd.isna(index_value):
                    real_gdp = np.nan
                elif not pd.isna(real_gdp):
                    real_gdp = real_gdp * float(index_value) / 100
            records.append({"province": province, "year": year, "gdp_real": real_gdp})
    return pd.DataFrame(records)


def load_digital_finance() -> pd.DataFrame:
    path = require_file(RAW_WORK_DIR / "digital_finance" / "北京大学数字普惠金融指数（PKU-DFIIC）2011-2023.xlsx")
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
    path = require_file(RAW_WORK_DIR / "patents" / "分地区国内发明专利授权量_2011-2022.xlsx")
    df = pd.read_excel(path, header=2, engine="openpyxl")
    df = df.rename(columns={df.columns[0]: "province"})
    df["province"] = df["province"].map(normalize_province)
    df = df[df["province"].isin(PROVINCES)].copy()

    year_columns = [col for col in df.columns if str(col).endswith("年")]
    long_df = df.melt(
        id_vars=["province"],
        value_vars=year_columns,
        var_name="year",
        value_name="patent_grants",
    )
    long_df["year"] = long_df["year"].astype(str).str.extract(r"(\d{4})").astype(int)
    long_df["patent_grants"] = pd.to_numeric(long_df["patent_grants"], errors="coerce")
    long_df["innovation"] = np.log1p(long_df["patent_grants"])
    return filter_years(long_df)


def load_carbon_emissions() -> pd.DataFrame:
    """Load CEADs apparent CO2 accounts.

    ``carbon_emissions_mt`` is from the row "Total apparent CO2 emissions (mt)".
    """
    path = require_file(RAW_WORK_DIR / "carbon_emissions" / "表观碳排放清单_1997-2022.xlsx")
    frames: list[pd.DataFrame] = []

    for year in YEARS:
        sheet = pd.read_excel(path, sheet_name=str(year), header=None, engine="openpyxl")
        header = sheet.iloc[0]
        total_row = sheet[sheet.iloc[:, 0] == "Total apparent CO2 emissions (mt)"]
        if total_row.empty:
            raise ValueError(f"Missing carbon rows in sheet {year}")

        records = []
        for col_idx in range(2, len(header)):
            province = normalize_province(header.iloc[col_idx])
            if province not in PROVINCES:
                continue
            carbon_emissions_mt = pd.to_numeric(total_row.iloc[0, col_idx], errors="coerce")
            records.append(
                {
                    "province": province,
                    "year": year,
                    "carbon_emissions_mt": carbon_emissions_mt,
                }
            )
        frames.append(pd.DataFrame(records))

    return pd.concat(frames, ignore_index=True)


def load_energy_structure() -> pd.DataFrame:
    """Calculate coal-related final energy consumption share in standard coal."""
    frames = []
    for year in YEARS:
        path = require_file(RAW_WORK_DIR / "energy" / f"省级能源清单_{year}.xlsx")
        xls = pd.ExcelFile(path, engine="openpyxl")
        for sheet_name in xls.sheet_names:
            if sheet_name == "NOTE":
                continue
            english_name = sheet_name.replace(str(year), "")
            province = ENERGY_PROVINCE_SHEET_MAP.get(english_name)
            if province not in PROVINCES:
                continue
            sheet = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
            row = sheet[sheet.iloc[:, 0] == "Total Final Consumption"]
            if row.empty:
                raise ValueError(f"Missing Total Final Consumption in {path.name} {sheet_name}")
            row = row.iloc[0]

            tce_values = {}
            for col, factor in ENERGY_TCE_FACTORS.items():
                if col not in sheet.columns:
                    raise ValueError(f"Missing energy column {col} in {path.name} {sheet_name}")
                value = pd.to_numeric(row[col], errors="coerce")
                tce_values[col] = value * factor

            coal_related_tce = sum(tce_values[col] for col in COAL_RELATED_ENERGY_COLUMNS)
            total_energy_tce = sum(tce_values.values())
            frames.append(
                {
                    "province": province,
                    "year": year,
                    "coal_related_tce": coal_related_tce,
                    "total_energy_tce": total_energy_tce,
                    "energy_structure": coal_related_tce / total_energy_tce if total_energy_tce else np.nan,
                }
            )
    return pd.DataFrame(frames)


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
    gdp = load_nbs_wide_csv("nbs/NBS_地区生产总值_GDP_省级_2011-2022.csv", "gdp_nominal")
    gdp_index = load_nbs_wide_csv(
        "nbs/NBS_地区生产总值指数_上年100_省级_2011-2022.csv",
        "gdp_index_previous_year_100",
    )
    real_gdp = calculate_real_gdp(gdp, gdp_index)
    population = load_nbs_wide_csv("nbs/NBS_年末常住人口_省级_2011-2022.csv", "population")
    urban_population = load_nbs_wide_csv("nbs/NBS_年末城镇人口_省级_2011-2022.csv", "urban_population")
    secondary_industry = load_nbs_wide_csv(
        "nbs/NBS_第二产业增加值_省级_2011-2022.csv",
        "secondary_industry",
    )
    fiscal_expenditure = load_nbs_wide_csv(
        "nbs/NBS_地方一般公共预算支出_省级_2011-2022.csv",
        "fiscal_expenditure",
    )
    digital_finance = load_digital_finance()
    patents = load_patents()
    carbon = load_carbon_emissions()
    energy = load_energy_structure()

    panel = merge_frames(
        [
            gdp,
            gdp_index,
            real_gdp,
            population,
            urban_population,
            secondary_industry,
            fiscal_expenditure,
            digital_finance,
            patents,
            carbon,
            energy,
        ]
    )

    panel["gdp_per_capita"] = panel["gdp_real"] / panel["population"]
    panel["industrial_structure"] = panel["secondary_industry"] / panel["gdp_nominal"]
    panel["urbanization"] = panel["urban_population"] / panel["population"]
    panel["government_intervention"] = panel["fiscal_expenditure"] / panel["gdp_nominal"]
    # CEADs uses million tonnes. GDP is 100 million yuan. This gives 10k tonnes
    # per 100 million yuan of 2011-base real GDP.
    panel["carbon_intensity"] = panel["carbon_emissions_mt"] * 100 / panel["gdp_real"]

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
        "gdp_nominal",
        "gdp_index_previous_year_100",
        "gdp_real",
        "population",
        "urban_population",
        "secondary_industry",
        "fiscal_expenditure",
        "carbon_emissions_mt",
        "patent_grants",
        "coal_related_tce",
        "total_energy_tce",
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
