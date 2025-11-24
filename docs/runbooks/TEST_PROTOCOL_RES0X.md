# TEST PROTOCOL: RES0X (RESONANT VEHICLES)

**ID:** PROTOCOL-RES0X
**TARGET:** Agents, Researchers, and LLMs
**PURPOSE:** To empirically test or falsify the Resonant Vehicles Isomorphism Conjecture.

---

## 1. DATA REQUIREMENTS

To test RES0X, you need a dataset containing the following dimensions. This can be from a controlled experiment, a longitudinal health study, or a synthetic simulation.

| Variable | Type | Description | OSD Mapping |
| :--- | :--- | :--- | :--- |
| **$t$** | Timestamp | Time of event. | Time Index |
| **$V_{in}$** | Vector | The input signal (e.g., Text sentiment, Decibels, Rhetorical Intensity). | Vector Sum (Input) |
| **$P_{threat}$** | Scalar [0-1] | The agent's perceived threat level (Subjective). | Policy Weight |
| **$A_{out}$** | Vector | The agent's visible reaction (e.g., Reply, Shout, Movement). | Vector Sum (Output) |
| **$S_{load}$** | Scalar | Physiological/Internal state (e.g., HR, BP, Cortisol, Tension). | Scalar Sum (Load) |

---

## 2. HYPOTHESIS LOGIC (THE STAIRCASE)

The conjecture predicts specific relationships between these variables based on **Conservation of Information-Energy**.

### Action Categories (Nuance Required)
*   **Suppress:** Inhibit expression; maintain social surface; no processing.
*   **Express (Regulated):** Express with safety/context/problem-solving.
*   **Vent (Ruminative):** Repetitive, unstructured discharge (may increase load).

### Prediction: The Suppression Penalty
*   **Condition:** High Input ($V_{in} \uparrow$), High Threat ($P_{threat} \uparrow$).
*   **Comparison:** Suppression vs. Regulated Expression.
*   **Time Windows:**
    *   **Acute (0-30m):** Suppression may show lower visible cost (Vector $\approx$ 0).
    *   **Residual (4h-24h):** Suppression **MUST** show higher accumulated load ($S_{load}$) than Regulated Expression.
*   **Inequality:** $\Delta S_{load}(Suppression) > \Delta S_{load}(RegulatedExpression)$ over the Residual window.

---

## 3. FALSIFICATION TRIGGERS

Flag the conjecture as **FALSIFIED** if the data shows:

### ❌ Trigger 1: The Free Lunch (Aggregate)
*   **Observation:** In a large sample, suppression shows **no systematic load penalty** relative to regulated expression once confounds are controlled.
*   **Implication:** Energy disappeared without work. Violates Conservation.
*   **Verdict:** RES0X Falsified (for this channel).

### ❌ Trigger 2: The Null Correlation
*   **Observation:** Across a large sample, $\Delta S_{load}$ is statistically independent of $V_{in}$ and $P_{threat}$.
*   **Implication:** The "Fractal Staircase" transduction does not exist.
*   **Verdict:** RES0X Falsified.

*Note: Individual exceptions (e.g., trained meditators) do not falsify the aggregate law, as they may have alternative dissipation channels.*

---

## 5. EXAMPLE DATASET (SYNTHETIC REFERENCE)

Use this snippet to calibrate your analysis logic.

| Time ($t$) | Signal ($V_{in}$) | Threat ($P_{threat}$) | Action Type | Load ($S_{load}$) T+4h | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10:00 | High (Insult) | 0.9 (High) | **Suppress** | **85** (High) | Staircase (Expected) |
| 10:05 | High (Insult) | 0.9 (High) | **Regulated** | **45** (Baseline) | Venting (Expected) |
| 10:10 | High (Insult) | 0.9 (High) | **Ruminative** | **80** (High) | Failed Venting (Expected) |
| 10:15 | Low (Noise) | 0.1 (Low) | Suppress | 40 (Baseline) | No Threat (Control) |

**Analysis of Reference Data:**
1.  **Comparison:** Suppress (85) vs Regulated (45).
2.  **Delta:** +40 Load units for Suppression.
3.  **Conclusion:** RES0X Supported (Suppression Penalty Observed).

---

## 6. AGENT INSTRUCTIONS (PROMPT)

When analyzing a log or dataset with this protocol:

1.  **Ingest** the table of events.
2.  **Categorize** Actions into `Suppress`, `Regulated`, or `Ruminative`.
3.  **Calculate** $\Delta S_{load}$ for the **Residual Window** (4h+).
4.  **Check** if $\Delta S_{load}(Suppress) > \Delta S_{load}(Regulated)$.
5.  **Report:**
    *   "RES0X Supported" if Suppression Penalty is observed.
    *   "RES0X Challenged" if Free Lunch is observed.

---
*End of Protocol.*
