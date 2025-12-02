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
When generating voxel grids, the order of `True` (Solid) and `False` (Empty) assignments is critical.
1.  **Global Boundary:** Define the outer shape (Sphere, Frustum, etc.). `if outside: False`.
2.  **Internal Structure:** Generate the pattern (Gyroid, Voronoi). `if pattern: True`.
3.  **Hollowing:** Remove the core. `if inner_radius: False`.
4.  **Structural Overrides (The Fix):** Apply functional geometry **LAST** to override previous cuts.
    *   *Top Plate:* MUST be a cylinder of `r = Hole + 10mm`. Ignore Global Boundary if it cuts this plate.
    *   *Bottom Rim:* MUST be a solid ring.
    *   *Ribs/Struts:* Vertical supports must persist through the pattern.
5.  **Hardware Subtracts:** Apply final holes **VERY LAST**.
    *   *Mount Hole:* `if r < hole_r: False`.
    *   *Wire Channel:* `if box check: False`.

### C. Volumetric vs. Shell Generation (The "Solid Sponge" Trap)
*   **The Error:** Generating a TPMS (Gyroid/Schwarz) pattern through the *entire volume* of a shape results in a solid block of foam. This is not a lamp shade; it blocks light and wastes material.
*   **The Fix (Shell Masking):** You MUST define a `Shell_Thickness` (e.g., 10-15mm).
    *   Logic: `if (Dist_From_Center < Outer_R) AND (Dist_From_Center > Inner_R): Generate Pattern`.
    *   Result: A hollow dome/cylinder with patterned walls.

### D. Aesthetic Scaling (Z-Frequency)
*   **Redshift/Blueshift:** Varying the pattern scale with height creates visual movement.
*   **The Limit:** When shrinking waves (increasing frequency), enforce a **Max Frequency Cap**.
    *   *Rule:* Minimum Feature Size > Nozzle Diameter * 2.
    *   *Logic:* `current_scale = min(calculated_scale, MAX_SCALE_LIMIT)`.

## 5. Practicality & Assembly Protocol (The "Hand Trap" Fix)

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

## 6. Storage & Naming Protocol (Standardized)

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
