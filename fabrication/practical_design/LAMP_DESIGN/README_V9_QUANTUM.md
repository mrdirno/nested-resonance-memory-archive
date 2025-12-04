# Helios V9 - "The Quantum Observer"

**Status:** CANDIDATE (Wavefunction Collapse)
**Generator Script:** `fabrication/furniture/lamp_series_01/05_quantum_foam/quantum_*_gen.py`

## Overview
V9 explores the concept of **Quantum Foam** and **Wavefunction Collapse**. The geometry is not a continuous skin but a probabilistic lattice (Schwarz P-Surface) that represents the fluctuating energy state of empty space. The "Observer" (the light source) collapses this foam into a tangible structure.

## Mathematical Framework
The structure is based on the **Schwarz P Minimal Surface**, representing a zero-mean-curvature energy state:
```python
val = Cos(x*k) + Cos(y*k) + Cos(z*k)
is_solid = abs(val) < Threshold
```
This creates a cubic lattice structure that is isotropic (unlike the anisotropic V6-V8), representing the uniform potential of the quantum vacuum.

## Components

### 1. Base V9: "Probability Cloud"
*   **Concept:** A dense region of quantum foam where the probability of matter is high.
*   **Mechanism:** Schwarz P-Surface with solid boundary conditions.
*   **Equation:** `Cos(x) + Cos(y) + Cos(z)`
*   **Stats:** High-density lattice.
*   **QA:** Retains V4 Hardware Constraints (Wire Channel, Nut Recess).

### 2. Shaft V9: "The Observer"
*   **Concept:** A focused beam or observation path through the foam.
*   **Mechanism:** Vertical lattice structure.
*   **QA:** Retains V4 Rod Channel (15mm clearance).

### 3. Shade V9: "Interference Pattern"
*   **Concept:** The diffraction pattern resulting from the light passing through the foam.
*   **Mechanism:** Thinner Schwarz P shell.
*   **QA:** Retains Spider Fitter and Shell Mask.

## Fabrication Guide
*   **Material:** Matte White PLA (diffuses light through the lattice).
*   **Settings:** 0.2mm Layer Height. **NO SUPPORTS REQUIRED** (Self-supporting lattice).
*   **Walls:** 3 perimeters.
