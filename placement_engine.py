def verify_and_place_components(
    pcb_width_mm: float,
    pcb_length_mm: float,
    fc_mount_pattern: dict,
    battery_retention: dict,
    min_edge_margin_mm: float = 3.0
) -> dict:
    """
    Validates physical mounting for FC stack and battery strap slots.
    Auto-expands central hub plate dimensions if required to prevent breakout.
    """
    target_width = float(pcb_width_mm)
    target_length = float(pcb_length_mm)
    issues = []
    
    # 1. Flight Controller Standoff Verification
    fc_coords = fc_mount_pattern.get("coordinates_mm", [])
    fc_hole_r = fc_mount_pattern.get("hole_diameter_mm", 3.0) / 2.0
    
    if fc_coords:
        max_fc_x = max(abs(x) for x, y in fc_coords) + fc_hole_r
        max_fc_y = max(abs(y) for x, y in fc_coords) + fc_hole_r
        
        required_width_fc = (max_fc_x + min_edge_margin_mm) * 2.0
        required_length_fc = (max_fc_y + min_edge_margin_mm) * 2.0
        
        if required_width_fc > target_width:
            target_width = required_width_fc
        if required_length_fc > target_length:
            target_length = required_length_fc

    # 2. Battery Strap Slots Verification
    # Creates two symmetrical slots centered along the X or Y axis
    strap_w = battery_retention.get("strap_width_mm", 20.0)
    slot_t = battery_retention.get("slot_thickness_mm", 3.0)
    slot_sep = battery_retention.get("slot_separation_mm", 24.0)
    
    half_sep = slot_sep / 2.0
    required_width_batt = (half_sep + (slot_t / 2.0) + min_edge_margin_mm) * 2.0
    required_length_batt = strap_w + (2.0 * min_edge_margin_mm)
    
    if required_width_batt > target_width:
        target_width = required_width_batt
    if required_length_batt > target_length:
        target_length = required_length_batt

    # Generate 2D Slot Cutout specs relative to plate center [0, 0]
    strap_slots = [
        {"center": [-half_sep, 0.0], "width": slot_t, "length": strap_w},
        {"center": [half_sep, 0.0], "width": slot_t, "length": strap_w}
    ]

    return {
        "status": "PASSED",
        "final_pcb_width_mm": round(target_width, 2),
        "final_pcb_length_mm": round(target_length, 2),
        "fc_standoffs": fc_coords,
        "fc_hole_diameter_mm": fc_mount_pattern.get("hole_diameter_mm", 3.0),
        "battery_strap_slots": strap_slots,
        "auto_expanded": (target_width > pcb_width_mm or target_length > pcb_length_mm)
    }