# 图表图片目录

本目录用于存放论文使用的图片。

## 命名规则

| 文件名示例 | 内容 |
| --- | --- |
| `fig01_trend_carbon_intensity.png` | 碳强度趋势图 |
| `fig02_moran_scatter.png` | Moran 散点图 |
| `fig03_spatial_distribution.png` | 空间分布图 |

## 使用要求

1. 图片应由 `code/` 中脚本生成，避免手工复制导致无法复现。
2. 正式论文图片内部不放标题，图名由论文正文图注单独给出，例如：`图1  研究框架与技术路线图`。
3. 图片进入论文前，需要检查坐标轴、图例、单位和中文显示。
4. 结果图采用白底、细网格、必要图例和 300 dpi 输出，便于插入 Word 正文。

## 当前论文图表

| 文件名 | 内容 | 生成脚本 |
| --- | --- | --- |
| `figure01_carbon_intensity_trend.png` | 全国平均碳强度年度趋势 | `code/13_generate_figures.py` |
| `figure02_digital_finance_trend.png` | 全国平均数字普惠金融指数年度趋势 | `code/13_generate_figures.py` |
| `figure03_moran_i_trend.png` | 碳强度 Moran's I 年度变化 | `code/13_generate_figures.py` |
| `figure04_regional_heterogeneity_coefficients.png` | 数字普惠金融影响的区域异质性系数 | `code/13_generate_figures.py` |
| `figure05_spatial_weight_robustness.png` | 不同空间权重矩阵下的空间滞后项对比 | `code/13_generate_figures.py` |
| `figure06_policy_typology_quadrant.png` | 省份数字金融-碳强度政策分型象限图 | `code/13_generate_figures.py` |

## 研究框架图

| 文件名 | 内容 | 生成脚本 | 论文用途 |
| --- | --- | --- | --- |
| `figure00_research_framework.png` | 研究框架与技术路线图 | `code/14_generate_research_framework.py` | 建议放在引言末尾或模型设定开头 |
