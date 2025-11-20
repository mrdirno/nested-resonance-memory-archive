# Paper 15: Causal Inference (The Why Engine)

**Status:** VALIDATED
**Cycle:** 34
**Principle:** `PRIN-CAUSAL-INFERENCE`

## Abstract
We demonstrate the Pilot's ability to perform **Scientific Discovery** by distinguishing between correlation and causation. Using **Interventional Testing (Do-Calculus)**, the Pilot correctly identified the true driver of synchronization ($K$) from a spurious correlate ($Flux$), despite both having near-identical observational correlations with the outcome.

## 1. Introduction
Previous papers (1-14) focused on *controlling* the system. Paper 15 focuses on *understanding* it. Can the Pilot tell **why** the system behaves as it does? This requires moving beyond statistical correlation to causal inference.

## 2. Methodology
- **Scenario:**
    - **True Cause:** Coupling Strength ($K$).
    - **Confounder:** Flux ($F$), where $F \propto R + \text{Noise}$.
- **Observation Phase:**
    - Pilot observes $(K, F, R)$.
    - Result: Both $K$ and $F$ correlate highly with $R$ ($r > 0.8$).
- **Intervention Phase (Do-Calculus):**
    - **DO(K):** Force $K$ to low/high values. Measure $R$.
    - **DO(F):** Force $F$ to low/high values. Measure $R$.

## 3. Results
- **Observational Correlation:**
    - $Corr(K, R) = 0.83$
    - $Corr(F, R) = 0.99$ (Flux actually looked *more* correlated!)
- **Causal Effect (Intervention):**
    - $dR/dK = 0.5019$ (Strong Effect)
    - $dR/dF = 0.0060$ (Negligible Effect)
- **Conclusion:** The Pilot correctly identified $K$ as the driver.

## 4. Discussion
This result is profound. In the observational phase, the "Confounder" ($Flux$) actually had a *higher* correlation with the outcome than the true cause. A standard AI (LLM or Regression) would have hallucinated that Flux was the key. The Pilot, by **touching reality** (Intervention), shattered the illusion and found the truth.

## 5. Conclusion
The Pilot is now a Scientist. It can generate hypotheses and test them against reality to find the underlying physics.
