import pytest
from physics_engine import audit_structural_integrity

def test_max_thrust_governs_light_racing_drone():
    # 500g drone, 4 motors, 14.7N max thrust per motor. 
    # Hover = 1.22N, Hard Landing = 3.67N, Max Thrust = 14.7N
    audit = audit_structural_integrity(
        takeoff_mass_kg=0.5, arm_length_mm=100.0, arm_width_mm=30.0, 
        arm_height_mm=5.0, cutout_width_mm=10.0, cutout_height_mm=5.0, 
        max_motor_thrust_n=14.7, motor_count=4
    )
    assert audit["governing_load_case"] == "MAX_THRUST"
    assert audit["governing_force_n"] == 14.7

def test_hard_landing_governs_heavy_cargo_drone():
    # 25kg drone, 8 motors, 25.0N max thrust per motor.
    # Hover = 30.6N, Hard Landing = 91.9N, Max Thrust = 25.0N
    audit = audit_structural_integrity(
        takeoff_mass_kg=25.0, arm_length_mm=350.0, arm_width_mm=40.0, 
        arm_height_mm=20.0, cutout_width_mm=20.0, cutout_height_mm=20.0, 
        max_motor_thrust_n=25.0, motor_count=8
    )
    assert audit["governing_load_case"] == "HARD_LANDING"
    assert audit["governing_force_n"] == 91.97