import csv
import os

def export_bom_to_csv(result: dict, filename="CopterCode_BOM.csv"):
    if "hardware_manifest" not in result:
        return False
        
    hw = result["hardware_manifest"]
    mfg = result.get("manufacturing", {})
    
    headers = ["Component Type", "Manufacturer", "Part Number", "Name", "Quantity", "Unit Mass (g)", "Total Mass (g)", "Data Status"]
    rows = []
    
    # Electronics
    m = hw.get("motor", {})
    rows.append(["Motor", m.get("manufacturer"), m.get("part_number"), m.get("name"), m.get("count"), m.get("unit_mass_g"), m.get("total_mass_g"), m.get("data_status")])
    
    fc = hw.get("flight_controller", {})
    rows.append(["Flight Controller", fc.get("manufacturer"), fc.get("part_number"), fc.get("name"), 1, fc.get("mass_g"), fc.get("mass_g"), fc.get("data_status")])
    
    batt = hw.get("battery", {})
    rows.append(["Battery", batt.get("manufacturer"), batt.get("part_number"), batt.get("name"), 1, batt.get("mass_g"), batt.get("mass_g"), batt.get("data_status")])
    
    w = hw.get("wiring", {})
    rows.append(["Wiring/Harness", "Generic", "N/A", w.get("name"), 1, w.get("mass_g"), w.get("mass_g"), "ASSUMED"])
    
    # Physical Structure
    rows.append(["Frame", "CopterCode Auto-Gen", "3D-Printed STL", "Custom Frame", 1, mfg.get("weight_g"), mfg.get("weight_g"), "COMPUTED"])
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    return True