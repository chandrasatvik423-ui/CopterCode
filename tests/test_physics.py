import pytest
from physics_engine import audit_structural_integrity
from pipeline import run_pipeline

def test_stress_concentration_factor_applied():
    """
    Validates deterministic calculation of stress and safety factor.
    Inputs: L=100mm, W=30mm, H=5mm, F=14.7N, solid beam (cutouts=0).
    With Kt=1.5: governing force = MAX_THRUST = 14.7N.
    M = 14.7 * 0.1 = 1.47 Nm. I = (0.03 * 0.005^3)/12 = 3.125e-10 m^4.
    sigma_base = 1.47 * 0.0025 / 3.125e-10 = 11.76 MPa.
    sigma_corrected = 11.76 * 1.5 = 17.64 MPa. SF = 30 / 17.64 = 1.70.
    """
    audit = audit_structural_integrity(
        takeoff_mass_kg=0.5,
        arm_length_mm=100.0,
        arm_width_mm=30.0,
        arm_height_mm=5.0,
        cutout_width_mm=0.0,
        cutout_height_mm=0.0,
        max_motor_thrust_n=14.7,
        motor_count=4
    )
    assert audit["corrected_stress_mpa"] == 17.64
    assert audit["safety_factor"] == 1.70

def fake_parser_standard(prompt):
    return {"drone_type": "standard drone", "diagonal_mm": 220.0, "payload_mass_g": 0.0, "mission": "standard"}

def test_frame_mass_is_float():
    """Ensures downstream mass outputs return numeric types."""
    result = run_pipeline("standard drone", requirements_parser=fake_parser_standard)
    assert "mass" in result, f"Pipeline failed early: {result.get('status')} - {result.get('blocking_reasons')}"
    assert isinstance(result["mass"]["frame_mass_g"], float)