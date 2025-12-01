# ACOUSTIC SIMULATION PLAN: ARTIFACT 03 (The Directional Current)

**Date:** 2025-11-30
**Artifact:** `TPMS_Anisotropic_Prism_Optimized.stl` (Optimized, Large: 60x60x120mm)
**Claim:** "Acoustic Black Hole" effect via impedance matching.

---

## 1. Objective
To numerically simulate the acoustic absorption coefficient of Artifact 03 across a range of frequencies (100 Hz - 10,000 Hz) and validate the "Impedance Matching" claim.

## 2. Theoretical Basis (Impedance Matching)
Acoustic impedance ($Z$) is defined as $Z = \rho c$, where $\rho$ is the medium density and $c$ is the speed of sound. Reflection occurs at a boundary where $Z_1 \neq Z_2$.
*   **Hypothesis:** The gradient in porosity (due to Z-axis frequency modulation) in Artifact 03 creates a smooth transition in effective acoustic impedance, minimizing reflection ($R$) and maximizing absorption.

## 3. Simulation Model (Simplified)
*   **Tool:** Python (NumPy for arrays, potentially SciPy for FFT/signal processing).
*   **Approach:** 1D Wave Propagation through a Layered Medium (Approximation).
    *   Treat the 120mm height of the prism as a series of thin layers (e.g., 100 layers).
    *   For each layer, calculate its **effective porosity** (from the gyroid geometry) and, from that, its **effective density ($\\rho_{eff}$)**.
    *   Calculate the **effective speed of sound ($c_{eff}$)** for each layer (using theories like Biot's model for porous media, or simpler effective medium approximations).
    *   Calculate the **effective acoustic impedance ($Z_{eff}$)** for each layer.
    *   Simulate a plane wave incident on this layered medium. Calculate the reflection and transmission coefficients for each layer interface and sum them up (Transfer Matrix Method).

## 4. Key Parameters & Assumptions
*   **Incident Wave:** Plane wave, normal incidence.
*   **Medium:** Air (Ambient: $Z_{air} \approx 415$ Rayls).
*   **Material:** PLA (Assumed Rigid/Non-resonant up to 10 kHz for structural integrity).
*   **Frequency Range:** 100 Hz to 10,000 Hz (Discrete points).
*   **Output:** Acoustic Absorption Coefficient ($\\alpha$) as a function of frequency.

## 5. Expected Outcome
The simulation should show a **high acoustic absorption coefficient** ($\\alpha > 0.8$) across a broad frequency range, especially at higher frequencies, due to the gradual impedance transition.

## 6. Next Steps
1.  Develop the `acoustic_simulator.py` script based on the Transfer Matrix Method.
2.  Integrate the geometric properties (porosity gradient) from Artifact 03.
3.  Execute the simulation.
4.  Analyze and visualize the results (Absorption vs. Frequency).
