# CopterCode — Hardcode Governance Audit

> **Document status:** LIVING DOCUMENT — updated whenever a new constant is introduced or an existing one is externalised.

This document records the audit trail for every constant, magic number, and assumed value that has ever appeared in CopterCode source code. Its purpose is to prove to reviewers (and to our future selves) that no unexplained value silently governs engineering decisions.

---

## Phase 0 — Baseline (pre-audit state)

| File | Line | Value | Description | Disposition |
|------|------|-------|-------------|-------------|
| `physics_engine.py` | 7 | `30.0` MPa | PLA allowable bending stress | **MOVED** → `config/materials.json["PLA"]["allowable_stress_mpa"]` |
| `physics_engine.py` | 8 | `1.5` | Stress concentration factor Kt | **DOCUMENTED** → module docstring + `ENGINEERING_ASSUMPTIONS.md` |
| `manufacturing_estimator.py` | 16 | `1.24` g/cm³ | PLA density | **MOVED** → `config/materials.json["PLA"]["density_g_cm3"]` |
| `manufacturing_estimator.py` | 19 | `0.02` USD/g | PLA material cost | **MOVED** → `config/materials.json["PLA"]["cost_per_kg_usd"]` |
| `manufacturing_estimator.py` | 22 | `4.0` g/hr | PLA FDM print rate | **MOVED** → `config/materials.json["PLA"]["print_rate_g_hr"]` |
| `pipeline.py` | 73 | `15.0` mm | Body-to-prop clearance buffer | **MOVED** → `CONFIG.safety.body_clearance_buffer_mm` |
| `pipeline.py` | 95 | `40.0` mm | Max solver arm width | **MOVED** → `CONFIG.solver.max_arm_width_mm` |
| `pipeline.py` | 95 | `12.0` mm | Min solver arm width | **MOVED** → `CONFIG.solver.min_arm_width_mm` |
| `pipeline.py` | 113 | `1.5` | Min structural safety factor | **MOVED** → `CONFIG.safety.min_structural_safety_factor` |
| `pipeline.py` | 114 | `1.5` | Min thrust-to-weight ratio | **MOVED** → `CONFIG.safety.min_thrust_to_weight_ratio` |
| `pipeline.py` | 118 | `2.0×` | Max height multiplier limit | **MOVED** → `CONFIG.solver.height_multiplier_limit` |

---

## Phase 1 — Post-audit state

All values listed above have been externalised. The remaining `1.2` and `2.0` literals in `pipeline.py` are printer-profile slot values (minimum wall thickness) that belong in a future `config/printer_profiles.json`.

### Remaining known assumptions (not yet externalised)
| File | Value | Description | Action |
|------|-------|-------------|--------|
| `pipeline.py` | `1.2` mm | Minimum FDM wall thickness | Future: `config/printer_profiles.json` |
| `pipeline.py` | `2.0` mm | Minimum edge clearance | Future: `config/printer_profiles.json` |
| `dfm_engine.py` | various | DFM rule thresholds | Future: `config/dfm_rules.json` |

---

## Governance Rules

1. **No float literal may be introduced** in any `_engine.py`, `pipeline.py`, or `estimator.py` without a corresponding entry in this document or a named config key.
2. Every `config/*.json` value must carry `"status"` (`"VERIFIED_DATASHEET"` or `"ASSUMED"`) and `"source"`.
3. Assumed values must be confirmed by physical test or manufacturer datasheet before this tool is used for flight certification decisions.
