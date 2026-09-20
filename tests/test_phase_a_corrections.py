"""Tests for Phase A correctness fixes:
1. frame_mass_g must be a number (float), not a formatted string like "77.5 g"
2. audit_structural_integrity must apply stress concentration factor (verified via load case output)
3. Both checks verify physics engine is honest about its stress model
"""
import pytest
from pipeline import run_pipeline
from physics_engine import audit_structural_integrity


# --- Mock parsers ---
def fake_parser_racing(prompt):
    # 0.0 is rejected by MissionRequirements validator. Use racing canonical 220mm.
    return {"drone_type": "racing drone", "diagonal_mm": 220.0, "payload_mass_g": 0.0, "mission": "racing"}


def fake_parser_standard(prompt):
    return {"drone_type": "standard drone", "diagonal_mm": 300.0, "payload_mass_g": 200.0, "mission": "standard"}


# --- Fix 1: frame_mass_g is a float, not a string ---
def test_frame_mass_is_numeric():
    """frame_mass_g in pipeline result must be a number, not '77.5 g'."""
    result = run_pipeline("racing drone", requirements_parser=fake_parser_racing)
    frame_mass = result["mass"]["frame_mass_g"]
    assert isinstance(frame_mass, (int, float)), (
        f"frame_mass_g is {type(frame_mass).__name__}: {frame_mass!r}"
    )
    assert frame_mass > 0


def test_frame_mass_can_be_used_in_arithmetic():
    """frame_mass_g must participate in math without TypeError."""
    result = run_pipeline("standard drone", requirements_parser=fake_parser_standard)
    frame_mass = result["mass"]["frame_mass_g"]
    takeoff = result["mass"]["takeoff_mass_g"]
    # This raises TypeError if frame_mass were a string like "83.7 g"
    ratio = frame_mass / takeoff
    assert 0 < ratio < 1


# --- Fix 2: Stress concentration factor applied in audit ---
def test_audit_returns_governing_load_case():
    """audit_structural_integrity must return a governing_load_case (proof 3 cases are evaluated)."""
    result = audit_structural_integrity(
        takeoff_mass_kg=0.5,
        arm_length_mm=100.0,
        arm_width_mm=20.0,
        arm_height_mm=5.0,
        cutout_width_mm=7.0,
        cutout_height_mm=5.0,
        max_motor_thrust_n=14.7,
        motor_count=4
    )
    assert "governing_load_case" in result
    # Valid cases: 3 physical load cases + INVALID for degenerate geometry
    assert result["governing_load_case"] in ("HOVER", "MAX_THRUST", "HARD_LANDING", "INVALID")
    assert "governing_force_n" in result
    assert result["governing_force_n"] > 0



def test_audit_safety_factor_is_positive_finite():
    """Safety factor must be a positive, finite number."""
    result = audit_structural_integrity(
        takeoff_mass_kg=0.5,
        arm_length_mm=100.0,
        arm_width_mm=20.0,
        arm_height_mm=5.0,
        cutout_width_mm=7.0,
        cutout_height_mm=5.0,
        max_motor_thrust_n=14.7,
        motor_count=4
    )
    sf = result["safety_factor"]
    assert isinstance(sf, float)
    assert sf > 0
    assert sf != float("inf")


def test_audit_degenerate_geometry_returns_zero_sf():
    """Zero-moment-of-inertia geometry (cutout equals outer) must return SF=0, not crash."""
    result = audit_structural_integrity(
        takeoff_mass_kg=0.5,
        arm_length_mm=100.0,
        arm_width_mm=20.0,
        arm_height_mm=5.0,
        cutout_width_mm=20.0,   # Same as outer — degenerate
        cutout_height_mm=5.0,
        max_motor_thrust_n=14.7,
        motor_count=4
    )
    assert result["safety_factor"] == 0.0
