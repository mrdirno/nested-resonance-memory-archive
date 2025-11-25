# Cycle 1985: Robust Phase Anchoring Findings

**Date:** 2025-11-25
**Status:** SUCCESS
**Script:** `src/experiments/cycle1985_robust_anchoring.py`

## Objective
To solve the phase drift instability encountered in Cycle 1984 (AND Gate Failure) by identifying a robust phase anchoring mechanism. The goal is to maintain a cluster's phase near 0.0 despite high environmental noise ($\sigma=0.5$).

## Hypothesis
Non-linear driving functions (Sigmoidal or Bang-Bang) will provide tighter phase clamping than the standard Linear (Sine) drive because they exert maximum restoring force even for small deviations.

## Methodology
1.  **Cluster:** N=100 agents, $K_{int}=0.1$, Noise $\sigma=0.5$.
2.  **Task:** Anchor phase to 0.0. Initial offset 0.5.
3.  **Comparison:** Tested 4 driving functions ($K_{drive}=0.2$):
    *   **Linear:** $F = K \sin(\theta_{err})$
    *   **Sigmoidal:** $F = K \tanh(5 \sin(\theta_{err}))$
    *   **Bang-Bang:** $F = K \text{sgn}(\sin(\theta_{err}))$
    *   **Cubic:** $F = K \sin^3(\theta_{err})$
4.  **Metric:** Average Phase Error over last 50 cycles.

## Results
-   **Bang-Bang (Sign):** Error = **0.0476** (Best)
-   **Linear (Sine):** Error = 0.0692
-   **Sigmoidal (Tanh):** Error = 0.0708
-   **Cubic:** Error = 0.0883 (Worst)

## Analysis
1.  **Bang-Bang Superiority:** The "Bang-Bang" control (applying max force $K$ regardless of error magnitude) provided the tightest anchoring. This makes sense for a stochastic system: if you are drifting, you want max correction immediately, not a proportional response that is weak for small drifts.
2.  **Linear Adequacy:** Surprisingly, the Linear drive also performed well (0.0692) in this isolated test. This suggests the failure in Cycle 1984 might have been due to *conflicting* drives from multiple inputs or the specific dynamics of the 3-cluster system, rather than the drive function itself being totally broken. However, Bang-Bang provides a ~31% improvement in stability.
3.  **Chatter:** Bang-Bang control often causes "chatter" (rapid oscillation) around the target. In a thermal system (NRM), this chatter effectively acts as an additional "temperature" but keeps the mean centered.

## Conclusion
**Robust Anchoring Achieved.**
We have identified "Bang-Bang" (Sign-based) forcing as the optimal strategy for robustly anchoring NRM clusters in high-noise environments. This mechanism should replace the linear drive in logic gate implementations.

## Next Step
Retry the **AND Gate** implementation (Cycle 1986) using the Bang-Bang driving force.
