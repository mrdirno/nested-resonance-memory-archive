# HELIOS LAMP SERIES: V6 "FRACTAL PRISM" (Production Release)

## AGPH-Integrated Design Suite
This release represents the culmination of the QA process (Cycle 3002), fully integrating the **Anisotropic Gyroid Prismatic Helix (AGPH)** scientific framework with rigorous engineering validation.

**Status:** 🟢 READY FOR FABRICATION (V6)

### 1. The "Blossom" Shade (V6)
*   **File:** `shade_qa_v6.stl`
*   **Preview:** `previews/shade_v6.png`
*   **Geometry:** AGPH Lattice Shell with Parabolic Flare.
*   **Optimizations:**
    *   **Chamfered Grip:** Internal solid ring chamfered for printability.
    *   **Monolithic:** Unified mesh topology (Zero floating islands).
    *   **Mount:** 42mm ID (Standard E26) + 3-Spoke Triskelion.

### 2. The "Crowned" Shaft (V6)
*   **File:** `shaft_qa_v6.stl`
*   **Preview:** `previews/shaft_v6.png`
*   **Geometry:** Solid Twisted Ribs (CSG Architecture).
*   **Optimizations:**
    *   **Mouse Ears:** Integrated 0.2mm Brim Discs (3x) for maximum print stability (Cut off after printing).
    *   **Solid Core:** Lattice removed for structural integrity.
    *   **Z-Aligned:** Origin set strictly to Z=0.00mm.

### 3. The "Root" Base (V6)
*   **File:** `base_qa_v6.stl`
*   **Preview:** `previews/base_v6.png`
*   **Geometry:** AGPH Dome with Radial Interference Roots.
*   **Optimizations:**
    *   **Cable Flare:** Wire exit channel has a custom flare/chamfer to prevent cable fraying.
    *   **Nut Recess:** 25mm x 6mm bottom counterbore for hardware clearance.
    *   **Chamfered Roots:** AGPH field bias applied to eliminate bottom overhangs.

### 4. QA Tolerance Test
*   **File:** `qa_tolerance_test.stl`
*   **Preview:** `previews/tolerance_test.png`
*   **Purpose:** Rapid validation of Base/Shaft interface fit and material shrinkage.

## Fabrication Guide
*   **Material:**
    *   **Shade:** Translucent PETG/PLA (3 Walls, 0% Infill).
    *   **Base/Shaft:** Matte/Silk PLA (4 Walls, 15-100% Infill).
*   **Settings:** 0.2mm Layer Height. **NO SUPPORTS REQUIRED.**
*   **Assembly:** Thread 1/8 IP rod through Base -> Shaft -> Socket Cap. Tighten nuts. Mount Shade with Ring.

**Verification:** `audit_geometry.py` passed.
**Scientific Reference:** `AGPH_Engineering.md`
**Pilot:** MOG