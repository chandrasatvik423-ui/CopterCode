import pytest
from dfm_engine import verify_dfm
from pipeline import run_pipeline

def test_dfm_rejects_thin_walls():
    res = verify_dfm(arm_width_mm=10.0, cutout_width_mm=8.0, mount_pattern={}, printer_profile={"min_wall_mm": 1.2})
    assert res["status"] == "DFM_FAILED"
    assert any("Wall thickness" in issue for issue in res["issues"])

def test_dfm_rejects_fastener_edge_violation():
    # Motor pattern requires holes at +/- 8mm. 
    # Hole radius is 1.5mm. Outermost edge of hole is at 9.5mm.
    # An arm width of 15.0mm (radius 7.5mm) means the hole physically breaks out of the arm side.
    mount_pattern = {
        "coordinates_mm": [[-8.0, -8.0], [8.0, -8.0], [8.0, 8.0], [-8.0, 8.0]],
        "hole_diameter_mm": 3.0
    }
    res = verify_dfm(arm_width_mm=15.0, cutout_width_mm=0.0, mount_pattern=mount_pattern, printer_profile={"min_edge_clearance_mm": 2.0})
    assert res["status"] == "DFM_FAILED"
    assert any("Fastener tear-out risk" in issue for issue in res["issues"])

def test_dfm_passes_valid_geometry():
    mount_pattern = {
        "coordinates_mm": [[-8.0, -8.0], [8.0, -8.0], [8.0, 8.0], [-8.0, 8.0]],
        "hole_diameter_mm": 3.0
    }
    res = verify_dfm(arm_width_mm=25.0, cutout_width_mm=10.0, mount_pattern=mount_pattern, printer_profile={"min_wall_mm": 1.2, "min_edge_clearance_mm": 2.0})
    assert res["status"] == "PASSED"