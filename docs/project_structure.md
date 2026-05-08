# 项目目录结构说明

本文档说明当前仓库的目录职责和数据流，用于三人协作和结果复现。

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `code/` | 数据清洗、描述统计、基准回归、空间自相关检验等可复现脚本 |
| `data_raw/` | 原始数据归档、空间权重矩阵、地区分组和数据来源说明 |
| `data_processed/` | 清洗后可直接建模的面板数据 |
| `docs/` | 建模规格、项目结构、协作说明 |
| `figures/` | 后续论文图片输出 |
| `tables/` | 数据质量、变量审计、描述统计、相关性、回归和空间检验结果 |


## 关键辅助数据

- `data_raw/spatial/`：保存邻接矩阵、地理距离矩阵、经济距离矩阵和省级行政中心坐标。
- `data_raw/region_groups.csv`：保存东部、中部、西部、东北四大地区分组。
- `tables/table00b_variable_consistency_audit.csv`：保存变量公式、实际 GDP 折算、空间矩阵和地区分组一致性审计结果。

## 数据流

1. 严欣浩整理原始数据并放入 `data_raw/<source>/`。
2. 清洗脚本或人工核验后形成 `data_processed/panel_data.csv`。
3. 你运行 `code/02_descriptive_analysis.py`、`code/03_baseline_model.py`、`code/04_spatial_analysis.py`。
4. 结果统一输出到 `tables/`，其中 `table00b_variable_consistency_audit.csv` 用于记录变量和矩阵一致性审计；后续图像输出到 `figures/`。
5. 徐若诚根据 `tables/`、`figures/` 和 `docs/model_spec.md` 撰写论文实证部分。

## 当前正式样本

- 地区：剔除西藏后的中国大陆 30 个省级地区。
- 年份：2011-2022 年。
- 样本量：360 个省份-年份观测值。
- 被解释变量：`carbon_intensity`，单位为万吨 CO2 / 亿元实际 GDP。
- 核心解释变量：`digital_finance`，北京大学数字普惠金融省级综合指数。

## 复现命令

```powershell
D:\anaconda\envs\statistical_modeling_env\python.exe code/02_descriptive_analysis.py
D:\anaconda\envs\statistical_modeling_env\python.exe code/03_baseline_model.py
D:\anaconda\envs\statistical_modeling_env\python.exe code/04_spatial_analysis.py
D:\anaconda\envs\statistical_modeling_env\python.exe code/07_heterogeneity_analysis.py
D:\anaconda\envs\statistical_modeling_env\python.exe code/08_validate_variable_consistency.py
```
