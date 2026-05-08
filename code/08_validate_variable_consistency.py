"""Validate core variable formulas and spatial auxiliary files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data_processed" / "panel_data.csv"
TABLE_PATH = ROOT / "tables" / "table00b_variable_consistency_audit.csv"
SPATIAL_DIR = ROOT / "data_raw" / "spatial"
REGION_GROUPS_PATH = ROOT / "data_raw" / "region_groups.csv"


def audit_row(item: str, passed: bool, detail: str) -> dict[str, object]:
    return {"item": item, "passed": bool(passed), "detail": detail}


def main() -> None:
    panel = pd.read_csv(PANEL_PATH)
    rows = []

    carbon_recalc = panel["carbon_emissions_mt"] * 100 / panel["gdp_real"]
    rows.append(
        audit_row(
            "carbon_intensity = carbon_emissions_mt * 100 / gdp_real",
            np.allclose(panel["carbon_intensity"], carbon_recalc, rtol=1e-10, atol=1e-10),
            f"max_abs_diff={(panel['carbon_intensity'] - carbon_recalc).abs().max():.12g}",
        )
    )

    energy_recalc = panel["coal_related_tce"] / panel["total_energy_tce"]
    rows.append(
        audit_row(
            "energy_structure = coal_related_tce / total_energy_tce",
            np.allclose(panel["energy_structure"], energy_recalc, rtol=1e-10, atol=1e-10),
            f"max_abs_diff={(panel['energy_structure'] - energy_recalc).abs().max():.12g}",
        )
    )

    innovation_recalc = np.log1p(panel["patent_grants"])
    rows.append(
        audit_row(
            "innovation = ln(1 + patent_grants)",
            np.allclose(panel["innovation"], innovation_recalc, rtol=1e-10, atol=1e-10),
            f"max_abs_diff={(panel['innovation'] - innovation_recalc).abs().max():.12g}",
        )
    )

    base_2011 = panel[panel["year"] == 2011]
    rows.append(
        audit_row(
            "gdp_real base year equals 2011 nominal GDP",
            np.allclose(base_2011["gdp_real"], base_2011["gdp_nominal"], rtol=1e-10, atol=1e-10),
            f"max_abs_diff={(base_2011['gdp_real'] - base_2011['gdp_nominal']).abs().max():.12g}",
        )
    )

    chained = []
    for province, group in panel.sort_values(["province", "year"]).groupby("province"):
        previous_real = None
        for _, row in group.iterrows():
            if row["year"] == 2011:
                previous_real = row["gdp_real"]
                continue
            expected = previous_real * row["gdp_index_previous_year_100"] / 100
            chained.append(abs(row["gdp_real"] - expected))
            previous_real = row["gdp_real"]
    rows.append(
        audit_row(
            "gdp_real chain calculation uses previous year index",
            max(chained) < 1e-8,
            f"max_abs_diff={max(chained):.12g}",
        )
    )

    panel_provinces = set(panel["province"].unique())
    expected_edges = len(panel_provinces) * (len(panel_provinces) - 1)
    for filename in [
        "spatial_weights.csv",
        "spatial_weights_geo_distance.csv",
        "spatial_weights_economic_distance.csv",
    ]:
        path = SPATIAL_DIR / filename
        weights = pd.read_csv(path)
        weight_provinces = set(weights["province_i"]) | set(weights["province_j"])
        if filename == "spatial_weights.csv":
            passed = weight_provinces == panel_provinces and weights["weight"].notna().all()
            detail = f"rows={len(weights)}, province_count={len(weight_provinces)}"
        else:
            passed = (
                weight_provinces == panel_provinces
                and len(weights) == expected_edges
                and weights["weight"].notna().all()
                and (weights["weight"] > 0).all()
            )
            detail = f"rows={len(weights)}, expected_rows={expected_edges}, province_count={len(weight_provinces)}"
        rows.append(audit_row(f"{filename} matches panel provinces", passed, detail))

    region_groups = pd.read_csv(REGION_GROUPS_PATH)
    rows.append(
        audit_row(
            "region_groups.csv matches panel provinces",
            set(region_groups["province"]) == panel_provinces
            and region_groups["province"].nunique() == len(panel_provinces)
            and region_groups["region"].notna().all(),
            f"rows={len(region_groups)}, regions={','.join(sorted(region_groups['region'].unique()))}",
        )
    )

    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(TABLE_PATH, index=False, encoding="utf-8-sig")
    print(f"Exported audit table: {TABLE_PATH}")


if __name__ == "__main__":
    main()
