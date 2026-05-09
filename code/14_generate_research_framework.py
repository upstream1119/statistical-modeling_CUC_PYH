"""Generate a polished research framework and technical route figure."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "figures"
OUT_PATH = FIGURES_DIR / "figure00_research_framework.png"


def setup_font() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def box(ax, x, y, w, h, text, fc, ec, fs=10, weight="normal", ls="-", radius=0.045):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.025,rounding_size={radius}",
        linewidth=1.15,
        linestyle=ls,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        weight=weight,
        color="#172033",
        linespacing=1.22,
        wrap=True,
    )


def arrow(ax, x1, y1, x2, y2, color="#9aa4b2", lw=1.15, scale=12):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=scale,
            linewidth=lw,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def main() -> None:
    setup_font()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12.4, 7.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0.85, 7.6)
    ax.axis("off")

    # Palette.
    red, red_bg = "#dc2626", "#fff5f5"
    blue, blue_mid, blue_bg = "#2563eb", "#60a5fa", "#f8fbff"
    orange, orange_bg = "#ea580c", "#fff7ed"
    green, green_bg = "#059669", "#ecfdf5"
    grey, grey_bg = "#9ca3af", "#f9fafb"

    # Column headers.
    box(ax, 0.35, 6.95, 2.15, 0.42, "研究逻辑", red_bg, red, fs=12.5, weight="bold")
    box(ax, 3.0, 6.95, 5.95, 0.42, "技术路线", "#eff6ff", blue, fs=12.5, weight="bold")
    box(ax, 9.55, 6.95, 2.1, 0.42, "方法体系", orange_bg, orange, fs=12.5, weight="bold")

    # Geometry.
    y_vals = [6.15, 5.15, 4.15, 3.15, 2.15, 1.15]
    h = 0.66

    left = [
        "问题提出\n双碳目标与数字金融",
        "文献梳理\n识别研究缺口",
        "理论机制\n创新与能源结构路径",
        "实证识别\n空间依赖与异质性",
        "政策转化\n分型治理与协同优化",
        "结论形成\n研究发现与应用输出",
    ]
    mid_titles = [
        "研究问题凝练",
        "数据与变量构造",
        "基础实证分析",
        "空间计量识别",
        "拓展与稳健性",
        "结论与政策输出",
    ]
    mid_bodies = [
        "国家战略背景  →  数字普惠金融  →  区域低碳转型",
        "2011-2022年30省面板  →  碳强度与核心变量  →  空间权重矩阵",
        "数据质量审计  →  描述统计与相关性  →  基准回归",
        "Moran's I 空间自相关  →  SAR / SEM / SDM  →  邻接矩阵主模型",
        "权重矩阵替换  →  区域异质性  →  机制路径检验",
        "研究发现归纳  →  数字金融-碳强度分型  →  区域协同治理",
    ]
    right = [
        "文献归纳\n比较分析",
        "变量构造\n一致性审计",
        "OLS回归\nHC1稳健标准误",
        "Moran's I\nSAR / SEM / SDM",
        "稳健性检验\n异质性回归\n机制路径检验",
        "四象限分型\n政策建议",
    ]

    for i, y in enumerate(y_vals):
        box(ax, 0.3, y, 2.25, h, left[i], red_bg, "#ef4444", fs=9.2, ls="--")
        box(ax, 3.0, y - 0.02, 5.95, h + 0.04, "", blue_bg, blue_mid)
        ax.text(3.22, y + 0.43, mid_titles[i], ha="left", va="center", fontsize=11.0, weight="bold", color="#1d4ed8")
        ax.text(3.22, y + 0.20, mid_bodies[i], ha="left", va="center", fontsize=8.75, color="#263244")
        box(ax, 9.45, y, 2.25, h, right[i], orange_bg, orange, fs=9.15)

        if i < len(y_vals) - 1:
            arrow(ax, 1.43, y, 1.43, y_vals[i + 1] + h, color="#ef4444", lw=1.05, scale=11)
            arrow(ax, 5.98, y - 0.02, 5.98, y_vals[i + 1] + h + 0.02, color=blue, lw=1.25, scale=12)
        arrow(ax, 2.58, y + h / 2, 3.0, y + h / 2, color="#b8c0cc", lw=1.1, scale=11)
        arrow(ax, 8.95, y + h / 2, 9.45, y + h / 2, color="#b8c0cc", lw=1.1, scale=11)

    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight", pad_inches=0.16)
    plt.close(fig)
    print(f"Exported polished research framework figure: {OUT_PATH}")


if __name__ == "__main__":
    main()
