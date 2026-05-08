# 备选空间权重矩阵与地区分组说明

本文档用于说明后续空间计量稳健性检验和区域异质性分析所需的辅助数据。

## 1. 空间权重矩阵

当前项目保留三类空间权重矩阵。

| 文件 | 类型 | 构造方式 | 用途 |
| --- | --- | --- | --- |
| `data_raw/spatial/spatial_weights.csv` | 邻接矩阵 | 省级地区接壤则 `weight = 1`，否则为 0；海南按与广东相邻处理 | 主空间权重矩阵 |
| `data_raw/spatial/spatial_weights_geo_distance.csv` | 地理距离倒数矩阵 | 根据省级行政中心经纬度计算 Haversine 球面距离，`weight = 1 / distance_km` | 稳健性检验 |
| `data_raw/spatial/spatial_weights_economic_distance.csv` | 经济距离倒数矩阵 | 以 2011-2022 年平均人均实际 GDP 差异作为经济距离，`weight = 1 / economic_distance` | 稳健性检验 |

三类矩阵的省份范围均与正式建模样本一致，即 2011-2022 年中国大陆 30 个省级地区，不含西藏、香港、澳门、台湾。原始权重文件均不进行行标准化，后续空间计量代码读取后再进行行标准化。

## 2. 地理距离矩阵数据来源

省级行政中心经纬度原始数据来自“最全中国各省份城市编码及经纬度 Excel 数据”资源。该资源说明其数据来源为高德地图网站公开数据，更新时间为 2023 年 3 月 31 日。本文仅提取正式样本 30 个省级地区的省级行政中心经纬度，用于构造地理距离空间权重矩阵。

原始文件归档为：

```text
data_raw/spatial/source_adcode_lng_lat_gaode_20230331.xlsx
```

整理后的坐标文件为：

```text
data_raw/spatial/province_capital_coordinates.csv
```

字段说明：

| 字段 | 含义 |
| --- | --- |
| `province` | 与 `panel_data.csv` 一致的省份简称 |
| `capital_city` | 省级行政中心或直辖市名称 |
| `source_name` | 原始经纬度表中的省级行政区名称 |
| `adcode` | 原始行政区划编码 |
| `longitude` | 经度 |
| `latitude` | 纬度 |
| `source` | 坐标来源说明 |

## 3. 经济距离矩阵口径

经济距离矩阵使用 `data_processed/panel_data.csv` 中的 `gdp_per_capita` 构造。具体做法是先计算每个省 2011-2022 年人均实际 GDP 的均值，再计算两省之间均值差异的绝对值：

```text
economic_distance_ij = abs(avg_gdp_per_capita_i - avg_gdp_per_capita_j)
weight_ij = 1 / (economic_distance_ij + 1e-6)
```

该矩阵衡量经济发展水平相近程度，权重越大表示两省人均实际 GDP 水平越接近。

## 4. 四大地区分组

区域异质性分析采用国家统计局常用的东部、中部、西部、东北四大地区划分。依据可引用国家统计局《第七次全国人口普查公报（第三号）》注释中的地区划分。由于本文正式样本不含西藏，西部地区在本文样本中相应剔除西藏。

地区分组文件为：

```text
data_raw/region_groups.csv
```

本文正式样本中的分组如下：

| 地区 | 省份 |
| --- | --- |
| 东部 | 北京、天津、河北、上海、江苏、浙江、福建、山东、广东、海南 |
| 中部 | 山西、安徽、江西、河南、湖北、湖南 |
| 西部 | 内蒙古、广西、重庆、四川、贵州、云南、陕西、甘肃、青海、宁夏、新疆 |
| 东北 | 辽宁、吉林、黑龙江 |

写作时可表述为：

```text
本文参照国家统计局四大地区划分口径，将正式样本省份划分为东部、中部、西部和东北地区。由于 CEADs 表观碳排放清单缺失西藏数据，本文正式样本不含西藏，因此西部地区样本不包括西藏。
```

