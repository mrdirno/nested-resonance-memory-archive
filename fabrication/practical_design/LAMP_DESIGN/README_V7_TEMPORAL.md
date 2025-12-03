# Helios V7 - "The Temporal Echo"

**Status:** IMPLEMENTED (4D Dynamics)
**Generator Script:** `fabrication/scripts/run_v7_generation.sh`

## Overview
V7 maps **Time** onto the Z-axis. The design is not just a static shape, but a "frozen moment" of a dynamic system. It uses phase-shifted interference (Moire) and chaos theory (Perlin/Noise) to create structures that appear to be in motion or transition.

## Mathematical Framework
Instead of `Gyroid(x,y,z)`, we use functions where `z` acts as `t` (time):
```python
val = Gyroid(x,y,z) + Chaos(x,y,t)
```

## Components

### 1. Base V7: "Echo Chamber"
*   **Concept:** A drop hitting a liquid surface, frozen in time.
*   **Mechanism:** Standing Wave Interference + Spiral Perturbation.
*   **Equation:** `Sin(r*k) * Cos(z*k) + Sin(theta*N + r*0.1)`
*   **Stats:** ~230k Triangles.
*   **QA:** Retains V4 Hardware Constraints.

### 2. Shaft V7: "The Timeline"
*   **Concept:** A timeline that glitches and echoes as it progresses.
*   **Mechanism:** Spatial Distortion + Temporal Echo (Lag).
*   **Equation:** `Gyroid(p + Chaos(z)) + 0.5 * Gyroid(p_lag)`
*   **Stats:** ~1.6M Triangles.
*   **QA:** Retains V4 Rod Channel.

### 3. Shade V7: "Event Horizon"
*   **Concept:** Transition from Order to Chaos.
*   **Mechanism:** Linear Interpolation (Lerp) between Gyroid and Noise.
*   **Equation:** `(1-t)*Gyroid + t*Noise`
*   **Stats:** ~1.7M Triangles.
*   **QA:** Retains Spider Fitter and Shell Mask.

## Usage
To generate the V7 suite:
```bash
./fabrication/scripts/run_v7_generation.sh
```
Outputs:
- `lamp_base/lamp_base_v7_temporal_echo.stl`
- `lamp_shade/lamp_shade_v7_temporal_echo.stl`
- `lamp_shaft/lamp_shaft_v7_temporal_echo.stl`
