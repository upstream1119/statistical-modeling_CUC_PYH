"""Prepare alternative spatial weights and region grouping files.

The adjacency matrix remains the main spatial weights matrix. This script
creates two robustness alternatives:

1. inverse geographic distance between provincial administrative centers;
2. inverse economic distance based on average real GDP per capita.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_SPATIAL_DIR = ROOT / "data_raw" / "spatial"
PANEL_PATH = ROOT / "data_processed" / "panel_data.csv"
COORD_SOURCE_PATH = RAW_SPATIAL_DIR / "source_adcode_lng_lat_gaode_20230331.xlsx"

COORD_OUTPUT_PATH = RAW_SPATIAL_DIR / "province_capital_coordinates.csv"
GEO_WEIGHTS_PATH = RAW_SPATIAL_DIR / "spatial_weights_geo_distance.csv"
ECON_WEIGHTS_PATH = RAW_SPATIAL_DIR / "spatial_weights_economic_distance.csv"
REGION_GROUPS_PATH = ROOT / "data_raw" / "region_groups.csv"

MUNICIPALITIES = {"北京", "天津", "上海", "重庆"}
FULL_NAME_MAP = {
    "内蒙古": "内蒙古自治区",
    "广西": "广西壮族自治区",
    "宁夏": "宁夏回族自治区",
    "新疆": "新疆维吾尔自治区",
}
CAPITAL_CITY_MAP = {
    "北京": "北京",
    "天津": "天津",
    "河北": "石家庄",
    "山西": "太原",
    "内蒙古": "呼和浩特",
    "辽宁": "沈阳",
    "吉林": "长春",
    "黑龙江": "哈尔滨",
    "上海": "上海",
    "江苏": "南京",
    "浙江": "杭州",
    "安徽": "合肥",
    "福建": "福州",
    "江西": "南昌",
    "山东": "济南",
    "河南": "郑州",
    "湖北": "武汉",
    "湖南": "长沙",
    "广东": "广州",
    "广西": "南宁",
    "海南": "海口",
    "重庆": "重庆",
    "四川": "成都",
    "贵州": "贵阳",
    "云南": "昆明",
    "陕西": "西安",
    "甘肃": "兰州",
    "青海": "西宁",
    "宁夏": "银川",
    "新疆": "乌鲁木齐",
}

REGION_GROUPS = {
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


def source_name(province: str) -> str:
    if province in MUNICIPALITIES:
        return f"{province}市"
    return FULL_NAME_MAP.get(province, f"{province}省")


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))


def load_coordinates(panel: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_excel(COORD_SOURCE_PATH)
    raw = raw.rename(
        columns={
            raw.columns[0]: "adcode",
            raw.columns[1]: "source_name",
            raw.columns[2]: "longitude",
            raw.columns[3]: "latitude",
        }
    )

    rows = []
    for province in panel["province"].drop_duplicates():
        name = source_name(province)
        match = raw[raw["source_name"] == name]
        if match.empty:
            raise ValueError(f"Missing coordinate for {province} ({name})")
        row = match.iloc[0]
        rows.append(
            {
                "province": province,
                "capital_city": CAPITAL_CITY_MAP[province],
                "source_name": name,
                "adcode": int(row["adcode"]),
                "longitude": float(row["longitude"]),
                "latitude": float(row["latitude"]),
                "source": "高德地图公开数据，经CSDN/GitCode资源整理，更新时间2023-03-31",
            }
        )

    coords = pd.DataFrame(rows)
    if coords["province"].duplicated().any():
        raise ValueError("Duplicate province in coordinates")
    return coords


def build_geo_weights(coords: pd.DataFrame) -> pd.DataFrame:
    rows = []
    records = coords.to_dict("records")
    for left in records:
        for right in records:
            if left["province"] == right["province"]:
                continue
            distance = haversine_km(
                left["longitude"],
                left["latitude"],
                right["longitude"],
                right["latitude"],
            )
            rows.append(
                {
                    "province_i": left["province"],
                    "province_j": right["province"],
                    "distance_km": distance,
                    "weight": 1 / distance,
                }
            )
    return pd.DataFrame(rows)


def build_economic_weights(panel: pd.DataFrame) -> pd.DataFrame:
    avg = (
        panel.groupby("province", as_index=False)["gdp_per_capita"]
        .mean()
        .rename(columns={"gdp_per_capita": "avg_gdp_per_capita_2011_2022"})
    )
    records = avg.to_dict("records")
    rows = []
    epsilon = 1e-6
    for left in records:
        for right in records:
            if left["province"] == right["province"]:
                continue
            distance = abs(
                left["avg_gdp_per_capita_2011_2022"]
                - right["avg_gdp_per_capita_2011_2022"]
            )
            rows.append(
                {
                    "province_i": left["province"],
                    "province_j": right["province"],
                    "economic_distance": distance,
                    "weight": 1 / (distance + epsilon),
                }
            )
    return pd.DataFrame(rows)


def build_region_groups(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for province in panel["province"].drop_duplicates():
        if province not in REGION_GROUPS:
            raise ValueError(f"Missing region group for {province}")
        rows.append({"province": province, "region": REGION_GROUPS[province]})
    return pd.DataFrame(rows)


def main() -> None:
    panel = pd.read_csv(PANEL_PATH)
    RAW_SPATIAL_DIR.mkdir(parents=True, exist_ok=True)

    coords = load_coordinates(panel)
    geo_weights = build_geo_weights(coords)
    economic_weights = build_economic_weights(panel)
    region_groups = build_region_groups(panel)

    expected_n = panel["province"].nunique()
    expected_edges = expected_n * (expected_n - 1)
    if len(coords) != expected_n:
        raise ValueError("Coordinate province count does not match panel")
    if len(geo_weights) != expected_edges:
        raise ValueError("Geographic weights are not a full directed matrix")
    if len(economic_weights) != expected_edges:
        raise ValueError("Economic weights are not a full directed matrix")

    coords.to_csv(COORD_OUTPUT_PATH, index=False, encoding="utf-8-sig")
    geo_weights.to_csv(GEO_WEIGHTS_PATH, index=False, encoding="utf-8-sig")
    economic_weights.to_csv(ECON_WEIGHTS_PATH, index=False, encoding="utf-8-sig")
    region_groups.to_csv(REGION_GROUPS_PATH, index=False, encoding="utf-8-sig")

    print(f"Exported coordinates: {COORD_OUTPUT_PATH}")
    print(f"Exported geographic distance weights: {GEO_WEIGHTS_PATH}")
    print(f"Exported economic distance weights: {ECON_WEIGHTS_PATH}")
    print(f"Exported region groups: {REGION_GROUPS_PATH}")
    print(f"Provinces: {expected_n}, directed edges per full matrix: {expected_edges}")


if __name__ == "__main__":
    main()
