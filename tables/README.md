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
| `table01_descriptive_statistics.csv` | 核心变量描述性统计 | `code/02_descriptive_analysis.py` |
| `table02_correlation_matrix.csv` | 核心变量相关性矩阵 | `code/02_descriptive_analysis.py` |
| `table02a_high_correlation_pairs.csv` | 绝对相关系数不低于 0.8 的变量对 | `code/02_descriptive_analysis.py` |
| `table02b_vif_diagnostics.csv` | 控制变量 VIF 共线性诊断 | `code/02_descriptive_analysis.py` |
| `table03_baseline_regression.csv` | 基准回归系数表 | `code/03_baseline_model.py` |
| `table03_baseline_regression_summary.txt` | 基准回归完整文本摘要 | `code/03_baseline_model.py` |
| `table04_moran_i_by_year.csv` | 碳强度逐年 Moran's I 空间自相关检验 | `code/04_spatial_analysis.py` |
