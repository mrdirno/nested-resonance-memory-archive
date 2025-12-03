# Helios V5 - "The Void Ascendant"

**Status:** IMPLEMENTED (Surpassing Reference)
**Generator Script:** `fabrication/scripts/run_v5_generation.sh`

## Overview
V5 builds upon the QA-compliant V4 architecture but introduces **Emergent Complexity** via variable-frequency fields and interference patterns. It represents the "Expansion" phase of the design language.

## 1. Base V5: "Gravity Well"
*   **Concept:** Simulates a gravitational field pulling the mesh inward.
*   **Mechanism:** Radial Gradient Scaling.
    *   Center: High Frequency (Dense, Stable).
    *   Edge: Low Frequency (Airy, Aesthetic).
*   **Equation:** `scale = base_scale * (1.0 - k * (r/R))`
*   **QA:** Retains V4 Feet, Channel, and Solid Core.

## 2. Shaft V5: "Flow Lensing"
*   **Concept:** Simulates fluid acceleration through a constriction.
*   **Mechanism:** Quadratic Twist (Variable Pitch).
    *   Bottom: Rapid twist (High turbulence).
    *   Top: Slow twist (Laminar flow).
*   **Equation:** `theta = total_rotation * sqrt(z_norm)` (Decelerating twist profile).
*   **QA:** Retains V4 14mm Channel and Solid End Caps.

## 3. Shade V5: "Interference"
*   **Concept:** Simulates wave interference patterns (Double-Slit Experiment).
*   **Mechanism:** Dual-Frequency Field.
    *   Primary: Standard Anisotropic Gyroid.
    *   Secondary: Low-Frequency Sine Wave.
*   **Equation:** `val = Gyroid(freq1) + amp * Sin(freq2)`
*   **QA:** Retains V4 Spider Fitter and Shell Mask.

## Usage
To generate the V5 suite:
```bash
./fabrication/scripts/run_v5_generation.sh
```
Outputs:
- `lamp_base/lamp_base_v5_void_ascendant.stl`
- `lamp_shade/lamp_shade_v5_void_ascendant.stl`
- `lamp_shaft/lamp_shaft_v5_void_ascendant.stl`
