import math

def verify_propeller_clearance(
    diagonal_mm: float, 
    prop_diam_mm: float, 
    body_width_mm: float, 
    body_length_mm: float, 
    motor_count: int = 4
) -> dict:
    """Calculates clearance for 4, 6, and 8 arm configurations dynamically."""

    if diagonal_mm <= 0 or prop_diam_mm <= 0:
        return {
            "status": "INVALID_INPUTS",
            "min_prop_clearance_mm": 0.0,
            "min_body_clearance_mm": 0.0
        }

    # Distance between adjacent motors on a regular polygon
    # Formula: D * sin(180 / n)
    adjacent_dist = diagonal_mm * math.sin(math.pi / motor_count)
    min_prop_clearance = adjacent_dist - prop_diam_mm
    
    # Hub clearance (simplified bounding box radius)
    hub_radius = math.hypot(body_width_mm, body_length_mm) / 2.0
    motor_hub_dist = (diagonal_mm / 2.0)
    min_body_clearance = motor_hub_dist - hub_radius - (prop_diam_mm / 2.0)
    
    status = "PASSED"
    if min_prop_clearance < 2.0:
        status = "FAILED_PROP_COLLISION"
    elif min_body_clearance < 2.0:
        status = "FAILED_BODY_COLLISION"
        
    return {
        "status": status,
        "min_prop_clearance_mm": round(min_prop_clearance, 2),
        "min_body_clearance_mm": round(min_body_clearance, 2)
    }