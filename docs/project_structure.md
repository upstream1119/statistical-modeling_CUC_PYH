# 项目结构与冲刺交付说明

本项目采用 GitHub 管理代码、数据接口和结果表，采用 Google Drive / OneDrive 管理论文正文与协作写作材料。当前阶段目标是冲击省一/国奖，因此项目结构服务于可复现、可解释和可交付。

## 1. 目录职责

| 目录 | 职责 |
| --- | --- |
| `code/` | 数据清洗、描述统计、基准回归、空间模型、稳健性、异质性、结果写作包脚本 |
| `data_raw/` | 原始数据和空间权重矩阵归档 |
| `data_processed/` | 正式建模面板数据和含西藏审计版数据 |
| `docs/` | 建模规格、数据说明、空间矩阵、文献写作和项目结构说明 |
| `tables/` | 所有可复现实证结果表 |
| `figures/` | 后续图表输出目录 |

## 2. 当前数据流

1. `code/01_data_cleaning.py` 读取 `data_raw/`，生成 `data_processed/panel_data.csv`。
2. `code/02_descriptive_analysis.py` 生成描述统计、相关性、VIF 和数据质量表。
3. `code/03_baseline_model.py` 生成基准回归结果。
4. `code/04_spatial_analysis.py` 生成 Moran's I 空间自相关检验。
5. `code/05_spatial_models.py` 生成 SAR、SEM、SDM 结果。
6. `code/06_robustness_checks.py` 生成普通稳健性检验。
7. `code/07_heterogeneity_analysis.py` 生成区域异质性结果。
8. `code/09_spatial_weight_robustness.py` 生成三类权重矩阵稳健性结果。
9. `code/10_empirical_findings_summary.py` 生成实证结果写作包。

## 3. 关键结果表

| 文件 | 用途 |
| --- | --- |
| `table00_data_quality_report.csv` | 样本量、年份、缺失值和重复键检查 |
| `table00b_variable_consistency_audit.csv` | 变量公式、实际 GDP、空间矩阵和地区分组审计 |
| `table03_baseline_regression.csv` | 基准回归 |
| `table04_moran_i_by_year.csv` | Moran's I 空间自相关 |
| `table05_spatial_model_comparison.csv` | SAR/SEM/SDM |
| `table08_heterogeneity_by_region.csv` | 区域异质性 |
| `table09_spatial_weight_robustness.csv` | 权重矩阵稳健性 |
| `table10_empirical_findings_summary.csv` | 论文写作总控 |

## 4. 冲奖版新增交付

现有实证主线基本完成，但冲击省一/国奖需要继续补以下交付：

1. 机制路径检验结果表。
2. 政策分型结果表。
3. 高质量图表，包括趋势图、Moran's I 图、区域异质性图、权重矩阵稳健性图和政策分型图。
4. Google Drive 中同步更新论文写作指南和数据口径白皮书。
5. 论文正文中使用统一谨慎口径，不夸大显著性。

## 5. 团队交付流

严欣浩负责确保 `data_raw/`、`data_processed/` 和数据说明文档一致。

彭意涵负责运行脚本、生成 `tables/` 和 `figures/`，并控制实证结论口径。

徐若诚负责从 `docs/`、`tables/` 和 Google Drive 写作指南中提取内容，写入论文正文。

每日同步时，三人只围绕三个问题汇报：数据口径是否有变、模型结果是否有新表、论文文字是否存在过度表述。

## 6. 当前正式复现命令

```bash
python code/01_data_cleaning.py
python code/02_descriptive_analysis.py
python code/03_baseline_model.py
python code/04_spatial_analysis.py
python code/05_spatial_models.py
python code/06_robustness_checks.py
python code/07_heterogeneity_analysis.py
python code/08_validate_variable_consistency.py
python code/09_spatial_weight_robustness.py
python code/10_empirical_findings_summary.py
```

## 7. 写作口径总原则

项目最终不是简单证明数字普惠金融在全国层面显著降碳，而是揭示低碳转型存在空间依赖，数字普惠金融作用具有区域差异和空间结构依赖。所有文档、表格和论文段落都必须服从这一主线。
