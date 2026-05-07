# 建模规格说明

本文档用于统一三人协作中的变量口径、数据交付格式、模型路线和结果交付接口。

## 变量清单

| 类型 | 字段名 | 中文含义 | 建议口径 | 负责人 |
| --- | --- | --- | --- | --- |
| 被解释变量 | `carbon_intensity` | 碳强度 | 碳排放量 / GDP，或单位 GDP 碳排放 | 严欣浩 |
| 核心解释变量 | `digital_finance` | 数字普惠金融指数 | 北京大学数字普惠金融总指数 | 严欣浩 |
| 控制变量 | `gdp_per_capita` | 人均 GDP | 地区生产总值 / 常住人口，建议后续取对数 | 严欣浩 |
| 控制变量 | `industrial_structure` | 产业结构 | 第二产业增加值 / GDP，或第三产业占比 | 严欣浩 |
| 控制变量 | `urbanization` | 城镇化率 | 城镇人口 / 总人口 | 严欣浩 |
| 控制变量 | `government_intervention` | 政府干预 | 财政支出 / GDP | 严欣浩 |
| 控制变量 | `innovation` | 创新水平 | 专利授权数或绿色专利数，建议后续取对数 | 严欣浩 |
| 控制变量 | `energy_structure` | 能源结构 | 煤炭消费占比、能源消费强度或可获得的近似指标 | 严欣浩 |

## 面板数据交付格式

严欣浩需要交付 `data_processed/panel_data.csv`，至少包含以下字段：

```text
province, year, carbon_intensity, digital_finance, gdp_per_capita,
industrial_structure, urbanization, government_intervention,
innovation, energy_structure
```

要求：

1. 每一行代表一个省份-年份观测值。
2. 省份名称统一使用中文简称，例如 `北京`、`天津`、`河北`。
3. 年份范围尽量保持所有变量一致。
4. 每个变量必须记录来源、单位、处理方式和缺失值情况。

## 空间权重矩阵交付格式

优先交付 `data_raw/spatial_weights.csv`：

```text
province_i, province_j, weight
```

如果暂时无法给出权重值，先交邻接关系表：

```text
province, neighbor_province
```

要求：

1. 省份名称必须和 `panel_data.csv` 中的 `province` 完全一致。
2. 权重矩阵需要说明来源和构造方法，例如邻接矩阵、地理距离矩阵或经济距离矩阵。
3. 第一版可以先用邻接矩阵，后续再用其他矩阵做稳健性检验。

## 模型路线

1. 描述统计：均值、标准差、最小值、最大值。
2. 相关性分析：观察变量方向和多重共线性风险。
3. 基准回归：`carbon_intensity` 对 `digital_finance` 和控制变量回归，加入年份固定效应。
4. 空间相关性检验：计算全局 Moran's I。
5. 空间计量模型：优先考虑 SDM，备选 SAR/SEM。
6. 稳健性检验：更换空间权重矩阵、替换变量口径或使用滞后一期核心解释变量。
7. 异质性分析：优先东中西部，时间允许再扩展。

## 三人协作接口

### 严欣浩

交付数据和变量来源说明：

- `data_processed/panel_data.csv`
- `data_raw/spatial_weights.csv` 或邻接关系表
- 变量来源、年份、单位、处理说明

### 你

负责运行代码和解释结果：

```bash
python code/01_data_cleaning.py
python code/02_descriptive_analysis.py
python code/03_baseline_model.py
python code/04_spatial_analysis.py
```

运行后把 `tables/` 和 `figures/` 中可进入论文的结果发给徐若诚，并说明每张表或图的含义。

### 徐若诚

先完成不依赖模型结果的文字部分：

- 研究背景
- 文献综述，至少 5 篇核心文献
- 机制分析
- 变量说明初稿
- 模型设定初稿

等 `tables/` 和 `figures/` 产出后，再补写实证结果分析。
