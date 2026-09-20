from mass_engine import calculate_total_mass

def test_payload_is_preserved():
    result = calculate_total_mass(
        frame_mass_g=420,
        hardware_mass_g=215, # Motors, ESCs, FC
        battery_mass_g=300,
        wiring_mass_g=65,
        payload_mass_g=2500
    )
    
    assert result["payload_mass_g"] == 2500
    assert result["takeoff_mass_g"] == 3500
    assert result["status"] == "VALID"

def test_missing_payload_halts_system():
    result = calculate_total_mass(
        frame_mass_g=420,
        hardware_mass_g=215,
        battery_mass_g=300,
        wiring_mass_g=65,
        payload_mass_g=None
    )
    
    assert result["status"] == "INPUT_INCOMPLETE"