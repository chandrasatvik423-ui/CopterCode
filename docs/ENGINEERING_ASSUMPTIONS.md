# CopterCode — Engineering Assumptions

> **IMPORTANT**: This document is a mandatory part of the CopterCode codebase.
> It lists every engineering simplification made in the screening models.
> Users must understand these assumptions before interpreting any output.

---

## Structural Screening (`physics_engine.py`)

### A1 — Euler–Bernoulli Beam Model
Each arm is modelled as a **cantilever beam** with the motor load applied at the tip and the root fixed to the central hub.

*Reality:* Arms are attached with finite-stiffness joints, the hub flexes, and vibration introduces fatigue loading. A full FEA with meshed joints is required for certification.

### A2 — Hollow Rectangular Cross-Section
The arm cross-section is assumed to be a **perfect hollow rectangle** with constant wall thickness along the full arm length.

*Reality:* 3D-printed parts have draft angles, layer adhesion anisotropy, infill voids, and surface roughness. The actual area moment of inertia will differ from the idealized value.

### A3 — Stress Concentration Factor Kt = 1.5
A fixed Kt of **1.5** is applied at the motor-mount root to approximate the stress raiser introduced by the bolt pattern and fillets.

*Basis:* Conservative engineering estimate for a bolted joint in FDM plastic. Not experimentally calibrated for CopterCode frame geometry. Physical coupon testing required.

### A4 — Load Cases
Three static load cases are evaluated:

| Case | Force (per arm) | Engineering rationale |
|------|-----------------|-----------------------|
| HOVER | Total weight / motor count | 1 g level flight |
| MAX_THRUST | Motor max_thrust_n | Full-throttle pull-up |
| HARD_LANDING | 3× total weight / motor count | 3g impact factor — industry screening heuristic |

*Reality:* Dynamic loads (wind gusts, rotor wash, resonance) are not modelled.

### A5 — PLA Allowable Stress = 30 MPa
The default allowable bending stress for PLA is **30 MPa** (source: `config/materials.json`, status: `ASSUMED`).

*Reality:* Published PLA tensile strength ranges from 37–65 MPa depending on brand, print settings, and humidity. The 30 MPa value is a conservative screening limit. It must be validated by physical test before flight.

---

## Manufacturing Estimation (`manufacturing_estimator.py`)

### B1 — Arm Volume Approximation
Arm volume is estimated as:
```
arm_vol = arm_length × arm_width × arm_height × (1 - 0.50 × 0.35)
```
The `0.50 × 0.35` term represents a 50%-length wire channel that occupies 35% of the cross-section.

### B2 — Central Body as Flat Plate
The central hub is modelled as:
```
body_vol = pcb_length × pcb_width × arm_height_mm
```
Standoffs, component relief pockets, and mounting bosses are not modelled.

### B3 — FDM Print Rate
Default print rate is **45 g/hr** for PLA (source: `config/materials.json`, status: `ASSUMED`).
Actual rate depends on slicer profile, nozzle diameter, and machine.

---

## Geometry & Propeller Clearance (`geometry_engine.py`)

### C1 — Single-Plane Clearance Check
Propeller clearance is checked in a **2D top-down projection** only.
Vertical tip-path clearance (propeller to arm surface in the plane of rotation) is not computed.

### C2 — Body Clearance Buffer = 15 mm
A fixed **15 mm** buffer is added to PCB body dimensions before checking whether props overhang the body.
This is configurable via `CONFIG.safety.body_clearance_buffer_mm`.

---

## Flight Dynamics (`dynamics_engine.py`)

### D1 — Simplified Endurance Model
Endurance is estimated from battery capacity and average current draw using a simplified energy model.
Aerodynamic efficiency (figure of merit), motor efficiency curves, and ESC losses are not modelled.

---

## Certification Boundary

```
flight_certification_status: NOT_CERTIFIED
```

CopterCode outputs are **screening candidates only**. No output from this tool constitutes
airworthiness approval, flight certification, or regulatory compliance under any jurisdiction
(including but not limited to FAA Part 107, EASA UAS regulations, or equivalent).

Required certification steps before any CopterCode design may fly:
1. Physical static load test to destruction (margin verification)
2. Dynamic vibration / resonance sweep
3. DFM tolerance stack-up verification with actual hardware
4. Regulatory review and registration
