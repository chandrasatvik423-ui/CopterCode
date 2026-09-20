import pytest
from geometry_engine import verify_propeller_clearance

def test_valid_standard_racer():
    # 220mm diagonal, 5.1" (129.54mm) props, 36x36mm body
    res = verify_propeller_clearance(220.0, 129.54, 36.0, 36.0)
    assert res["status"] == "PASSED"
    assert res["min_prop_clearance_mm"] == 26.02
    assert res["min_body_clearance_mm"] == 19.77

def test_propeller_collision():
    # 180mm diagonal, 5.1" props. 
    # Math: dist = 180 * sin(45) * 2 = 127.27. Clearance = 127.27 - 129.54 = -2.27
    res = verify_propeller_clearance(180.0, 129.54, 36.0, 36.0)
    assert res["status"] == "FAILED_PROP_COLLISION"
    assert res["min_prop_clearance_mm"] == -2.26
    
def test_body_collision():
    # 220mm diagonal, 5.1" props, oversized 120x120mm body
    res = verify_propeller_clearance(220.0, 129.54, 120.0, 120.0)
    assert res["status"] == "FAILED_BODY_COLLISION"
    assert res["min_body_clearance_mm"] == -39.62

def test_invalid_inputs():
    res = verify_propeller_clearance(0.0, 129.54, 36.0, 36.0)
    assert res["status"] == "INVALID_INPUTS"