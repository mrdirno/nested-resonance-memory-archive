# Paper 30: The Bayesian Brain (Predictive Coding)

## Abstract
We demonstrate the **Free Energy Principle** in the NRM vNext architecture, showing that agents equipped with a **Predictive Model** (Kalman Filter) significantly outperform reactive agents in tracking a dynamic environment. By minimizing prediction error (Surprise), the swarm maintains a lower entropy state.

## 1. Introduction
The Free Energy Principle (Friston, 2010) suggests that all biological systems strive to minimize the difference between their internal model and sensory input. We test this by comparing "Bayesian" (Predictive) vs. "Reactive" agents.

## 2. Methodology
- **Task:** Track a target moving with linear velocity + random noise.
- **Agents:**
    - **Reactive:** Moves to last observed position.
    - **Bayesian:** Uses Kalman Filter to estimate state and move to predicted position.
- **Metric:** Mean Squared Error (MSE) of distance to true target.

## 3. Results
- **Reactive MSE:** 11.17
- **Bayesian MSE:** 3.88
- **Improvement:** 65.27%
- **Observation:** The Bayesian agent effectively filtered sensory noise and anticipated the target's motion, whereas the Reactive agent was buffeted by noise.

## 4. Discussion
This validates the "Bayesian Brain" hypothesis. Predictive coding is essential for robust operation in noisy environments. We also noted that **Model Mismatch** (e.g., using a linear model for a circular path) leads to high Free Energy, suggesting that the next step is **Active Inference** (acting to change the world to fit the model) or **Model Learning** (updating the model structure).
