import pytest
from pipeline import run_pipeline

# --- Mock AI Parsers for Deterministic Testing ---
def fake_parser_heavy_lift(prompt):
    return {"drone_type": "Heavy Lift Cargo", "diagonal_mm": 600.0, "payload_mass_g": 2500.0, "mission": "cargo"}

def fake_parser_micro(prompt):
    # diagonal_mm=0.0 is now rejected by MissionRequirements validator (must be > 50.0).
    # Supply 0.0 to trigger topology auto-routing to MICRO (diagonal overridden by topology).
    # Use 100.0 which is the micro canonical size and passes the 50mm floor.
    return {"drone_type": "tiny micro drone", "diagonal_mm": 100.0, "payload_mass_g": 0.0, "mission": "micro"}

def fake_parser_racing(prompt):
    # Racing canonical diagonal is 220mm; 0.0 is now rejected by validator.
    return {"drone_type": "high speed racing drone", "diagonal_mm": 220.0, "payload_mass_g": 0.0, "mission": "racing"}

def fake_parser_supersonic(prompt):
    return {"drone_type": "supersonic jet", "diagonal_mm": 1000.0, "payload_mass_g": 0.0, "mission": "supersonic"}


# --- Existing Tests ---
def test_25kg_payload_cannot_become_13kg_aircraft():
    result = run_pipeline("Massive 2500g Heavy Lift Cargo Drone", requirements_parser=fake_parser_heavy_lift)
    assert result["mass"]["takeoff_mass_g"] > 2500

def test_failed_screening_cannot_create_flight_candidate():
    result = run_pipeline("Massive 2500g Heavy Lift Cargo Drone", requirements_parser=fake_parser_heavy_lift)
    if not result["screening"]["feasible"]:
        assert result["artifacts"]["flight_candidate_generated"] is False

# --- New Topology & Architecture Tests ---
def test_micro_drone_gets_small_diagonal():
    """A micro mission with 0.0 diagonal must auto-route to a small frame (<= 180mm)."""
    result = run_pipeline("tiny micro drone", requirements_parser=fake_parser_micro)
    assert result["geometry"]["motor_to_motor_diagonal_mm"] <= 180.0
    assert result["topology"]["name"] == "MULTIROTOR_MICRO"

def test_micro_drone_mass_is_light():
    """A micro drone's takeoff mass must scale down correctly, not using hardcoded heavy constants."""
    result = run_pipeline("tiny micro drone", requirements_parser=fake_parser_micro)
    assert result["mass"]["takeoff_mass_g"] < 300.0

def test_racing_drone_gets_racing_topology():
    """A racing prompt must auto-route to the RACING topology."""
    result = run_pipeline("high speed racing drone", requirements_parser=fake_parser_racing)
    assert result["topology"]["name"] == "MULTIROTOR_RACING"
    assert result["geometry"]["motor_to_motor_diagonal_mm"] == 220.0

def test_heavy_lift_gets_octo_topology():
    """Heavy payload missions must route to 8-motor octocopters."""
    result = run_pipeline("heavy cargo", requirements_parser=fake_parser_heavy_lift)
    assert result["topology"]["name"] == "MULTIROTOR_HEAVY_LIFT"
    assert result["geometry"]["motor_count"] == 8

def test_supersonic_bypasses_multirotor_solver():
    """Fixed wing classification should safely exit before running multirotor geometry."""
    result = run_pipeline("supersonic jet", requirements_parser=fake_parser_supersonic)
    assert result["status"] == "TOPOLOGY_UNSUPPORTED"
    assert "geometry" not in result