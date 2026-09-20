import pytest
from pipeline import run_pipeline

def fake_parser_standard(prompt):
    return {"drone_type": "standard drone", "diagonal_mm": 300.0, "payload_mass_g": 0.0, "mission": "standard"}

def test_certification_boundary_exists_on_success():
    result = run_pipeline("standard drone", requirements_parser=fake_parser_standard)
    assert "certification" in result
    assert result["certification"]["flight_certification_status"] == "NOT_CERTIFIED"
    assert "physical static load test" in result["certification"]["certification_path_required"]

def test_certification_boundary_exists_on_failure():
    # Will fail early due to impossible geometry/mass constraints but still return certification boundary
    result = run_pipeline("10kg heavy payload racing drone", requirements_parser=fake_parser_standard)
    assert "certification" in result
    assert result["certification"]["flight_certification_status"] == "NOT_CERTIFIED"