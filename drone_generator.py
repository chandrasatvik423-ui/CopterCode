import os
import shutil
import subprocess


def find_openscad() -> str | None:
    """Cross-platform OpenSCAD executable discovery."""
    candidates = [
        r"C:\Program Files\OpenSCAD\openscad.exe",
        r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
        "/usr/bin/openscad",
        "/usr/local/bin/openscad",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return shutil.which("openscad")


def generate_drone_frame(
    diagonal_mm: float,
    arm_width: float,
    arm_height: float,
    motor_diam: float,
    pcb_length: float,
    pcb_width: float,
    mount_pattern: dict,
    drone_type: str,
    output_filename: str,
    motor_count: int = 4,
    screening_passed: bool = False,
    placement_data: dict = None,
    auto_open: bool = False
):
    if placement_data is None:
        placement_data = {}

    openscad_path = find_openscad()

    scad_filename = output_filename.replace(".stl", ".scad")
    radius = diagonal_mm / 2.0

    # --- FC Standoff holes & Battery strap slots ---
    placement_cuts = ""
    fc_coords = placement_data.get("fc_standoffs", [])
    fc_diam = placement_data.get("fc_hole_diameter_mm", 3.0)
    for x, y in fc_coords:
        placement_cuts += (
            f"        translate([{x}, {y}, 0])"
            f" cylinder(h={arm_height + 2}, d={fc_diam}, center=true, $fn=20);\n"
        )

    battery_slots = placement_data.get("battery_strap_slots", [])
    for slot in battery_slots:
        cx, cy = slot["center"]
        sw = slot["width"]
        sl = slot["length"]
        placement_cuts += (
            f"        translate([{cx}, {cy}, 0])"
            f" cube([{sw}, {sl}, {arm_height + 2}], center=true);\n"
        )

    # --- Dynamic radial geometry for 4, 6, 8 arms ---
    angle_offset = 180.0 / motor_count
    angles = [(i * (360.0 / motor_count)) + angle_offset for i in range(motor_count)]

    # --- Motor mount holes ---
    motor_cuts = ""
    if mount_pattern:
        mount_coords = mount_pattern.get("coordinates_mm", [])
        hole_d = mount_pattern.get("hole_diameter_mm", 3.0)
        for angle in angles:
            motor_cuts += f"        rotate([0, 0, {angle}]) translate([{radius}, 0, 0]) {{\n"
            motor_cuts += (
                f"            cylinder(h={arm_height + 2},"
                f" d={motor_diam * 0.4}, center=true, $fn=30);\n"
            )
            for mx, my in mount_coords:
                motor_cuts += (
                    f"            translate([{mx}, {my}, 0])"
                    f" cylinder(h={arm_height + 2}, d={hole_d}, center=true, $fn=20);\n"
                )
            motor_cuts += "        }\n"

    # --- Structural arms ---
    arms_scad = ""
    for angle in angles:
        arms_scad += (
            f"        rotate([0, 0, {angle}])"
            f" translate([{radius / 2}, 0, 0])"
            f" cube([{radius}, {arm_width}, {arm_height}], center=true);\n"
        )
        arms_scad += (
            f"        rotate([0, 0, {angle}])"
            f" translate([{radius}, 0, 0])"
            f" cylinder(h={arm_height}, d={motor_diam + 4}, center=true, $fn=50);\n"
        )

    # Centre body height matches arm height (structural continuity fix)
    scad_script = f"""// COPTERCODE AUTO-GENERATED FRAME
// MISSION: {drone_type}
// TOPOLOGY: {motor_count} ARMS
// STATUS: {"PASSED" if screening_passed else "FAILED - REJECTED FOR FLIGHT"}

difference() {{
    union() {{
        // Central hub — height matches arm_height for joint continuity
        cube([{pcb_width}, {pcb_length}, {arm_height}], center=true);
{arms_scad}
    }}
    union() {{
        // FC standoffs, battery slots
{placement_cuts}
        // Motor mount holes
{motor_cuts}
    }}
}}
"""

    with open(scad_filename, "w") as f:
        f.write(scad_script)

    print(f"[Generator] Compiling ready-to-print STL file: {output_filename}...")

    if openscad_path:
        try:
            subprocess.run(
                [openscad_path, "-o", output_filename, scad_filename],
                check=True,
                capture_output=True
            )
            print(f"[Generator] ✅ STL Export Complete: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"[Generator] ❌ STL Compilation failed: {e}")
    else:
        print("[Generator] ⚠️ OpenSCAD not found. SCAD file written; STL not compiled.")

    if auto_open and openscad_path:
        try:
            if os.name == "nt":
                os.startfile(scad_filename)
            else:
                subprocess.Popen([openscad_path, scad_filename])
            print(f"[Generator] 🖥️ Opened visualizer for: {scad_filename}")
        except Exception as e:
            print(f"[Generator] ⚠️ Could not auto-launch OpenSCAD GUI: {e}")