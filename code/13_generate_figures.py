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
    plt.rcParams["axes.edgecolor"] = "#4b5563"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["xtick.color"] = "#374151"
    plt.rcParams["ytick.color"] = "#374151"
    plt.rcParams["axes.labelcolor"] = "#111827"
    plt.rcParams["legend.frameon"] = False


def save_current_figure(filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)


def plot_carbon_intensity_trend(panel: pd.DataFrame) -> None:
    yearly = panel.groupby("year", as_index=False)["carbon_intensity"].mean()
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(
        yearly["year"],
        yearly["carbon_intensity"],
        marker="o",
        markersize=4.5,
        linewidth=2.1,
        color="#1f77b4",
        label="全国平均碳强度",
    )
    ax.set_xlabel("年份")
    ax.set_ylabel("碳强度（万吨 $CO_2$/亿元实际 GDP）")
    ax.legend(loc="upper right", fontsize=8.5)
    style_axes(ax)
    save_current_figure("figure01_carbon_intensity_trend.png")


def plot_digital_finance_trend(panel: pd.DataFrame) -> None:
    yearly = panel.groupby("year", as_index=False)["digital_finance"].mean()
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(
        yearly["year"],
        yearly["digital_finance"],
        marker="o",
        markersize=4.5,
        linewidth=2.1,
        color="#2ca25f",
        label="全国平均数字普惠金融指数",
    )
    ax.set_xlabel("年份")
    ax.set_ylabel("数字普惠金融综合指数")
    ax.legend(loc="upper left", fontsize=8.5)
    style_axes(ax)
    save_current_figure("figure02_digital_finance_trend.png")


def plot_moran_i_trend() -> None:
    moran = pd.read_csv(MORAN_PATH)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(
        moran["year"],
        moran["moran_i"],
        marker="o",
        markersize=4.5,
        linewidth=2.1,
        color="#8c564b",
        label="Moran's I",
    )
    ax.axhline(0, color="#111827", linewidth=0.8, linestyle="--", label="零基准线")
    ax.set_xlabel("年份")
    ax.set_ylabel("Moran's I")
    ax.legend(loc="upper right", fontsize=8.5)
    style_axes(ax)
    save_current_figure("figure03_moran_i_trend.png")


def plot_regional_heterogeneity() -> None:
    heterogeneity = pd.read_csv(HETEROGENEITY_PATH)
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    colors = ["#2ca25f" if coef < 0 else "#de2d26" for coef in heterogeneity["digital_finance_coef"]]
    bars = ax.bar(
        heterogeneity["region"],
        heterogeneity["digital_finance_coef"],
        yerr=1.96 * heterogeneity["digital_finance_std_err"],
        color=colors,
        edgecolor="#374151",
        linewidth=0.6,
        capsize=4,
        label="估计系数及 95% 置信区间",
    )
    ax.axhline(0, color="#111827", linewidth=0.8, linestyle="--", label="零基准线")
    for bar, p_value in zip(bars, heterogeneity["digital_finance_p_value"]):
        marker = "*" if p_value < 0.1 else "n.s."
        y = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y + (0.010 if y >= 0 else -0.010),
            marker,
            ha="center",
            va="bottom" if y >= 0 else "top",
            fontsize=8.5,
            color="#111827",
        )
    ax.set_xlabel("区域")
    ax.set_ylabel("数字普惠金融估计系数")
    ax.legend(loc="upper left", fontsize=8.0)
    style_axes(ax)
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
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    bars = ax.bar(
        target["label"],
        target["coefficient"],
        yerr=1.96 * target["std_err"],
        color=["#756bb1", "#3182bd", "#6b7280"],
        edgecolor="#374151",
        linewidth=0.6,
        capsize=4,
        label="估计系数及 95% 置信区间",
    )
    ax.axhline(0, color="#111827", linewidth=0.8, linestyle="--", label="零基准线")
    for _, row in target.iterrows():
        ax.text(
            row["label"],
            row["coefficient"] + (0.025 if row["coefficient"] >= 0 else -0.025),
            f"p={row['p_value']:.3f}",
            ha="center",
            va="bottom" if row["coefficient"] >= 0 else "top",
            fontsize=8.0,
            color="#111827",
        )
    ax.set_xlabel("空间权重矩阵")
    ax.set_ylabel("$W\\_digital\\_finance$ 估计系数")
    ax.legend(loc="upper left", fontsize=8.0)
    style_axes(ax)
    save_current_figure("figure05_spatial_weight_robustness.png")


def plot_policy_typology() -> None:
    typology = pd.read_csv(POLICY_TYPOLOGY_PATH)
    color_map = {
        "示范引领型": "#2ca25f",
        "转型压力型": "#de2d26",
        "稳态优化型": "#3182bd",
        "重点扶持型": "#fdae6b",
    }
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    for policy_type, group in typology.groupby("policy_type"):
        ax.scatter(
            group["digital_finance_mean"],
            group["carbon_intensity_mean"],
            label=policy_type,
            s=62,
            alpha=0.88,
            color=color_map.get(policy_type),
            edgecolor="#374151",
            linewidth=0.4,
        )
    x_threshold = typology["digital_threshold_median"].iloc[0]
    y_threshold = typology["carbon_threshold_median"].iloc[0]
    ax.axvline(x_threshold, color="#111827", linewidth=0.8, linestyle="--", label="数字金融中位数")
    ax.axhline(y_threshold, color="#6b7280", linewidth=0.8, linestyle=":", label="碳强度中位数")
    ax.set_xlabel("数字普惠金融指数均值")
    ax.set_ylabel("碳强度均值")
    ax.legend(loc="upper right", fontsize=7.8, ncol=1)
    style_axes(ax)
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
