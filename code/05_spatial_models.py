"""Spatial econometric models for carbon intensity.

This script estimates pooled spatial econometric models on the province-year
panel. The spatial weights connect provinces within the same year only, so the
model captures cross-province spatial dependence without linking observations
across different years.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from libpysal.weights import W
from spreg import ML_Error, ML_Lag

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data_processed" / "panel_data.csv"
WEIGHTS_PATH = ROOT / "data_raw" / "spatial_weights.csv"
TABLES_DIR = ROOT / "tables"
OUT_COMPARISON = TABLES_DIR / "table05_spatial_model_comparison.csv"
OUT_EFFECTS = TABLES_DIR / "table06_spatial_effect_decomposition.csv"

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
        raise ValueError("No complete observations available for spatial models.")
    return model_df.sort_values(["year", "province"]).reset_index(drop=True)


def load_spatial_weights() -> pd.DataFrame:
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Missing spatial weights: {WEIGHTS_PATH}")
    weights = pd.read_csv(WEIGHTS_PATH)
    required = ["province_i", "province_j", "weight"]
    missing = [col for col in required if col not in weights.columns]
    if missing:
        raise ValueError(f"Missing spatial weight columns: {missing}")
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


def collect_model_rows(model_name: str, result) -> list[dict[str, object]]:
    output = result.output.copy()
    output["model"] = model_name
    output["aic"] = float(getattr(result, "aic", np.nan))
    output["log_likelihood"] = float(getattr(result, "logll", np.nan))
    output["n_obs"] = int(getattr(result, "n", 0))
    return output[
        ["model", "var_names", "coefficients", "std_err", "zt_stat", "prob", "aic", "log_likelihood", "n_obs"]
    ].to_dict("records")


def export_effect_decomposition(sdm_result) -> pd.DataFrame:
    """Export a transparent first-pass SDM effect table.

    The spreg simple impacts multiplier gives the spatial feedback multiplier
    for the spatially lagged dependent variable. For SDM, the W_x coefficient is
    also reported so the paper can distinguish local and neighboring effects.
    """
    output = sdm_result.output.set_index("var_names")
    multiplier = getattr(sdm_result, "sp_multipliers", {}).get("simple", (1.0, np.nan, np.nan))
    indirect_multiplier = float(multiplier[1])
    total_multiplier = float(multiplier[2])
    records = []

    for var in MODEL_VARS:
        local_coef = float(output.loc[var, "coefficients"])
        local_p = float(output.loc[var, "prob"])
        w_var = f"W_{var}"
        spillover_coef = float(output.loc[w_var, "coefficients"]) if w_var in output.index else np.nan
        spillover_p = float(output.loc[w_var, "prob"]) if w_var in output.index else np.nan
        records.append(
            {
                "variable": var,
                "local_coefficient": local_coef,
                "local_p_value": local_p,
                "spatial_lag_coefficient": spillover_coef,
                "spatial_lag_p_value": spillover_p,
                "simple_indirect_multiplier": indirect_multiplier,
                "simple_total_multiplier": total_multiplier,
                "interpretation_note": "local coefficient is X effect; spatial_lag_coefficient is W_X spillover term",
            }
        )

    effects = pd.DataFrame(records)
    effects.to_csv(OUT_EFFECTS, index=False, encoding="utf-8-sig")
    return effects


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel_data()
    weights = load_spatial_weights()
    panel_w = build_panel_weights(df, weights)
    y, x, x_names = build_model_arrays(df)
    slx_vars = [name in MODEL_VARS for name in x_names]

    sar = ML_Lag(
        y,
        x,
        w=panel_w,
        name_y=DEPENDENT_VAR,
        name_x=x_names,
        name_w="yearly_adjacency",
        name_ds="province_panel_2011_2022",
        spat_impacts="simple",
    )
    sem = ML_Error(
        y,
        x,
        w=panel_w,
        name_y=DEPENDENT_VAR,
        name_x=x_names,
        name_w="yearly_adjacency",
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
        name_w="yearly_adjacency",
        name_ds="province_panel_2011_2022",
        spat_impacts="simple",
    )

    rows = []
    rows.extend(collect_model_rows("SAR", sar))
    rows.extend(collect_model_rows("SEM", sem))
    rows.extend(collect_model_rows("SDM", sdm))
    comparison = pd.DataFrame(rows)
    comparison.to_csv(OUT_COMPARISON, index=False, encoding="utf-8-sig")
    export_effect_decomposition(sdm)

    print(f"Exported spatial model comparison: {OUT_COMPARISON}")
    print(f"Exported SDM effect table: {OUT_EFFECTS}")
    print("Main interpretation target: SDM W_digital_finance for spatial spillover.")


if __name__ == "__main__":
    main()
