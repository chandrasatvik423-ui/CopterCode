import os
import pytest
from drone_generator import generate_drone_frame


def test_cad_generates_multi_hole_mount_pattern():
    """SCAD output must contain the 4 motor mount hole coordinates from the pattern."""
    test_pattern = {
        "type": "square",
        "spacing_mm": 16.0,
        "hole_diameter_mm": 3.0,
        "coordinates_mm": [[-8.0, -8.0], [8.0, -8.0], [8.0, 8.0], [-8.0, 8.0]]
    }

    generate_drone_frame(
        diagonal_mm=220.0,
        arm_width=30.0,
        arm_height=5.0,
        motor_diam=28.0,
        pcb_length=36.0,
        pcb_width=36.0,
        mount_pattern=test_pattern,
        drone_type="Test Drone",
        output_filename="test_multi_hole.stl",
        motor_count=4,
        screening_passed=True,
        auto_open=False,
    )

    scad_file = "test_multi_hole.scad"
    assert os.path.exists(scad_file), "SCAD file was not written"

    with open(scad_file, "r") as f:
        content = f.read()

    # Each hole coordinate should appear in the SCAD motor_cuts block
    assert "translate([-8.0, -8.0, 0])" in content, "Missing [-8,-8] motor hole"
    assert "translate([8.0, -8.0, 0])" in content, "Missing [8,-8] motor hole"
    assert "translate([8.0, 8.0, 0])" in content, "Missing [8,8] motor hole"
    assert "translate([-8.0, 8.0, 0])" in content, "Missing [-8,8] motor hole"
    assert "d=3.0" in content, "Hole diameter not written"