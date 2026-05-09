"""Build a writing-oriented summary of empirical findings.

This script converts the current result tables into a compact writing package
for the paper. It does not estimate new models; it only indexes verified
results and standardizes the interpretation boundaries.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table10_empirical_findings_summary.csv"


def format_coef_p(coef: float, p_value: float, digits: int = 4) -> str:
    return f"coef={coef:.{digits}f}, p={p_value:.{digits}f}"


def read_baseline() -> tuple[float, float]:
    df = pd.read_csv(TABLES_DIR / "table03_baseline_regression.csv")
    row = df[df.iloc[:, 0] == "digital_finance"].iloc[0]
    return float(row["coef"]), float(row["p_value"])


def read_moran_range() -> tuple[float, float, float]:
    df = pd.read_csv(TABLES_DIR / "table04_moran_i_by_year.csv")
    return float(df["moran_i"].min()), float(df["moran_i"].max()), float(df["p_two_sided"].max())


def read_spatial_term(model: str, term: str) -> tuple[float, float]:
    df = pd.read_csv(TABLES_DIR / "table05_spatial_model_comparison.csv")
    row = df[(df["model"] == model) & (df["var_names"] == term)].iloc[0]
    return float(row["coefficients"]), float(row["prob"])


def read_region(region: str) -> tuple[float, float, int, int]:
    df = pd.read_csv(TABLES_DIR / "table08_heterogeneity_by_region.csv")
    row = df[df["region"] == region].iloc[0]
    return (
        float(row["digital_finance_coef"]),
        float(row["digital_finance_p_value"]),
        int(row["n_provinces"]),
        int(row["n_obs"]),
    )


def read_weight_term(weight_name: str, term: str = "W_digital_finance") -> tuple[float, float]:
    df = pd.read_csv(TABLES_DIR / "table09_spatial_weight_robustness.csv")
    row = df[(df["weight_name"] == weight_name) & (df["model"] == "SDM") & (df["key_term"] == term)].iloc[0]
    return float(row["coefficient"]), float(row["p_value"])


def read_mechanism_summary() -> tuple[str, str]:
    df = pd.read_csv(TABLES_DIR / "table11_mechanism_tests.csv")
    parts = []
    cautions = set()
    for _, row in df.iterrows():
        parts.append(
            f"{row['mechanism_label']}: "
            f"path_a coef={row['path_a_digital_finance_coef']:.4f}, p={row['path_a_digital_finance_p_value']:.4f}; "
            f"path_b coef={row['path_b_mechanism_coef']:.4f}, p={row['path_b_mechanism_p_value']:.4f}"
        )
        cautions.add(str(row["writing_caution"]))
    return " | ".join(parts), "；".join(sorted(cautions))


def read_policy_counts() -> dict[str, int]:
    df = pd.read_csv(TABLES_DIR / "table12_policy_typology.csv")
    return {str(key): int(value) for key, value in df["policy_type"].value_counts().items()}


def build_rows() -> list[dict[str, str]]:
    baseline_coef, baseline_p = read_baseline()
    moran_min, moran_max, moran_max_p = read_moran_range()
    sar_rho, sar_p = read_spatial_term("SAR", "W_carbon_intensity")
    sem_lambda, sem_p = read_spatial_term("SEM", "lambda")
    sdm_local, sdm_local_p = read_spatial_term("SDM", "digital_finance")
    sdm_spillover, sdm_spillover_p = read_spatial_term("SDM", "W_digital_finance")
    east_coef, east_p, east_n_provinces, east_n_obs = read_region("东部")
    central_coef, central_p, _, _ = read_region("中部")
    west_coef, west_p, _, _ = read_region("西部")
    northeast_coef, northeast_p, northeast_n_provinces, northeast_n_obs = read_region("东北")
    adjacency_w, adjacency_p = read_weight_term("adjacency")
    geo_w, geo_p = read_weight_term("geo_distance")
    economic_w, economic_p = read_weight_term("economic_distance")
    mechanism_statistic, mechanism_caution = read_mechanism_summary()
    policy_counts = read_policy_counts()

    return [
        {
            "paper_section": "数据质量与变量审计",
            "source_table": "table00_data_quality_report.csv; table00b_variable_consistency_audit.csv",
            "key_result": "正式样本为2011-2022年中国大陆30个省级地区，共360条观测；核心变量无缺失，变量一致性审计通过。",
            "statistic": "n_obs=360; province_count=30; audit_passed=True",
            "paper_interpretation": "可作为数据可靠性和变量构造可信度的基础说明，支撑后续实证分析。",
            "writing_status": "可直接写入论文的数据来源与变量说明部分。",
            "do_not_write": "不要写31个省份、34个省份或包含西藏的正式样本。",
        },
        {
            "paper_section": "基准回归",
            "source_table": "table03_baseline_regression.csv",
            "key_result": "全国平均基准回归中digital_finance系数为正但不显著。",
            "statistic": format_coef_p(baseline_coef, baseline_p),
            "paper_interpretation": "说明普通基准回归下数字普惠金融的全国平均效应方向不稳定，不能直接得出显著降碳结论。",
            "writing_status": "作为引出空间相关性、区域异质性和权重矩阵稳健性的铺垫。",
            "do_not_write": "不要写数字普惠金融显著降低全国碳强度；不要写方向符合降碳预期。",
        },
        {
            "paper_section": "空间自相关检验",
            "source_table": "table04_moran_i_by_year.csv",
            "key_result": "2011-2022年Moran's I均为正且显著。",
            "statistic": f"Moran's I range={moran_min:.3f}-{moran_max:.3f}; max_p_two_sided={moran_max_p:.3f}",
            "paper_interpretation": "说明省域碳强度存在稳定的空间正相关和空间集聚特征，有必要引入空间计量模型。",
            "writing_status": "可作为空间模型设定的核心依据。",
            "do_not_write": "不要只依赖OLS解释低碳转型；不要忽略空间依赖。",
        },
        {
            "paper_section": "空间计量模型",
            "source_table": "table05_spatial_model_comparison.csv; table06_spatial_effect_decomposition.csv",
            "key_result": "SAR空间滞后项显著为正；SEM误差项不显著；SDM中本地digital_finance显著为正，W_digital_finance为负但不显著。",
            "statistic": (
                f"SAR W_carbon_intensity={sar_rho:.4f}, p={sar_p:.4g}; "
                f"SEM lambda={sem_lambda:.4f}, p={sem_p:.4f}; "
                f"SDM digital_finance={sdm_local:.4f}, p={sdm_local_p:.4f}; "
                f"SDM W_digital_finance={sdm_spillover:.4f}, p={sdm_spillover_p:.4f}"
            ),
            "paper_interpretation": "碳强度空间依赖稳健存在，但数字普惠金融本地效应和空间溢出效应不能被解释为稳健降碳证据。",
            "writing_status": "可写空间依赖显著；空间溢出只能写方向性线索。",
            "do_not_write": "不要写显著空间溢出效应已经成立；不要把本地正系数解释成低碳促进。",
        },
        {
            "paper_section": "普通稳健性检验",
            "source_table": "table07_robustness_checks.csv",
            "key_result": "滞后一期、创新变换、剔除城镇化、GDP取对数等普通稳健性下，核心变量方向和显著性仍不稳定。",
            "statistic": "baseline and robustness p-values are not conventionally significant for the expected negative effect.",
            "paper_interpretation": "说明不应过度强调全国平均直接效应，而应把论文重点放在空间依赖、区域异质性和权重矩阵敏感性上。",
            "writing_status": "作为谨慎性说明，不作为强结论。",
            "do_not_write": "不要写所有稳健性检验均支持核心结论。",
        },
        {
            "paper_section": "区域异质性",
            "source_table": "table08_heterogeneity_by_region.csv",
            "key_result": "东部地区呈边际负向关系；中部和西部为负但不显著；东北显著为正但样本较小。",
            "statistic": (
                f"East {format_coef_p(east_coef, east_p)}; "
                f"Central {format_coef_p(central_coef, central_p)}; "
                f"West {format_coef_p(west_coef, west_p)}; "
                f"Northeast {format_coef_p(northeast_coef, northeast_p)}"
            ),
            "paper_interpretation": (
                f"东部{east_n_provinces}省、{east_n_obs}条观测提供边际负向线索；"
                f"东北仅{northeast_n_provinces}省、{northeast_n_obs}条观测，需谨慎作为现象讨论。"
            ),
            "writing_status": "可用于解释全国平均效应不稳定，并引出分区政策建议。",
            "do_not_write": "不要写东中西均显著；不要把东北结果上升为稳健规律。",
        },
        {
            "paper_section": "空间权重矩阵稳健性",
            "source_table": "table09_spatial_weight_robustness.csv",
            "key_result": "邻接矩阵下W_digital_finance为负但不显著；地理距离矩阵下为负且接近10%边际显著；经济距离矩阵下不显著且转正。",
            "statistic": (
                f"Adjacency {format_coef_p(adjacency_w, adjacency_p)}; "
                f"Geo-distance {format_coef_p(geo_w, geo_p)}; "
                f"Economic-distance {format_coef_p(economic_w, economic_p)}"
            ),
            "paper_interpretation": "数字普惠金融空间溢出对权重矩阵设定敏感，地理邻近渠道存在边际负向证据。",
            "writing_status": "可作为模型优化后的重要补充结果。",
            "do_not_write": "不要写空间溢出效应稳健显著；不要把经济距离矩阵结果解释为支持低碳外溢。",
        },
        {
            "paper_section": "机制路径检验",
            "source_table": "table11_mechanism_tests.csv",
            "key_result": "技术创新和能源结构路径提供一定线索；产业结构路径支持不足。",
            "statistic": mechanism_statistic,
            "paper_interpretation": "机制检验用于说明数字普惠金融可能通过技术创新和能源结构调整影响碳强度，但当前结果不能作为严格因果中介识别。",
            "writing_status": "可写入实证结果的机制路径小节，表述为补充证据或路径线索。",
            "do_not_write": mechanism_caution,
        },
        {
            "paper_section": "政策分型",
            "source_table": "table12_policy_typology.csv",
            "key_result": "基于数字普惠金融水平与碳强度压力构建四象限政策分型。",
            "statistic": "; ".join(f"{key}={value}" for key, value in policy_counts.items()),
            "paper_interpretation": "四象限分型用于将实证结果转化为差异化政策建议，支撑第六章政策优化分析。",
            "writing_status": "可写入政策分型与优化建议章节，完整省份名单可放正文表格或附录。",
            "do_not_write": "不要写成 TOPSIS/K-means；不要写成因果模型；不要写某类地区必然适用某项政策。",
        },
        {
            "paper_section": "综合结论口径",
            "source_table": "table03-table12",
            "key_result": "空间依赖稳健存在，数字普惠金融的全国平均直接效应不稳定，地理邻近下存在边际负向外溢线索，区域差异明显，机制路径和政策分型提供补充支撑。",
            "statistic": "synthesis of current empirical tables",
            "paper_interpretation": "论文应聚焦空间依赖、区域差异和政策优化，而不是强行宣称数字普惠金融显著降碳。",
            "writing_status": "作为实证小结和政策建议的统一主线。",
            "do_not_write": "不要把当前结果包装成所有假设均被强支持。",
        },
    ]


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(build_rows())
    result.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported empirical findings writing package: {OUT_PATH}")


if __name__ == "__main__":
    main()
