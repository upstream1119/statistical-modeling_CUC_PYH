"""Generate polished competition-paper figure previews.

The outputs are written to ``figures_polished`` and do not replace the
original manuscript figures. The script only uses existing result tables.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "tables"
OUT_DIR = ROOT / "figures_polished"

WEIGHT_ROBUSTNESS_PATH = TABLES_DIR / "table09_spatial_weight_robustness.csv"
HETEROGENEITY_PATH = TABLES_DIR / "table08_heterogeneity_by_region.csv"
POLICY_TYPOLOGY_PATH = TABLES_DIR / "table12_policy_typology.csv"
KMEANS_PATH = TABLES_DIR / "table13_kmeans_policy_typology_robustness.csv"
TOPSIS_PATH = TABLES_DIR / "table14_entropy_topsis_policy_priority.csv"

NAVY = "#172033"
TEXT = "#243044"
MUTED = "#64748B"
GRID = "#E5E7EB"
BLUE = "#2563EB"
GREEN = "#16A34A"
ORANGE = "#F97316"
RED = "#DC2626"
PURPLE = "#7C3AED"

POLICY_COLORS = {
    "示范引领型": GREEN,
    "稳态优化型": BLUE,
    "转型压力型": RED,
    "重点扶持型": ORANGE,
}

TOPSIS_COLORS = {
    "示范扩散优先": GREEN,
    "稳步优化": BLUE,
    "重点提升优先": ORANGE,
}

KMEANS_COLORS = {
    1: "#1D4ED8",
    2: "#B45309",
    3: "#059669",
    4: "#7C3AED",
}

KMEANS_PROFILE_RENAME = {
    "高数字金融-高碳压力": "混合过渡组",
    "低数字金融-高碳压力": "低数字金融-较高碳压力",
}

KMEANS_PROFILE_BY_CLUSTER = {
    1: "高数字金融-低碳压力",
    2: "混合过渡组",
    3: "低数字金融-较高碳压力",
    4: "低数字金融-高碳压力",
}

KMEANS_LABEL_OVERRIDES = {
    "辽宁": (-16, 2),
    "陕西": (12, -8),
    "安徽": (-13, -11),
    "四川": (-8, -11),
    "江苏": (12, -10),
    "福建": (-24, 9),
    "广东": (15, 8),
    "北京": (-18, -9),
    "上海": (17, 5),
}

POLICY_LABEL_OFFSETS = {
    "北京": (-32, -2),
    "上海": (10, 8),
    "广东": (8, 8),
    "山东": (8, 7),
    "山西": (8, 6),
    "贵州": (8, 7),
    "青海": (8, 4),
    "辽宁": (9, 5),
    "四川": (8, -10),
    "湖北": (8, 6),
}


def configure_matplotlib() -> None:
    for font_path in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc"]:
        if Path(font_path).exists():
            font_manager.fontManager.addfont(font_path)
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 140
    plt.rcParams["savefig.dpi"] = 320
    plt.rcParams["axes.edgecolor"] = "#CBD5E1"
    plt.rcParams["axes.linewidth"] = 0.9
    plt.rcParams["xtick.color"] = TEXT
    plt.rcParams["ytick.color"] = TEXT
    plt.rcParams["axes.labelcolor"] = NAVY


def require_paths() -> None:
    required = [
        WEIGHT_ROBUSTNESS_PATH,
        HETEROGENEITY_PATH,
        POLICY_TYPOLOGY_PATH,
        KMEANS_PATH,
        TOPSIS_PATH,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required tables: {missing}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(OUT_DIR / filename, bbox_inches="tight", facecolor="white", pad_inches=0.22)
    plt.close(fig)
    print(OUT_DIR / filename)


def clean_axes(ax, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)


def p_label(p_value: float) -> str:
    if p_value < 0.001:
        return "p<0.001"
    return f"p={p_value:.3f}"


def rounded_box(ax, x, y, w, h, title, body, face, edge, number=None):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.022,rounding_size=0.11",
        linewidth=1.8,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    if number is not None:
        ax.text(
            x + 0.36,
            y + h - 0.42,
            str(number),
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="white",
            bbox=dict(boxstyle="circle,pad=0.24", fc=edge, ec=edge),
        )
    ax.text(
        x + w / 2,
        y + h - 0.86,
        title,
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        x + w / 2,
        y + h - 1.48,
        body,
        ha="center",
        va="top",
        fontsize=10.7,
        linespacing=1.42,
        color=TEXT,
    )


def arrow(ax, x1, y1, x2, y2, color="#94A3B8"):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.8,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def plot_research_framework() -> None:
    fig, ax = plt.subplots(figsize=(14.2, 8.8))
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 8.8)
    ax.axis("off")

    def simple_box(x, y, w, h, text, face, edge, dashed=False, fs=10.2, weight="normal"):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.025,rounding_size=0.035",
            linewidth=1.35,
            linestyle="--" if dashed else "-",
            edgecolor=edge,
            facecolor=face,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=fs,
            fontweight=weight,
            color=NAVY,
            linespacing=1.18,
        )

    def route_box(x, y, w, h, title, body):
        multiline = "\n" in body
        title_fs = 10.4 if multiline else 11.2
        body_fs = 8.05 if multiline else 8.75
        body_y = y + (0.10 if multiline else 0.20)
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.025,rounding_size=0.045",
            linewidth=1.45,
            edgecolor="#60A5FA",
            facecolor="#F8FBFF",
        )
        ax.add_patch(patch)
        ax.text(
            x + 0.28,
            y + h - 0.24,
            title,
            ha="left",
            va="top",
            fontsize=title_fs,
            fontweight="bold",
            color=BLUE,
        )
        ax.text(
            x + 0.28,
            body_y,
            body,
            ha="left",
            va="bottom",
            fontsize=body_fs,
            color=TEXT,
            linespacing=1.08,
        )

    def route_arrow(x1, y1, x2, y2, color="#9AA4B2", lw=1.20):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=13,
                linewidth=lw,
                color=color,
                shrinkA=2,
                shrinkB=2,
            )
        )

    left_x, mid_x, right_x = 0.42, 3.48, 11.02
    left_w, mid_w, right_w = 2.62, 6.92, 2.70
    header_y, header_h = 8.02, 0.50
    row_h = 0.88
    row_ys = [6.98, 5.80, 4.62, 3.44, 2.26, 1.08]

    simple_box(left_x, header_y, left_w, header_h, "研究逻辑", "#FFF5F5", RED, fs=14.2, weight="bold")
    simple_box(mid_x, header_y, mid_w, header_h, "技术路线", "#EFF6FF", BLUE, fs=14.2, weight="bold")
    simple_box(right_x, header_y, right_w, header_h, "方法体系", "#FFF7ED", ORANGE, fs=14.2, weight="bold")

    left_texts = [
        "问题提出\n双碳目标与数字金融",
        "文献梳理\n识别研究缺口",
        "理论机制\n创新与能源结构路径",
        "实证识别\n空间依赖与异质性",
        "政策转化\n分型治理与协同优化",
        "结论形成\n研究发现与应用输出",
    ]
    mid_items = [
        ("研究问题凝练", "国家战略背景 → 数字普惠金融 → 区域低碳转型"),
        ("数据与变量构造", "2011-2022年30省面板 → 碳强度与核心变量 → 空间权重矩阵"),
        ("基础实证分析", "数据质量审计 → 描述统计与相关性 → 基准回归"),
        ("空间计量识别", "Moran's I空间自相关 → SAR / SEM / SDM → 邻接矩阵主模型"),
        ("拓展与稳健性", "权重矩阵替换 → 区域异质性 → 双向固定效应\n分阶段检验 → 机制路径检验"),
        ("结论与政策输出", "研究发现归纳 → 四象限分型 → K-means稳健性\n熵权TOPSIS优先级 → 分区治理建议"),
    ]
    right_texts = [
        "文献归纳\n比较分析",
        "变量构造\n一致性审计",
        "OLS回归\nHC1稳健标准误",
        "Moran's I\nSAR / SEM / SDM",
        "权重稳健性\n区域异质性\n双向固定效应\n分阶段检验\n机制路径检验",
        "四象限分型\nK-means\n熵权TOPSIS\n政策建议",
    ]

    for i, y in enumerate(row_ys):
        simple_box(left_x, y, left_w, row_h, left_texts[i], "#FFF5F5", "#EF4444", dashed=True)
        route_box(mid_x, y - 0.01, mid_w, row_h + 0.02, mid_items[i][0], mid_items[i][1])
        simple_box(right_x, y, right_w, row_h, right_texts[i], "#FFF7ED", ORANGE, fs=8.9)

        route_arrow(left_x + left_w + 0.06, y + row_h / 2, mid_x - 0.03, y + row_h / 2)
        route_arrow(mid_x + mid_w + 0.06, y + row_h / 2, right_x - 0.03, y + row_h / 2)
        if i < len(row_ys) - 1:
            route_arrow(left_x + left_w / 2, y - 0.05, left_x + left_w / 2, row_ys[i + 1] + row_h + 0.05, "#EF4444", 1.15)
            route_arrow(mid_x + mid_w / 2, y - 0.04, mid_x + mid_w / 2, row_ys[i + 1] + row_h + 0.04, BLUE, 1.20)

    save(fig, "figure00_research_framework_polished.png")


def plot_spatial_weight_robustness() -> None:
    df = pd.read_csv(WEIGHT_ROBUSTNESS_PATH)
    target = df[(df["model"] == "SDM") & (df["key_term"] == "W_digital_finance")].copy()
    labels = {
        "adjacency": "邻接矩阵",
        "geo_distance": "地理距离矩阵",
        "economic_distance": "经济距离矩阵",
    }
    target["label"] = target["weight_name"].map(labels).fillna(target["weight_name"])
    order = ["邻接矩阵", "地理距离矩阵", "经济距离矩阵"]
    target = target.set_index("label").loc[order].reset_index()

    x = np.arange(len(target))
    coef = target["coefficient"].to_numpy(float)
    ci = 1.96 * target["std_err"].to_numpy(float)
    colors = ["#94A3B8", BLUE, "#94A3B8"]

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.axhline(0, color=NAVY, linewidth=1.2, linestyle="--")
    ax.errorbar(x, coef, yerr=ci, fmt="none", ecolor="#334155", elinewidth=1.8, capsize=6, zorder=2)
    ax.scatter(x, coef, s=150, color=colors, edgecolor="white", linewidth=1.8, zorder=3)
    for i, row in target.iterrows():
        if i == 1:
            continue
        offset = 0.060 if i == 2 else 0.045
        ax.text(i, coef[i] + (offset if coef[i] >= 0 else -offset), p_label(row["p_value"]),
                ha="center", va="bottom" if coef[i] >= 0 else "top", fontsize=10.5, color=TEXT)
    ax.annotate(
        "p=0.094\n负向且接近10%水平",
        xy=(1, coef[1]),
        xytext=(0.56, coef[1] - 0.072),
        fontsize=10.2,
        color=BLUE,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.30", fc="#EFF6FF", ec="none", alpha=0.92),
        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.35),
    )
    ax.set_xticks(x, order, fontsize=11.5)
    ax.set_ylabel("SDM空间滞后项估计系数", fontsize=12)
    ax.set_xlabel("空间权重矩阵设定", fontsize=12)
    ax.text(
        0.5,
        -0.16,
        "注：点为数字普惠金融空间滞后项估计系数，误差线为95%置信区间；该图仅说明空间负向线索，不解释为稳健显著溢出。",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    clean_axes(ax)
    save(fig, "figure05_spatial_weight_robustness_polished.png")


def plot_regional_heterogeneity() -> None:
    df = pd.read_csv(HETEROGENEITY_PATH).set_index("region").loc[["东部", "中部", "西部", "东北"]].reset_index()
    y = np.arange(len(df))[::-1]
    coef = df["digital_finance_coef"].to_numpy(float)
    ci = 1.96 * df["digital_finance_std_err"].to_numpy(float)
    colors = [GREEN, "#94A3B8", "#94A3B8", "#CBD5E1"]

    fig, ax = plt.subplots(figsize=(8.8, 5.3))
    ax.axvline(0, color=NAVY, linewidth=1.2, linestyle="--")
    for i, row in df.iterrows():
        ax.errorbar(
            coef[i],
            y[i],
            xerr=ci[i],
            fmt="o",
            markersize=9,
            color=colors[i],
            ecolor="#334155",
            elinewidth=1.7,
            capsize=5,
            markeredgecolor="white",
            markeredgewidth=1.4,
            zorder=3,
        )
        detail = f"{int(row['n_provinces'])}省，{p_label(row['digital_finance_p_value'])}"
        ax.text(coef[i] + (0.018 if coef[i] >= 0 else -0.018), y[i] + 0.20, detail,
                ha="left" if coef[i] >= 0 else "right", va="center", fontsize=10, color=TEXT)
    ax.text(coef[0] - ci[0] - 0.012, y[0] - 0.28, "东部呈边际负向线索", ha="left",
            fontsize=10.5, color=GREEN, fontweight="bold")
    ax.text(coef[3] + 0.015, y[3] - 0.28, "东北仅3省，谨慎解释", ha="left",
            fontsize=10.5, color=MUTED, fontweight="bold")
    ax.set_yticks(y, df["region"], fontsize=12)
    ax.set_xlabel("数字普惠金融估计系数", fontsize=12)
    ax.text(
        0.5,
        -0.16,
        "注：点为分区域估计系数，横线为95%置信区间；东北地区样本较少，结果仅作描述性参考。",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    clean_axes(ax, grid_axis="x")
    save(fig, "figure04_regional_heterogeneity_coefficients_polished.png")


def annotate_selected(ax, df: pd.DataFrame, offsets: dict[str, tuple[int, int]]) -> None:
    for _, row in df[df["province"].isin(offsets)].iterrows():
        offset = offsets[row["province"]]
        ax.annotate(
            row["province"],
            (row["digital_finance_mean"], row["carbon_intensity_mean"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=9.2,
            color=NAVY,
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="#CBD5E1", lw=0.7, alpha=0.88),
            arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.8, shrinkA=2, shrinkB=2),
        )


def plot_policy_typology() -> None:
    df = pd.read_csv(POLICY_TYPOLOGY_PATH)
    xmed = float(df["digital_threshold_median"].iloc[0])
    ymed = float(df["carbon_threshold_median"].iloc[0])
    xmin, xmax = df["digital_finance_mean"].min() - 9, df["digital_finance_mean"].max() + 12
    ymin, ymax = 0, df["carbon_intensity_mean"].max() + 0.75

    fig, ax = plt.subplots(figsize=(9.2, 6.2))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    backgrounds = [
        (xmed, ymed, xmax - xmed, ymax - ymed, "#FEE2E2", "转型压力型\n高数字金融 / 高碳压力", 0.70, 0.76),
        (xmin, ymed, xmed - xmin, ymax - ymed, "#FFEDD5", "重点扶持型\n低数字金融 / 高碳压力", 0.35, 0.76),
        (xmed, ymin, xmax - xmed, ymed - ymin, "#DCFCE7", "示范引领型\n高数字金融 / 低碳压力", 0.45, 0.30),
        (xmin, ymin, xmed - xmin, ymed - ymin, "#DBEAFE", "稳态优化型\n低数字金融 / 低碳压力", 0.36, 0.42),
    ]
    for x, y, w, h, face, label, rx, ry in backgrounds:
        ax.add_patch(Rectangle((x, y), w, h, fc=face, ec="none", alpha=0.32, zorder=0))
        ax.text(x + w * rx, y + h * ry, label, ha="center", va="center", fontsize=10.5, color=NAVY,
                bbox=dict(boxstyle="round,pad=0.36", fc="white", ec="none", alpha=0.64))

    for policy_type, sub in df.groupby("policy_type"):
        ax.scatter(
            sub["digital_finance_mean"],
            sub["carbon_intensity_mean"],
            s=82,
            label=policy_type,
            color=POLICY_COLORS[policy_type],
            alpha=0.92,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
    ax.axvline(xmed, color=NAVY, linestyle="--", linewidth=1.4)
    ax.axhline(ymed, color=NAVY, linestyle=":", linewidth=1.7)
    annotate_selected(ax, df, POLICY_LABEL_OFFSETS)
    ax.set_xlabel("数字普惠金融指数均值", fontsize=12)
    ax.set_ylabel("碳强度均值", fontsize=12)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=10, frameon=False)
    ax.text(
        0.5,
        -0.15,
        "注：虚线为数字普惠金融中位数，点线为碳强度中位数；标签仅标注重点代表省份。",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    clean_axes(ax)
    save(fig, "figure06_policy_typology_quadrant_polished.png")


def label_all_provinces(ax, df: pd.DataFrame, xcol: str, ycol: str) -> None:
    candidates = [
        (7, 7), (-7, 7), (7, -8), (-7, -8), (14, 0), (-14, 0),
        (0, 14), (0, -14), (19, 9), (-19, 9), (19, -10), (-19, -10),
    ]
    used: list[tuple[float, float, float, float]] = []

    def approx_bbox(x_value: float, y_value: float, text: str, offset: tuple[int, int]):
        base_x, base_y = ax.transData.transform((x_value, y_value))
        scale = ax.figure.dpi / 72.0
        cx, cy = base_x + offset[0] * scale, base_y + offset[1] * scale
        width = len(text) * 11.0 + 8.0
        height = 15.0
        return cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2

    def overlaps(a, b) -> bool:
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    ordered = df.assign(_priority=(df[xcol] - df[xcol].mean()).abs() + (df[ycol] - df[ycol].mean()).abs())
    ordered = ordered.sort_values("_priority", ascending=False)
    for _, row in ordered.iterrows():
        province = row["province"]
        options = [KMEANS_LABEL_OVERRIDES[province]] if province in KMEANS_LABEL_OVERRIDES else []
        options += candidates
        chosen = options[0]
        for option in options:
            box = approx_bbox(row[xcol], row[ycol], province, option)
            if not any(overlaps(box, existing) for existing in used):
                chosen = option
                used.append(box)
                break
        else:
            used.append(approx_bbox(row[xcol], row[ycol], province, chosen))
        ax.annotate(
            province,
            (row[xcol], row[ycol]),
            xytext=chosen,
            textcoords="offset points",
            fontsize=7.4,
            color=NAVY,
            bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="#CBD5E1", lw=0.55, alpha=0.83),
            arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.55, shrinkA=1, shrinkB=2),
        )


def plot_kmeans_typology() -> None:
    df = pd.read_csv(KMEANS_PATH)
    profile = df.groupby("kmeans_cluster")["kmeans_profile"].first().to_dict()
    profile = {key: KMEANS_PROFILE_RENAME.get(value, value) for key, value in profile.items()}
    profile.update(KMEANS_PROFILE_BY_CLUSTER)

    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    for cluster, sub in df.groupby("kmeans_cluster"):
        ax.scatter(
            sub["digital_finance_mean"],
            sub["carbon_intensity_mean"],
            s=84,
            color=KMEANS_COLORS.get(cluster, "#64748B"),
            label=f"聚类{cluster}：{profile[cluster]}",
            alpha=0.90,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
    label_all_provinces(ax, df, "digital_finance_mean", "carbon_intensity_mean")
    ax.set_xlabel("数字普惠金融指数均值", fontsize=12)
    ax.set_ylabel("碳强度均值", fontsize=12)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9.2, frameon=False)
    ax.text(
        0.5,
        -0.15,
        "注：K-means使用数字普惠金融、碳强度、能源结构和创新水平四项省均指标；聚类用于补充分型稳健性，不作为因果识别。",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.3,
        color=MUTED,
    )
    clean_axes(ax)
    save(fig, "figure07_kmeans_policy_typology_robustness_polished.png")


def plot_topsis_priority() -> None:
    df = pd.read_csv(TOPSIS_PATH).sort_values("topsis_rank", ascending=False)
    colors = df["topsis_group"].map(TOPSIS_COLORS)
    y = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(8.8, 10.6))
    ax.barh(y, df["topsis_score"], color=colors, edgecolor="#334155", linewidth=0.55)
    ax.set_yticks(y, df["province"], fontsize=10.5)
    ax.set_xlabel("熵权 TOPSIS 综合贴近度", fontsize=12, labelpad=16)
    for _, row in df[df["topsis_rank"].isin([1, 2, 3, 28, 29, 30])].iterrows():
        yi = df.index.get_loc(row.name)
        ax.text(row["topsis_score"] + 0.010, yi, str(int(row["topsis_rank"])),
                va="center", ha="left", fontsize=10.5, color=TEXT)

    display = df.reset_index(drop=True)
    separators = []
    for idx in range(1, len(display)):
        if display.loc[idx, "topsis_group"] != display.loc[idx - 1, "topsis_group"]:
            separators.append(idx - 0.5)
    for sep in separators:
        ax.axhline(len(display) - 1 - sep, color="#CBD5E1", linestyle="--", linewidth=1.3)

    handles = [
        Line2D([0], [0], marker="s", markersize=10, linestyle="", color=color, label=label)
        for label, color in TOPSIS_COLORS.items()
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=10.5, frameon=False)
    ax.text(
        0.5,
        -0.095,
        "注：颜色表示TOPSIS三类优先级分组，得分用于政策排序参考，不代表因果效应大小。",
        transform=ax.transAxes,
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    ax.set_xlim(0, min(1.0, df["topsis_score"].max() + 0.08))
    clean_axes(ax, grid_axis="x")
    save(fig, "figure08_topsis_policy_priority_polished.png")


def main() -> None:
    configure_matplotlib()
    require_paths()
    plot_research_framework()
    plot_spatial_weight_robustness()
    plot_regional_heterogeneity()
    plot_policy_typology()
    plot_kmeans_typology()
    plot_topsis_priority()
    print(f"Exported polished previews to: {OUT_DIR}")


if __name__ == "__main__":
    main()
