"""
manufacturing_estimator.py
---------------------------
Geometry-driven frame mass and cost estimator.

All material constants (density, cost, print rate) are loaded from
config/materials.json to prevent inline magic numbers.

ASSUMPTIONS (see docs/ENGINEERING_ASSUMPTIONS.md):
  - Frame volume is approximated as: (arm prismatic beams) + (central PCB body)
  - A 50% fill-factor reduction accounts for the hollow channel along each arm
  - Central body modelled as a flat plate of uniform thickness equal to arm_height_mm
"""

import json
import os


def _load_materials() -> dict:
    path = os.path.join(os.path.dirname(__file__), "config", "materials.json")
    with open(path, "r") as f:
        return json.load(f)


def estimate_build_cost(
    diagonal_mm: float,
    arm_width_mm: float,
    arm_height_mm: float,
    pcb_length: float,
    pcb_width: float,
    motor_count: int = 4,
    material_name: str = "PLA",
) -> dict:
    """
    Estimate frame mass (g), material cost (USD), and FDM print time (hours).

    Parameters
    ----------
    diagonal_mm    : motor-to-motor diagonal distance (mm)
    arm_width_mm   : arm cross-section width (mm)
    arm_height_mm  : arm cross-section height (mm)
    pcb_length     : central body length (mm)
    pcb_width      : central body width (mm)
    motor_count    : number of arms
    material_name  : key into config/materials.json (default "PLA")
    """
    mats = _load_materials()
    mat = mats.get(material_name, mats["PLA"])

    density_g_cm3   = mat["density_g_cm3"]
    cost_per_kg_usd = mat["cost_per_kg_usd"]
    print_rate_g_hr = mat["print_rate_g_hr"]

    # ── Arm volume ────────────────────────────────────────────────────────────
    arm_length_mm = diagonal_mm / 2.0
    solid_arm_vol_mm3  = arm_length_mm * arm_width_mm * arm_height_mm
    # 50 % fill factor: wire-routing channel runs half the arm length
    cutout_fraction    = 0.50 * 0.35          # 50% of length × 35% of cross-section
    arm_vol_mm3        = solid_arm_vol_mm3 * (1.0 - cutout_fraction)

    # ── Central body volume ───────────────────────────────────────────────────
    # Flat plate: PCB footprint × arm height (uniform slab assumption)
    body_vol_mm3 = pcb_length * pcb_width * arm_height_mm

    total_vol_mm3 = (motor_count * arm_vol_mm3) + body_vol_mm3
    total_vol_cm3 = total_vol_mm3 / 1000.0

    weight_g       = total_vol_cm3 * density_g_cm3
    cost_usd       = (weight_g / 1000.0) * cost_per_kg_usd
    print_time_hrs = weight_g / print_rate_g_hr if print_rate_g_hr > 0 else 0.0

    return {
        "material":           material_name,
        "weight_g":           round(weight_g, 1),
        "material_cost_usd":  round(cost_usd, 2),
        "print_time_hrs":     round(print_time_hrs, 1),
    }