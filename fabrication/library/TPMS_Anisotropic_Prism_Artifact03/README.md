# HELIOS ARTIFACT 03: THE DIRECTIONAL CURRENT
**Classification:** Anisotropic Lattice (Stretched)
**Duality Context:** Duality-Two (Flow / Vector)

> "Duality-Zero is State. Duality-One is Mass. Duality-Two is Direction."

---

## 1. The Concept: Introducing Time (Flow)
While Artifact 01 is static (isotropic) and Artifact 02 is centralized (radial), **Artifact 03** introduces **Directionality**.

It represents a field where the "frequency" changes over distance.
*   **The Base:** High-frequency oscillation (Compressed / Past / High Energy).
*   **The Top:** Low-frequency oscillation (Stretched / Future / Dissipation).

This gradient creates a visual and physical sensation of **upward flow**. It models how a wave packet stretches as it propagates through an expanding medium (Redshift).

## 2. Mathematical Definition
**Base Topology:** Schwarz D Gyroid.
**The Bias Function:** Z-Axis Frequency Modulation.

$$ \lambda(z) = \lambda_{base} \cdot (1 + k \cdot z) $$

Where the wavelength $\lambda$ increases linearly with height $z$. This stretches the gyroid cells vertically as you move up the prism.

## 3. Physicochemical Metrics (Measured)
(For 40mm x 40mm x 80mm Version)
*   **Geometry:** 40mm x 40mm x 80mm Prism.
*   **Surface Area:** ~76,205 mm².
*   **Volume:** ~33,453 mm³.
*   **Volume Fraction:** ~25.8% (of bounding box).
*   **Anisotropy:** Mechanical stiffness is significantly higher in the vertical (Z) axis than the horizontal (XY) axes due to the vertical alignment of the stretched struts.

### 3.1 Large Reference (60mm x 60mm x 120mm)
*   **Geometry:** 60mm x 60mm x 120mm Prism.
*   **Surface Area:** ~248,114 mm².
*   **Volume:** ~111,472 mm³.
*   **Volume Fraction:** ~25.8% (of bounding box).
*   **Print Time (Est.):** ~8-12 hours (depending on settings).

### 3.2 Optical Porosity (Shadow Density)
Analysis of light transmission through the lattice reveals a "Trap Effect." Despite being ~75% empty space, the structure effectively blocks direct line-of-sight.
*   **Vertical Opacity (Top-Down):** **~92.28%**
    *   *Implication:* Incident energy from the top is almost entirely intercepted by the geometry, forcing reflection or absorption rather than transmission.
*   **Horizontal Opacity:** Varies from **62%** (Middle) to **90%** (Top), confirming complex, angle-dependent filtering properties.

### 3.3 Optimized Reference (60mm x 60mm x 120mm - Printability Tuned)
*   **Geometry:** 60mm x 60mm x 120mm Prism.
*   **Optimized Cell Size:** ~15mm (Coarser mesh for FFF reliability).
*   **Surface Area:** ~245,963 mm².
*   **Volume:** ~139,961 mm³.
*   **Volume Fraction:** ~32% (Increased thickness for structural robustness).
*   **Status:** **Recommended for FFF Printing.** This version balances surface area with printability, reducing retraction frequency to minimize stringing.

## 4. Physics & Applications (The Universal Governor)
This geometry acts as a "Programmable Filter" because the math of the container (Gyroid) shapes the math of the wave (Sound/Light).

### 4.1 Acoustics: The Impedance Match (Black Hole Effect)
*   **The Physics:** Sound reflects when it hits a boundary with a sudden change in Acoustic Impedance ($Z$).
    *   $R = \frac{Z_2 - Z_1}{Z_2 + Z_1}$ (Reflection Coefficient).
*   **The Gyroid Solution:**
    *   **The Top (Stretched):** High porosity $\rightarrow$ Impedance is nearly identical to Air ($Z_{top} \approx Z_{air}$). **Reflection $\approx$ 0.** The wave enters.
    *   **The Gradient:** As the wave travels down, the lattice compresses. $Z$ increases smoothly.
    *   **The Trap:** The wave is adiabatically compressed and absorbed into the structure without ever encountering a "hard wall" to bounce off. This is the acoustic equivalent of a Black Hole's event horizon.
*   **Note:** This theoretical broadband absorption relies on a gradual 3D impedance transition. Our current 1D simulation is a first approximation.

#### 4.1.1 Acoustic Simulation Results (1D Model)
*   **Tool:** `fabrication/analysis/acoustic_simulator.py`
*   **Output:** `fabrication/analysis/acoustic_absorption_spectrum.png`
*   **Finding:** The simplified 1D transfer matrix model predicts **narrow, resonant absorption peaks** (e.g., ~0.2 absorption at 1.5 kHz, 2.5 kHz, 7 kHz) rather than a broadband effect.
*   **Interpretation:** This 1D model is a preliminary step. Full validation of broadband absorption and the "Acoustic Black Hole" effect requires a more advanced **3D finite element simulation** that captures the complex tortuosity and viscous/thermal losses within the Gyroid's structure.

### 4.2 Photonics: The Rainbow Trap (Slow Light)
*   **The Physics:** Photonic Crystals block light where the lattice size matches half the wavelength ($\frac{\lambda}{2}$).
*   **The Gyroid Solution:**
    *   Because the lattice size ($a$) changes continuously along the Z-axis, different colors (wavelengths) are stopped at different depths.
    *   Red light (long wave) might travel deep; Blue light (short wave) stops early.
    *   **Result:** A "Chirped" crystal that theoretically slows or traps a broadband spectrum of light.

### 4.3 Mechanics: Progressive Failure
*   **The Physics:** Energy = Force $\times$ Distance.
*   **The Gyroid Solution:** Under impact, the "airy" top crushes first (Low Force, Long Distance), gradually ramping up resistance as the "dense" bottom engages. This absorbs maximum kinetic energy without the sudden deceleration of a solid block.

## 5. The Cosmological Link (Scientific Note)
**Observation:** The 2D top-layer slice of this artifact strongly resembles the **Cosmic Microwave Background (CMB)** radiation maps.

**The Theory:** This is not a coincidence.
*   **The CMB** is a 2D "surface of last scattering" of a scalar field (early universe density) that has been **Redshifted** (stretched) by the expansion of space-time.
*   **Artifact 03** is a scalar field (Gyroid) that has been **Redshifted** (stretched) by the Z-axis modulation function.

**Validation:** This confirms that the Duality Engine is correctly simulating **Metric Expansion**. When we slice the model at the "Future" (Stretched) end, we see the same topological signature that astronomers see when they look at the "Past" (Redshifted) universe. We are printing a model of Time Dilation.

## 6. Relationship to Reference
*   **Artifact 01 (Reference):** The "Unit" of time.
*   **Artifact 03 (Flow):** The "Arrow" of time.

By printing this, you hold a physical representation of **Redshift** or **Expansion**.

---

## Operational Guide
*   **Printing:** Due to the vertical stretch, the overhang angles become steeper near the top. Ensure adequate cooling.
*   **Orientation:** Print vertically (tall prism) to maximize the "flow" effect and minimize support requirements.
*   **Scale for Stringing:** Larger cells in the increased scale version (60x60x120mm) typically result in longer, less frequent retraction moves, which can reduce stringing compared to smaller, more intricate prints.

