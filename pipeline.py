import json
import requests
from schemas.requirements import MissionRequirements
from schemas.engineering_config import CONFIG
from schemas.status import StatusAuthority, PipelineState
from hardware.hardware_selector import select_hardware
from mass_engine import calculate_total_mass
from physics_engine import audit_structural_integrity
from vehicle_classifier import classify_vehicle
from topology_selector import select_topology
from schema_validator import build_design_schema
from manufacturing_estimator import estimate_build_cost
from geometry_engine import verify_propeller_clearance
from dfm_engine import verify_dfm
from placement_engine import verify_and_place_components
from dynamics_engine import calculate_flight_dynamics
from slicer_engine import slice_and_evaluate

def default_ai_parser(prompt: str) -> dict:
    system_instruction = 'Analyze intent. Output ONLY valid JSON with keys: "diagonal_mm" (float), "drone_type" (string), "payload_mass_g" (float), "mission" (string).'
    try:
        res = requests.post(CONFIG.app.llm_endpoint, json={"model": CONFIG.app.llm_model, "prompt": f"{system_instruction}\n\nUser: {prompt}", "stream": False, "format": "json"})
        return json.loads(res.json()["response"])
    except Exception:
        raise ValueError("AI parser failed to communicate with local model or returned invalid JSON.")

CERTIFICATION_BOUNDARY = {
    "flight_certification_status": "NOT_CERTIFIED",
    "certification_path_required": [
        "physical static load test",
        "dynamic vibration test",
        "DFM tolerance stack-up verification",
        "regulatory review (e.g., FAA Part 107)"
    ]
}

def run_pipeline(prompt: str, requirements_parser=default_ai_parser) -> dict:
    status_authority = StatusAuthority()
    
    try:
        raw_data = requirements_parser(prompt)
        raw_data = {k: v for k, v in raw_data.items() if v is not None}
        if "mission" not in raw_data:
            raw_data["mission"] = raw_data.get("drone_type", prompt)
        reqs = MissionRequirements(**raw_data)
    except Exception as e:
        status_authority.fail_closed(PipelineState.INPUT_INVALID, str(e), "REJECTED_INPUT.stl")
        return {"status": status_authority.state.value, "blocking_reasons": status_authority.blocking_reasons, "artifacts": {"flight_candidate_generated": False, "filename": status_authority.export_filename}}

    classification_reqs = {"mission": reqs.mission, "drone_type": reqs.drone_type, "payload_mass_g": reqs.payload_mass_g}
    vehicle_class = classify_vehicle(classification_reqs)
    topology_name = select_topology(classification_reqs)
    
    if vehicle_class == "FIXED_WING":
        status_authority.fail_closed(PipelineState.TOPOLOGY_UNSUPPORTED, "Fixed wing topology not currently supported.", "REJECTED_TOPOLOGY.stl")
        return {"status": status_authority.state.value, "blocking_reasons": status_authority.blocking_reasons, "requirements": reqs.model_dump(), "topology": {"name": topology_name, "vehicle_class": vehicle_class}, "artifacts": {"flight_candidate_generated": False, "filename": status_authority.export_filename}}

    schema = build_design_schema(reqs.diagonal_mm, reqs.drone_type, topology_name)
    geo = schema["geometry"]
    hw = select_hardware(topology_name)
    total_hardware_mass = hw.motor.total_mass_g + hw.flight_controller.mass_g + hw.battery.mass_g + hw.wiring.mass_g

    placement = verify_and_place_components(
        pcb_width_mm=geo["pcb_width"],
        pcb_length_mm=geo["pcb_length"],
        fc_mount_pattern=hw.flight_controller.mount_pattern.model_dump(),
        battery_retention=hw.battery.retention.model_dump(),
        min_edge_margin_mm=3.0
    )
    geo["pcb_width"], geo["pcb_length"], geo["placement"] = placement["final_pcb_width_mm"], placement["final_pcb_length_mm"], placement

    original_diagonal = geo["motor_to_motor_diagonal_mm"]
    buf = CONFIG.safety.body_clearance_buffer_mm
    geom_check = verify_propeller_clearance(geo["motor_to_motor_diagonal_mm"], hw.motor.prop_diam_mm, geo["pcb_width"] + buf, geo["pcb_length"] + buf, geo["motor_count"])
    
    while geom_check["status"] != "PASSED" and geo["motor_to_motor_diagonal_mm"] <= CONFIG.solver.max_diagonal_limit_mm:
        geo["motor_to_motor_diagonal_mm"] += CONFIG.solver.auto_correction_step_mm
        geom_check = verify_propeller_clearance(geo["motor_to_motor_diagonal_mm"], hw.motor.prop_diam_mm, geo["pcb_width"] + buf, geo["pcb_length"] + buf, geo["motor_count"])

        
    geo["auto_corrected"] = geo["motor_to_motor_diagonal_mm"] != original_diagonal
    geo["original_diagonal_mm"] = original_diagonal
    
    if geom_check["status"] != "PASSED":
        status_authority.fail_closed(PipelineState.COLLISION_DETECTED, "Propeller clearance constraints violated.", "REJECTED_COLLISION.stl")
        return {"status": status_authority.state.value, "blocking_reasons": status_authority.blocking_reasons, "requirements": reqs.model_dump(), "geometry": geo, "clearance": geom_check, "artifacts": {"flight_candidate_generated": False, "filename": status_authority.export_filename}}

    current_width = geo["arm_width_mm"]
    current_height = geo["arm_height_mm"]
    max_height = current_height * CONFIG.solver.height_multiplier_limit   # computed ONCE
    solver_feasible = False
    
    twr = 0.0
    total_thrust_n = hw.motor.max_thrust_n * geo["motor_count"]
    audit, dfm_check = {}, {}
    printer_profile = {"min_wall_mm": 1.2, "min_edge_clearance_mm": 2.0}
    
    while current_width <= CONFIG.solver.max_arm_width_mm:
        mfg = estimate_build_cost(geo["motor_to_motor_diagonal_mm"], current_width, current_height, geo["pcb_length"], geo["pcb_width"], geo["motor_count"])
        mass_budget = calculate_total_mass(mfg["weight_g"], hw.motor.total_mass_g + hw.flight_controller.mass_g, hw.battery.mass_g, hw.wiring.mass_g, reqs.payload_mass_g)
        
        if mass_budget["status"] == "INPUT_INCOMPLETE":
            status_authority.fail_closed(PipelineState.INPUT_INCOMPLETE, "Mass calculation inputs missing.", "REJECTED_MASS.stl")
            return {"status": status_authority.state.value, "blocking_reasons": status_authority.blocking_reasons, "requirements": reqs.model_dump(), "certification": CERTIFICATION_BOUNDARY}

        total_mass_kg = mass_budget["takeoff_mass_g"] / 1000.0
        cutout_w = current_width * geo["cutout_width_ratio"]
        
        audit = audit_structural_integrity(total_mass_kg, geo["arm_length_mm"], current_width, current_height, cutout_w, current_height * geo["cutout_height_ratio"], hw.motor.max_thrust_n, geo["motor_count"])
        
        weight_n = total_mass_kg * 9.81
        twr = total_thrust_n / weight_n if weight_n > 0 else 0.0
        
        dfm_check = verify_dfm(current_width, cutout_w, hw.motor.mount_pattern.model_dump(), printer_profile)
        
        if audit["safety_factor"] >= CONFIG.safety.min_structural_safety_factor and dfm_check["status"] == "PASSED":
            solver_feasible = twr >= CONFIG.safety.min_thrust_to_weight_ratio
            break
            
        if current_width >= CONFIG.solver.max_arm_width_mm:
            if current_height < max_height:
                current_height += 1.0; current_width = CONFIG.solver.min_arm_width_mm
                continue
            break
            
        current_width += CONFIG.solver.width_iteration_step_mm


    provenance_verified = all(c.data_status == "VERIFIED_DATASHEET" for c in [hw.motor, hw.flight_controller, hw.battery])
    
    if not solver_feasible and dfm_check.get("status") == "DFM_FAILED":
        status_authority.fail_closed(PipelineState.DFM_FAILED, "Physical printer constraints violated.", "REJECTED_DFM.stl")
    elif audit.get("safety_factor", 0.0) >= CONFIG.safety.min_structural_safety_factor and twr < CONFIG.safety.min_thrust_to_weight_ratio:
        status_authority.fail_closed(PipelineState.INSUFFICIENT_THRUST, f"TWR {twr} below limit {CONFIG.safety.min_thrust_to_weight_ratio}", "REJECTED_THRUST.stl")
    elif not solver_feasible:
        status_authority.fail_closed(PipelineState.NO_FEASIBLE_GEOMETRY, "Max dimensions reached without achieving safety factor.", "REJECTED_STRUCTURAL.stl")
    elif not provenance_verified:
        status_authority.fail_closed(PipelineState.UNVERIFIED_PROVENANCE, "Hardware data contains assumed generics.", "REJECTED_PROVENANCE.stl")
    else:
        status_authority.pass_screening("drone_blueprint.stl")

    geo["arm_width_mm"], geo["arm_height_mm"] = current_width, current_height

    return {
        "status": status_authority.state.value,
        "blocking_reasons": status_authority.blocking_reasons,
        "requirements": reqs.model_dump(),
        "topology": {"name": topology_name, "vehicle_class": vehicle_class},
        "geometry": geo,
        "hardware_manifest": hw.model_dump(),
        "manufacturing": mfg,
        "mass": {"frame_mass_g": mfg["weight_g"], "hardware_mass_g": total_hardware_mass, "payload_mass_g": reqs.payload_mass_g, "takeoff_mass_g": mass_budget["takeoff_mass_g"]},
        "screening": {"feasible": solver_feasible, "dfm_status": dfm_check, "governing_safety_factor": audit.get("safety_factor", 0.0), "governing_load_case": audit.get("governing_load_case", "INVALID"), "governing_force_n": audit.get("governing_force_n", 0.0), "thrust_to_weight_ratio": round(twr, 2), "last_evaluated_width_mm": current_width, "last_evaluated_height_mm": current_height},
        "flight_dynamics": calculate_flight_dynamics(mass_budget["takeoff_mass_g"], hw.battery.name, total_thrust_n),
        "slicer_data": slice_and_evaluate(status_authority.export_filename, mfg["weight_g"]),
        "clearance": geom_check,
        "certification": CERTIFICATION_BOUNDARY,
        "artifacts": {"flight_candidate_generated": status_authority.generate_flight_candidate_stl, "filename": status_authority.export_filename}
    }