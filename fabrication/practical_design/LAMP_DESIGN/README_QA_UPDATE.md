# QA UPDATE: Helios V4-V8 Specification

**Status:** REFINED (Cycle 3002)
**Generator Script:** `fabrication/scripts/run_all_updates.sh`

## Overview
This update addresses critical QA failures identified in the V2 designs and user feedback regarding structural integrity and adhesion.

## 1. Lamp Shade (Refined)
**Improvements:**
*   **Spider Fitter:** Mandatory Hub + 3 Spokes (Triskelion) at the top. No "Crosshairs".
*   **Clearance:** 14mm Keep-Out Zone (7mm radius hole).
*   **Shell Masking:** Wall thickness constrained to **25.4mm (1 inch)** max.
*   **Solid Top Rim:** Top 10mm is forced SOLID (matching shell shape) to ensure the gyroid wave merges structurally.
*   **Solid Bottom Ring:** Bottom 2mm is forced SOLID (matching shell shape, 1 inch width) to ensure bed adhesion and base integrity.

**Generators:** `helios_lamp_shade_v*_gen.py`

## 2. Lamp Base
**Improvements:**
*   **Feet Recesses:** 4x cylindrical recesses.
*   **Wire Channel:** 8x8mm tunnel.
*   **Stability:** Solid Core (20mm radius).
*   **Nut Recess:** 30mm x 6mm counterbore.

## 3. Lamp Shaft
**Improvements:**
*   **Monolithic Integrity:** Thickened roots near core.
*   **Solid End Caps:** Top/Bottom 2mm solid.
*   **Channel:** 14mm internal clearance.

## Usage
To regenerate all artifacts:
```bash
./fabrication/scripts/run_all_updates.sh
```
