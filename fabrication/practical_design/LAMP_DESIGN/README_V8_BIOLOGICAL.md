# Helios V8 - "The Biological Mimicry"

**Status:** IMPLEMENTED (Cellular Approximation)
**Generator Script:** `fabrication/scripts/run_v8_generation.sh`

## Overview
V8 emulates natural growth patterns found in biology. It moves away from pure geometric symmetry towards **Domain Warped** cellular structures. This creates artifacts that look grown rather than manufactured.

## Mathematical Framework
Instead of standard `Gyroid(p)`, we use **Domain Warping** (Turbulence):
```python
val = Gyroid(p + Strength * Noise(p))
```
This distorts the coordinate space before evaluating the gyroid, creating "veins" and "cells" similar to Voronoi diagrams or reaction-diffusion systems.

## Components

### 1. Base V8: "Mycelium Network"
*   **Concept:** Fungal root structure.
*   **Mechanism:** Low-frequency warp applied to a standard gyroid.
*   **Equation:** `Gyroid(p + 8.0 * Sin(p/40))`
*   **Stats:** ~280k Triangles.
*   **QA:** Retains V4 Hardware Constraints.

### 2. Shaft V8: "Bone Lattice"
*   **Concept:** Trabecular bone structure (maximum strength-to-weight).
*   **Mechanism:** Stretched (Anisotropic) Gyroid rotated 45 degrees to align load paths.
*   **Equation:** `StretchedGyroid(Rotated(p))`
*   **Stats:** ~1.7M Triangles.
*   **QA:** Retains V4 Rod Channel.

### 3. Shade V8: "Dragonfly Wing"
*   **Concept:** Thin, veined cellular membrane.
*   **Mechanism:** High-frequency warp applied to a thin-shell gyroid.
*   **Equation:** `Gyroid(p + 5.0 * Sin(p/scale)) < 0.3` (Thin Wall)
*   **Stats:** ~1.4M Triangles.
*   **QA:** Retains Triskelion Fitter and Shell Mask.

## Usage
To generate the V8 suite:
```bash
./fabrication/scripts/run_v8_generation.sh
```
Outputs:
- `lamp_base/lamp_base_v8_biological_mimicry.stl`
- `lamp_shade/lamp_shade_v8_biological_mimicry.stl`
- `lamp_shaft/lamp_shaft_v8_biological_mimicry.stl`
