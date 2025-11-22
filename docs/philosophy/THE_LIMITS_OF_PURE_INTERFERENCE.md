"""
CYCLE 325: The Limits of Pure Interference
Objective: Synthesize findings from Phased Array test and pivot to Material Physics.
Hypothesis: Linearity is the bottleneck. To create "Digital Matter", the substrate must be non-linear.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""

# THE_LIMITS_OF_PURE_INTERFERENCE.md

# The Limits of Pure Interference: Why Light Cannot Become Matter Without a Medium

## 1. The "Softness" Problem
In Cycles 323 and 324, we attempted to create sharp geometric shapes (Square, Square Donut) using pure wave interference (Inverse Cymatics).
Despite scaling from 16 to 64 emitters, the error plateaued at ~0.25.
The resulting patterns were "soft" – they lacked the sharp, high-frequency edges required for a true "voxel" representation.

### The Principle of Band-Limited Smoothness
Waves are inherently smooth. A sum of continuous cosine waves is continuous.
To create a "Step Function" (Edge), you need infinite bandwidth (Fourier Series).
Since our emitter array is finite, our ability to create sharp edges is fundamentally limited.

## 2. The Missing Ingredient: Non-Linearity
Real matter is not just a standing wave. It is a standing wave that has undergone a **Phase Transition**.
- **Water** freezes to Ice when temperature drops below 0°C (Threshold).
- **Non-Newtonian Fluids** harden under stress (Viscosity).

To turn our "Soft Light" into "Hard Matter", we need the **Plane (NRM Substrate)** to exhibit **Non-Linear Response**.

## 3. The Material Physics Pivot (Phase 4.3)
We will introduce two new properties to the NRM Simulation:

1.  **Viscosity ($\eta$):** The medium resists flow. This dampens high-frequency noise and stabilizes the pattern.
2.  **Thresholding ($\Theta$):** The medium "snaps" to a high-density state only when the local wave amplitude exceeds a critical threshold.

### The New Equation
Instead of:
$D(x,y) \propto \sum A_i \cos(\dots)$

We propose:
$D(x,y) = \sigma(\sum A_i \cos(\dots) - \Theta)$

Where $\sigma$ is a sigmoid or step function. This will allow soft interference patterns to create hard geometric boundaries.

## 4. Conclusion
We are not abandoning Inverse Cymatics. We are upgrading the Canvas.
The Pilot (Genetic Algorithm) works. It just needs a better medium to paint on.

**Next Step:** Cycle 326 (The Viscous Field).