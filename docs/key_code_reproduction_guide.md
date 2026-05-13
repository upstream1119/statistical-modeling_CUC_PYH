# 数据分析关键代码说明

本文档用于说明论文主要数据分析结果如何由项目代码复现，重点回应“缺少数据分析结果的关键性代码”这一反馈。本文档不是论文正文，而是提交代码包和 GitHub 仓库中的复现说明。

## 1. 复现目标与样本口径

- 研究题目：数字普惠金融驱动区域低碳转型的空间溢出效应与政策优化研究——基于中国省级面板数据的分析。
- 正式样本：2011-2022 年中国大陆 30 个省级地区，共 360 条省份-年份观测。
- 正式建模数据：`data_processed/panel_data.csv`。
- 审计追溯数据：`data_processed/panel_data_with_tibet_audit.csv`。
- 西藏剔除原因：CEADs 表观碳排放清单未提供西藏地区省级表观碳排放数据，无法构造核心被解释变量 `carbon_intensity`，因此正式建模样本不含西藏、港澳台。

核心复现目标是说明论文中的描述统计、基准回归、空间自相关检验、空间计量模型、稳健性检验、区域异质性、机制路径检验、政策分型和图件均可由 `code/` 目录下脚本生成。

## 2. 运行环境与依赖

建议使用 Python 3.10 或兼容版本。依赖包记录在 `requirements.txt`，主要包括：

```text
pandas
numpy
statsmodels
openpyxl
libpysal
esda
spreg
```

安装依赖后，在仓库根目录执行脚本。当前仓库没有封装一键运行脚本，建议按下方顺序逐步运行，便于检查每一步输出。

## 3. 推荐运行顺序

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

说明：`code/04_spatial_analysis.py` 只生成逐年 Moran's I 空间自相关检验；SAR、SEM、SDM 空间计量模型结果由 `code/05_spatial_models.py` 生成。空间权重矩阵稳健性由 `code/09_spatial_weight_robustness.py` 生成。

## 4. 关键代码模块说明

| 模块 | 脚本 | 输入 | 关键逻辑 | 主要输出 |
| --- | --- | --- | --- | --- |
| 数据清洗与变量构造 | `code/01_data_cleaning.py` | `data_raw/` 原始数据 | 合并省级面板数据，构造碳强度、实际 GDP、能源结构、创新变量，并保留含西藏审计版数据 | `data_processed/panel_data.csv`；`data_processed/panel_data_with_tibet_audit.csv` |
| 描述统计与相关性 | `code/02_descriptive_analysis.py` | `data_processed/panel_data.csv` | 生成数据质量报告、描述统计、相关矩阵、高相关变量对和 VIF 诊断 | `table00`、`table01`、`table02`、`table02a`、`table02b` |
| 基准回归 | `code/03_baseline_model.py` | `data_processed/panel_data.csv` | 估计加入年份固定效应的基准回归，并采用 HC1 稳健标准误 | `table03_baseline_regression.csv`；`table03_baseline_regression_summary.txt` |
| 空间自相关 | `code/04_spatial_analysis.py` | `panel_data.csv`；`data_raw/spatial_weights.csv` | 使用邻接矩阵逐年计算碳强度 Moran's I | `table04_moran_i_by_year.csv` |
| 空间计量模型 | `code/05_spatial_models.py` | `panel_data.csv`；`data_raw/spatial_weights.csv` | 估计 SAR、SEM、SDM，并输出模型比较和 SDM 空间滞后项 | `table05_spatial_model_comparison.csv`；`table06_spatial_effect_decomposition.csv` |
| 普通稳健性 | `code/06_robustness_checks.py` | `panel_data.csv` | 进行滞后项、变量变换、控制变量调整等普通稳健性检查 | `table07_robustness_checks.csv` |
| 区域异质性 | `code/07_heterogeneity_analysis.py` | `panel_data.csv`；`data_raw/region_groups.csv` | 按东部、中部、西部、东北四大地区分组回归 | `table08_heterogeneity_by_region.csv` |
| 变量一致性审计 | `code/08_validate_variable_consistency.py` | `panel_data.csv`；空间矩阵；地区分组 | 审计变量公式、实际 GDP 折算、空间权重矩阵和地区分组是否一致 | `table00b_variable_consistency_audit.csv` |
| 空间权重稳健性 | `code/09_spatial_weight_robustness.py` | 邻接矩阵、地理距离矩阵、经济距离矩阵 | 比较不同空间权重矩阵下的 SAR、SEM、SDM 关键结果 | `table09_spatial_weight_robustness.csv` |
| 实证发现总览 | `code/10_empirical_findings_summary.py` | `tables/` 中主要结果表 | 汇总可写结论、关键统计量和禁止表述 | `table10_empirical_findings_summary.csv` |
| 机制路径检验 | `code/11_mechanism_tests.py` | `panel_data.csv` | 围绕技术创新、产业结构、能源结构进行机制路径检验 | `table11_mechanism_tests.csv` |
| 政策分型 | `code/12_policy_typology.py` | `panel_data.csv`；`region_groups.csv` | 基于数字普惠金融均值和碳强度均值进行四象限政策分型 | `table12_policy_typology.csv` |
| 结果图生成 | `code/13_generate_figures.py` | `panel_data.csv`；`tables/` 结果表 | 生成碳强度趋势、数字金融趋势、Moran's I、异质性、权重稳健性和政策分型图 | `figure01`-`figure06` |
| 研究框架图 | `code/14_generate_research_framework.py` | 脚本内图形结构设定 | 生成研究框架与技术路线图 | `figure00_research_framework.png` |

## 5. 论文表格与代码对应关系

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

补充说明：`tables/table00_data_quality_report.csv` 和 `tables/table00b_variable_consistency_audit.csv` 可用于支撑数据质量、变量公式和空间矩阵一致性说明；`tables/table10_empirical_findings_summary.csv` 是面向论文写作的结果口径总览，不建议直接作为正文实证结果表。

## 6. 论文图件与代码对应关系

| 论文图号 | 内容 | 对应图件文件 | 生成脚本 |
| --- | --- | --- | --- |
| 图1 | 研究框架与技术路线图 | `figures/figure00_research_framework.png` | `code/14_generate_research_framework.py` |
| 图2 | 碳强度趋势 | `figures/figure01_carbon_intensity_trend.png` | `code/13_generate_figures.py` |
| 图3 | 数字普惠金融趋势 | `figures/figure02_digital_finance_trend.png` | `code/13_generate_figures.py` |
| 图4 | Moran's I 年度变化 | `figures/figure03_moran_i_trend.png` | `code/13_generate_figures.py` |
| 图5 | 区域异质性 | `figures/figure04_regional_heterogeneity_coefficients.png` | `code/13_generate_figures.py` |
| 图6 | 空间权重矩阵稳健性 | `figures/figure05_spatial_weight_robustness.png` | `code/13_generate_figures.py` |
| 图7 | 政策分型 | `figures/figure06_policy_typology_quadrant.png` | `code/13_generate_figures.py` |

## 7. 关键代码逻辑与论文口径

以下口径用于保证代码、结果表和论文解释一致：

- `code/03_baseline_model.py` 的基准模型为“加入年份固定效应的面板基准回归模型”，采用 HC1 稳健标准误；论文中不要写成严格双向固定效应模型。
- `code/04_spatial_analysis.py` 的 Moran's I 检验对象是碳强度，结论是碳强度存在空间正相关；不能写成 Moran's I 证明数字普惠金融具有显著空间溢出。
- `code/05_spatial_models.py` 中 SDM 的 `W_digital_finance` 为负但未通过常规显著性检验，只能写为空间负向线索。
- `code/09_spatial_weight_robustness.py` 显示地理距离矩阵下存在边际负向线索，但经济距离矩阵不支持低碳外溢；因此不能写成空间溢出稳健显著。
- `code/11_mechanism_tests.py` 只能支持机制路径线索，不能写成严格因果中介效应成立。
- `code/12_policy_typology.py` 是四象限政策分型，不是 TOPSIS、K-means 或因果识别模型。

## 8. 给论文附录 B 的写作接口

论文附录 B 可直接命名为“主要代码与复现流程说明”。建议写成“文字说明 + 附录表 B1”的形式，重点说明各代码模块与论文表图的对应关系，不需要粘贴整段源代码。

建议附录 B 包含以下内容：

```markdown
### 附录B 主要代码与复现流程说明

本文主要实证结果由 Python 脚本复现。数据处理流程包括原始数据清洗、变量构造、省份—年份面板合并、空间权重矩阵构建、描述性统计、基准回归、空间自相关检验、空间计量模型估计、机制路径检验、政策分型和论文图件生成。各部分代码与结果文件对应关系见附录表 B1。
```

附录表 B1 建议使用本文档第 4-6 节内容压缩整理。附录中应避免新增未完成方法，不写 TOPSIS、K-means、双向固定效应，也不把机制检验写成严格中介效应。
