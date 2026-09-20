import pytest
from pipeline import run_pipeline
from hardware.hardware_selector import select_hardware


def fake_parser_standard(prompt):
    return {"drone_type": "standard drone", "diagonal_mm": 220.0, "payload_mass_g": 0.0, "mission": "standard"}


def test_verified_hardware_passes_provenance():
    """
    All hardware tiers are now VERIFIED_DATASHEET.
    A structurally feasible standard drone must NOT be rejected at the provenance gate.
    It should proceed to STRUCTURAL_SCREENING_PASSED.
    """
    result = run_pipeline("standard drone", requirements_parser=fake_parser_standard)
    # Must not be blocked by provenance
    assert result["status"] != "UNVERIFIED_PROVENANCE", (
        "Provenance gate falsely blocked a design with VERIFIED_DATASHEET components"
    )


def test_hardware_selector_returns_verified_status_for_all_tiers():
    """
    Every topology tier's motor, FC, and battery must carry VERIFIED_DATASHEET.
    This verifies the JSON databases are correctly marked.
    """
    for topology in ["MULTIROTOR_MICRO", "MULTIROTOR_RACING", "MULTIROTOR_HEAVY_LIFT", "MULTIROTOR_STANDARD"]:
        hw = select_hardware(topology)
        for component_key in ("motor", "flight_controller", "battery"):
            comp = getattr(hw, component_key)
            status = getattr(comp, "data_status", "MISSING")
            assert status == "VERIFIED_DATASHEET", (
                f"{topology} / {component_key} has data_status={status!r}, expected VERIFIED_DATASHEET"
            )


def test_hardware_manifest_contains_provenance_fields():
    """Each component object must expose id, manufacturer, part_number, data_status."""
    hw = select_hardware("MULTIROTOR_RACING")
    for key in ("motor", "flight_controller", "battery"):
        comp = getattr(hw, key)
        assert hasattr(comp, "id"), f"{key} missing 'id'"
        assert hasattr(comp, "manufacturer"), f"{key} missing 'manufacturer'"
        assert hasattr(comp, "part_number"), f"{key} missing 'part_number'"
        assert hasattr(comp, "data_status"), f"{key} missing 'data_status'"