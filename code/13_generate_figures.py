"""Generate paper-ready figures from existing result tables."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

MORAN_PATH = TABLES_DIR / "table04_moran_i_by_year.csv"
HETEROGENEITY_PATH = TABLES_DIR / "table08_heterogeneity_by_region.csv"
WEIGHT_ROBUSTNESS_PATH = TABLES_DIR / "table09_spatial_weight_robustness.csv"
POLICY_TYPOLOGY_PATH = TABLES_DIR / "table12_policy_typology.csv"


def configure_matplotlib() -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 120


def save_current_figure(filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_carbon_intensity_trend(panel: pd.DataFrame) -> None:
    yearly = panel.groupby("year", as_index=False)["carbon_intensity"].mean()
    plt.figure(figsize=(7, 4))
    plt.plot(yearly["year"], yearly["carbon_intensity"], marker="o", linewidth=2)
    plt.title("全国平均碳强度变化趋势")
    plt.xlabel("年份")
    plt.ylabel("碳强度（万吨CO2/亿元实际GDP）")
    plt.grid(alpha=0.25)
    save_current_figure("figure01_carbon_intensity_trend.png")


def plot_digital_finance_trend(panel: pd.DataFrame) -> None:
    yearly = panel.groupby("year", as_index=False)["digital_finance"].mean()
    plt.figure(figsize=(7, 4))
    plt.plot(yearly["year"], yearly["digital_finance"], marker="o", linewidth=2, color="#2f7ed8")
    plt.title("全国平均数字普惠金融指数变化趋势")
    plt.xlabel("年份")
    plt.ylabel("数字普惠金融综合指数")
    plt.grid(alpha=0.25)
    save_current_figure("figure02_digital_finance_trend.png")


def plot_moran_i_trend() -> None:
    moran = pd.read_csv(MORAN_PATH)
    plt.figure(figsize=(7, 4))
    plt.plot(moran["year"], moran["moran_i"], marker="o", linewidth=2, color="#8b5a2b")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("碳强度 Moran's I 年度变化")
    plt.xlabel("年份")
    plt.ylabel("Moran's I")
    plt.grid(alpha=0.25)
    save_current_figure("figure03_moran_i_trend.png")


def plot_regional_heterogeneity() -> None:
    heterogeneity = pd.read_csv(HETEROGENEITY_PATH)
    plt.figure(figsize=(7, 4))
    colors = ["#2ca25f" if coef < 0 else "#de2d26" for coef in heterogeneity["digital_finance_coef"]]
    plt.bar(heterogeneity["region"], heterogeneity["digital_finance_coef"], color=colors)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("数字普惠金融影响的区域异质性")
    plt.xlabel("区域")
    plt.ylabel("digital_finance 系数")
    save_current_figure("figure04_regional_heterogeneity_coefficients.png")


def plot_spatial_weight_robustness() -> None:
    robustness = pd.read_csv(WEIGHT_ROBUSTNESS_PATH)
    target = robustness[(robustness["model"] == "SDM") & (robustness["key_term"] == "W_digital_finance")].copy()
    labels = {
        "adjacency": "邻接矩阵",
        "geo_distance": "地理距离矩阵",
        "economic_distance": "经济距离矩阵",
    }
    target["label"] = target["weight_name"].map(labels).fillna(target["weight_name"])
    plt.figure(figsize=(7, 4))
    plt.bar(target["label"], target["coefficient"], color=["#756bb1", "#3182bd", "#636363"])
    plt.axhline(0, color="black", linewidth=0.8)
    for _, row in target.iterrows():
        plt.text(row["label"], row["coefficient"], f"p={row['p_value']:.3f}", ha="center", va="bottom" if row["coefficient"] >= 0 else "top")
    plt.title("不同空间权重矩阵下的空间滞后项")
    plt.xlabel("空间权重矩阵")
    plt.ylabel("W_digital_finance 系数")
    save_current_figure("figure05_spatial_weight_robustness.png")


def plot_policy_typology() -> None:
    typology = pd.read_csv(POLICY_TYPOLOGY_PATH)
    color_map = {
        "示范引领型": "#2ca25f",
        "转型压力型": "#de2d26",
        "稳态优化型": "#3182bd",
        "重点扶持型": "#fdae6b",
    }
    plt.figure(figsize=(7, 5))
    for policy_type, group in typology.groupby("policy_type"):
        plt.scatter(
            group["digital_finance_mean"],
            group["carbon_intensity_mean"],
            label=policy_type,
            s=55,
            alpha=0.85,
            color=color_map.get(policy_type),
        )
    x_threshold = typology["digital_threshold_median"].iloc[0]
    y_threshold = typology["carbon_threshold_median"].iloc[0]
    plt.axvline(x_threshold, color="black", linewidth=0.8, linestyle="--")
    plt.axhline(y_threshold, color="black", linewidth=0.8, linestyle="--")
    plt.title("省份数字金融-碳强度政策分型")
    plt.xlabel("数字普惠金融均值")
    plt.ylabel("碳强度均值")
    plt.legend(frameon=False, fontsize=8)
    plt.grid(alpha=0.2)
    save_current_figure("figure06_policy_typology_quadrant.png")


def main() -> None:
    configure_matplotlib()
    panel = pd.read_csv(DATA_PATH)
    required_paths = [MORAN_PATH, HETEROGENEITY_PATH, WEIGHT_ROBUSTNESS_PATH, POLICY_TYPOLOGY_PATH]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required result tables: {missing}")

    plot_carbon_intensity_trend(panel)
    plot_digital_finance_trend(panel)
    plot_moran_i_trend()
    plot_regional_heterogeneity()
    plot_spatial_weight_robustness()
    plot_policy_typology()
    print(f"Exported figures to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
