import pytest
from status_gate import enforce_status

def test_passed_solver_generates_flight_candidate():
    result = enforce_status(solver_feasible=True, max_width_reached=False)
    assert result["status"] == "STRUCTURAL_SCREENING_PASSED"
    assert result["generate_flight_candidate_stl"] is True
    assert result["export_filename"] == "drone_blueprint.stl"

def test_failed_solver_cannot_be_flight_candidate():
    result = enforce_status(solver_feasible=False, max_width_reached=True)
    assert result["status"] == "NO_FEASIBLE_GEOMETRY"
    assert result["generate_flight_candidate_stl"] is False
    assert result["export_filename"] == "FAILED_SCREENING_GEOMETRY.stl"

def test_no_flight_candidate_can_exist_with_failed_screening():
    # Even if solver_feasible is somehow True but it hit the max limit in a weird state, 
    # we just want to ensure standard failure conditions block the STL.
    result = enforce_status(solver_feasible=False, max_width_reached=False)
    assert result["generate_flight_candidate_stl"] is False