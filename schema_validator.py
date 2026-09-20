from topology_selector import TOPOLOGIES

def build_design_schema(diagonal_mm: float, ai_drone_type: str, topology_name: str = "MULTIROTOR_STANDARD"):
    topo = TOPOLOGIES.get(topology_name, TOPOLOGIES["MULTIROTOR_STANDARD"])
    
    # If diagonal is 0 or not specified, use the topology's default
    if not diagonal_mm or diagonal_mm <= 0:
        diagonal_mm = topo.get("default_diagonal_mm", 350)
        
    # Handle fixed wing or missing ranges gracefully
    if topo.get("diagonal_range_mm"):
        lo, hi = topo["diagonal_range_mm"]
        diagonal_mm = max(lo, min(hi, diagonal_mm))
        
    arm_length = diagonal_mm / 2.0
    
    return {
        "mission": {
            "type": ai_drone_type,
            "vehicle_class": topo["vehicle_class"],
            "topology": topology_name
        },
        "geometry": {
            "motor_to_motor_diagonal_mm": diagonal_mm,
            "arm_length_mm": arm_length,
            "arm_width_mm": 12.0,  # Starting solver width
            "arm_height_mm": topo.get("arm_height_mm", 6.0),
            "motor_diam": 28 if "HEAVY" in topology_name else (12 if "MICRO" in topology_name else 28),
            "pcb_length": 30.0 if "MICRO" in topology_name else 36.0,
            "pcb_width": 30.0 if "MICRO" in topology_name else 36.0,
            "cutout_width_ratio": 0.35,
            "cutout_height_ratio": 1.0,
            "motor_count": topo.get("motor_count", 4)
        }
    }