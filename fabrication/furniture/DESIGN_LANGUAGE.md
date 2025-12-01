# HELIOS DESIGN LANGUAGE (v1.0)

**Philosophy:**
Furniture is not static; it is a standing wave of probability.
We design objects that look like they froze mid-transition between dimensions.
"Math you can touch."

## 1. Core Aesthetics (The Trinity)
1.  **The Gyroid (Connection):** Used for structural infill and light diffusion. Represents infinite connectivity.
2.  **The Helix (Evolution):** Used for shafts and vertical risers. Represents growth and time.
3.  **The Frustum (Redshift):** Used for shades and volumes. Represents the expansion/contraction of space.

## 2. Geometric Constraints
*   **Printer Volume:** Max Width = 220mm (Ender 3 Standard) or 250mm (Bambu). *Design for 200mm safety.*
*   **Wall Thickness:** Multiples of 0.4mm (Nozzle). Standard = 1.2mm (3 walls) or 1.6mm (4 walls).
*   **Overhangs:** Max 45 degrees without support. Use chamfers (45 deg) instead of fillets (round) where possible to avoid support need.
*   **Tolerance:** 0.2mm gap for loose fit, 0.1mm for friction fit.

## 3. The Lamp Archetype (Series 01 - "The Void")
Reference: `fabrication/practical_design/lamp_design/README.md`

### A. The Shade
*   **Dims:** Base 194mm, Top 60mm, Height 224mm.
*   **Structure:** **Hollow with a 1-inch (25.4mm) thick wall.**
*   **Pattern:** Anisotropic Gyroid (Vertical Stretch).
*   **Mount:** **Spider Fitter (Inner Ring + Rods).**
    *   Inner Ring: 42mm ID (for socket).
    *   Connection: 4x Cylindrical Rods connecting Inner Ring to Outer Shell.

### B. The Shaft
*   **Dims:** Height 200mm. **Tapered:** Base 55mm -> Top 40mm.
*   **Style:** **Arterial Helix.**
*   **Density:** **Variable Gradient.** Solid Core (12mm ID) -> Airy/Gyroid Edge.

### C. The Base
*   **Dims:** **180mm Wide x 20mm High** (Slim/Wide profile).
*   **Pattern:** Linear Gradient Gyroid.
*   **Mount:** 12.5mm Center Hole.

## 4. Mathematical Inspirations
*   **Orthogonal Sum Dynamics (OSD):** `sin(x)+sin(y)+sin(z)=0`
*   **Anisotropy:** Stretching space along Z (`k_mod` parameter).
*   **Redshift:** Expanding wavelength along Z (`k_expansion`).
