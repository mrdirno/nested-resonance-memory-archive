# HELIOS LAMP SERIES: PHYSICAL MANIFEST (Production Release)

## Status: 🟢 READY FOR FABRICATION (Cycle 2999)

This manifest tracks the physical artifacts authorized for production. All files have passed **Deep Geometric Audit** (Z-Alignment, Connectivity, Overhang Analysis).

### 1. Base Component
*   **File:** `base_qa_v6.stl`
*   **Description:** "Root" Base with AGPH radial interference pattern.
*   **Optimizations:**
    *   **Chamfered Roots:** Bottom 5mm bias-field applied to eliminate bed-level overhangs.
    *   **Vertical Anisotropy:** Adjusted to (1.0, 1.0, 1.0) to reduce overhang steepness on root arches.
*   **Key Features:**
    *   **Arch Tunnel:** 12x12mm wire exit (Braided cable safe).
    *   **Socket Recess:** 40.5mm ID x 3mm Depth (Gravity lock).
*   **Print Settings:**
    *   **Material:** Matte PLA (Stone/Marble).
    *   **Infill:** 100% (Required for ballast/stability).
    *   **Walls:** 4+.
    *   **Supports:** None required (Overhangs < 13% non-critical).

### 2. Shaft Component
*   **File:** `shaft_qa_v6.stl`
*   **Description:** "Pillar" Shaft with Solid Twisted Ribs (CSG).
*   **Optimizations:**
    *   **Pure Solid:** Internal lattice removed for maximum printability and weight.
    *   **Z-Aligned:** Mesh origin normalized to Z=0.00mm.
*   **Key Features:**
    *   **Cable Core:** 15.0mm guaranteed internal clearance.
    *   **Crown Flare:** 55mm top diameter (Visual integration).
*   **Print Settings:**
    *   **Material:** Silk PLA (Metallic/Opaque).
    *   **Infill:** 15% Gyroid (Structural).
    *   **Walls:** 3+.
    *   **Supports:** None required (Ribs are self-supporting < 45 deg).

### 3. Shade Component
*   **File:** `shade_qa_v6.stl`
*   **Description:** "Blossom" Shade with AGPH Lattice Shell.
*   **Optimizations:**
    *   **Chamfered Grip:** Internal Grip Zone chamfered to reduce overhangs during print.
    *   **Unified Mesh:** Monolithic topology (no floating islands).
*   **Key Features:**
    *   **Grip Zone:** Integrated Solid Ring for handling.
    *   **Mount:** 42mm Standard E26 + 3-Spoke Triskelion.
*   **Print Settings:**
    *   **Material:** Translucent PETG/PLA.
    *   **Infill:** 0% (Walls Only) if printing hollow, or 100% if printing solid. *Recommended: 3 Walls, 0% Infill for max translucency.*
    *   **Walls:** 3.
    *   **Supports:** Minimal/None (Dome is self-supporting).

## Assembly Bill of Materials
1.  **Lamp Kit:** Standard 1/8 IP Rod (threaded), Nut, Washer.
2.  **Socket:** Standard E26 Keyless or Turn-Knob Socket.
3.  **Cord:** Braided fabric cable (max 8mm diameter recomended, 10mm fits).
4.  **Bulb:** LED A19 or ST64 (Max 10W / Low Heat). **DO NOT USE INCANDESCENT.**

**Verification:** MOG-Audit-v6.1 (Overhangs Checked: <14% Global)