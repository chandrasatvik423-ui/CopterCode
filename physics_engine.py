"""
physics_engine.py
-----------------
Structural screening engine.

IMPORTANT: This module performs computational SCREENING only.
It is NOT a finite-element analysis (FEA) tool and does NOT
constitute flight certification. All outputs are screening
candidates subject to physical testing.

Engineering assumptions:
  - Hollow rectangular beam in bending (Euler–Bernoulli)
  - Stress concentration factor Kt = 1.5 at arm root joint
    (documented assumption — not experimentally calibrated)
  - Hard landing modelled as 3× total weight per arm (impact factor assumption)
  - Material allowable stress loaded from config/materials.json
"""

import json
import os


def _load_materials() -> dict:
    path = os.path.join(os.path.dirname(__file__), "config", "materials.json")
    with open(path, "r") as f:
        return json.load(f)


def audit_structural_integrity(
    takeoff_mass_kg: float,
    arm_length_mm: float,
    arm_width_mm: float,
    arm_height_mm: float,
    cutout_width_mm: float,
    cutout_height_mm: float,
    max_motor_thrust_n: float,
    motor_count: int,
    material_name: str = "PLA"
) -> dict:
    """
    Evaluate structural safety factor for a hollow rectangular arm cross-section.

    Returns a dict containing all load cases, the governing case, nominal and
    corrected stress (MPa), allowable stress (MPa), and safety factor.
    """
    mats = _load_materials()
    mat = mats.get(material_name, mats["PLA"])
    allowable_stress_mpa = mat["allowable_stress_mpa"]

    # ── Cross-section moment of inertia (mm⁴) ───────────────────────────────
    # Hollow rectangular section: I_net = I_outer - I_inner
    I_outer = (arm_width_mm * (arm_height_mm ** 3)) / 12.0
    I_inner = (cutout_width_mm * (cutout_height_mm ** 3)) / 12.0
    I_net = I_outer - I_inner

    if I_net <= 0:
        # Degenerate cross-section (cutout equals or exceeds outer) → zero strength
        return {
            "load_cases_evaluated": ["HOVER", "MAX_THRUST", "HARD_LANDING"],
            "governing_load_case": "INVALID",
            "governing_force_n": 0.0,
            "nominal_stress_mpa": float("inf"),
            "corrected_stress_mpa": float("inf"),
            "allowable_stress_mpa": allowable_stress_mpa,
            "safety_factor": 0.0,
            "material": material_name,
        }

    weight_n = takeoff_mass_kg * 9.81
    c = arm_height_mm / 2.0                             # distance to extreme fibre (mm)

    # ── Load cases ────────────────────────────────────────────────────────────
    # Engineering assumption: load is shared equally between all arms.
    hover_force_n   = weight_n / motor_count
    max_thrust_n    = max_motor_thrust_n                # per-motor value passed in
    # Engineering assumption: hard landing = 3× total weight shared over all arms.
    hard_landing_n  = (weight_n * 3.0) / motor_count

    load_cases = {
        "HOVER":        hover_force_n,
        "MAX_THRUST":   max_thrust_n,
        "HARD_LANDING": hard_landing_n,
    }
    governing_case  = max(load_cases, key=load_cases.get)
    governing_force = load_cases[governing_case]

    # ── Bending stress (mm-based, result in MPa = N/mm²) ─────────────────────
    bending_moment_n_mm = governing_force * arm_length_mm
    nominal_stress_mpa  = (bending_moment_n_mm * c) / I_net

    # Stress concentration factor at motor-mount root joint (engineering assumption)
    KT = 1.5
    corrected_stress_mpa = nominal_stress_mpa * KT

    safety_factor = (
        allowable_stress_mpa / corrected_stress_mpa
        if corrected_stress_mpa > 0
        else float("inf")
    )

    return {
        "load_cases_evaluated": list(load_cases.keys()),
        "governing_load_case": governing_case,
        "governing_force_n": round(governing_force, 2),
        "nominal_stress_mpa": round(nominal_stress_mpa, 2),
        "corrected_stress_mpa": round(corrected_stress_mpa, 2),
        "allowable_stress_mpa": allowable_stress_mpa,
        "safety_factor": round(safety_factor, 2),
        "material": material_name,
    }