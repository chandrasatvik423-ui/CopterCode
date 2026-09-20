import re

def calculate_flight_dynamics(takeoff_mass_g: float, battery_name: str, total_thrust_n: float) -> dict:
    """Calculates theoretical aerodynamic and electrical performance metrics."""
    
    # Parse battery specs (e.g., "4S 1300mAh 100C LiPo" or "6S-5000")
    s_match = re.search(r'(\d+)S', battery_name, re.IGNORECASE)
    mah_match = re.search(r'(\d{3,4})(?:mAh|-| )', battery_name, re.IGNORECASE)
    
    cells = int(s_match.group(1)) if s_match else 4
    capacity_mah = float(mah_match.group(1)) if mah_match else 1500.0
    
    voltage = cells * 3.7
    energy_wh = (capacity_mah / 1000.0) * voltage
    
    # Aerodynamic Hover Estimate: ~150 Watts per kg to hover (Empirical Drone Constant)
    mass_kg = takeoff_mass_g / 1000.0
    hover_power_w = mass_kg * 150.0 
    
    hover_time_mins = (energy_wh / hover_power_w) * 60.0 if hover_power_w > 0 else 0.0
    
    # Top Speed Estimate: Scaled by TWR (Empirical limit for multirotors)
    twr = total_thrust_n / (mass_kg * 9.81) if mass_kg > 0 else 0.0
    top_speed_kmh = (twr * 22.5) if twr > 1.0 else 0.0 
    
    return {
        "hover_time_mins": round(hover_time_mins, 1),
        "top_speed_kmh": round(top_speed_kmh, 1),
        "est_hover_power_w": round(hover_power_w, 1),
        "battery_energy_wh": round(energy_wh, 1)
    }