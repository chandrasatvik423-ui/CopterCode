# CopterCode // Astro-Forge

CopterCode is an AI-assisted parametric UAV design and computational screening platform. It translates natural-language mission requirements into strict, deterministically bounded aerospace geometry. 

## Capabilities
* **Parametric Generation:** Generates multirotor geometries (4, 6, and 8 arms) based on mission payload and selected hardware.
* **Engineering Screening:** Evaluates structural integrity against explicit material limits (e.g., PLA yield stress) and calculates Thrust-to-Weight Ratios (TWR) using a verified hardware database.
* **Design for Manufacturing (DFM):** Verifies 3D printer constraints, including minimum wall thicknesses and fastener edge clearances.
* **Artifact Generation:** Outputs OpenSCAD scripts, ready-to-print STLs, and itemized CSV Bills of Materials (BOM).

## ⚠️ CERTIFICATION BOUNDARY & LIMITATIONS
**This software performs computational engineering screening only. Outputs are NOT flight certified.**

*   **No Flight Validation:** The generation of a `drone_blueprint.stl` flight candidate indicates that the geometry passed baseline computational math. It does not guarantee real-world flight safety.
*   **Assumption-Based Physics:** The physics engine relies on explicit heuristic assumptions (e.g., a 3G hard landing multiplier and a static 1.5 stress concentration factor) in place of rigorous Finite Element Analysis (FEA). 
*   **Physical Testing Required:** Do not execute flight without completing a required physical engineering certification path, including static load testing and vibration analysis. Software screening is not a substitute for physical validation.
