"""Policy typology enhancement with K-means and entropy-weight TOPSIS.

This script is an application-oriented supplement. K-means checks whether
the existing quadrant policy typology has multi-indicator support; TOPSIS
provides a policy-priority ranking. Neither result is causal evidence.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
POLICY_TYPOLOGY_PATH = ROOT / "tables" / "table12_policy_typology.csv"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

KMEANS_OUT = TABLES_DIR / "table13_kmeans_policy_typology_robustness.csv"
TOPSIS_OUT = TABLES_DIR / "table14_entropy_topsis_policy_priority.csv"
KMEANS_FIG = FIGURES_DIR / "figure07_kmeans_policy_typology_robustness.png"
TOPSIS_FIG = FIGURES_DIR / "figure08_topsis_policy_priority.png"

RANDOM_SEED = 2026
K_CLUSTERS = 4
KMEANS_FEATURES = ["digital_finance", "carbon_intensity", "energy_structure", "innovation"]
TOPSIS_POSITIVE = ["digital_finance", "innovation", "gdp_per_capita"]
TOPSIS_NEGATIVE = ["carbon_intensity", "energy_structure"]

POLICY_TYPE_COLORS = {
    "示范引领型": "#2ca25f",
    "转型压力型": "#de2d26",
    "稳态优化型": "#3182bd",
    "重点扶持型": "#fdae6b",
}

CLUSTER_COLORS = ["#2f6fbb", "#d95f02", "#1b9e77", "#7570b3"]

LABEL_OFFSET_CANDIDATES = [
    (6, 7),
    (-6, 7),
    (6, -8),
    (-6, -8),
    (14, 0),
    (-14, 0),
    (0, 14),
    (0, -14),
    (18, 9),
    (-18, 9),
    (18, -11),
    (-18, -11),
    (26, 0),
    (-26, 0),
]

LABEL_OFFSET_OVERRIDES = {
    "辽宁": (-12, 2),
    "陕西": (6, -9),
    "安徽": (-10, -8),
    "四川": (-7, -9),
    "江苏": (7, -9),
}


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


def style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    if not POLICY_TYPOLOGY_PATH.exists():
        raise FileNotFoundError(f"Missing policy typology table: {POLICY_TYPOLOGY_PATH}")
    panel = pd.read_csv(DATA_PATH)
    typology = pd.read_csv(POLICY_TYPOLOGY_PATH)
    required_panel = ["province", "year", *KMEANS_FEATURES, *TOPSIS_POSITIVE, *TOPSIS_NEGATIVE]
    missing_panel = sorted(set(required_panel) - set(panel.columns))
    if missing_panel:
        raise ValueError(f"Missing panel columns: {missing_panel}")
    required_typology = ["province", "region", "policy_type", "digital_threshold_median", "carbon_threshold_median"]
    missing_typology = sorted(set(required_typology) - set(typology.columns))
    if missing_typology:
        raise ValueError(f"Missing typology columns: {missing_typology}")
    return panel, typology[required_typology].drop_duplicates("province")


def build_province_means(panel: pd.DataFrame, typology: pd.DataFrame) -> pd.DataFrame:
    features = sorted(set(KMEANS_FEATURES + TOPSIS_POSITIVE + TOPSIS_NEGATIVE))
    grouped = panel.groupby("province", as_index=False).agg(
        start_year=("year", "min"),
        end_year=("year", "max"),
        **{f"{col}_mean": (col, "mean") for col in features},
    )
    result = grouped.merge(typology, on="province", how="left")
    missing = sorted(result.loc[result["policy_type"].isna(), "province"].tolist())
    if missing:
        raise ValueError(f"Missing policy typology for provinces: {missing}")
    if result["province"].nunique() != 30:
        raise ValueError(f"Expected 30 provinces, got {result['province'].nunique()}")
    return result


def zscore(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    if np.any(std == 0):
        zero_cols = [KMEANS_FEATURES[i] for i, value in enumerate(std) if value == 0]
        raise ValueError(f"Cannot standardize zero-variance columns: {zero_cols}")
    return (values - mean) / std, mean, std


def run_kmeans(values: np.ndarray, k: int = K_CLUSTERS, seed: int = RANDOM_SEED) -> tuple[np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(seed)
    initial_idx = rng.choice(values.shape[0], size=k, replace=False)
    centroids = values[initial_idx].copy()
    labels = np.zeros(values.shape[0], dtype=int)
    for _ in range(200):
        distances = ((values[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        new_labels = distances.argmin(axis=1)
        new_centroids = centroids.copy()
        for cluster in range(k):
            members = values[new_labels == cluster]
            if len(members) == 0:
                farthest = distances.min(axis=1).argmax()
                new_centroids[cluster] = values[farthest]
            else:
                new_centroids[cluster] = members.mean(axis=0)
        if np.array_equal(new_labels, labels) and np.allclose(new_centroids, centroids):
            break
        labels = new_labels
        centroids = new_centroids
    inertia = float(((values - centroids[labels]) ** 2).sum())
    return labels, centroids, inertia


def cluster_profile_label(row: pd.Series, digital_median: float, carbon_median: float) -> str:
    digital = "高数字金融" if row["digital_finance_mean"] >= digital_median else "低数字金融"
    carbon = "低碳压力" if row["carbon_intensity_mean"] < carbon_median else "高碳压力"
    return f"{digital}-{carbon}"


def build_kmeans_table(province_means: pd.DataFrame) -> pd.DataFrame:
    feature_cols = [f"{col}_mean" for col in KMEANS_FEATURES]
    standardized, _, _ = zscore(province_means[feature_cols].to_numpy(dtype=float))
    labels, _, inertia = run_kmeans(standardized)
    result = province_means.copy()
    result["kmeans_cluster"] = labels + 1

    cluster_summary = result.groupby("kmeans_cluster", as_index=False).agg(
        cluster_size=("province", "count"),
        digital_finance_mean=("digital_finance_mean", "mean"),
        carbon_intensity_mean=("carbon_intensity_mean", "mean"),
        energy_structure_mean=("energy_structure_mean", "mean"),
        innovation_mean=("innovation_mean", "mean"),
    )
    digital_median = float(result["digital_finance_mean"].median())
    carbon_median = float(result["carbon_intensity_mean"].median())
    cluster_summary["kmeans_profile"] = cluster_summary.apply(
        cluster_profile_label,
        axis=1,
        digital_median=digital_median,
        carbon_median=carbon_median,
    )

    dominant = (
        result.groupby(["kmeans_cluster", "policy_type"], as_index=False)
        .size()
        .sort_values(["kmeans_cluster", "size", "policy_type"], ascending=[True, False, True])
        .drop_duplicates("kmeans_cluster")
        .rename(columns={"policy_type": "dominant_quadrant_type", "size": "dominant_type_count"})
    )
    cluster_summary = cluster_summary.merge(dominant, on="kmeans_cluster", how="left")
    result = result.merge(
        cluster_summary[
            [
                "kmeans_cluster",
                "cluster_size",
                "kmeans_profile",
                "dominant_quadrant_type",
                "dominant_type_count",
            ]
        ],
        on="kmeans_cluster",
        how="left",
    )
    result["matches_dominant_quadrant"] = result["policy_type"] == result["dominant_quadrant_type"]
    result["kmeans_inertia"] = inertia
    result["random_seed"] = RANDOM_SEED
    columns = [
        "province",
        "region",
        "policy_type",
        "kmeans_cluster",
        "kmeans_profile",
        "dominant_quadrant_type",
        "matches_dominant_quadrant",
        "cluster_size",
        "dominant_type_count",
        "digital_finance_mean",
        "carbon_intensity_mean",
        "energy_structure_mean",
        "innovation_mean",
        "kmeans_inertia",
        "random_seed",
    ]
    return result[columns].sort_values(["kmeans_cluster", "policy_type", "province"]).reset_index(drop=True)


def minmax_orient(data: pd.DataFrame, positive_cols: list[str], negative_cols: list[str]) -> pd.DataFrame:
    oriented = pd.DataFrame(index=data.index)
    for col in positive_cols:
        series = data[col].astype(float)
        denom = series.max() - series.min()
        oriented[col] = 1.0 if denom == 0 else (series - series.min()) / denom
    for col in negative_cols:
        series = data[col].astype(float)
        denom = series.max() - series.min()
        oriented[col] = 1.0 if denom == 0 else (series.max() - series) / denom
    return oriented


def entropy_weights(oriented: pd.DataFrame) -> pd.Series:
    eps = 1e-12
    matrix = oriented.to_numpy(dtype=float) + eps
    proportions = matrix / matrix.sum(axis=0, keepdims=True)
    entropy = -(proportions * np.log(proportions)).sum(axis=0) / np.log(matrix.shape[0])
    diversity = 1 - entropy
    if np.isclose(diversity.sum(), 0):
        weights = np.full(matrix.shape[1], 1 / matrix.shape[1])
    else:
        weights = diversity / diversity.sum()
    return pd.Series(weights, index=oriented.columns)


def build_topsis_table(province_means: pd.DataFrame) -> pd.DataFrame:
    mean_cols = [f"{col}_mean" for col in TOPSIS_POSITIVE + TOPSIS_NEGATIVE]
    positive = [f"{col}_mean" for col in TOPSIS_POSITIVE]
    negative = [f"{col}_mean" for col in TOPSIS_NEGATIVE]
    oriented = minmax_orient(province_means[mean_cols], positive, negative)
    weights = entropy_weights(oriented)

    norm = np.sqrt((oriented**2).sum(axis=0))
    weighted = oriented.div(norm.replace(0, np.nan), axis=1).fillna(0).mul(weights, axis=1)
    positive_ideal = weighted.max(axis=0)
    negative_ideal = weighted.min(axis=0)
    d_positive = np.sqrt(((weighted - positive_ideal) ** 2).sum(axis=1))
    d_negative = np.sqrt(((weighted - negative_ideal) ** 2).sum(axis=1))
    score = d_negative / (d_positive + d_negative)

    result = province_means.copy()
    result["topsis_score"] = score
    result["topsis_rank"] = result["topsis_score"].rank(ascending=False, method="first").astype(int)
    result["topsis_group"] = pd.qcut(
        result["topsis_score"],
        q=3,
        labels=["重点提升优先", "稳步优化", "示范扩散优先"],
        duplicates="drop",
    )
    result["weight_digital_finance"] = weights["digital_finance_mean"]
    result["weight_innovation"] = weights["innovation_mean"]
    result["weight_gdp_per_capita"] = weights["gdp_per_capita_mean"]
    result["weight_carbon_intensity"] = weights["carbon_intensity_mean"]
    result["weight_energy_structure"] = weights["energy_structure_mean"]
    columns = [
        "province",
        "region",
        "policy_type",
        "topsis_rank",
        "topsis_score",
        "topsis_group",
        "digital_finance_mean",
        "innovation_mean",
        "gdp_per_capita_mean",
        "carbon_intensity_mean",
        "energy_structure_mean",
        "weight_digital_finance",
        "weight_innovation",
        "weight_gdp_per_capita",
        "weight_carbon_intensity",
        "weight_energy_structure",
    ]
    return result[columns].sort_values("topsis_rank").reset_index(drop=True)


def label_bbox(ax, x_value: float, y_value: float, province: str, offset: tuple[int, int]) -> tuple[float, float, float, float]:
    base_x, base_y = ax.transData.transform((x_value, y_value))
    scale = ax.figure.dpi / 72.0
    text_x = base_x + offset[0] * scale
    text_y = base_y + offset[1] * scale
    width = len(str(province)) * 12.0 + 10.0
    height = 16.0
    return (text_x - width / 2, text_y - height / 2, text_x + width / 2, text_y + height / 2)


def overlaps(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
    return not (first[2] < second[0] or first[0] > second[2] or first[3] < second[1] or first[1] > second[3])


def choose_label_offsets(ax, kmeans: pd.DataFrame) -> dict[str, tuple[int, int]]:
    coords = kmeans[["province", "digital_finance_mean", "carbon_intensity_mean"]].copy()
    x_std = coords["digital_finance_mean"].std()
    y_std = coords["carbon_intensity_mean"].std()
    x_std = 1.0 if pd.isna(x_std) or np.isclose(x_std, 0) else float(x_std)
    y_std = 1.0 if pd.isna(y_std) or np.isclose(y_std, 0) else float(y_std)
    values = coords[["digital_finance_mean", "carbon_intensity_mean"]].to_numpy(dtype=float)
    scaled = values / np.array([x_std, y_std])
    density_scores = []
    for idx, point in enumerate(scaled):
        distances = np.sqrt(((scaled - point) ** 2).sum(axis=1))
        density_scores.append(np.partition(distances, min(4, len(distances) - 1))[1:4].sum())
    coords["density_score"] = density_scores
    coords = coords.sort_values(["density_score", "carbon_intensity_mean"], ascending=[True, False])

    placed: list[tuple[float, float, float, float]] = []
    offsets: dict[str, tuple[int, int]] = {}
    for _, row in coords.iterrows():
        province = row["province"]
        x_value = float(row["digital_finance_mean"])
        y_value = float(row["carbon_intensity_mean"])
        best_offset = LABEL_OFFSET_CANDIDATES[0]
        best_overlap_count = len(placed) + 1
        for candidate in LABEL_OFFSET_CANDIDATES:
            bbox = label_bbox(ax, x_value, y_value, province, candidate)
            overlap_count = sum(overlaps(bbox, existing) for existing in placed)
            if overlap_count < best_overlap_count:
                best_offset = candidate
                best_overlap_count = overlap_count
            if overlap_count == 0:
                break
        offsets[province] = best_offset
        placed.append(label_bbox(ax, x_value, y_value, province, best_offset))
    return offsets


def plot_kmeans(kmeans: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    for cluster, group in kmeans.groupby("kmeans_cluster"):
        color = CLUSTER_COLORS[(int(cluster) - 1) % len(CLUSTER_COLORS)]
        ax.scatter(
            group["digital_finance_mean"],
            group["carbon_intensity_mean"],
            s=62,
            color=color,
            edgecolor="#374151",
            linewidth=0.45,
            alpha=0.88,
            label=f"聚类{int(cluster)}：{group['kmeans_profile'].iloc[0]}",
        )
    x_threshold = float(kmeans["digital_finance_mean"].median())
    y_threshold = float(kmeans["carbon_intensity_mean"].median())
    ax.axvline(x_threshold, color="#111827", linewidth=0.8, linestyle="--", label="数字金融中位数")
    ax.axhline(y_threshold, color="#6b7280", linewidth=0.8, linestyle=":", label="碳强度中位数")

    x_min = float(kmeans["digital_finance_mean"].min())
    x_max = float(kmeans["digital_finance_mean"].max())
    y_min = float(kmeans["carbon_intensity_mean"].min())
    y_max = float(kmeans["carbon_intensity_mean"].max())
    x_pad = (x_max - x_min) * 0.10
    y_pad = (y_max - y_min) * 0.08
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_max + y_pad)

    label_offsets = choose_label_offsets(ax, kmeans)
    available_provinces = set(kmeans["province"])
    label_offsets.update(
        {province: offset for province, offset in LABEL_OFFSET_OVERRIDES.items() if province in available_provinces}
    )
    for _, row in kmeans.iterrows():
        province = row["province"]
        offset = label_offsets[province]
        ax.annotate(
            province,
            xy=(row["digital_finance_mean"], row["carbon_intensity_mean"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=6.3,
            ha="center",
            va="center",
            color="#111827",
            bbox=dict(boxstyle="round,pad=0.08", fc="white", ec="#eef2f7", alpha=0.82),
            arrowprops=dict(arrowstyle="-", color="#9ca3af", linewidth=0.35, shrinkA=0, shrinkB=3),
        )
    ax.set_xlabel("数字普惠金融指数均值")
    ax.set_ylabel("碳强度均值")
    ax.legend(loc="upper right", fontsize=7.0)
    style_axes(ax)
    plt.tight_layout()
    plt.savefig(KMEANS_FIG, dpi=300, bbox_inches="tight")
    plt.close()


def plot_topsis(topsis: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    ordered = topsis.sort_values("topsis_score", ascending=True)
    colors = [POLICY_TYPE_COLORS.get(value, "#6b7280") for value in ordered["policy_type"]]
    fig, ax = plt.subplots(figsize=(7.2, 7.4))
    ax.barh(ordered["province"], ordered["topsis_score"], color=colors, edgecolor="#374151", linewidth=0.35)
    ax.set_xlabel("熵权 TOPSIS 综合贴近度")
    ax.set_ylabel("省份")
    style_axes(ax)
    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", markerfacecolor=color, markeredgecolor=color, label=label)
        for label, color in POLICY_TYPE_COLORS.items()
        if label in set(topsis["policy_type"])
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=7.8)
    plt.tight_layout()
    plt.savefig(TOPSIS_FIG, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    configure_matplotlib()
    panel, typology = load_inputs()
    province_means = build_province_means(panel, typology)

    kmeans = build_kmeans_table(province_means)
    topsis = build_topsis_table(province_means)
    kmeans.to_csv(KMEANS_OUT, index=False, encoding="utf-8-sig")
    topsis.to_csv(TOPSIS_OUT, index=False, encoding="utf-8-sig")
    plot_kmeans(kmeans)
    plot_topsis(topsis)

    print(f"Exported K-means robustness table: {KMEANS_OUT}")
    print(f"Exported entropy TOPSIS table: {TOPSIS_OUT}")
    print(f"Exported figures: {KMEANS_FIG}, {TOPSIS_FIG}")


if __name__ == "__main__":
    main()
