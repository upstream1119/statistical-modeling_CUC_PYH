# 清洗后数据目录

本目录用于存放可直接用于建模的清洗后数据。

## 主数据文件

默认主数据文件为：`panel_data.csv`

建议字段如下：

| 字段 | 含义 | 类型 | 说明 |
| --- | --- | --- | --- |
| `province` | 省份名称 | string | 与空间权重矩阵省份顺序保持一致 |
| `year` | 年份 | int | 面板年份 |
| `carbon_intensity` | 碳强度 | float | 被解释变量，建议口径为碳排放量 / GDP 或单位 GDP 碳排放 |
| `digital_finance` | 数字普惠金融指数 | float | 核心解释变量 |
| `gdp_per_capita` | 人均 GDP | float | 控制变量 |
| `industrial_structure` | 产业结构 | float | 控制变量 |
| `urbanization` | 城镇化率 | float | 控制变量 |
| `government_intervention` | 政府干预程度 | float | 控制变量 |
| `innovation` | 科技创新水平 | float | 控制变量 |
| `energy_structure` | 能源结构 | float | 控制变量 |

## 清洗规则

1. 每一行代表一个省份-年份观测值。
2. 省份名称使用统一中文简称，例如 `北京`、`天津`、`河北`。
3. 缺失值处理方式必须在代码注释或结果说明中记录。
4. 进入论文的结果必须能由本目录数据和 `code/` 脚本复现。
