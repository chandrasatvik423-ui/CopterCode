def verify_dfm(arm_width_mm: float, cutout_width_mm: float, mount_pattern: dict, printer_profile: dict) -> dict:
    """
    Evaluates geometry against 3D printing and physical assembly constraints.
    """
    issues = []
    
    # 1. Minimum Wall Thickness (Distance between outer arm edge and inner cutout)
    wall_thickness = (arm_width_mm - cutout_width_mm) / 2.0
    min_wall = printer_profile.get("min_wall_mm", 1.2)
    if wall_thickness < min_wall:
        issues.append(f"Wall thickness ({wall_thickness:.2f}mm) < printer minimum ({min_wall}mm)")
        
    # 2. Fastener Edge Clearance (Distance from outermost screw hole to arm edge)
    if mount_pattern and "coordinates_mm" in mount_pattern:
        max_hole_y = max(abs(cy) for cx, cy in mount_pattern["coordinates_mm"])
        hole_radius = mount_pattern.get("hole_diameter_mm", 3.0) / 2.0
        
        edge_clearance = (arm_width_mm / 2.0) - max_hole_y - hole_radius
        min_edge = printer_profile.get("min_edge_clearance_mm", 2.0)
        
        if edge_clearance < min_edge:
            req_width = (max_hole_y + hole_radius + min_edge) * 2.0
            issues.append(f"Fastener tear-out risk: clearance ({edge_clearance:.2f}mm) < minimum ({min_edge}mm). Requires arm width >= {req_width:.1f}mm")
            
    status = "PASSED" if not issues else "DFM_FAILED"
    return {
        "status": status,
        "issues": issues
    }