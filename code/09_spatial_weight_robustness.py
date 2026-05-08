"""Spatial weights robustness checks for spatial econometric models.

This script compares the key SAR, SEM, and SDM coefficients under three
spatial weights matrices: adjacency, inverse geographic distance, and inverse
economic distance. The goal is to test whether the spatial model conclusions
depend on the weights matrix definition.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from libpysal.weights import W
from spreg import ML_Error, ML_Lag

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLES_DIR = ROOT / "tables"
OUT_PATH = TABLES_DIR / "table09_spatial_weight_robustness.csv"

WEIGHT_SPECS = [
    ("adjacency", ROOT / "data_raw" / "spatial_weights.csv"),
    ("geo_distance", ROOT / "data_raw" / "spatial" / "spatial_weights_geo_distance.csv"),
    ("economic_distance", ROOT / "data_raw" / "spatial" / "spatial_weights_economic_distance.csv"),
]

DEPENDENT_VAR = "carbon_intensity"
CORE_VAR = "digital_finance"
CONTROL_VARS = [
    "gdp_per_capita",
    "industrial_structure",
    "urbanization",
    "government_intervention",
    "innovation",
    "energy_structure",
]
MODEL_VARS = [CORE_VAR] + CONTROL_VARS


def load_panel_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel data: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    required = ["province", "year", DEPENDENT_VAR] + MODEL_VARS
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing panel columns: {missing}")
    model_df = df.dropna(subset=required).copy()
    if model_df.empty:
        raise ValueError("No complete observations available for spatial weights robustness checks.")
    return model_df.sort_values(["year", "province"]).reset_index(drop=True)


def load_spatial_weights(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing spatial weights: {path}")
    weights = pd.read_csv(path)
    required = ["province_i", "province_j", "weight"]
    missing = [col for col in required if col not in weights.columns]
    if missing:
        raise ValueError(f"Missing spatial weight columns in {path}: {missing}")
    if weights.empty:
        raise ValueError(f"Spatial weights file is empty: {path}")
    return weights


def build_panel_weights(df: pd.DataFrame, weights: pd.DataFrame) -> W:
    """Build block-diagonal yearly spatial weights for the pooled panel."""
    obs_index = {(row.year, row.province): idx for idx, row in df.iterrows()}
    neighbors = {idx: [] for idx in range(len(df))}
    neighbor_weights = {idx: [] for idx in range(len(df))}

    for year in sorted(df["year"].unique()):
        for _, row in weights.iterrows():
            source = obs_index.get((year, row["province_i"]))
            target = obs_index.get((year, row["province_j"]))
            if source is None or target is None:
                continue
            neighbors[source].append(target)
            neighbor_weights[source].append(float(row["weight"]))

    isolated = [idx for idx, values in neighbors.items() if not values]
    if isolated:
        examples = df.loc[isolated[:5], ["province", "year"]].to_dict("records")
        raise ValueError(f"Spatial weights contain isolated observations: {examples}")

    panel_w = W(neighbors, neighbor_weights, silence_warnings=True)
    panel_w.transform = "r"
    return panel_w


def build_model_arrays(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    year_dummies = pd.get_dummies(df["year"].astype(str), prefix="year", drop_first=True, dtype=float)
    x_df = pd.concat([df[MODEL_VARS].astype(float), year_dummies], axis=1)
    y = df[[DEPENDENT_VAR]].to_numpy(dtype=float)
    x = x_df.to_numpy(dtype=float)
    return y, x, x_df.columns.tolist()


def extract_key_row(weight_name: str, weight_path: Path, model_name: str, result, term: str) -> dict[str, object]:
    output = result.output.set_index("var_names")
    if term not in output.index:
        raise ValueError(f"Term {term} not found in {model_name} output for {weight_name}.")
    row = output.loc[term]
    return {
        "weight_name": weight_name,
        "weight_file": str(weight_path.relative_to(ROOT)),
        "model": model_name,
        "key_term": term,
        "coefficient": float(row["coefficients"]),
        "std_err": float(row["std_err"]),
        "z_or_t_stat": float(row["zt_stat"]),
        "p_value": float(row["prob"]),
        "aic": float(getattr(result, "aic", np.nan)),
        "log_likelihood": float(getattr(result, "logll", np.nan)),
        "n_obs": int(getattr(result, "n", 0)),
        "interpretation_note": interpretation_note(model_name, term),
    }


def interpretation_note(model_name: str, term: str) -> str:
    if model_name == "SAR" and term == f"W_{DEPENDENT_VAR}":
        return "Spatial dependence of carbon intensity."
    if model_name == "SEM" and term == "lambda":
        return "Spatial autocorrelation in the error term."
    if model_name == "SDM" and term == CORE_VAR:
        return "Local digital finance coefficient; do not interpret alone as total effect."
    if model_name == "SDM" and term == f"W_{CORE_VAR}":
        return "Spatial-lag digital finance coefficient; key spillover reference."
    return ""


def estimate_for_weights(weight_name: str, weight_path: Path, df: pd.DataFrame) -> list[dict[str, object]]:
    weights = load_spatial_weights(weight_path)
    panel_w = build_panel_weights(df, weights)
    y, x, x_names = build_model_arrays(df)
    slx_vars = [name in MODEL_VARS for name in x_names]

    sar = ML_Lag(
        y,
        x,
        w=panel_w,
        name_y=DEPENDENT_VAR,
        name_x=x_names,
        name_w=weight_name,
        name_ds="province_panel_2011_2022",
        spat_impacts="simple",
    )
    sem = ML_Error(
        y,
        x,
        w=panel_w,
        name_y=DEPENDENT_VAR,
        name_x=x_names,
        name_w=weight_name,
        name_ds="province_panel_2011_2022",
    )
    sdm = ML_Lag(
        y,
        x,
        w=panel_w,
        slx_lags=1,
        slx_vars=slx_vars,
        name_y=DEPENDENT_VAR,
        name_x=x_names,
        name_w=weight_name,
        name_ds="province_panel_2011_2022",
        spat_impacts="simple",
    )

    return [
        extract_key_row(weight_name, weight_path, "SAR", sar, f"W_{DEPENDENT_VAR}"),
        extract_key_row(weight_name, weight_path, "SEM", sem, "lambda"),
        extract_key_row(weight_name, weight_path, "SDM", sdm, CORE_VAR),
        extract_key_row(weight_name, weight_path, "SDM", sdm, f"W_{CORE_VAR}"),
    ]


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    rows = []
    for weight_name, weight_path in WEIGHT_SPECS:
        rows.extend(estimate_for_weights(weight_name, weight_path, df))

    result = pd.DataFrame(rows)
    result.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported spatial weights robustness checks: {OUT_PATH}")
    print("Main interpretation target: SDM W_digital_finance across weight matrices.")


if __name__ == "__main__":
    main()
