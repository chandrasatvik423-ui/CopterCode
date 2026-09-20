def classify_vehicle(requirements: dict) -> str:
    mission = requirements.get("mission", "").upper()
    drone_type = requirements.get("drone_type", "").upper()
    text = f"{mission} {drone_type}"
    
    if "SUPERSONIC" in text or "JET" in text or "FIXED" in text or "WING" in text:
        return "FIXED_WING"
    return "MULTIROTOR"