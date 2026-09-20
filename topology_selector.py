TOPOLOGIES = {
    "MULTIROTOR_MICRO": {
        "vehicle_class": "MULTIROTOR", "motor_count": 4, "layout": "X_QUAD",
        "diagonal_range_mm": (80, 180),
        "default_diagonal_mm": 120,
        "arm_height_mm": 3.5,
        "hardware_profile": "micro",
    },
    "MULTIROTOR_RACING": {
        "vehicle_class": "MULTIROTOR", "motor_count": 4, "layout": "X_QUAD",
        "diagonal_range_mm": (180, 280),
        "default_diagonal_mm": 220,
        "arm_height_mm": 5.0,
        "hardware_profile": "racing",
    },
    "MULTIROTOR_STANDARD": {
        "vehicle_class": "MULTIROTOR", "motor_count": 4, "layout": "X_QUAD",
        "diagonal_range_mm": (250, 400),
        "default_diagonal_mm": 350,
        "arm_height_mm": 6.0,
        "hardware_profile": "standard",
    },
    "MULTIROTOR_HEAVY_LIFT": {
        "vehicle_class": "MULTIROTOR", "motor_count": 8, "layout": "OCTO",
        "diagonal_range_mm": (350, 700),
        "default_diagonal_mm": 500,
        "arm_height_mm": 8.0,
        "hardware_profile": "heavy",
    },
    "FIXED_WING_SUPERSONIC": {
        "vehicle_class": "FIXED_WING", "layout": "SWEPT_WING",
        "diagonal_range_mm": None,
        "hardware_profile": None,
    },
}

def select_topology(requirements: dict) -> str:
    mission = requirements.get("mission", "").upper()
    drone_type = requirements.get("drone_type", "").upper()
    payload = requirements.get("payload_mass_g", 0)
    text = f"{mission} {drone_type}"
    
    if "SUPERSONIC" in text or "JET" in text or "FIXED" in text:
        return "FIXED_WING_SUPERSONIC"
    if "MICRO" in text or "TINY" in text or "WHOOP" in text:
        return "MULTIROTOR_MICRO"
    if "RACING" in text or "FPV" in text or "SPEED" in text or "AGILE" in text:
        return "MULTIROTOR_RACING"
    if payload >= 2000 or "CARGO" in text or "HEAVY" in text:
        return "MULTIROTOR_HEAVY_LIFT"
        
    return "MULTIROTOR_STANDARD"