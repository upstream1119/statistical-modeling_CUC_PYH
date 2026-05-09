# 结果表复现说明

本文档用于说明 `tables/` 中主要结果表与生成脚本的对应关系，便于论文写作、代码包整理和后续省赛复核。

## 1. 数据清洗与基础诊断

| 结果文件 | 生成脚本 | 说明 |
| --- | --- | --- |
| `data_processed/panel_data.csv` | `code/01_data_cleaning.py` | 正式建模面板数据，样本为 2011-2022 年中国大陆 30 个省级地区。 |
| `data_processed/panel_data_with_tibet_audit.csv` | `code/01_data_cleaning.py` | 含西藏审计版数据，仅用于说明缺失原因，不进入正式建模。 |
| `tables/table00_data_quality_report.csv` | `code/02_descriptive_analysis.py` | 数据规模、缺失值和重复观测检查。 |
| `tables/table00b_variable_consistency_audit.csv` | `code/08_validate_variable_consistency.py` | 变量公式、实际 GDP 折算、空间矩阵和地区分组一致性审计。 |

## 2. 描述统计、基准回归与空间模型

| 结果文件 | 生成脚本 | 说明 |
| --- | --- | --- |
| `tables/table01_descriptive_statistics.csv` | `code/02_descriptive_analysis.py` | 主要变量描述性统计。 |
| `tables/table02_correlation_matrix.csv` | `code/02_descriptive_analysis.py` | 主要变量相关系数矩阵。 |
| `tables/table02a_high_correlation_pairs.csv` | `code/02_descriptive_analysis.py` | 高相关变量对提示。 |
| `tables/table02b_vif_diagnostics.csv` | `code/02_descriptive_analysis.py` | 多重共线性 VIF 诊断。 |
| `tables/table03_baseline_regression.csv` | `code/03_baseline_model.py` | 加入年份固定效应的面板基准回归结果，采用 HC1 稳健标准误。 |
| `tables/table03_baseline_regression_summary.txt` | `code/03_baseline_model.py` | 基准回归文本摘要。 |
| `tables/table04_moran_i_by_year.csv` | `code/04_spatial_analysis.py` | 逐年 Moran's I 空间自相关检验。 |
| `tables/table05_spatial_model_comparison.csv` | `code/05_spatial_models.py` | SAR、SEM、SDM 空间计量模型比较。 |
| `tables/table06_spatial_effect_decomposition.csv` | `code/05_spatial_models.py` | 空间模型效应分解辅助表。 |

注意：`code/04_spatial_analysis.py` 只负责 Moran's I，不生成 SAR、SEM、SDM；空间模型结果由 `code/05_spatial_models.py` 生成。论文中不要把基准模型写成严格双向固定效应模型。

## 3. 拓展分析与写作总览

| 结果文件 | 生成脚本 | 说明 |
| --- | --- | --- |
| `tables/table07_robustness_checks.csv` | `code/06_robustness_checks.py` | 普通稳健性检验。 |
| `tables/table08_heterogeneity_by_region.csv` | `code/07_heterogeneity_analysis.py` | 东部、中部、西部、东北区域异质性分析。 |
| `tables/table09_spatial_weight_robustness.csv` | `code/09_spatial_weight_robustness.py` | 邻接矩阵、地理距离矩阵、经济距离矩阵下的空间模型稳健性对比。 |
| `tables/table10_empirical_findings_summary.csv` | `code/10_empirical_findings_summary.py` | 面向论文写作的实证发现总览。 |
| `tables/table11_mechanism_tests.csv` | `code/11_mechanism_tests.py` | 技术创新、产业结构、能源结构机制路径检验。 |
| `tables/table12_policy_typology.csv` | `code/12_policy_typology.py` | 基于数字普惠金融水平与碳强度压力的四象限政策分型。 |

机制检验只能写为路径线索，不能写成严格因果中介效应。政策分型是四象限应用分类，不能写成 TOPSIS 或 K-means。

## 4. 论文图件

| 图件文件 | 生成脚本 | 说明 |
| --- | --- | --- |
| `figures/figure00_research_framework.png` | `code/14_generate_research_framework.py` | 研究框架与技术路线图。 |
| `figures/figure01_carbon_intensity_trend.png` | `code/13_generate_figures.py` | 省域平均碳强度变化趋势。 |
| `figures/figure02_digital_finance_trend.png` | `code/13_generate_figures.py` | 数字普惠金融发展水平变化趋势。 |
| `figures/figure03_moran_i_trend.png` | `code/13_generate_figures.py` | Moran's I 年度变化趋势。 |
| `figures/figure04_regional_heterogeneity_coefficients.png` | `code/13_generate_figures.py` | 区域异质性系数比较。 |
| `figures/figure05_spatial_weight_robustness.png` | `code/13_generate_figures.py` | 不同空间权重矩阵下的空间滞后项比较。 |
| `figures/figure06_policy_typology_quadrant.png` | `code/13_generate_figures.py` | 数字普惠金融水平与碳强度压力政策分型。 |

正式论文图片内部不放标题，图名由正文图注单独给出。
