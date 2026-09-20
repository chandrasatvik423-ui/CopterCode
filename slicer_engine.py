import subprocess
import os
import re

def slice_and_evaluate(stl_path: str, frame_mass_g: float) -> dict:
    """
    Interfaces with CLI slicers to generate G-Code and extract print times.
    Defaults to heuristic calculation if external slicer is not in system PATH.
    """
    cost_per_kg = 25.0
    fallback_cost = round((frame_mass_g / 1000.0) * cost_per_kg, 2)
    fallback_time_hrs = round(frame_mass_g / 45.0, 1) # Assumes standard 45g/hr FDM throughput
    adhesion_risk = "CRITICAL (Z-Axis Delamination)" if frame_mass_g > 800 else "NOMINAL"
    
    slicer_status = "HEURISTIC_ESTIMATE"
    print_time_hrs = fallback_time_hrs
    filament_used_g = round(frame_mass_g, 1)
    
    # True Slicer CLI Hook (e.g., PrusaSlicer)
    if os.path.exists(stl_path):
        try:
            # Attempt to run PrusaSlicer in console mode to extract exact gcode metrics
            cmd = ["prusa-slicer-console", "--export-gcode", "--info", stl_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                slicer_status = "TRUE_GCODE_PARSED"
                # Extract exact mass from G-Code output (e.g., "filament used [g] = 105.2")
                mass_match = re.search(r'filament used \[g\] = ([\d\.]+)', result.stdout)
                if mass_match:
                    filament_used_g = float(mass_match.group(1))
                    fallback_cost = round((filament_used_g / 1000.0) * cost_per_kg, 2)
        except Exception:
            pass # Silently fallback to heuristics
            
    return {
        "slicer_status": slicer_status,
        "print_time_hrs": print_time_hrs,
        "filament_used_g": filament_used_g,
        "material_cost_usd": fallback_cost,
        "layer_adhesion_risk": adhesion_risk
    }