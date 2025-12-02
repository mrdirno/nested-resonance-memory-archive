# HELIOS FURNITURE PROTOCOL (v1.0)

**Directive:** Practical, Safe, and Reproducible 3D Printed Furniture.

## 1. Design Principles (The Physical Reality)

### A. The Mounting Imperative
*   **Top Plates (Spider Fitters):** Shades MUST NOT be solid caps (heat trap). Use a **Spider Fitter** design:
    *   **Hub:** Central ring (ID 42mm, OD 60mm+).
    *   **Spokes:** Min 3 solid arms connecting Hub to Outer Rim.
    *   **Thickness:** Hub and Spokes must be **4mm thick**.
*   **Thickness:** Mounting plates must be at least **4mm thick** (approx 20 layers at 0.2mm) to withstand torque from the shade ring.
*   **Clearance:** Always leave **1-2mm clearance** around hardware holes (e.g., 42mm hole for 40mm socket).

### B. Wall Thickness & Structural Integrity
*   **Minimum Wall:** 1.2mm (3 perimeters) for non-structural cosmetic parts.
*   **Structural Wall:** 2.4mm (6 perimeters) or 25.4mm (1 inch) gyroid-filled for load-bearing.
*   **Gyroid Infill:** Acts as internal trusses. For "Solid" appearance with lightweight, use 10-15% Gyroid. For "Diffusion", use 0% slicer infill and model the gyroid geometry directly.

### C. Edge Cases & Failures
*   **The "Floating Ring" Bug:** If `Wall_Thickness` > `(Radius - Hole_Radius)`, the inner wall creates a gap that disconnects the mounting ring from the outer shell.
    *   *Fix:* Top Cap logic overrides Wall logic. The Cap is always solid from `Hole_Radius` to `Outer_Radius`.
*   **The "Melting Shade" Risk:** PLA deforms at ~55°C.
    *   *Requirement:* LED Bulbs ONLY (9W max).
    *   *Design:* Vents at top of shade to let heat escape.
*   **The "Topple" Risk:**
    *   *Rule:* Base Weight > (Shaft + Shade Weight) * (Height / Base_Width).
    *   *Fix:* Bases must have cavities for sand/plaster ballast.

## 2. Electrical Safety Protocol
1.  **Strain Relief:** All bases must have a mechanism (knot, clamp, or zigzag channel) to prevent pulling the wire from the socket.
2.  **Insulation:** 3D printed plastic is insulating, but layers can have gaps. Do not rely on print for primary insulation. Use jacketed cord.
3.  **Pass-Throughs:** All wire channels must be at least **6mm** diameter for standard lamp cord.

## 3. Fabrication Checklist
- [ ] **Slicer:** Check for "non-manifold" edges.
- [ ] **Preview:** Scroll through layers. Is the Top Plate connected to the walls?
- [ ] **Material:** Use PETG for shades (higher heat resistance) if possible. PLA is acceptable for low-wattage LED.
- [ ] **Supports:** Design for 45° overhangs to minimize supports.

## 4. Geometric Logic Protocol (The Code)

### A. Order of Operations (Boolean Logic)
1.  **Global Boundary:** Define outer shape.
2.  **Spider Fitter (Top 5mm):** MUST be generated FIRST or override everything.
    *   **Hub:** Solid Disk (Diam 40mm).
    *   **Spokes:** Solid Arms connecting Hub to Outer Rim.
    *   **Rim:** Solid ring merging with the Shell.
3.  **Shell Masking:** Define the "Wall" region (e.g., 1-inch thick).
4.  **Pattern:** Generate TPMS only within the Shell.
5.  **Hardware Subtracts:** Drill the hole through the Hub LAST.

### B. Structural Integrity (The 1-Inch Rule)
*   **Wall Thickness:** Large shades (>150mm) MUST have **1-inch (25.4mm) thick walls**.
*   **Pattern Density:** A 1-inch wall requires a robust lattice. Ensure the implicit threshold (e.g., `val < 0.4`) creates a connected network, not isolated islands.
*   **Reinforcement:** Bottom Rims and Corners (for square shades) should be solid.

## 5. Storage & Naming Protocol (Standardized)

### A. Hand Access & Bulb Clearance
*   **The Issue:** A shade might be hollow, but if it narrows at the top (Dome/Sphere), you cannot fit your hand inside to screw on the socket ring.
*   **The Rule (Cylindrical Keep-Out):** You MUST enforce a central **Cylindrical Void** of **Diameter 80-90mm** (Hand size) extending from the bottom up to the mounting plate.
    *   *Logic:* `if dist_xy < 40mm: is_solid = False` (Overrides pattern and shell).
    *   *Exception:* The Mounting Plate (Top 4mm) obviously cuts into this (Hole 42mm).
*   **Bulb Fit:** Standard A19/E26 bulbs are ~60mm diameter. The 80mm hand clearance automatically covers this.

### B. Light Passage (Pattern Openness)
*   **Density Trap:** High-frequency TPMS can become "functionally solid" (blocking light) even if mathematically porous.
*   **Rule:** When Z-scaling (shrinking waves), ensure the **Minimum Hole Size** stays > 5mm.
    *   *Implementation:* Clamp the frequency scaling factor (e.g., Max 1.5x or 2.0x).
    *   *Check:* If the shade looks opaque in slicer preview, reduce frequency.

## 7. Spider Fitter Protocol (Mounting Standard)
*   **The Goal:** Heat dissipation + Aesthetic consistency.
*   **The Geometry:**
    *   **Hub:** Solid central washer seat (Radius ~15mm).
    *   **Hole:** 42mm (E26 Shade Ring) or 12.5mm (Finial/Harp) depending on design.
    *   **Spokes:** 4x arms (width ~6mm) connecting Hub to Outer Rim.
    *   **Void:** Air gaps between spokes allow hot air to escape (Chimney Effect).

## 8. Scale Constraints (The "Reference" Rule)
*   **Baseline:** The "Redshift" shade sets the standard for feature size.
*   **Rule:** "Smallest wave cannot be smaller than the original."
    *   If Redshift uses `Base_Scale` and *redshifts* (gets larger), then `Base_Scale` is the smallest wave.
    *   Therefore, any new design (e.g., Event Horizon) MUST NOT use a frequency higher than `Redshift_Base_Scale`.
    *   *Implementation:* `Max_Freq <= Redshift_Base_Freq`.

## 9. Storage & Naming Protocol (Standardized)

### A. Directory Hierarchy
Organize by **Collection** (Series) then by **Design**.

```text
fabrication/furniture/
├── concepts/                         # Brainstorming
├── lamp_series_01/                   # Collection Folder
│   ├── README.md                     # Collection Index
│   ├── 01_redshift/                  # Design Folder (ID_Name)
│   │   ├── README.md                 # Design BOM & Assembly
│   │   ├── redshift_shade_gen.py     # Generator: [name]_[part]_gen.py
│   │   ├── redshift_shade.stl        # Artifact: [name]_[part].stl
│   │   └── ...
│   └── 02_event_horizon/             # Next Design...
└── chair_series_01/                  # Future Collection...
```

### B. Naming Convention
*   **Folders:** `[ID]_[design_name_snake_case]` (e.g., `01_redshift`).
*   **Generators:** `[design]_[part]_gen.py` (e.g., `redshift_base_gen.py`).
*   **Geometry (Raw):** `[design]_[part].stl` (e.g., `redshift_base.stl`).
*   **Production (Gold Standard):** `[design]_[part].3mf` (Contains orientation, supports, modifiers).
*   **Scripts:** Use explicit variables at the top of scripts for dimensions.

### C. The Design Package
Each Design Folder MUST contain:
1.  **README.md:** Specific to that object (Assembly, BOM).
2.  **Source:** All generator scripts.
3.  **Output (Geometry):** Pre-generated Binary STLs.
4.  **Production (Gold Standard):** Validated `.3mf` Project Files.
    *   *Why?* STLs are just geometry. `.3mf` captures the *manufacturing intent*: orientation, seam placement, support blockers, and fuzzy skin settings. This is the true "Design".

## 10. Shaft Complexity Protocol (The "Boring Shaft" Ban)
*   **The Issue:** A complex, math-heavy shade paired with a simple extruded cylinder looks cheap and unfinished.
*   **The Rule:** Shafts MUST match the aesthetic complexity of the shade.
    *   *Twist:* Helical rotation of the profile.
    *   *Lensing:* Gravitational distortion (pinching/bulging) that is non-linear.
    *   *Texture:* TPMS or noise applied to the surface.
    *   *Lattice:* Voronoi or Truss structures (if structurally sound).
*   **Ban:** No simple cylinders or basic sine-wave tubes. Use interference patterns or high-order distortions.

## 6. The Practical DIY Checklist (Edge Cases)

### A. Wiring & Ports
*   **The "Strain Relief" Rule:** Can you yank the cord without ripping the socket?
    *   *Standard:* Zig-zag channel or zip-tie anchor point inside the base.
*   **Pass-Through Sizing:**
    *   Standard Lamp Cord (SPT-2): **Min 4mm x 8mm** slot or **7mm** round hole.
    *   USB-C Head: **Min 13mm x 7mm**.
    *   Power Brick Plug: **Min 40mm** (if passing plug through).
*   **Hidden Wiring:** Channels should be internal. If external, provide clips.

### B. Mounting Points
*   **Nut Traps:** Use hex recesses to trap nuts for one-handed assembly.
    *   *M3 Nut:* 5.5mm flat-to-flat (Print at 5.7mm).
    *   *M4 Nut:* 7.0mm flat-to-flat (Print at 7.2mm).
*   **Threaded Rods:** The backbone of lamp design.
    *   *M10 / 1/8 IP:* Standard lamp rod. Hole size **10.5mm**.
*   **Heat Inserts:** Preferred over printed threads for frequently disassembled parts.

### C. Stability & Weight
*   **The Ballast Chamber:** Bases should be hollow with a screw-cap to fill with sand, rice, or plaster.
*   **Feet:** Add 10mm recesses for rubber feet to clear bottom nuts/wires.

### D. User Experience
*   **Switch Access:** Don't bury the switch. If using a cord switch, ensure the cord exit is accessible.
*   **Bulb Replacement:** Can the user change the bulb without disassembling the lamp?
    *   *Rule:* Hand must fit inside shade (Min 80mm top opening) OR Shade must unclip easily.

## 11. The Perfection Loop (Perpetual Refinement)

**Directive:** Design is never "Finished", only "Versioned".
We do not simply "generate and forget". We perpetually refine until the artifact is a **perfect physical object**.

### A. The "One Aspect" Rule
*   **Focus:** Do not rebuild the entire object every cycle. Refine **ONE** specific aspect to perfection.
    *   *Example:* "Optimize the overhang angles on the Lattice Shaft."
    *   *Example:* "Thicken the mounting plate by 0.5mm for stiffness."
    *   *Example:* "Adjust the Gyroid phase to ensure the bottom layer is a single connected path."

### B. The "Zero Post-Processing" Goal
*   **Target:** The part should come off the printer ready to use.
*   **Brims/Rafts:** Avoid if possible. Design integrated adhesion pads ("Mouse Ears") if corners lift.
*   **Supports:** Design specifically to avoid slicer-generated supports. Use 45° chamfers and teardrop holes.
*   **Tolerances:** Mating parts must slide together with a satisfying "click". No sanding.

### C. The "Bed Adhesion" Mandate
*   **First Layer:** The first 3 layers (0.6mm) MUST be a **Solid, Continuous Geometry**.
    *   *Why?* A lattice starting on Layer 1 results in disconnected islands that detach.
    *   *Fix:* Always generate a solid "Base Plate" or "Rim" that anchors the complex pattern above it.

