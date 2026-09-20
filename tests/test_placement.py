import pytest
from placement_engine import verify_and_place_components

def test_placement_fits_within_default_hub():
    fc_pattern = {
        "coordinates_mm": [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
        "hole_diameter_mm": 2.0
    }
    retention = {
        "strap_width_mm": 12.0,
        "slot_thickness_mm": 2.0,
        "slot_separation_mm": 14.0
    }
    res = verify_and_place_components(
        pcb_width_mm=36.0,
        pcb_length_mm=36.0,
        fc_mount_pattern=fc_pattern,
        battery_retention=retention,
        min_edge_margin_mm=3.0
    )
    assert res["status"] == "PASSED"
    assert res["auto_expanded"] is False
    assert len(res["fc_standoffs"]) == 4
    assert len(res["battery_strap_slots"]) == 2

def test_placement_auto_expands_small_hub():
    # 45x45mm FC pattern cannot fit on a 36x36mm hub with 3mm margin
    fc_pattern = {
        "coordinates_mm": [[-22.5, -22.5], [22.5, -22.5], [22.5, 22.5], [-22.5, 22.5]],
        "hole_diameter_mm": 3.5
    }
    retention = {
        "strap_width_mm": 25.0,
        "slot_thickness_mm": 3.5,
        "slot_separation_mm": 30.0
    }
    res = verify_and_place_components(
        pcb_width_mm=36.0,
        pcb_length_mm=36.0,
        fc_mount_pattern=fc_pattern,
        battery_retention=retention,
        min_edge_margin_mm=3.0
    )
    assert res["status"] == "PASSED"
    assert res["auto_expanded"] is True
    # (22.5 + 1.75 + 3.0) * 2 = 54.5 mm required
    assert res["final_pcb_width_mm"] >= 54.5
    assert res["final_pcb_length_mm"] >= 54.5