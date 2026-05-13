# 统计建模大赛项目仓库

本仓库用于同步 2026 年第十二届全国大学生统计建模大赛项目的代码、数据说明、图表和结果表。

论文正文、报名表、承诺书、AI 工具使用情况表等正式文档优先放在 OneDrive 共享文件夹中协同编辑；本仓库主要保证数据分析过程可复现。

## 研究题目

数字普惠金融驱动区域低碳转型的空间溢出效应与政策优化研究——基于中国省级面板数据的分析

## 省赛复现说明入口

本仓库的核心用途是保证论文数据分析过程可复现。评审或复核时建议优先阅读：

- `docs/key_code_reproduction_guide.md`：数据分析关键代码说明。
- `docs/result_table_reproduction_note.md`：结果表与生成脚本对应关系。
- `docs/data_source_variable_processing.md`：数据来源、变量构造与处理说明。
- `docs/spatial_weights_and_region_groups.md`：空间权重矩阵与区域分组说明。

## 运行环境

建议使用 Python 3.10 或兼容版本，在仓库根目录运行脚本。依赖包记录在 `requirements.txt`，包括 `pandas`、`numpy`、`statsmodels`、`openpyxl`、`libpysal`、`esda` 和 `spreg`。

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

## 主要脚本与输出结果

| 脚本 | 主要作用 | 主要输出 |
| --- | --- | --- |
| `01_data_cleaning.py` | 数据清洗与变量构造 | `data_processed/panel_data.csv`；`data_processed/panel_data_with_tibet_audit.csv` |
| `02_descriptive_analysis.py` | 数据质量、描述统计、相关性、VIF | `table00`、`table01`、`table02`、`table02a`、`table02b` |
| `03_baseline_model.py` | 年份固定效应基准回归 | `table03_baseline_regression.csv` |
| `04_spatial_analysis.py` | Moran's I 空间自相关检验 | `table04_moran_i_by_year.csv` |
| `05_spatial_models.py` | SAR / SEM / SDM 空间模型 | `table05_spatial_model_comparison.csv`；`table06_spatial_effect_decomposition.csv` |
| `06_robustness_checks.py` | 普通稳健性检验 | `table07_robustness_checks.csv` |
| `07_heterogeneity_analysis.py` | 区域异质性分析 | `table08_heterogeneity_by_region.csv` |
| `09_spatial_weight_robustness.py` | 空间权重矩阵稳健性 | `table09_spatial_weight_robustness.csv` |
| `10_empirical_findings_summary.py` | 实证发现与写作口径总览 | `table10_empirical_findings_summary.csv` |
| `11_mechanism_tests.py` | 机制路径检验 | `table11_mechanism_tests.csv` |
| `12_policy_typology.py` | 四象限政策分型 | `table12_policy_typology.csv` |
| `13_generate_figures.py` | 论文结果图生成 | `figure01`—`figure06` |
| `14_generate_research_framework.py` | 研究框架图生成 | `figure00_research_framework.png` |

完整关键代码复现说明见 `docs/key_code_reproduction_guide.md`。

## 论文表图复现关系

| 论文表号 | 内容 | 对应结果文件 | 生成脚本 |
| --- | --- | --- | --- |
| 表1 | 描述性统计 | `tables/table01_descriptive_statistics.csv` | `code/02_descriptive_analysis.py` |
| 表2 | 相关性分析 | `tables/table02_correlation_matrix.csv` | `code/02_descriptive_analysis.py` |
| 表3 | VIF 诊断 | `tables/table02b_vif_diagnostics.csv` | `code/02_descriptive_analysis.py` |
| 表4 | 基准回归 | `tables/table03_baseline_regression.csv` | `code/03_baseline_model.py` |
| 表5 | Moran's I 空间自相关检验 | `tables/table04_moran_i_by_year.csv` | `code/04_spatial_analysis.py` |
| 表6 | 空间计量模型比较 | `tables/table05_spatial_model_comparison.csv` | `code/05_spatial_models.py` |
| 表7 | 空间权重矩阵稳健性 | `tables/table09_spatial_weight_robustness.csv` | `code/09_spatial_weight_robustness.py` |
| 表8 | 区域异质性 | `tables/table08_heterogeneity_by_region.csv` | `code/07_heterogeneity_analysis.py` |
| 表9 | 机制路径检验 | `tables/table11_mechanism_tests.csv` | `code/11_mechanism_tests.py` |
| 表10 | 政策分型 | `tables/table12_policy_typology.csv` | `code/12_policy_typology.py` |

| 论文图号 | 内容 | 对应图件文件 | 生成脚本 |
| --- | --- | --- | --- |
| 图1 | 研究框架与技术路线图 | `figures/figure00_research_framework.png` | `code/14_generate_research_framework.py` |
| 图2 | 碳强度趋势 | `figures/figure01_carbon_intensity_trend.png` | `code/13_generate_figures.py` |
| 图3 | 数字普惠金融趋势 | `figures/figure02_digital_finance_trend.png` | `code/13_generate_figures.py` |
| 图4 | Moran's I 年度变化 | `figures/figure03_moran_i_trend.png` | `code/13_generate_figures.py` |
| 图5 | 区域异质性 | `figures/figure04_regional_heterogeneity_coefficients.png` | `code/13_generate_figures.py` |
| 图6 | 空间权重矩阵稳健性 | `figures/figure05_spatial_weight_robustness.png` | `code/13_generate_figures.py` |
| 图7 | 政策分型 | `figures/figure06_policy_typology_quadrant.png` | `code/13_generate_figures.py` |

写作时需要注意：基准回归写为“加入年份固定效应的面板基准回归模型”；Moran's I 说明碳强度存在空间自相关，不能直接写成数字普惠金融空间溢出显著；机制检验只能写为路径线索；政策分型是四象限应用分类，不是 TOPSIS 或 K-means。

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
