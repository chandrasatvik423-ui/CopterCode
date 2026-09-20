from pipeline import run_pipeline
from drone_generator import generate_drone_frame
from rich.console import Console

console = Console()

console.print("\n")
user_request = console.input("[bold yellow]📡 USER INTENT: What kind of drone do you want to build today? [/bold yellow]\n> ")

console.print("\n[bold blue]⚙️ Executing Deterministic Aerospace Pipeline...[/bold blue]")

try:
    result = run_pipeline(user_request)
except ValueError as e:
    console.print(f"\n[bold red]❌ Pipeline Error: {e}[/bold red]")
    console.print("[red]Ensure the Ollama application is running locally and the 'phi3' model is available.[/red]")
    exit(1)

if result["status"] in ["TOPOLOGY_UNSUPPORTED", "INPUT_INCOMPLETE"]:
    console.print(f"[bold red]❌ Pipeline blocked: {result['status']}[/bold red]")
    exit(0)

# Safely extract dictionaries with fallbacks to prevent KeyErrors on early-exit failure modes
reqs = result.get("requirements", {})
geo = result.get("geometry", {})
hw = result.get("hardware_manifest", {})
mfg = result.get("manufacturing", {"material_cost_usd": "N/A", "print_time_hrs": "N/A", "weight_g": "N/A"})
mass_data = result.get("mass", {"takeoff_mass_g": "N/A"})
artifacts = result.get("artifacts", {})
screening = result.get("screening", {})
clearance = result.get("clearance", {})
cert = result.get("certification", {"flight_certification_status": "UNKNOWN", "certification_path_required": []})

# Generate CAD Output with Level 5 Component Placement
generate_drone_frame(
    diagonal_mm=geo.get("motor_to_motor_diagonal_mm", 0.0),
    arm_width=geo.get("arm_width_mm", 12.0),
    arm_height=geo.get("arm_height_mm", 4.0),
    motor_diam=geo.get("motor_diam", 28.0),
    pcb_length=geo.get("pcb_length", 36.0),
    pcb_width=geo.get("pcb_width", 36.0),
    mount_pattern=hw.get("motor", {}).get("mount_pattern", {}),
    drone_type=reqs.get("drone_type", "Unknown Drone"),
    output_filename=artifacts.get("filename", "REJECTED_drone_blueprint.stl"),
    motor_count=geo.get("motor_count", 4),
    screening_passed=artifacts.get("flight_candidate_generated", False),
    placement_data=geo.get("placement", {}),
    auto_open=True
)

# Write Assembly Manual
cert_list = "\n".join([f"- [ ] {task}" for task in cert.get("certification_path_required", [])])
hw_motor = hw.get("motor", {})
hw_fc = hw.get("flight_controller", {})
hw_batt = hw.get("battery", {})
hw_wire = hw.get("wiring", {})

manual_content = f"""# Astro-Forge Assembly Manual
## Mission: {reqs.get('drone_type', 'N/A')}
- **Topology:** {result.get('topology', {}).get('name', 'N/A')}
- **Status:** {result.get('status', 'N/A')}
- **Takeoff Mass:** {mass_data.get('takeoff_mass_g', 'N/A')} g

## Geometry & Specifications
- **Motor-to-Motor Diagonal:** {geo.get('motor_to_motor_diagonal_mm', 'N/A')} mm
- **Motor Count:** {geo.get('motor_count', 'N/A')}
- **Arm Width:** {screening.get('last_evaluated_width_mm', 'N/A')} mm
- **Arm Height:** {screening.get('last_evaluated_height_mm', 'N/A')} mm
- **Safety Factor:** {screening.get('governing_safety_factor', 'N/A')}

## Itemized Bill of Materials (BOM) & Electronics
- **Motors:** {hw_motor.get('count', 'N/A')}x {hw_motor.get('name', 'N/A')} ({hw_motor.get('total_mass_g', 'N/A')} g)
- **Flight Controller:** {hw_fc.get('name', 'N/A')} ({hw_fc.get('mass_g', 'N/A')} g)
- **Battery:** {hw_batt.get('name', 'N/A')} ({hw_batt.get('mass_g', 'N/A')} g)
- **Wiring & Harness:** {hw_wire.get('name', 'N/A')} ({hw_wire.get('mass_g', 'N/A')} g)

## Fabrication Estimates
- **Frame Material Cost:** ${mfg.get('material_cost_usd', 'N/A')}
- **Estimated Print Time:** {mfg.get('print_time_hrs', 'N/A')} hrs
- **Estimated Frame Weight:** {mfg.get('weight_g', 'N/A')} g

## ⚠️ Certification Boundary
**Flight Certification Status:** `{cert.get('flight_certification_status', 'N/A')}`

This geometry is an unverified computational screening output. Do not execute flight without completing the required engineering certification path:
{cert_list}
"""

with open("Assembly_Manual.md", "w", encoding="utf-8") as manual_file:
    manual_file.write(manual_content)
console.print("[Generator] 📄 Assembly_Manual.md generated successfully.")

# Terminal Report
console.print("\n╭────────────── Astro-Forge Engineering Validation ──────────────╮")
console.print(f"│ Mission: {reqs.get('drone_type', 'N/A'):<61}│")
console.print(f"│ Topology:{result.get('topology', {}).get('name', 'N/A'):<61}│")
console.print(f"│ Status:  {result.get('status', 'N/A'):<61}│")
console.print(f"│ Output:  {artifacts.get('filename', 'N/A'):<61}│")
console.print("╰─────────────────────────────────────────────────────────────────╯\n")

if artifacts.get("flight_candidate_generated", False):
    if geo.get("auto_corrected", False):
        console.print(f"[bold yellow]⚠️ Geometry Auto-Corrected:[/bold yellow] LLM input diagonal of {geo.get('original_diagonal_mm')} mm was mathematically expanded to {geo.get('motor_to_motor_diagonal_mm')} mm to clear propellers.")
        
    console.print(f"\n[bold cyan]Mass Closure & Structural Screening:[/bold cyan]")
    console.print(f"  Takeoff Mass:     {mass_data.get('takeoff_mass_g', 'N/A')} g")
    console.print(f"  Final Arm Dims:   {screening.get('last_evaluated_width_mm', 'N/A')} mm W x {screening.get('last_evaluated_height_mm', 'N/A')} mm H")
    console.print(f"  Governing Case:   {screening.get('governing_load_case', 'N/A')} ({screening.get('governing_force_n', 'N/A')} N)")
    console.print(f"  Safety Factor:    {screening.get('governing_safety_factor', 'N/A')}")
    console.print(f"  Thrust-to-Weight: {screening.get('thrust_to_weight_ratio', 'N/A')}")
    
    console.print("\n[bold yellow]⚠️ CERTIFICATION REQUIRED[/bold yellow]")
    console.print(f"  Status: {cert.get('flight_certification_status', 'N/A')}")
    for task in cert.get("certification_path_required", []):
        console.print(f"  - [ ] {task}")
else:
    console.print("\n[bold red]❌ GEOMETRY REJECTED — ENGINEERING SCREENING FAILED[/bold red]")
    status = result.get("status", "UNKNOWN_ERROR")
    
    if status == "NO_FEASIBLE_GEOMETRY":
        console.print(f"  Reason: Max bounds reached without achieving Safety Factor ≥ 1.5")
        console.print(f"  Governing Load: {screening.get('governing_load_case')} ({screening.get('governing_force_n')} N per arm)")
        console.print(f"  Resulting SF: {screening.get('governing_safety_factor')}")
        
    elif status == "INSUFFICIENT_THRUST":
        console.print(f"  Reason: Thrust-to-Weight Ratio (TWR) < 1.5")
        console.print(f"  Calculated TWR: {screening.get('thrust_to_weight_ratio')}")
        
    elif status in ["FAILED_PROP_COLLISION", "FAILED_BODY_COLLISION"]:
        console.print(f"  Reason: Geometric Interference Detected")
        console.print(f"  Prop-to-Prop Clearance: {clearance.get('min_prop_clearance_mm', 'N/A')} mm")
        console.print(f"  Prop-to-Body Clearance: {clearance.get('min_body_clearance_mm', 'N/A')} mm")
        console.print("  Recommendation: Increase frame diagonal or use smaller propellers.")
        
    elif status == "DFM_FAILED":
        console.print(f"  Reason: Design for Manufacturing (DFM) Constraints Violated")
        console.print(f"  Max Dims Tested: {screening.get('last_evaluated_width_mm')} mm W x {screening.get('last_evaluated_height_mm')} mm H")
        dfm_issues = screening.get('dfm_status', {}).get('issues', [])
        for issue in dfm_issues:
            console.print(f"  - [red]{issue}[/red]")
        console.print("  Recommendation: Adjust printer profile minimums or reduce frame cutouts.")
        
    elif status == "UNVERIFIED_PROVENANCE":
        console.print(f"  Reason: Bill of Materials contains unverified assumptions")
        console.print(f"  Structural and mass calculations require verified manufacturer data.")
        console.print(f"  [bold]Unverified Components:[/bold]")
        for comp_type, comp_data in [("Motor", hw_motor), ("Flight Controller", hw_fc), ("Battery", hw_batt)]:
            if comp_data.get("data_status") != "VERIFIED_DATASHEET":
                console.print(f"  - {comp_type} ({comp_data.get('name', 'N/A')}): [red]{comp_data.get('data_status', 'UNKNOWN')}[/red]")
        console.print("  Recommendation: Provide verified datasheets in hardware JSON before flight approval.")