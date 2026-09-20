import json
import os
from schemas.hardware import HardwareManifest, Motor, FlightController, Battery, Wiring, MountPattern, BatteryRetention

def load_json(filename: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r") as f:
        return json.load(f)

def select_hardware(topology_name: str) -> HardwareManifest:
    motors_db = load_json("motors.json")
    fcs_db = load_json("flight_controllers.json")
    batts_db = load_json("batteries.json")
    
    if "MICRO" in topology_name:
        profile, motor_count, wire_name, wire_mass = "micro", 4, "Silicone Wire & Connectors", 15.0
    elif "RACING" in topology_name:
        profile, motor_count, wire_name, wire_mass = "racing", 4, "12AWG Power Leads & Signal Wires", 40.0
    elif "HEAVY_LIFT" in topology_name:
        profile, motor_count, wire_name, wire_mass = "heavy", 8, "Heavy-Duty Distribution Harness", 120.0
    else: 
        profile, motor_count, wire_name, wire_mass = "standard", 4, "Standard Wire Harness", 65.0
        
    m_data = motors_db[profile]
    fc_data = fcs_db[profile]
    b_data = batts_db[profile]
    
    motor = Motor(
        id=m_data.get("id", "unknown"),
        manufacturer=m_data.get("manufacturer", "unknown"),
        part_number=m_data.get("part_number", "unknown"),
        name=m_data["name"],
        data_status=m_data.get("data_status", "ASSUMED_GENERIC"),
        count=motor_count,
        unit_mass_g=m_data["unit_mass_g"],
        total_mass_g=m_data["unit_mass_g"] * motor_count,
        max_thrust_n=m_data["max_thrust_n"],
        prop_diam_mm=m_data.get("prop_diam_mm", 0.0),
        mount_pattern=MountPattern(**m_data.get("mount_pattern", {}))
    )
    
    fc = FlightController(
        id=fc_data.get("id", "unknown"),
        manufacturer=fc_data.get("manufacturer", "unknown"),
        part_number=fc_data.get("part_number", "unknown"),
        name=fc_data["name"],
        data_status=fc_data.get("data_status", "ASSUMED_GENERIC"),
        mass_g=fc_data["mass_g"],
        mount_pattern=MountPattern(**fc_data.get("mount_pattern", {}))
    )
    
    batt = Battery(
        id=b_data.get("id", "unknown"),
        manufacturer=b_data.get("manufacturer", "unknown"),
        part_number=b_data.get("part_number", "unknown"),
        name=b_data["name"],
        data_status=b_data.get("data_status", "ASSUMED_GENERIC"),
        mass_g=b_data["mass_g"],
        retention=BatteryRetention(**b_data.get("retention", {}))
    )
    
    wiring = Wiring(name=wire_name, mass_g=wire_mass)
    
    return HardwareManifest(profile=profile, motor=motor, flight_controller=fc, battery=batt, wiring=wiring)