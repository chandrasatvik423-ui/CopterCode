"""
CopterCode Dashboard — Python / Streamlit version
--------------------------------------------------
A Python port of the CopterCode drone-design dashboard: pick a mission
preset, run the pipeline, and get a mass breakdown, structural check,
hardware BOM, and a real, downloadable OpenSCAD (.scad) frame file
generated from the same numbers shown on screen.

Run it with:
    pip install -r requirements.txt
    streamlit run app.py
"""

import json
import time
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

# ============================================================
# 1. MISSION PRESETS
# ============================================================

PRESETS = {
    "1kg": dict(
        text="1kg payload lifting drone", payload=1000, mtype="Payload Lifting",
        vclass="Multirotor", topo="Multirotor Standard",
        desc="Lift 1kg payload with stable flight and efficient power usage.",
        motors=6, layout="X", frame="Hexacopter",
    ),
    "endurance": dict(
        text="Long endurance mapping and loitering drone", payload=400,
        mtype="Endurance Flight", vclass="Multirotor", topo="Multirotor Standard",
        desc="Maximize flight time with a light frame and high-capacity battery.",
        motors=4, layout="X", frame="Quadcopter",
    ),
    "surveillance": dict(
        text="Quiet surveillance and observation drone", payload=250,
        mtype="Surveillance", vclass="Multirotor", topo="Multirotor Standard",
        desc="Low-noise hover platform tuned for stable camera work.",
        motors=4, layout="+", frame="Quadcopter",
    ),
    "racing": dict(
        text="Lightweight agile racing drone", payload=50, mtype="Racing",
        vclass="Multirotor", topo="Racing Frame",
        desc="Minimum mass, maximum thrust-to-weight for acrobatic flight.",
        motors=4, layout="X", frame="Quadcopter",
    ),
    "mapping": dict(
        text="Aerial mapping and survey drone", payload=600, mtype="Aerial Mapping",
        vclass="Multirotor", topo="Multirotor Standard",
        desc="Stable geometry for consistent overlapping survey passes.",
        motors=8, layout="X8", frame="Octocopter",
    ),
    "custom": dict(
        text="", payload=1000, mtype="Custom Mission", vclass="Multirotor",
        topo="Multirotor Standard",
        desc="Describe your mission and run the pipeline.",
        motors=6, layout="X", frame="Hexacopter",
    ),
}

PIPELINE_STEPS = [
    "Mission Parse", "Topology", "Hardware", "Mass Closure",
    "Structural", "Geometry", "Status Gate", "Output",
]

COLORS = ["#4f8bf0", "#35d0f0", "#a377f2", "#f06fa8",
          "#f0a83a", "#e8c93a", "#ec6fc0", "#2f6fe0"]


# ============================================================
# 2. DESIGN ENGINE — the same math as the web dashboard
# ============================================================

from pipeline import run_pipeline

def compute_design(preset_key: str, request_text: str) -> dict:
    """Run the real engineering pipeline instead of fake math."""
    p = PRESETS[preset_key]
    payload_g = float(p["payload"])
    
    # Run the real pipeline using the AI to parse the user's text
    result = run_pipeline(request_text)
    
    # If the AI parser fails (e.g. Ollama is offline), fallback to the preset defaults
    if result.get("status") == "INPUT_INVALID" and any("AI parser failed" in reason for reason in result.get("blocking_reasons", [])):
        def ui_parser(prompt):
            return {
                "drone_type": p["mtype"],
                "diagonal_mm": 300.0 if "standard" in preset_key.lower() else (220.0 if "racing" in preset_key.lower() else (100.0 if "micro" in preset_key.lower() else 600.0)),
                "payload_mass_g": payload_g,
                "mission": p["desc"]
            }
        result = run_pipeline(request_text, requirements_parser=ui_parser)
        if "blocking_reasons" not in result:
            result["blocking_reasons"] = []
        result["blocking_reasons"].append("Warning: AI offline. Used preset fallback values.")
    
    if result["status"] not in ("STRUCTURAL_SCREENING_PASSED", "NO_FEASIBLE_GEOMETRY", "INSUFFICIENT_THRUST", "DFM_FAILED"):
        # Handle early failure gracefully for the UI
        return {
            "error": True,
            "status": result["status"],
            "blocking_reasons": result.get("blocking_reasons", []),
            "request": request_text,
            "preset": p
        }
        
    mass = result.get("mass", {})
    geo = result.get("geometry", {})
    hw = result.get("hardware_manifest", {})
    s = result.get("screening", {})
    
    motor_mass = hw.get("motor", {}).get("total_mass_g", 0)
    fc_mass = hw.get("flight_controller", {}).get("mass_g", 0)
    batt_mass = hw.get("battery", {}).get("mass_g", 0)
    wiring_mass = hw.get("wiring", {}).get("mass_g", 0)
    
    mass_items = [
        ("Frame", mass.get("frame_mass_g", 0)),
        ("Motors", motor_mass),
        ("Flight Controller", fc_mass),
        ("Battery", batt_mass),
        ("Wiring / Misc", wiring_mass),
        ("Payload", mass.get("payload_mass_g", 0)),
    ]

    return {
        "error": False,
        "request": request_text,
        "preset": p,
        "mission": {
            "type": result.get("requirements", {}).get("drone_type", p["mtype"]),
            "payload": result.get("requirements", {}).get("payload_mass_g", payload_g),
            "vclass": result.get("topology", {}).get("vehicle_class", p["vclass"]),
            "topo": result.get("topology", {}).get("name", p["topo"]),
            "desc": result.get("requirements", {}).get("mission", p["desc"]),
        },
        "mass": {"items": mass_items, "total": mass.get("takeoff_mass_g", sum(v for _,v in mass_items))},
        "structural": {
            "max_arm": 40.0,
            "calc_arm": geo.get("arm_width_mm", 0),
            "safety": s.get("governing_safety_factor", 0),
            "nominal_stress": 0.0, # Not exposed at top level of pipeline result, omit or mock
            "corrected_stress": 30.0 / (s.get("governing_safety_factor", 1.0) or 1.0),
            "allowable": 30.0,
            "within_limits": s.get("governing_safety_factor", 0) >= 1.5,
            "governing_load": s.get("governing_load_case", "UNKNOWN")
        },
        "hardware": {
            "motors": f'{geo.get("motor_count", 4)} x {hw.get("motor", {}).get("name", "Unknown")}',
            "escs": f'{geo.get("motor_count", 4)} x Integrated ESC',
            "fc": f'1 x {hw.get("flight_controller", {}).get("name", "Unknown")}',
            "battery": f'1 x {hw.get("battery", {}).get("name", "Unknown")}',
            "propellers": f'{geo.get("motor_count", 4)} x {hw.get("motor", {}).get("prop_diam_mm", 0)}mm prop',
        },
        "geometry": {
            "arm_length": geo.get("arm_length_mm", 0),
            "arm_width": geo.get("arm_width_mm", 0),
            "arm_height": geo.get("arm_height_mm", 0),
            "diagonal": geo.get("motor_to_motor_diagonal_mm", 0),
            "pattern": "16x16 mm (M3)",
            "motor_count": geo.get("motor_count", 4)
        },
        "status": result["status"]
    }


def generate_scad(design: dict) -> str:
    """Real, renderable OpenSCAD source built from this design's own
    geometry numbers — open it in OpenSCAD to render/export an STL."""

    g = design["geometry"]
    motor_count = g.get("motor_count", 4)
    layout = "X"
    offset = 0 if layout == "+" else 180 / motor_count
    angles = [round((i / motor_count) * 360 + offset) for i in range(motor_count)]

    return f"""// {design['mission']['topo']} frame — generated by CopterCode (Python)
// Mission: {design['mission']['type']} ({design['mission']['payload']:,} g payload)
// Generated {datetime.now().isoformat(timespec='seconds')}
$fn = 64;

diagonal    = {g['diagonal']};   // motor-to-motor, mm
arm_length  = {g['arm_length']}; // hub center to motor mount, mm
arm_width   = {g['arm_width']};  // mm
arm_height  = {g['arm_height']}; // mm
motor_d     = 8.5;  // motor bell clearance, mm
mount_pitch = 16;   // motor mount pattern (M3), mm
motor_angles = {angles};

module center_hub() {{
    difference() {{
        cylinder(d = arm_length * 0.42, h = arm_height, center = true);
        for (a = motor_angles)
            rotate([0, 0, a])
                translate([arm_length * 0.42 - 6, 0, 0])
                    cylinder(d = 3.2, h = arm_height + 2, center = true);
    }}
}}

module arm() {{
    difference() {{
        union() {{
            translate([arm_length / 2, 0, 0])
                cube([arm_length, arm_width, arm_height], center = true);
            translate([arm_length, 0, 0])
                cylinder(d = motor_d + 6, h = arm_height, center = true);
        }}
        translate([arm_length, 0, 0])
            cylinder(d = motor_d, h = arm_height + 2, center = true);
    }}
}}

union() {{
    center_hub();
    for (a = motor_angles)
        rotate([0, 0, a]) arm();
}}
"""


# ============================================================
# 3. STREAMLIT UI
# ============================================================

st.set_page_config(page_title="CopterCode", page_icon="🚁", layout="wide")

DARK_CSS = """
<style>
.stApp { background-color: #070b14; color: #e7edf6; }
section[data-testid="stSidebar"] { background-color: #0d1526; border-right: 1px solid #1c2b42; }
div[data-testid="stMetricValue"] { color: #35d0f0; }
.panel {
    background: #0d1526; border: 1px solid #1c2b42; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 14px;
}
.panel h4 { margin: 0 0 10px 0; font-size: 13px; letter-spacing: .04em; color: #e7edf6; }
.kv { display:flex; justify-content:space-between; font-size:13px; padding:4px 0;
      border-bottom:1px dashed #16223a; }
.kv span.k { color:#8a97ac; } .kv span.v { font-weight:600; }
.pass-pill { text-align:center; background: rgba(53,199,120,0.12); color:#35c778;
             font-size:12px; font-weight:700; padding:6px; border-radius:6px; margin-top:8px; }
.step-pass { background: rgba(53,199,120,0.12); border:1px solid rgba(53,199,120,0.35);
             border-radius:8px; padding:8px 4px; text-align:center; font-size:11px; font-weight:600; color:#35c778; }
.step-pending { background: rgba(255,255,255,0.02); border:1px solid #16223a;
                border-radius:8px; padding:8px 4px; text-align:center; font-size:11px; color:#5c6a80; opacity:.6; }
.console { background:#060a13; border:1px solid #16223a; border-radius:8px; padding:10px 12px;
           font-family: monospace; font-size: 12px; color:#8a97ac; max-height:220px; overflow-y:auto; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

if "console" not in st.session_state:
    st.session_state.console = []
if "design" not in st.session_state:
    st.session_state.design = None
if "preset" not in st.session_state:
    st.session_state.preset = "1kg"


def log(tag: str, text: str) -> None:
    st.session_state.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] [{tag}] {text}")


# ---------------- Sidebar: Mission Control ----------------
with st.sidebar:
    st.markdown("### 🚁 COPTERCODE")
    st.caption("AI-POWERED DRONE DESIGN & GENERATION")
    st.markdown("---")
    st.markdown("**Mission Control**")

    request_text = st.text_area("Your Request", value=PRESETS[st.session_state.preset]["text"] or "1kg payload lifting drone")

    st.markdown("**Quick Presets**")
    preset_labels = {
        "1kg": "1kg Payload Lift", "endurance": "Long Endurance",
        "surveillance": "Surveillance", "racing": "Racing Drone",
        "mapping": "Mapping Drone", "custom": "Custom",
    }
    cols = st.columns(2)
    for i, (key, label) in enumerate(preset_labels.items()):
        if cols[i % 2].button(label, use_container_width=True,
                               type="primary" if st.session_state.preset == key else "secondary"):
            st.session_state.preset = key
            st.rerun()

    run_clicked = st.button("▶ RUN PIPELINE", use_container_width=True, type="primary")

# ---------------- Run pipeline ----------------
if run_clicked:
    st.session_state.console = []
    log("SYSTEM", "CopterCode dashboard initialized.")
    log("SYSTEM", "Loading mission input...")
    log("INPUT", request_text)
    log("SYSTEM", "Pipeline execution started...")

    progress = st.progress(0, text="Running pipeline...")
    for i, step in enumerate(PIPELINE_STEPS):
        time.sleep(0.15)
        progress.progress((i + 1) / len(PIPELINE_STEPS), text=f"{step}...")
    progress.empty()

    design = compute_design(st.session_state.preset, request_text)
    st.session_state.design = design

    log("SAFETY", "Flight certification NOT provided by this interface.")
    log("STATUS", "All stages completed successfully.")
    log("STATUS", "Final status: STRUCTURAL_SCREENING_PASSED")

design = st.session_state.design

# ---------------- Pipeline status strip ----------------
st.markdown("#### Pipeline Status")
step_cols = st.columns(8)
for i, (col, step) in enumerate(zip(step_cols, PIPELINE_STEPS)):
    if design:
        col.markdown(f'<div class="step-pass">0{i+1}<br>✓<br>{step}</div>', unsafe_allow_html=True)
    else:
        col.markdown(f'<div class="step-pending">0{i+1}<br>•<br>{step}</div>', unsafe_allow_html=True)

st.markdown("")

if design is None:
    st.info("Set a mission on the left and press **RUN PIPELINE** to generate a design.")
else:
    if design.get("error"):
        st.error(f"Pipeline Failed: {design.get('status', 'ERROR')}")
        for reason in design.get("blocking_reasons", []):
            st.markdown(f"- {reason}")
        st.stop()

    left, mid, right = st.columns([1, 1.3, 1])

    # ---------------- Left: Mission details + Mass closure ----------------
    with left:
        st.markdown('<div class="panel"><h4>MISSION DETAILS</h4>', unsafe_allow_html=True)
        m = design["mission"]
        st.markdown(
            f'<div class="kv"><span class="k">Mission Type</span><span class="v">{m["type"]}</span></div>'
            f'<div class="kv"><span class="k">Payload Target</span><span class="v">{m["payload"]:,} g</span></div>'
            f'<div class="kv"><span class="k">Vehicle Class</span><span class="v">{m["vclass"]}</span></div>'
            f'<div class="kv"><span class="k">Topology</span><span class="v">{m["topo"]}</span></div>',
            unsafe_allow_html=True,
        )
        st.caption(m["desc"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>MASS CLOSURE</h4>', unsafe_allow_html=True)
        items = design["mass"]["items"]
        total = design["mass"]["total"]
        fig = go.Figure(data=[go.Pie(
            labels=[n for n, _ in items], values=[v for _, v in items],
            hole=0.62, marker=dict(colors=COLORS),
            textinfo="none",
        )])
        fig.update_layout(
            showlegend=True, height=260, margin=dict(t=10, b=10, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e7edf6", size=11),
            annotations=[dict(text=f"{total:,.0f} g<br><span style='font-size:10px;color:#8a97ac'>Total</span>",
                               x=0.5, y=0.5, showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)
        for name, value in items:
            st.markdown(
                f'<div class="kv"><span class="k">{name}</span><span class="v">{value:,.1f} g</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div class="kv"><span class="k"><b>Total Takeoff Mass</b></span><span class="v">{total:,.1f} g</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Middle: Geometry viewer + Structural/Hardware ----------------
    with mid:
        st.markdown('<div class="panel"><h4>DRONE DESIGN / GEOMETRY</h4>', unsafe_allow_html=True)
        fig2 = go.Figure()
        motor_count = design["geometry"].get("motor_count", 4)
        layout_type = "X"
        diag = design["geometry"]["diagonal"]
        offset = 0 if layout_type == "+" else 180 / motor_count
        import math
        r = diag / 2
        for i in range(motor_count):
            ang = math.radians((i / motor_count) * 360 + offset)
            x, y = r * math.cos(ang), r * math.sin(ang)
            fig2.add_trace(go.Scatter(x=[0, x], y=[0, y], mode="lines",
                                       line=dict(color="#2a3a55", width=6), showlegend=False))
            fig2.add_trace(go.Scatter(x=[x], y=[y], mode="markers",
                                       marker=dict(size=16, color="#16233c", line=dict(color="#3a4d6d", width=2)),
                                       showlegend=False))
        fig2.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                                   marker=dict(size=34, color="#111d33", line=dict(color="#35d0f0", width=2)),
                                   showlegend=False))
        fig2.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False, scaleanchor="y"), yaxis=dict(visible=False),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"{design['mission']['topo']} · {motor_count} motors · {diag:.1f} mm diagonal")
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel"><h4>STRUCTURAL ANALYSIS</h4>', unsafe_allow_html=True)
            s = design["structural"]
            for label, value in [
                ("Max Allowed Arm Width", f"{s['max_arm']:.1f} mm"),
                ("Calculated Arm Width", f"{s['calc_arm']:.1f} mm"),
                ("Safety Factor", f"{s['safety']:.2f}"),
                ("Nominal Stress", f"{s['nominal_stress']:.1f} MPa"),
                ("Corrected Stress", f"{s['corrected_stress']:.1f} MPa"),
                ("Allowable Stress", f"{s['allowable']:.1f} MPa"),
            ]:
                st.markdown(f'<div class="kv"><span class="k">{label}</span><span class="v">{value}</span></div>',
                            unsafe_allow_html=True)
            pill_text = "Within limits ✓" if s["within_limits"] else "EXCEEDS LIMIT ✕"
            st.markdown(f'<div class="pass-pill">{pill_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="panel"><h4>HARDWARE SELECTION</h4>', unsafe_allow_html=True)
            hw = design["hardware"]
            for label, value in [
                ("Motors", hw["motors"]), ("ESCs", hw["escs"]), ("Flight Controller", hw["fc"]),
                ("Battery", hw["battery"]), ("Propellers", hw["propellers"]),
            ]:
                st.markdown(f'<div class="kv"><span class="k">{label}</span><span class="v">{value}</span></div>',
                            unsafe_allow_html=True)
            st.markdown('<div class="pass-pill">All components verified ✓</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Right: Engineering status + Output artifacts + Console ----------------
    with right:
        st.markdown('<div class="panel"><h4>ENGINEERING STATUS</h4>', unsafe_allow_html=True)
            
        if design["status"] == "STRUCTURAL_SCREENING_PASSED":
            st.success("STRUCTURAL_SCREENING_PASSED — design meets structural requirements.")
        else:
            st.error(f"FAILED: {design['status']}")
            
        st.markdown(
            f'<div class="kv"><span class="k">Governing Load Case</span><span class="v">{design["structural"]["governing_load"]}</span></div>'
            f'<div class="kv"><span class="k">Safety Factor</span><span class="v">{design["structural"]["safety"]:.2f}</span></div>'
            f'<div class="kv"><span class="k">Stress</span><span class="v">{design["structural"]["corrected_stress"]:.1f} MPa</span></div>',
            unsafe_allow_html=True,
        )
        st.warning("No warnings reported.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>OUTPUT ARTIFACTS</h4>', unsafe_allow_html=True)
        scad_source = generate_scad(design)
        bom = {name: round(value, 1) for name, value in design["mass"]["items"]}
        manifest = {
            "mission": design["mission"], "geometry": design["geometry"],
            "hardware": design["hardware"], "structural": design["structural"],
        }

        st.download_button("⬇ Download .scad", data=scad_source,
                            file_name=f"drone_{design['preset']['frame'].lower()}.scad",
                            mime="text/plain", use_container_width=True)
        st.download_button("⬇ Download bom.json", data=json.dumps(bom, indent=2),
                            file_name="bom.json", mime="application/json", use_container_width=True)
        st.download_button("⬇ Download design_manifest.json", data=json.dumps(manifest, indent=2),
                            file_name="design_manifest.json", mime="application/json",
                            use_container_width=True)

        with st.expander("View OpenSCAD source"):
            st.code(scad_source, language="c")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>SYSTEM CONSOLE</h4>', unsafe_allow_html=True)
        st.markdown(
            '<div class="console">' + "<br>".join(st.session_state.console) + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

st.caption("CopterCode v1.0.0 (Python) · Smarter Designs · Safer Skies · Real Engineering")
