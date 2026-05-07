# 统计建模大赛项目仓库

本仓库用于同步 2026 年第十二届全国大学生统计建模大赛项目的代码、数据说明、图表和结果表。

论文正文、报名表、承诺书、AI 工具使用情况表等正式文档优先放在 OneDrive 共享文件夹中协同编辑；本仓库主要保证数据分析过程可复现。

## 研究题目

数字普惠金融驱动区域低碳转型的空间溢出效应与政策优化研究

## 成员分工

| 成员 | 主要职责 | 交付物 |
| --- | --- | --- |
| 你 | 建模、实验、结果解释 | 建模代码、回归结果、空间检验、结果解释 |
| 严欣浩 | 数据收集、变量整理、数据清洗 | 原始数据来源、清洗后数据、变量说明 |
| 徐若诚 | 文献、论文写作、材料整理 | 参考文献、论文初稿、AI 工具表、图表清单 |

## 目录说明

| 目录 | 用途 |
| --- | --- |
| `data_raw/` | 原始数据来源说明和小型原始数据样例。大型原始文件放 OneDrive。 |
| `data_processed/` | 清洗后的建模数据，例如 `panel_data.csv`。 |
| `code/` | 数据清洗、描述统计、基准回归、空间分析代码。 |
| `figures/` | 论文使用的图片输出。 |
| `tables/` | 描述统计表、相关性表、回归结果表。 |

## 推荐运行顺序

```bash
python code/01_data_cleaning.py
python code/02_descriptive_analysis.py
python code/03_baseline_model.py
python code/04_spatial_analysis.py
```

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
