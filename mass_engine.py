def calculate_total_mass(frame_mass_g, hardware_mass_g, battery_mass_g, wiring_mass_g, payload_mass_g):
    """Strictly calculates mass closure. Halts if payload is missing."""
    
    if payload_mass_g is None:
        return {"status": "INPUT_INCOMPLETE"}
        
    takeoff_mass = frame_mass_g + hardware_mass_g + battery_mass_g + wiring_mass_g + payload_mass_g
    
    return {
        "status": "VALID",
        "payload_mass_g": payload_mass_g,
        "takeoff_mass_g": takeoff_mass,
        "closure_report": {
            "Frame": f"{frame_mass_g} g",
            "Hardware (Motors, FC, ESC)": f"{hardware_mass_g} g",
            "Battery": f"{battery_mass_g} g",
            "Wiring/Misc": f"{wiring_mass_g} g",
            "Payload": f"{payload_mass_g} g",
            "TAKEOFF MASS": f"{takeoff_mass} g"
        }
    }