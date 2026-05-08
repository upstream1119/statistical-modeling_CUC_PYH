# 原始数据目录

本目录用于记录和存放项目原始数据。大型原始数据文件优先放在 OneDrive 共享文件夹，GitHub 中只保留来源说明或小型样例文件。

## 数据登记表

| 变量/数据集 | 年份范围 | 地区层级 | 单位 | 来源 | OneDrive 路径 | 处理说明 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 北京大学数字普惠金融指数 | 2011-2023/已确认 | 省级 | 指数 | 北京大学数字金融研究中心 | `data_raw/digital_finance/` | 作为 digital_finance，取省级综合指数 | 严欣浩 |
| 省级碳排放量 | 1997-2022/已确认 | 省级 | 百万吨/已确认 | CEADs 中国碳核算数据库 | `data_raw/carbon_emissions/` | 与 GDP 相除计算 carbon_intensity | 严欣浩 |
| 地区生产总值 GDP | 2011-2022/已确认 | 省级 | 亿元 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | 用于计算碳强度和人均 GDP | 严欣浩 |
| 地区生产总值指数 | 2011-2022/已确认 | 省级 | 上年=100 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | 以2011年为基期链式折算实际 GDP | 严欣浩 |
| 年末常住人口 | 2011-2022/已确认 | 省级 | 万人 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | GDP / 人口计算 gdp_per_capita | 严欣浩 |
| 第二产业增加值或第三产业增加值 | 2011-2022/已确认 | 省级 | 亿元 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | 用于计算 industrial_structure | 严欣浩 |
| 城镇人口或城镇化率 | 2011-2022/已确认 | 省级 | %/万人 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | 用于 urbanization | 严欣浩 |
| 地方财政支出 | 2011-2022/已确认 | 省级 | 亿元 | 国家统计局/中国统计年鉴 | `data_raw/nbs/` | 财政支出 / GDP 计算 government_intervention | 严欣浩 |
| 专利授权数 | 2011-2022/已确认 | 省级 | 件 | 国家知识产权局 | `data_raw/patents/` | 用于 innovation，后续可取 log(1+x) | 严欣浩 |
| 能源消费结构 | 2011-2022/已确认 | 省级 | 万吨标准煤/比重 | CEADs 省级能源清单、中国能源统计年鉴2022附录4 | `data_raw/energy/` | 按折标准煤参考系数折算，计算煤炭相关能源消费占总终端能源消费比重 | 严欣浩 |
| 省份邻接关系 | 固定 | 省级 | 0/1 权重 | 根据中国省级行政区接壤关系人工整理 | `data_raw/spatial_weights.csv` 和 `data_raw/spatial/` | 用于空间权重矩阵；正式建模样本为30个大陆省级地区，不含CEADs表观碳排放清单缺失的西藏；含西藏审计版见`data_raw/spatial_weights_with_tibet_audit.csv`；海南按与广东相邻处理，后续模型中再行标准化 | 严欣浩 |
| 省级行政中心经纬度 | 固定 | 省级 | 经度/纬度 | 高德地图公开数据，经 CSDN/GitCode 资源整理，更新时间2023-03-31 | `data_raw/spatial/source_adcode_lng_lat_gaode_20230331.xlsx` | 用于构造省级行政中心地理距离倒数矩阵 | 严欣浩 |
| 经济距离权重矩阵 | 2011-2022/已确认 | 省级 | 权重 | 根据 `panel_data.csv` 中人均实际 GDP 计算 | `data_raw/spatial/spatial_weights_economic_distance.csv` | 使用2011-2022年平均人均实际GDP差异的倒数构造 | 严欣浩 |
| 四大地区分组 | 固定 | 省级 | 东部/中部/西部/东北 | 国家统计局常用四大地区划分 | `data_raw/region_groups.csv` | 用于后续区域异质性分析；正式样本不含西藏 | 严欣浩 |


## 数据收集要求

1. 每个数据源必须记录下载时间、来源链接或数据库名称。
2. 省份名称、年份范围、单位口径必须写清楚。
3. 如果数据经过换算、取对数、缩尾或插值，需要在处理说明中记录。
4. 不要直接上传无法确认授权的大型商业数据库文件。

## 读取路径规则

1. 正式建模优先读取根目录中的 `data_raw/spatial_weights.csv`。
2. `data_raw/spatial/` 用作空间权重矩阵归档副本，保留严欣浩上传的原始整理结果。
3. 原始数据按来源分目录归档：
   - `data_raw/carbon_emissions/`
   - `data_raw/digital_finance/`
   - `data_raw/energy/`
   - `data_raw/nbs/`
   - `data_raw/patents/`
   - `data_raw/spatial/`
   - `data_raw/region_groups.csv`
4. 后续如果新增数据源，应先放入对应来源目录，再同步更新本 README 的数据登记表。
