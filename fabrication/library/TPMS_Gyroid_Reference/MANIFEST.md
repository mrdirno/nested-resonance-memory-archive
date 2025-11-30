# TPMS_Gyroid_Reference

**Scientific Classification:** Triply Periodic Minimal Surface (TPMS) - Gyroid
**Equation:** `sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0`
**Reference Scale:** 40 mm base size, exported at 120-sample resolution, metric units.
**Geometry License:** GPL-3.0, consistent with parent repository.

## Contents

1.  **Source Geometry:** `TPMS_Gyroid_HighRes.stl`
    *   Format: ASCII STL
    *   Vertices: ~426k
    *   Base Unit: Millimeters

2.  **Documentation:** `README.md` (Scientific context, biological references, mathematical definition).

3.  **Fabrication Files (G-code):**
    *   `TPMS_Gyroid_40mm.gcode`
        *   **Time:** ~2 hours
        *   **Profile:** Ender 3 (Klipper)
        *   **Nozzle:** 0.4mm
        *   **Layer Height:** 0.2mm
        *   **Material:** Generic PLA
        *   **Infill:** 0% (Self-supporting shell)
    *   `TPMS_Gyroid_76mm.gcode`
        *   **Time:** ~17 hours
        *   **Profile:** Ender 3 (Klipper)
        *   **Nozzle:** 0.4mm
        *   **Layer Height:** 0.2mm
        *   **Material:** Generic PLA
        *   **Infill:** 0% (Self-supporting shell)

## Significance
This directory serves as a standardized reference for the Gyroid geometry within the Duality Fabrication Library. It is decoupled from specific project branding ("Helios") to serve as a neutral scientific control.