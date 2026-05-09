# 统计建模大赛项目仓库

本仓库用于同步 2026 年第十二届全国大学生统计建模大赛项目的代码、数据说明、图表和结果表。

论文正文、报名表、承诺书、AI 工具使用情况表等正式文档优先放在 OneDrive 共享文件夹中协同编辑；本仓库主要保证数据分析过程可复现。

## 研究题目

数字普惠金融驱动区域低碳转型的空间溢出效应与政策优化研究——基于中国省级面板数据的分析

## 成员分工

| 成员 | 主要职责 | 交付物 |
| --- | --- | --- |
| 彭意涵 | 建模、实验、结果解释、论文口径终审 | 建模代码、回归结果、空间检验、结果解释 |
| 严欣浩 | 数据收集、变量整理、数据清洗 | 原始数据来源、清洗后数据、变量说明 |
| 徐若诚 | 文献、论文写作、材料整理 | 参考文献、论文初稿、AI 工具表、图表清单 |

## 目录说明

| 目录 | 用途 |
| --- | --- |
| `data_raw/` | 原始数据来源说明和小型原始数据样例。大型原始文件放 OneDrive。 |
| `data_processed/` | 清洗后的建模数据，例如 `panel_data.csv`。 |
| `code/` | 数据清洗、描述统计、基准回归、空间模型、机制检验、政策分型和图表生成代码。 |
| `figures/` | 论文使用的图片输出，包括研究框架图和实证结果图。 |
| `tables/` | 数据质量、描述统计、回归、空间模型、机制检验和政策分型结果表。 |
| `docs/` | 建模规格、变量说明、复现说明和论文修改清单。 |

## 推荐运行顺序

```bash
python code/01_data_cleaning.py
python code/02_descriptive_analysis.py
python code/03_baseline_model.py
python code/04_spatial_analysis.py
python code/05_spatial_models.py
python code/06_robustness_checks.py
python code/07_heterogeneity_analysis.py
python code/09_spatial_weight_robustness.py
python code/10_empirical_findings_summary.py
python code/11_mechanism_tests.py
python code/12_policy_typology.py
python code/13_generate_figures.py
python code/14_generate_research_framework.py
```

说明：`04_spatial_analysis.py` 只生成逐年 Moran's I 空间自相关检验；SAR、SEM、SDM 结果由 `05_spatial_models.py` 生成。机制检验、四象限政策分型和论文图件分别由 `11`、`12`、`13`、`14` 号脚本生成。更多表格复现关系见 `docs/result_table_reproduction_note.md`。

## 预设建模数据字段

`data_processed/panel_data.csv` 建议至少包含以下字段：

| 字段 | 含义 |
| --- | --- |
| `province` | 省份名称 |
| `year` | 年份 |
| `carbon_intensity` | 碳强度，作为被解释变量 |
| `digital_finance` | 数字普惠金融指数 |
| `gdp_per_capita` | 人均 GDP |
| `industrial_structure` | 产业结构 |
| `urbanization` | 城镇化率 |
| `government_intervention` | 政府干预程度 |
| `innovation` | 科技创新水平 |
| `energy_structure` | 能源结构 |

## 协作规则

1. 数据来源必须记录清楚，包含来源、年份、地区层级、单位和处理方式。
2. 真实原始数据如果较大，不直接提交到 GitHub，优先放 OneDrive，并在 `data_raw/README.md` 记录路径。
3. 每次导出论文图表时，同时保存源表或生成脚本，避免后期无法复现。
4. 回归结果进入论文前，需要确认变量口径、样本范围和模型设定一致。
5. AI 工具只用于结构梳理、语言润色、代码排错和材料检查，核心数据处理与实证结论必须人工核验。
