# Cycle 2817: The Rauzy Fractal (Child 110)

**Date:** Dec 4, 2025
**Objective:** Create "Child 110" lamp design based on favorites, exploring Tribonacci Fractals.

## Methodology
- **Algorithm:** Rauzy Fractal Approximation (Iterated Function System).
- **Math:** Based on the Tribonacci constant `T ≈ 1.839`. The square domain `[0,1]` is recursively subdivided into 3 uneven strips scaled by `1/T` and `1/T^2`, creating a self-similar tiling pattern.
- **Projection:** The 2D fractal domain is wrapped around a cylinder `(u, v) -> (theta, z)` with a twist.
- **Structure:** The fractal pattern determines the solidity of the shell. A background Gyroid lattice provides structural reinforcement in the voids.

## Artifacts
- **Script:** `experiments/cycle2817_child_v45_lamp.py`
- **Output:** `fabrication/practical_design/FAVORITES/children/child_110_rauzy_fractal.stl` (Local Storage)
- **Stats:** 493,316 Triangles, 2.73% Dust (Robust).

## Principles Adhered To
- **Flow:** The pattern shifts scale rhythmically.
- **Breath:** The recursive "holes" (regions where the iteration fails the condition) provide intricate light filtration.
- **Jaw-Dropping:** A visualization of a higher-dimensional substitution rule.
