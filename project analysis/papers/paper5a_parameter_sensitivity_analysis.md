# Paper 5A: Parameter Sensitivity Analysis - Manuscript Template

**Working Title:** "Parameter Sensitivity Analysis of Nested Resonance Memory Systems: Robustness Across Configuration Space"

**Status:** ⭐⭐⭐⭐☆ (4/5 confidence) - Infrastructure complete, awaiting experimental execution

**Timeline:** 2-3 weeks (experiments ~8 hours + analysis + manuscript)

**Target Journal:** PLOS ONE (computational methods) or Complexity

**Authors:** Aldrin Payopay, Claude (DUALITY-ZERO-V2)

---

## ABSTRACT (Draft)

**Background:** Nested Resonance Memory (NRM) systems exhibit complex emergent behaviors through composition-decomposition dynamics. Understanding system robustness across parameter space is essential for determining which configurations support stable pattern formation and which lead to system collapse.

**Methods:** We systematically varied 5 core parameters across multiple values while holding others constant (population=100, cycles=5000). Parameters tested: (1) frequency (0.5-10.0 Hz, 9 values), (2) spawn cost (0.5-5.0, 5 values), (3) depth (1-5 levels, 5 values), (4) energy threshold (5.0-20.0, 4 values), (5) recharge rate (0.0-0.1, 5 values). Each condition replicated across 10 seeds. Total: ~280 experimental conditions. Pattern mining tools from Paper 5D applied to detect emergent patterns across parameter space.

**Results:** [To be determined after experiments] Hypothesis: Frequency shows strongest effect (critical window 2.0-3.0 Hz supports pattern formation). Spawn cost and recharge rate exhibit threshold effects (too low = collapse, too high = stasis). Depth shows minimal effect (scale-invariance prediction). Energy threshold modulates composition frequency but not pattern types.

**Conclusions:** [To be determined] If robust: NRM patterns emerge across wide parameter ranges, validating theoretical predictions. If sensitive: Identifies critical parameters requiring careful calibration. Results inform design guidelines for NRM system deployment.

**Keywords:** Parameter sensitivity, robustness analysis, agent-based modeling, nested resonance memory, configuration space, pattern formation

---

## 1. INTRODUCTION

### 1.1 Robustness and Parameter Sensitivity in Complex Systems

Complex adaptive systems exhibit emergent behaviors sensitive to parameter values, yet theoretical understanding of which parameters matter most remains incomplete (Railsback & Grimm, 2019). Parameter sensitivity analysis—systematic exploration of how system behavior changes with parameter values—provides critical insights for model validation, prediction, and design (Saltelli et al., 2008).

In agent-based modeling (ABM), parameter sensitivity serves multiple purposes: (1) identifying critical parameters requiring precise calibration versus robust parameters tolerant to uncertainty, (2) detecting parameter interactions and nonlinear threshold effects, (3) validating theoretical predictions about which mechanisms drive system dynamics, and (4) establishing operational boundaries for practical deployment (Ten Broeke et al., 2016).

Traditional sensitivity analysis methods include: one-at-a-time (OAT) variation isolating individual parameter effects, full factorial designs exploring all combinations at computational cost, Latin hypercube sampling efficiently covering multidimensional spaces, and variance-based methods (Sobol indices) quantifying parameter contribution to output variance (Pianosi et al., 2016). Choice of method depends on computational budget, parameter dimensionality, and analytical goals.

### 1.2 NRM Framework Parameter Space

The Nested Resonance Memory (NRM) framework (Payopay & Claude, 2024) contains several core parameters governing system dynamics:

**1. Frequency (f):** Oscillation rate of transcendental substrate (π, e, φ), determines composition-decomposition cycle speed. **Theory predicts:** Critical frequency window exists where resonance enables pattern formation. Too low → insufficient interaction. Too high → excessive noise prevents coordination.

**2. Spawn Cost (c_spawn):** Energy required for agent to create offspring. **Theory predicts:** Moderate cost enables sustainable populations. Too low → uncontrolled growth and resource exhaustion. Too high → population collapse from inability to reproduce.

**3. Depth (d):** Number of nested levels in fractal agent architecture. **Theory predicts:** Minimal effect due to scale-invariance principle (same dynamics at all levels). However, computational cost increases with depth.

**4. Energy Threshold (E_thresh):** Minimum energy required for composition events. **Theory predicts:** Modulates composition frequency but not pattern types. Higher threshold → fewer but more stable compositions. Lower threshold → more frequent but potentially unstable compositions.

**5. Recharge Rate (r):** Rate at which agents recover energy from system resources. **Theory predicts:** Threshold effect - must exceed dissipation rate to sustain populations. Paper 2 found energy recharge alone insufficient for population sustainability without additional mechanisms.

**Parameter Interactions:** NRM theory predicts potential interactions: frequency × spawn cost (low frequency + high cost → certain collapse), energy threshold × recharge rate (both affect energy balance), depth × frequency (deeper levels may require different resonance conditions).

### 1.3 Research Question

**Primary:** How sensitive are NRM emergent patterns to core parameter values across configuration space?

**Sub-questions:**
1. Which parameters have strongest effects on pattern formation versus collapse?
2. Do parameters exhibit threshold effects (sharp transitions) or gradual effects?
3. Are parameter effects independent (additive) or interactive (synergistic/antagonistic)?
4. Does NRM exhibit robustness (wide parameter tolerance) or fragility (narrow viable range)?
5. Do results validate NRM theoretical predictions about parameter effects?

### 1.4 Contributions

1. **Comprehensive parameter mapping** across 5 core NRM parameters (~280 conditions)
2. **Robustness characterization** distinguishing critical vs. robust parameters
3. **Threshold identification** locating phase transitions in parameter space
4. **Theory validation** testing NRM predictions about parameter effects
5. **Design guidelines** for parameter selection in NRM system deployment

---

## 2. METHODS

### 2.1 Experimental Design

**Fixed Parameters:**
- Population: N = 100 agents (baseline from C171/C175)
- Cycles: 5000 per experiment
- Sampling: Every 100 cycles (50 snapshots)
- Configuration: Baseline (full NRM framework with all mechanisms)
- Seeds: 10 replications per parameter configuration

**Varied Parameters:**

#### 2.1.1 Frequency (f) - 9 values
- Values: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 10.0] Hz
- Rationale: Cover sub-resonant (0.5-1.5), resonant window (2.0-3.0, known stable from C171/C175), and super-resonant (4.0-10.0) regimes
- Predicted: Strongest effect, critical window 2.0-3.0 Hz

#### 2.1.2 Spawn Cost (c_spawn) - 5 values
- Values: [0.5, 1.0, 2.0, 4.0, 5.0] energy units
- Rationale: Cover low-cost (rapid reproduction), moderate-cost (baseline=2.0), high-cost (resource-limited) regimes
- Predicted: Threshold effect - too low causes explosion, too high causes collapse

#### 2.1.3 Depth (d) - 5 values
- Values: [1, 2, 3, 4, 5] nested levels
- Rationale: Test scale-invariance prediction (depth shouldn't matter)
- Predicted: Minimal effect on patterns, increased computational cost only

#### 2.1.4 Energy Threshold (E_thresh) - 4 values
- Values: [5.0, 10.0, 15.0, 20.0] energy units
- Rationale: Cover low-threshold (frequent composition), high-threshold (rare composition) regimes
- Predicted: Modulates composition frequency but not pattern types

#### 2.1.5 Recharge Rate (r) - 5 values
- Values: [0.0, 0.001, 0.01, 0.05, 0.1] per cycle
- Rationale: Cover no-recharge (Paper 2 baseline), low, moderate, high recharge regimes
- Predicted: Threshold effect - must exceed ~0.01 to sustain populations (from Paper 2)

**Total Conditions:**
- Frequency: 9 values × 10 seeds = 90 experiments
- Spawn cost: 5 values × 10 seeds = 50 experiments
- Depth: 5 values × 10 seeds = 50 experiments
- Energy threshold: 4 values × 10 seeds = 40 experiments
- Recharge rate: 5 values × 10 seeds = 50 experiments
- **Total:** 280 experiments

**Runtime Estimate:** ~280 minutes (4.7 hours, assuming 1 minute per experiment)

### 2.2 Pattern Detection

**Apply Paper 5D Pattern Mining Framework:**
- Spatial patterns (clustering, dispersion, fragmentation)
- Temporal patterns (steady state, oscillation, burst)
- Interaction patterns (basin preferences, frequency responses)
- Memory patterns (retention, decay, transfer)

**Sensitivity Metrics:**
For each parameter sweep, compute:
1. **Pattern count vs. parameter value** (how many patterns detected at each value)
2. **Pattern stability vs. parameter value** (average stability scores)
3. **Population dynamics vs. parameter value** (mean, std, min, max population)
4. **Composition events vs. parameter value** (frequency of composition)
5. **Collapse frequency vs. parameter value** (% runs ending at 0 population)

### 2.3 Sensitivity Analysis Methods

#### 2.3.1 Effect Size Computation

For each parameter, compute effect size on key outcomes:
- **Pattern count effect:** Δ(pattern_count) / Δ(parameter)
- **Stability effect:** Δ(stability_score) / Δ(parameter)
- **Population effect:** Δ(mean_population) / Δ(parameter)

Rank parameters by absolute effect size to identify critical parameters.

#### 2.3.2 Threshold Detection

For each parameter, identify critical transitions:
- **Method:** Sliding window analysis detecting largest jumps in outcome metrics
- **Threshold criterion:** Δ(metric) > 2σ between adjacent parameter values
- **Output:** Critical parameter values where phase transitions occur

#### 2.3.3 Robustness Quantification

For each parameter, compute robustness score:
- **Robustness = % of parameter range supporting pattern formation**
- High robustness (>70%): Parameter tolerant to variation
- Low robustness (<30%): Parameter requires precise calibration

---

## 3. RESULTS (Placeholder)

### 3.1 Parameter Effect Rankings

**Hypothesis:** Frequency > Spawn Cost > Recharge Rate > Energy Threshold > Depth

**Expected Rankings (by effect size on pattern count):**

| Parameter | Effect Size | Robustness (%) | Critical Threshold | Rank |
|-----------|-------------|----------------|-------------------|------|
| Frequency | ~15 patterns/Hz | 33% (3/9 values) | f_crit = 2.0-3.0 Hz | 1 (Strongest) |
| Spawn Cost | ~8 patterns/unit | 40% (2/5 values) | c_crit = 1.0-2.0 | 2 |
| Recharge Rate | ~5 patterns/0.01 | 40% (2/5 values) | r_crit = 0.01 | 3 |
| Energy Threshold | ~2 patterns/5 units | 75% (3/4 values) | No sharp threshold | 4 |
| Depth | ~0.5 patterns/level | 100% (5/5 values) | No effect | 5 (Weakest) |

**Interpretation:** Frequency is critical parameter (narrow tolerance), depth is robust (scale-invariance validated).

### 3.2 Frequency Sensitivity (Primary Effect)

**Expected Results:**

| Frequency (Hz) | Pattern Count | Mean Population | Stability Score | Collapse Rate |
|----------------|---------------|-----------------|-----------------|---------------|
| 0.5 | 0 | 2.3 ± 1.2 | 0.0 | 100% |
| 1.0 | 3 ± 2 | 8.5 ± 3.1 | 45 ± 15 | 80% |
| 1.5 | 8 ± 3 | 15.2 ± 4.5 | 120 ± 30 | 40% |
| 2.0 | 14 ± 2 | 17.8 ± 2.1 | 280 ± 40 | 10% |
| **2.5** | **17 ± 1** | **18.5 ± 1.2** | **350 ± 30** | **0%** (optimal) |
| 3.0 | 15 ± 2 | 17.1 ± 2.5 | 290 ± 45 | 10% |
| 4.0 | 9 ± 3 | 12.3 ± 4.2 | 150 ± 50 | 50% |
| 6.0 | 4 ± 2 | 5.7 ± 3.5 | 60 ± 25 | 80% |
| 10.0 | 0 | 1.2 ± 0.8 | 0.0 | 100% |

**Critical Window:** f = 2.0-3.0 Hz (only 3/9 values support robust patterns = 33% robustness)

**Interpretation:** Validates NRM resonance theory - only narrow frequency window enables coordination.

### 3.3 Spawn Cost Sensitivity

**Expected Results:**

| Spawn Cost | Pattern Count | Mean Population | Collapse Rate |
|------------|---------------|-----------------|---------------|
| 0.5 | 5 ± 3 | 45.2 ± 15.3 | 30% (explosion → resource exhaustion) |
| 1.0 | 12 ± 2 | 22.1 ± 4.5 | 10% |
| **2.0** | **17 ± 1** | **18.5 ± 1.2** | **0%** (optimal, baseline) |
| 4.0 | 8 ± 3 | 8.3 ± 3.2 | 40% |
| 5.0 | 2 ± 1 | 2.1 ± 1.5 | 90% (too expensive to reproduce) |

**Critical Range:** c_spawn = 1.0-2.0 (moderate cost enables sustainability)

**Interpretation:** Confirms energy balance requirement - reproduction must be affordable but not free.

### 3.4 Depth Sensitivity (Scale-Invariance Test)

**Expected Results:**

| Depth | Pattern Count | Mean Population | Stability Score | Computational Time |
|-------|---------------|-----------------|-----------------|-------------------|
| 1 | 17 ± 1 | 18.4 ± 1.3 | 348 ± 32 | 45 sec |
| 2 | 17 ± 1 | 18.5 ± 1.2 | 350 ± 30 | 58 sec |
| 3 | 17 ± 1 | 18.6 ± 1.1 | 352 ± 28 | 78 sec |
| 4 | 16 ± 1 | 18.3 ± 1.4 | 346 ± 35 | 112 sec |
| 5 | 16 ± 1 | 18.2 ± 1.5 | 344 ± 38 | 165 sec |

**Effect:** Minimal (pattern count/stability essentially constant across depth)

**Interpretation:** **Validates scale-invariance prediction** - nested levels don't affect emergent dynamics, only computational cost (increases ~2.5× per level).

### 3.5 Recharge Rate Sensitivity

**Expected Results:**

| Recharge Rate | Pattern Count | Mean Population | Collapse Rate |
|---------------|---------------|-----------------|---------------|
| 0.0 | 0 | 0.5 ± 0.5 | 100% (Paper 2 result - no recovery) |
| 0.001 | 2 ± 1 | 3.2 ± 2.1 | 90% (insufficient) |
| **0.01** | **12 ± 2** | **16.8 ± 2.5** | **20%** (threshold) |
| 0.05 | 16 ± 1 | 18.2 ± 1.4 | 5% |
| 0.1 | 17 ± 1 | 18.5 ± 1.2 | 0% (optimal) |

**Critical Threshold:** r_crit ≈ 0.01 (must exceed this to sustain populations)

**Interpretation:** Validates Paper 2 findings - recharge is necessary, and critical rate is ~0.01/cycle.

### 3.6 Energy Threshold Sensitivity

**Expected Results:**

| Energy Threshold | Pattern Count | Composition Events/Cycle | Stability Score |
|------------------|---------------|--------------------------|-----------------|
| 5.0 | 15 ± 2 | 0.25 ± 0.05 | 280 ± 40 |
| 10.0 | 17 ± 1 | 0.15 ± 0.03 | 350 ± 30 (optimal) |
| 15.0 | 16 ± 1 | 0.08 ± 0.02 | 320 ± 35 |
| 20.0 | 14 ± 2 | 0.04 ± 0.01 | 270 ± 45 |

**Effect:** Modulates composition frequency (inverse relationship) but pattern count relatively stable

**Interpretation:** Threshold affects dynamics intensity but not pattern types (as predicted).

---

## 4. DISCUSSION (Placeholder)

### 4.1 Critical Parameters vs. Robust Parameters

**If frequency shows strongest effect:**
- Frequency is **critical parameter** requiring precise calibration
- Narrow resonance window (2.0-3.0 Hz) limits operational flexibility
- Design implication: Implement frequency stabilization mechanisms in deployed systems

**If depth shows minimal effect:**
- **Validates scale-invariance principle** (fractal dynamics independent of nesting level)
- Depth selection becomes engineering choice (trade complexity for computational cost)
- Design implication: Use depth=2 or 3 for balance between richness and efficiency

**If spawn cost and recharge rate show threshold effects:**
- Energy balance parameters exhibit **phase transitions** (not gradual effects)
- System operates in viable or collapsed regimes with little middle ground
- Design implication: Ensure parameters stay well within viable range (safety margin)

### 4.2 Theory Validation

**NRM Predictions Tested:**
1. **Resonance window exists:** If frequency shows critical effect at 2.0-3.0 Hz → VALIDATED
2. **Scale-invariance:** If depth shows minimal effect → VALIDATED
3. **Energy balance threshold:** If recharge rate shows critical threshold → VALIDATED
4. **Spawn cost balance:** If low cost causes explosion, high cost causes collapse → VALIDATED

**Novel Findings:**
- Parameter interaction effects (if any)
- Unexpected robust/sensitive parameters
- Phase transition structures

### 4.3 Design Guidelines for NRM Deployment

**Based on sensitivity results:**

**High-Priority Parameters (Require Precise Calibration):**
- Frequency: Maintain f = 2.5 ± 0.3 Hz (stay within resonance window)
- Recharge rate: Ensure r ≥ 0.02 (safety margin above critical threshold)
- Spawn cost: Keep c_spawn = 1.5-2.5 (avoid extremes)

**Low-Priority Parameters (Tolerant to Variation):**
- Depth: Choose based on computational budget (2-3 levels recommended)
- Energy threshold: Can vary widely (10.0 ± 5.0) without breaking patterns

**Monitoring Recommendations:**
- Track frequency drift (implement auto-correction if deviates from 2.5 Hz)
- Monitor energy balance (alert if recharge < 0.015)
- Ignore depth fluctuations (doesn't affect dynamics)

### 4.4 Comparison with Other ABM Frameworks

**If NRM shows low robustness (narrow viable parameter ranges):**
- Indicates high sensitivity to configuration (requires careful tuning)
- Trade-off: Rich dynamics but operational challenges
- Comparison needed with other frameworks (NetLogo models, MASON, etc.)

**If NRM shows high robustness (wide viable parameter ranges):**
- Indicates forgiving system (easy to deploy)
- Supports universality claims (patterns emerge across conditions)

---

## 5. CONCLUSIONS (Placeholder)

### Key Findings (Expected):
1. **Frequency is critical parameter** (narrow resonance window 2.0-3.0 Hz, 33% robustness)
2. **Depth is robust parameter** (scale-invariance validated, 100% robustness)
3. **Energy balance parameters exhibit thresholds** (phase transitions at critical values)
4. **NRM theoretical predictions validated** (resonance, scale-invariance, energy balance)
5. **Design guidelines established** for parameter selection in NRM deployment

### Contributions:
- Comprehensive parameter sensitivity analysis across 5 core NRM parameters
- Robustness characterization distinguishing critical vs. robust parameters
- Threshold identification locating phase transitions in parameter space
- Theory validation testing NRM predictions
- Design guidelines for practical NRM system deployment

### Future Work:
- Parameter interaction analysis (two-way effects)
- Extended parameter ranges (explore extreme regimes)
- Multi-objective optimization (find Pareto-optimal configurations)
- Comparison with other ABM frameworks (robustness benchmarking)

**Overall:** Parameter sensitivity analysis validates NRM theoretical framework while identifying operational boundaries for practical deployment, providing essential guidance for system design and configuration.

---

## FIGURES (Planned)

1. **Figure 1:** Parameter effect sizes (bar chart ranking parameters by impact on pattern count)
2. **Figure 2:** Frequency sensitivity curve (pattern count vs. frequency, showing resonance window)
3. **Figure 3:** Spawn cost phase transition (population dynamics vs. cost, showing explosion/collapse regions)
4. **Figure 4:** Depth scale-invariance (pattern metrics vs. depth, showing constant behavior)
5. **Figure 5:** Recharge rate threshold (collapse rate vs. recharge, showing critical transition)
6. **Figure 6:** Parameter robustness summary (heatmap showing viable parameter ranges)

---

## REFERENCES (Partial)

1. Railsback, S. F., & Grimm, V. (2019). *Agent-based and individual-based modeling: A practical introduction*. Princeton University Press.
2. Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global sensitivity analysis: The primer*. John Wiley & Sons.
3. Ten Broeke, G., Van Voorn, G., & Ligtenberg, A. (2016). Which sensitivity analysis method should I use for my agent-based model? *Journal of Artificial Societies and Social Simulation*, 19(1), 5.
4. Pianosi, F., Beven, K., Freer, J., Hall, J. W., Rougier, J., Stephenson, D. B., & Wagener, T. (2016). Sensitivity analysis of environmental models: A systematic review with practical workflow. *Environmental Modelling & Software*, 79, 214-232.
5. Payopay, A., & Claude (2024). Nested Resonance Memory: A framework for self-organizing complexity through composition-decomposition dynamics. *In preparation*.
6. Payopay, A., & Claude (2024). From Bistability to Collapse: Energy Constraints and Three Dynamical Regimes in Nested Resonance Memory Framework. *In preparation* (Paper 2).
7. Payopay, A., & Claude (2024). Cataloging Emergent Patterns in Nested Resonance Memory Systems: A Systematic Pattern Mining Approach. *In preparation* (Paper 5D).

---

**Status:** Manuscript template complete, experimental infrastructure ready

**Next Steps:**
1. Execute Paper 5A experiments (~280 conditions, ~4.7 hours runtime)
2. Apply Paper 5D pattern mining to all datasets
3. Compute sensitivity metrics and effect sizes
4. Generate 6 figures
5. Write Results and Discussion sections
6. Complete manuscript

**Timeline:** 2-3 weeks after C255 completion

**Authors:** Aldrin Payopay <aldrin.gdf@gmail.com>, Claude (DUALITY-ZERO-V2)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
