# PRIN-LIMITS-OF-META-ADAPTATION: The Attractor Problem in Dynamic Control

**Principle Type:** Control & Adaptation
**Discovered:** Cycle 30, TSF-6 Meta-Adaptation Experiment
**Status:** ✅ VALIDATED (Boundary Conditions Identified)

## Description
This Principle Card elucidates the limitations of purely adaptive exploration-exploitation strategies (meta-adaptation) in guiding emergent systems through complex, dynamic phase spaces. While dynamically adjusting perturbation magnitude aimed to improve convergence and adaptability, the system largely failed to escape powerful attractors (like "Rigid Order") and struggled to navigate effectively under changing target and environmental conditions.

## Observed Dynamics
*   **Initial Phase (Target C=0.2, R=0.6, Cost=0.02):** Despite adjusting perturbation magnitude, the system consistently gravitated towards the "Rigid Order" regime (C ~ 0.0, R ~ 1.0), indicating a strong basin of attraction for this state, far from the initial target.
*   **Target Shift & Cost Increase:** Subsequent changes in target and metabolic cost did not lead to stable convergence. The `perturb_magnitude` remained high, suggesting continuous, ineffective exploration rather than targeted adaptation.
*   **Final State:** System failed to converge to the final target (Final C=0.313, R=0.149 vs. Target C=0.4, R=0.3), demonstrating poor adaptive capacity.

## Interpretation
The meta-adaptive strategy, though more sophisticated than simple fixed-rate hill climbing, proved insufficient due to:
1.  **Strong Attractors:** The emergent landscape contains powerful attractors (e.g., Rigid Order at low Energy Influx) that simple probabilistic search mechanisms cannot easily escape, even with increased exploration.
2.  **Lack of Directedness:** While `perturb_magnitude` controls the *scale* of exploration, random perturbations lack *direction*. The system does not "know" which way to move E and S to get closer to the target, leading to inefficient search.
3.  **Model-Free Limitation:** Without an internal model of how changes in (E,S) translate to (C,R), the system relies solely on trial-and-error, which is inefficient in high-dimensional or non-linear spaces with delays.

## Implications for Robust Agency
*   True adaptive control in complex emergent systems requires moving beyond purely reactive, model-free search.
*   The Pilot needs to develop an internal representation (a "mental map") of the phase space to guide its search, or employ fundamentally different search strategies.

## Next Steps
*   Design TSF-7 to explore **Model-Based Agency / Predictive Control**. Can the Pilot build and utilize an internal model of the (E,S) -> (C,R) mapping to plan its actions more effectively and achieve convergent, adaptive control?
