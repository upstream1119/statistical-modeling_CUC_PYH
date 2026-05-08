# 数据可信度与变量处理说明

本文件用于支撑论文中的“数据来源、变量构造与处理过程”章节。冲击省一/国奖时，数据说明不能只是列来源，而要形成一条可复核的数据可信度证据链。

## 1. 样本范围

正式建模样本为 2011-2022 年中国大陆 30 个省级地区，共 360 条省份-年份观测。正式样本不含西藏、港澳台。

西藏剔除原因是 CEADs 表观碳排放清单未提供西藏地区数据，导致无法构造 `carbon_intensity` 和相关能源变量。项目保留 `data_processed/panel_data_with_tibet_audit.csv` 作为审计版数据，用于说明缺失来源，不进入正式建模。

## 2. 数据来源总览

| 数据类别 | 文件或来源 | 用途 |
| --- | --- | --- |
| 碳排放 | CEADs 表观碳排放清单 | 构造碳排放量和碳强度 |
| GDP 与人口 | 国家统计局省级数据 | 构造实际 GDP、人均实际 GDP、城镇化等 |
| GDP 指数 | 国家统计局地区生产总值指数 | 将现价 GDP 链式折算为 2011 年基期实际 GDP |
| 数字普惠金融 | 北京大学数字普惠金融指数 Provinces 表 | 构造 `digital_finance` |
| 能源消费 | CEADs 省级能源清单 | 构造煤炭相关终端能源消费占比 |
| 标准煤系数 | 《中国能源统计年鉴2022》附录4 | 将能源品种折算为标准煤 |
| 创新 | 分地区国内发明专利授权量 | 构造 `innovation` |
| 空间数据 | 省会经纬度、邻接关系、经济距离 | 构造三类空间权重矩阵 |

## 3. 核心变量构造

### 3.1 碳强度

碳强度为本文被解释变量：

$$
\text{carbon\_intensity}_{it} =
\frac{\text{carbon\_emissions\_mt}_{it} \times 100}{\text{gdp\_real}_{it}}
$$

其中，`carbon_emissions_mt` 单位为百万吨 CO2，乘以 100 后转换为万吨 CO2；`gdp_real` 为 2011 年基期实际 GDP，单位为亿元。因此，碳强度单位为“万吨 CO2 / 亿元实际 GDP”。

### 3.2 实际 GDP

使用国家统计局“地区生产总值指数（上年=100）”进行链式折算：

$$
\text{gdp\_real}_{i,2011} = \text{gdp\_nominal}_{i,2011}
$$

$$
\text{gdp\_real}_{i,t} =
\text{gdp\_real}_{i,t-1}
\times
\frac{\text{gdp\_index}_{i,t}}{100}
$$

该处理避免使用现价 GDP 直接计算碳强度所带来的价格因素干扰。

### 3.3 能源结构

能源结构定义为煤炭及煤炭加工相关终端能源消费折标准煤占总终端能源消费的比重：

$$
\text{energy\_structure} =
\frac{\text{coal\_related\_tce}}{\text{total\_energy\_tce}}
$$

煤炭相关能源字段包括：

`Raw_Coal`、`Cleaned_Coal`、`Other_Washed_Coal`、`Briquettes`、`Coke`、`Coke_Oven_Gas`、`Other_Coking_Products`。

论文中应表述为“煤炭及煤炭加工相关终端能源消费折标准煤占比”，不要表述为“原煤碳排放占比”。

### 3.4 创新水平

创新水平采用国内发明专利授权量的对数化形式：

$$
\text{innovation} = \ln(1 + \text{patent\_grants})
$$

该处理用于缓解专利授权量右偏分布和极端值影响。

### 3.5 控制变量

| 变量 | 公式 | 说明 |
| --- | --- | --- |
| `gdp_per_capita` | `gdp_real / population` | 人均实际 GDP |
| `industrial_structure` | `secondary_industry / gdp_nominal` | 第二产业增加值占现价 GDP 比重 |
| `urbanization` | `urban_population / population` | 城镇化水平 |
| `government_intervention` | `fiscal_expenditure / gdp_nominal` | 政府干预程度 |
| `innovation` | `ln(1 + patent_grants)` | 创新水平 |
| `energy_structure` | `coal_related_tce / total_energy_tce` | 煤炭依赖程度代理变量 |

## 4. 一致性审计

变量和矩阵一致性审计结果保存在 `tables/table00b_variable_consistency_audit.csv`。审计内容包括：

1. 碳强度公式是否与 `carbon_emissions_mt * 100 / gdp_real` 一致。
2. 实际 GDP 基期和链式折算是否正确。
3. 能源结构公式是否与折标准煤口径一致。
4. 创新变量是否与 `ln(1 + patent_grants)` 一致。
5. 三类空间权重矩阵是否与正式样本省份匹配。
6. 四大地区分组是否覆盖全部 30 个正式样本省份。

该审计是冲高奖时应主动展示的可信度证据。

## 5. 与冲奖主线的关系

数据口径服务于最终论文主线：空间依赖稳健存在，数字普惠金融低碳作用具有区域差异和空间结构依赖。

实际 GDP 处理提升碳强度指标严谨性；能源折标煤提升控制变量解释力；创新对数化提升模型稳定性；空间矩阵和地区分组审计支撑空间计量和异质性分析的可信度。论文应主动把这些处理写成“可复核的数据治理过程”，而不是简单附录。

## 6. 当前局限

当前数据仍需如实说明以下局限：

1. 西藏因核心碳排放数据缺失不进入正式样本。
2. 数字普惠金融使用省级综合指数，暂未展开覆盖广度、使用深度、数字化程度等分项机制。
3. 机制检验、政策分型和图表升级是冲击省一/国奖的下一步必做任务，未完成前不能写成既有结果。
