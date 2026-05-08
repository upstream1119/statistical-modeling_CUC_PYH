# 结果表目录

本目录用于存放论文中的描述统计表、相关性表和模型结果表。

## 命名规则

| 文件名示例 | 内容 |
| --- | --- |
| `table01_descriptive_statistics.csv` | 描述统计表 |
| `table02_correlation_matrix.csv` | 相关性矩阵 |
| `table03_baseline_regression.csv` | 基准回归结果 |
| `table04_spatial_model.csv` | 空间模型结果 |

## 使用要求

1. 结果表应由脚本导出，必要时再在 Word 中做格式美化。
2. 表格进入论文前，要确认变量名、样本量、显著性标记和模型设定。
3. 论文表名格式建议为：`表1  变量描述性统计`。

## 当前结果表

| 文件名 | 内容 | 生成脚本 |
| --- | --- | --- |
| `table00_data_quality_report.csv` | 面板样本量、年份范围、缺失值和重复键检查 | `code/02_descriptive_analysis.py` |
| `table00b_variable_consistency_audit.csv` | 变量公式、实际 GDP 折算、空间矩阵和地区分组一致性审计 | `code/08_validate_variable_consistency.py` |
| `table01_descriptive_statistics.csv` | 核心变量描述性统计 | `code/02_descriptive_analysis.py` |
| `table02_correlation_matrix.csv` | 核心变量相关性矩阵 | `code/02_descriptive_analysis.py` |
| `table02a_high_correlation_pairs.csv` | 绝对相关系数不低于 0.8 的变量对 | `code/02_descriptive_analysis.py` |
| `table02b_vif_diagnostics.csv` | 控制变量 VIF 共线性诊断 | `code/02_descriptive_analysis.py` |
| `table03_baseline_regression.csv` | 基准回归系数表 | `code/03_baseline_model.py` |
| `table03_baseline_regression_summary.txt` | 基准回归完整文本摘要 | `code/03_baseline_model.py` |
| `table04_moran_i_by_year.csv` | 碳强度逐年 Moran's I 空间自相关检验 | `code/04_spatial_analysis.py` |

## Spatial Models and Robustness Tables

- `table05_spatial_model_comparison.csv`: SAR, SEM, and SDM coefficient comparison. The SDM result is the main reference for spatial spillover discussion.
- `table06_spatial_effect_decomposition.csv`: first-pass SDM local coefficient and spatial-lag coefficient table. Use `W_digital_finance` as the key spillover term.
- `table07_robustness_checks.csv`: baseline robustness checks, including lagged digital finance, transformed innovation, removing urbanization, and log GDP per capita.

## Regional Heterogeneity

- `table08_heterogeneity_by_region.csv`: regional OLS heterogeneity results for East, Central, West, and Northeast China. Use this table to discuss whether the digital finance effect differs across regions.
- `table09_spatial_weight_robustness.csv`: compares key SAR, SEM, and SDM coefficients under adjacency, geographic-distance, and economic-distance spatial weights.
- `table10_empirical_findings_summary.csv`: writing-oriented empirical findings package. It maps each result table to the paper section, approved interpretation, and prohibited wording.
- `table11_mechanism_tests.csv`: mechanism-path checks for innovation, industrial structure, and energy structure. Use as pathway evidence, not strict causal mediation.
- `table12_policy_typology.csv`: province-level policy typology based on digital finance and carbon intensity medians. Use for differentiated policy recommendations.
