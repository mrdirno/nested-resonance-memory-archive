# QA UPDATE: Helios V4 Specification (Cycle 1101)

**Status:** IMPLEMENTED
**Generator:** `fabrication/scripts/run_qa_generation.sh`

## Overview
This update addresses critical QA failures identified in the V2 designs (Gemini Memories compliance).

## 1. Lamp Shade V4
**Improvements:**
*   **Spider Fitter:** Mandatory Hub + 4 Spokes structure implemented at the top mounting point.
*   **Clearance:** 14mm Keep-Out Zone (7mm radius hole) enforced for standard 1/8 IP nipples.
*   **Shell Masking:** Wall thickness constrained to ~25.4mm (1 inch) max, ensuring a hollow void rather than a solid block.
*   **Safety:** Structural integrity validated via "Crust" logic (solid rim merge).

**Generator:** `fabrication/generators/helios_lamp_shade_v4_gen.py`

## 2. Lamp Base V4
**Improvements:**
*   **Feet Recesses:** 4x cylindrical recesses (10mm radius, 3mm depth) added to bottom corners for rubber feet/pads.
*   **Wire Channel:** 8x8mm tunnel subtracted from center to edge to prevent cord crushing.
*   **Stability:** Solid Core (20mm radius) added around mounting hole for weighted stability.
*   **Pattern:** Anisotropic Gyroid maintained for aesthetic continuity.

**Generator:** `fabrication/generators/helios_lamp_base_v4_gen.py`

## Usage
To regenerate the artifacts:
```bash
./fabrication/scripts/run_qa_generation.sh
```
Outputs will be saved to `lamp_base/lamp_base_v4_QA.stl` and `lamp_shade/lamp_shade_v4_QA.stl`.
