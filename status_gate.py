def enforce_status(solver_feasible: bool, max_width_reached: bool):
    """Determines the final status and whether a flight-candidate STL is allowed."""
    
    if not solver_feasible or max_width_reached:
        return {
            "status": "NO_FEASIBLE_GEOMETRY",
            "generate_flight_candidate_stl": False,
            "export_filename": "FAILED_SCREENING_GEOMETRY.stl"
        }
        
    return {
        "status": "STRUCTURAL_SCREENING_PASSED",
        "generate_flight_candidate_stl": True,
        "export_filename": "drone_blueprint.stl"
    }