from vehicle_classifier import classify_vehicle
from topology_selector import select_topology

def test_supersonic_selects_fixed_wing():
    result = classify_vehicle({"mission": "SUPERSONIC"})
    assert result == "FIXED_WING"

def test_heavy_cargo_selects_heavy_multirotor():
    topology = select_topology({
        "mission": "CARGO",
        "payload_mass_g": 2500
    })
    assert topology == "MULTIROTOR_HEAVY_LIFT"

def test_supersonic_never_enters_quad_arm_solver():
    topology = select_topology({
        "mission": "SUPERSONIC"
    })
    assert topology != "MULTIROTOR_STANDARD"
    assert topology == "FIXED_WING_SUPERSONIC"