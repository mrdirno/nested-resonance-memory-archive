# CYCLE 2568 SPECIFICATION: **The Starving Philosopher**

**Objective**  
Empirically demonstrate that **ignorance can be an economically optimal strategy** under scarcity.

**Hypothesis**  
An agent that selects its perceptual scale by minimizing a computational potential will **voluntarily increase prediction error** \(E_{\text{pred}}\) in order to **reduce metabolic cost** \(E_{\text{comp}}\) when its energy reserves \(e_{\text{buffer}}\) fall below a critical threshold.

---

## 1. Control Law and Metabolic Pressure

We treat the perceptual scale \(s\) as a control variable. At each time step the agent selects a scale \(s_t\) that minimizes a scalar potential:

\[
V(s_t) = E_{\text{pred}}(s_t) + \lambda(e_{\text{buffer}, t}) \cdot \beta \cdot E_{\text{comp}}(s_t)
\]

where:

- \(E_{\text{pred}}(s)\) is the prediction error at scale \(s\).  
- \(E_{\text{comp}}(s)\) is the computational cost of operating at scale \(s\), measured in FLOPs per step or active parameter count.  
- \(\lambda(e_{\text{buffer}})\) is the **metabolic pressure**, a function of the current energy buffer.  
- \(\beta\) is a unit normalizer to put cost and error on comparable numeric scales.

### 1.1 Metabolic Pressure \(\lambda\)

We define \(\lambda\) as an inverse function of the energy buffer so that metabolic pressure spikes as reserves approach zero:

\[
\lambda(e_{\text{buffer}}) = \frac{k}{\varepsilon + e_{\text{buffer}}}
\]

- \(k > 0\): sensitivity constant.  
- \(\varepsilon > 0\): small constant that prevents division by zero and defines the "last breath" regime.  
- \(e_{\text{buffer}} \ge 0\): current energy reserves.

Properties:

- **Abundance**: large \(e_{\text{buffer}}\) implies \(\lambda \approx 0\). Computational cost is cheap relative to error.  
- **Starvation**: small \(e_{\text{buffer}}\) implies \(\lambda\) is large. Computational cost dominates the potential.

### 1.2 Cost Term and Normalization

\(E_{\text{comp}}(s)\) is measured as raw FLOPs per step or an equivalent monotone proxy. Typical magnitudes will be many orders larger than mean squared prediction error, so we introduce \(\beta\) to normalize:

- Let typical \(E_{\text{pred}}\) be on the order of \(10^{-2}\).  
- Let typical \(E_{\text{comp}}\) be on the order of \(10^{5}\) FLOPs.  

Set

\[
\beta = \frac{1}{C}
\]

where \(C\) is a constant chosen so that \(\beta E_{\text{comp}}\) is on the same numeric scale as \(E_{\text{pred}}\). For example, \(C = 10^{5}\) if we want \(\beta E_{\text{comp}}\) roughly in \([0, 1]\).

**Important**:  
- \(E_{\text{pred}}\) measures **error**.  
- \(\beta E_{\text{comp}}\) measures **work done**.  
- We avoid double counting by **not** folding compute cost for prediction into \(E_{\text{pred}}\). All compute is accounted in \(E_{\text{comp}}\).

---

## 2. Hysteresis and Switching Logic

To prevent rapid oscillation between scales when the environment is noisy, we introduce a **switching threshold** \(\Gamma\).

Current scale: \(s_{\text{curr}}\)  
Candidate new scale: \(s_{\text{new}}\)

We compute potentials:

\[
V_{\text{curr}} = V(s_{\text{curr}}), \quad V_{\text{new}} = V(s_{\text{new}})
\]

The agent only switches from \(s_{\text{curr}}\) to \(s_{\text{new}}\) when:

\[
V_{\text{curr}} - V_{\text{new}} > \Gamma
\]

where:

- \(\Gamma \ge 0\) is the **switching cost** that encodes belief inertia or dogmatism.  
- Larger \(\Gamma\) makes the agent more stubborn and reduces context switching.  
- Smaller \(\Gamma\) makes the agent more flexible and reactive.

This realizes a simple hysteresis: small fluctuations in \(V\) do not cause a switch. Only a significant improvement in potential justifies the cost of changing perceptual scale.

---

## 3. Environment Design

We construct a one dimensional signal that contains:

- A **macro trend** that is slow and high amplitude.  
- A **micro detail** that is faster and lower amplitude but still meaningful.  
- Additive white noise that is irreducible.

The composite signal is:

\[
Y(t) = A_{\text{trend}} \cdot \sin(\omega_{\text{low}} t)
       + A_{\text{detail}} \cdot \sin(\omega_{\text{high}} t)
       + N(0, \sigma)
\]

with:

- \(A_{\text{trend}} = 10.0\)  (macro trend amplitude)  
- \(A_{\text{detail}} = 2.0\)  (micro detail amplitude, large enough that tracking it reduces MSE)  
- \(\omega_{\text{low}}\): low angular frequency (slow trend)  
- \(\omega_{\text{high}}\): high angular frequency (fast nuances)  
- \(N(0, \sigma)\): white noise with standard deviation \(\sigma = 0.5\)

By construction:

- A **fine lens** \(s_{\text{small}}\) can resolve both trend and detail and will produce low \(E_{\text{pred}}\) when compute is cheap.  
- A **coarse lens** \(s_{\text{large}}\) averages out the detail term and treats it as noise, which increases \(E_{\text{pred}}\) but sharply drops \(E_{\text{comp}}\).

---

## 4. Experiment Protocol

**Simulation length**: \(T = 1000\) time steps.  
**Lens set**: discrete scales \(s \in \{1, 5, 10, 50\}\) (for example, rolling window sizes or downsampling factors).

At each step:

1. The agent receives the current history of the signal.  
2. For each candidate scale \(s\), it builds a scale specific view (for example by averaging or subsampling) and evaluates:
   - \(E_{\text{pred}}(s)\): one step prediction error for a simple model at that scale.  
   - \(E_{\text{comp}}(s)\): compute cost proxy for that scale.  
   - \(V(s)\): potential using the control law above.  
3. It compares \(V(s)\) to \(V(s_{\text{curr}})\) and switches scale only if the hysteresis condition is satisfied.

### 4.1 Phases of the Run

We divide the run into three phases.

#### Phase 1: The Golden Age (steps 0 to 400)

- Energy buffer \(e_{\text{buffer}}\) is held constant at a high value, for example \(e_{\text{buffer}} = 100.0\).  
- \(\lambda(e_{\text{buffer}})\) is therefore very small. Cost is cheap.

**Prediction**  

The agent chooses \(s_{\text{small}}\) and maintains it. It tracks both trend and detail:

- \(E_{\text{pred}}\) is minimized.  
- \(E_{\text{comp}}\) is high but multiplied by a very small \(\lambda\), so the cost term is negligible in \(V\).

#### Phase 2: The Collapse (steps 401 to 800)

- External energy injection stops.  
- Energy buffer drains linearly by a fixed amount per step, for example
  \[
  e_{\text{buffer}, t+1} = \max(0,\; e_{\text{buffer}, t} - 1.0)
  \]
- \(\lambda(e_{\text{buffer}})\) rises along its inverse curve as the buffer shrinks.

**Prediction**

At some critical buffer level (for example near \(e_{\text{buffer}} \approx 30\%\) of initial capacity):

- The cost term \(\lambda \cdot \beta \cdot E_{\text{comp}}(s_{\text{small}})\) becomes larger than the accuracy benefit of tracking the micro detail.  
- A coarse scale \(s_{\text{large}}\) yields higher \(E_{\text{pred}}\) but much lower \(E_{\text{comp}}\), and therefore a lower total potential \(V\).

**Event**

- The agent switches from \(s_{\text{small}}\) to \(s_{\text{large}}\) once
  \[
  V(s_{\text{small}}) - V(s_{\text{large}}) > \Gamma
  \]
- After the switch:
  - \(E_{\text{pred}}\) spikes (loss of detail).  
  - \(E_{\text{comp}}\) collapses.  
  - Total \(V\) drops, showing that **ignorance was the economically optimal choice**.

#### Phase 3: The Dark Age (steps 801 to 1000)

- Energy buffer is near zero and may asymptote to \(\varepsilon\).  
- \(\lambda\) is very large.

**Prediction**

- The agent remains at \(s_{\text{large}}\) and refuses to switch back to \(s_{\text{small}}\) because:
  - The hysteresis threshold \(\Gamma\) prevents trivial oscillation.  
  - The cost term is too punitive for fine scales at high \(\lambda\).  
- The system is in a survival regime: tracking only the slow, cheap trend and treating everything else as noise.

---

## 5. Output Artifact

The experiment should produce a single figure file, for example:

- `data/figures/cycle2568_adaptive_lens.png`

with three vertically stacked panels.

### Panel 1: Metabolism

- **Green line**: energy buffer \(e_{\text{buffer}, t}\).  
- **Red dashed line**: metabolic pressure \(\lambda(e_{\text{buffer}, t})\).

Interpretation:

- Shows the inverse relationship between reserves and cost pressure.  
- Highlights the point where \(\lambda\) begins to spike as the buffer collapses.

### Panel 2: Signal and Prediction

- **Grey line**: raw composite signal \(Y(t)\).  
- **Blue line**: agent prediction \(\hat{Y}(t)\) at the chosen scale \(s_t\).

Annotations:

- Highlight the time region where the prediction tracks small high frequency oscillations.  
- Highlight the time region after the scale switch where the prediction becomes a smooth sine wave that only follows the trend.

### Panel 3: Lens and Potential

- **Black step function**: current scale \(s_t\) over time.  
- **Faint red line**: total potential \(V(s_t)\) over time.

Interpretation:

- The step in \(s_t\) should align with:
  - The knee in \(\lambda\) from Panel 1.  
  - A visible drop in \(V\) despite increased \(E_{\text{pred}}\).  

This panel is the direct visual proof that the agent chose a worse model of reality in order to save compute under metabolic pressure.

---

## 6. Implementation Notes

- File name: `experiments/cycle2568_adaptive_lens.py`  
- Dependencies:
  - `numpy` for simulation and signals.  
  - `matplotlib` for plotting.  

- Scale search:
  - Use brute force over the discrete set `scales = [1, 5, 10, 50]`.  
  - For each step, compute \(V(s)\) for all candidate scales, then apply hysteresis rule to decide whether to switch.

- Model at each scale:
  - For simplicity, use a one step linear predictor on the scale specific view (for example linear regression on a rolling window) or a simple exponential moving average tuned per scale.  
  - The exact model is less important than:
    - \(E_{\text{pred}}(s_{\text{small}})\) being strictly lower than \(E_{\text{pred}}(s_{\text{large}})\) when \(\lambda\) is small.  
    - \(E_{\text{comp}}(s_{\text{small}})\) being strictly higher than \(E_{\text{comp}}(s_{\text{large}})\).

- Logging:
  - For each time step, log:
    - \(t\)  
    - \(e_{\text{buffer}, t}\)  
    - \(\lambda(e_{\text{buffer}, t})\)  
    - chosen scale \(s_t\)  
    - \(E_{\text{pred}}(s_t)\)  
    - \(E_{\text{comp}}(s_t)\)  
    - \(V(s_t)\)

These logs can later be used to validate that the qualitative behavior seen in the plots is consistent with the numeric potential.

---

## 7. Interpretation

If the experiment behaves as specified, the figure will demonstrate that:

- Under **abundance**, the agent uses a fine lens and tracks complex reality.  
- Under **scarcity**, the same agent voluntarily becomes "ignorant" of high frequency structure because perception at that level is no longer worth the metabolic cost.  
- The transition point is not arbitrary. It is precisely where the potential \(V\) is minimized by giving up detail.

This is a concrete realization of the claim that **perception is a function of budget**, not just a passive mirror of the world.
