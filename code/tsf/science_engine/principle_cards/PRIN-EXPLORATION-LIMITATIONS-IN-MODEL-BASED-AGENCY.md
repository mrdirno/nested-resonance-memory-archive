# PRIN-EXPLORATION-LIMITATIONS-IN-MODEL-BASED-AGENCY: The Attractor-Driven Bias

**Principle Type:** Control & Modeling
**Discovered:** Cycle 34, TSF-8 Advanced Model-Based Agency Experiment
**Status:** ✅ VALIDATED (Boundary Conditions Identified)

## Description
This Principle Card outlines a critical failure mode for model-based agency in non-linear emergent systems: the "Attractor-Driven Bias." Even with sophisticated non-linear models like Gaussian Process Regression (GPR) and uncertainty-guided exploration (Upper Confidence Bound - UCB), the Pilot can become trapped in strong, undesirable attractors of the underlying simulation, making it unable to effectively explore or converge to target states outside these regions.

## Observed Dynamics
*   **Persistent Trapping:** The GPR-based agent consistently drove the system into the "Rigid Order" regime (very low Energy Complexity C, very high Phase Order R), where it remained trapped for the entire duration of the experiment, even after target shifts and metabolic cost increases.
*   **Final State:** The system failed to converge to any of the target (C,R) states (e.g., Final C=0.000, R=0.890 vs. Target C=0.4, R=0.3), demonstrating a complete lack of adaptive capability beyond the local attractor.
*   **Model Degradation:** Warning messages from GPR (e.g., "ConvergenceWarning: The optimal value found for dimension 0 of parameter k2__length_scale is close to the specified lower bound") indicate that the model struggled to fit the limited, biased data, suggesting it was trying to compress the entire sampled landscape into a very small or flat region.

## Interpretation
The failure of advanced model-based agency under these conditions reveals:
1.  **Dominance of Attractors:** Strong attractors in the emergent phase space (like the "Rigid Order" regime at low E, high S) can overwhelm even uncertainty-guided exploration strategies. Once the agent samples heavily within such a basin, its model becomes biased towards it.
2.  **Insufficient Global Exploration:** The UCB strategy, while balancing exploration and exploitation, primarily samples around known good points or high-uncertainty regions *near* sampled points. It does not guarantee sufficient *global* exploration of the entire phase space, especially if vast, un-sampled regions contain highly rewarding states.
3.  **Model Bias from Self-Sampling:** The agent's actions (sampling within the attractor) continually reinforce its model's belief about the phase space, making it harder to discover paths out of the attractor.

## Implications for Robust Agency
*   Effective agency in complex emergent systems must incorporate strategies for active, intelligent exploration that explicitly counters attractor-driven biases and seeks global understanding of the phase space.
*   The Pilot needs mechanisms to identify and actively *jump out* of strong attractors when they prove to be suboptimal for the current task.

## Next Steps
*   Design TSF-9 to implement **Active Learning for Phase Space Mapping**. This strategy will focus on actively selecting (E,S) points to sample based on model uncertainty or expected information gain, aiming to build a comprehensive and unbiased internal model of the entire (E,S) -> (C,R) phase space before attempting navigation.
