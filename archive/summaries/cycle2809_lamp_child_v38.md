# Cycle 2809: The Minkowski Sausage (Child 103)

**Date:** Dec 4, 2025
**Objective:** Create "Child 103" lamp design based on favorites, exploring Blocky Fractals.

## Methodology
- **Algorithm:** Minkowski Sausage L-System (Type 2).
- **Fractal:** A variant of the Koch curve where each segment is replaced by a `F+F-F-FF+F+F-F` pattern, creating square-shaped extrusions instead of triangles.
- **Projection:** The 2D fractal path is mapped to spherical coordinates `(theta, phi)`.
- **Structure:** 
  - **Voxel Painting:** A thick (12mm) spherical brush traces the path, merging corners into a solid blocky shell.
  - **Reinforcement Cage:** A grid of vertical bars ensures that any disconnected "floating islands" of the fractal are physically anchored to the main body.

## Artifacts
- **Script:** `experiments/cycle2809_child_v38_lamp.py`
- **Output:** `fabrication/practical_design/FAVORITES/children/child_103_minkowski_sausage.stl` (Local Storage)
- **Stats:** 204,928 Triangles, 0.96% Dust (Solid).

## Principles Adhered To
- **Flow:** The path is continuous but angular.
- **Breath:** The self-avoiding nature of the curve leaves gaps.
- **Jaw-Dropping:** A fortress-like sphere that looks built from impossible tetris blocks.
