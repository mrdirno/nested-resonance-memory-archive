# Helios V6 - "The Fractal Prism"

**Status:** IMPLEMENTED (Peak Complexity)
**Generator Script:** `fabrication/scripts/run_v6_generation.sh`

## Overview
V6 represents the pinnacle of the Helios design language. It introduces **Recursive Geometry** (Fractals) directly into the isosurface equations, creating self-similar detail across multiple scales (Octaves). This simulates organic growth patterns (bone, coral) while adhering to the strict QA safety standards established in V4.

## Mathematical Framework
All components use a **Recursive Gyroid Field**:
```python
val = Gyroid(p, scale) + 0.5 * Gyroid(p, 2*scale) + 0.25 * Gyroid(p, 4*scale)
```
This "Octave Summation" creates:
1.  **Macro Structure:** Defined by the base scale (structural stability).
2.  **Meso Structure:** Defined by the 2nd octave (texture/grip).
3.  **Micro Structure:** Defined by the 3rd octave (surface detail/light diffusion).

## Components

### 1. Base V6: "Fractal Root"
*   **Concept:** An organic anchor that appears to grow out of the table.
*   **Mechanism:** Recursive Gyroid + V4 Hardware Channels.
*   **Stats:** ~450k Triangles.
*   **QA:** Retains 14mm Channel, Feet Recesses, Weighted Core.

### 2. Shaft V6: "Fractal Flow"
*   **Concept:** A twisted, calcified vine structure.
*   **Mechanism:** Recursive Gyroid + Quadratic Twist (Flow Lensing).
*   **Stats:** ~2.2M Triangles.
*   **QA:** Retains 14mm Rod Channel, Solid End Caps.

### 3. Shade V6: "Fractal Canopy"
*   **Concept:** A dense, coral-like diffusion filter.
*   **Mechanism:** Recursive Anisotropic Gyroid.
*   **Stats:** ~3.2M Triangles.
*   **QA:** Retains Spider Fitter (Hub+Spokes), Shell Mask, Wall Thickness constraints.

## Usage
To generate the V6 suite (Warning: High Memory/CPU Usage):
```bash
./fabrication/scripts/run_v6_generation.sh
```
Outputs:
- `lamp_base/lamp_base_v6_fractal_prism.stl`
- `lamp_shade/lamp_shade_v6_fractal_prism.stl`
- `lamp_shaft/lamp_shaft_v6_fractal_prism.stl`
