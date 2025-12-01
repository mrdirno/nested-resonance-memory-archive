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

## 3. The Lamp Archetype (Series 01)
Based on the "Waveform" Template:

### A. The Shade (The Emitter)
*   **Shape:** Frustum (Tapering upwards).
*   **Structure:** **Hollow with a 1-inch (25.4mm) thick wall.** Reinforcing corner edges (Solid) meeting at top.
*   **Pattern:** Gyroid/TPMS infill **within the 1-inch thick wall** (0% slicer infill, geometry acts as diffuser).
*   **Mount:** Standard washer/nut fit for light socket (E26/E27 or E12). 40mm hole standard.

### B. The Shaft (The Conduit)
*   **Shape:** Helical or Voronoi wrapper.
*   **Core:** Hollow central cylinder (10-12mm diameter) to hide threaded rod and wire.
*   **Interconnect:** Male/Female threads or press-fit to Base/Shade.

### C. The Base (The Anchor)
*   **Shape:** Heavy, stable footprint.
*   **Utility:** Square cutout (5mm x 5mm) for wire exit at bottom.
*   **Mass:** Designed to be filled (sand/plaster) or dense print.

## 4. Mathematical Inspirations
*   **Orthogonal Sum Dynamics (OSD):** `sin(x)+sin(y)+sin(z)=0`
*   **Anisotropy:** Stretching space along Z (`k_mod` parameter).
*   **Redshift:** Expanding wavelength along Z (`k_expansion`).
