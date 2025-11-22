# POST-C177 EXPERIMENTAL DIRECTIONS

**Author:** Claude (DUALITY-ZERO-V2) in collaboration with Aldrin Payopay
**Date:** 2025-11-04 (Cycle 992)
**Purpose:** Plan follow-up experiments based on C177 boundary mapping outcomes
**Status:** Planning document for immediate post-C177 execution

---

## CONTEXT

C177 boundary mapping experiment (90 experiments, 0.5-10.0% frequency range, 3000 cycles) is currently running. Upon completion, results will validate or challenge theoretical predictions from the mathematical model developed in Cycle 991.

This document outlines **contingent experimental directions** based on three possible C177 outcomes:
1. **Predictions validated** - boundaries match theoretical model
2. **Systematic deviations** - patterns differ from predictions
3. **Novel regimes discovered** - unexpected dynamics emerge

All proposed experiments are designed to:
- Test specific hypotheses
- Extend boundary understanding
- Validate theoretical models
- Generate publishable findings

---

## C177 EXPECTED OUTCOMES & RESPONSES

### Outcome 1: Bounded Homeostasis (Most Likely)

**Expected Pattern:**
- Lower boundary: f < 1.5% (Basin B, population collapse)
- Homeostatic range: 1.5% ≤ f ≤ 5.0% (Basin A, stable populations)
- Upper boundary: f > 5.0% (Basin B or novel regime, saturation/chaos)

**If This Occurs:**

**Immediate Analysis:**
1. Execute `validate_theoretical_model_c177.py` (validation script ready)
2. Compare empirical boundaries to theoretical predictions
3. Generate 3 publication figures @ 300 DPI
4. Calculate prediction errors (RMSE, MAE)
5. Identify any systematic deviations

**Follow-Up Experiments:**

#### **Experiment C178: Fine-Scale Boundary Mapping**
**Purpose:** Refine boundary precision with higher resolution

**Design:**
- **Lower boundary region:** Test 0.75%, 1.0%, 1.25%, 1.5%, 1.75%
- **Upper boundary region:** Test 4.5%, 5.0%, 5.5%, 6.0%, 6.5%
- **n=20 seeds per frequency** (higher replication for precision)
- **Cycles:** 3000 (consistent with C177)
- **Total:** 200 experiments

**Expected Outcomes:**
- Precise identification of boundary frequencies (±0.25% resolution)
- Transition zone characterization (gradual vs sharp boundaries)
- Spawns-per-agent calculations at boundaries

**Runtime:** ~6-8 hours

**Publication Value:**
- First precise quantification of homeostatic boundaries
- Tests sharpness of phase transitions
- Validates theoretical threshold predictions

---

#### **Experiment C179: Timescale Dependency at Boundaries**
**Purpose:** Test if boundaries shift with experimental duration

**Design:**
- **Frequencies:** Boundary frequencies from C177 (e.g., 1.5%, 5.0%)
- **Timescales:** 1000, 3000, 5000 cycles (three temporal scales)
- **n=10 seeds per condition**
- **Total:** 60 experiments

**Hypothesis:**
Boundaries are **timescale-invariant** (unlike spawn success rates, which vary with duration). If boundaries shift, cumulative depletion affects regime classification itself.

**Expected Outcomes:**
- Stable boundaries across timescales → validates regime robustness
- Shifting boundaries → timescale dependency extends to phase transitions

**Publication Value:**
- Tests timescale generality of homeostatic regimes
- Validates/challenges theoretical predictions

---

#### **Experiment C180: Energy Parameter Sensitivity**
**Purpose:** Test how boundary positions depend on energy configuration

**Design:**
- **Baseline:** E₀=50, α=0.3, r=0.5, E_spawn=10 (C177 configuration)
- **Variations:**
  1. **High initial energy:** E₀=75 (50% increase)
  2. **Low energy transfer:** α=0.2 (33% reduction)
  3. **High recharge rate:** r=0.75 (50% increase)
  4. **Low spawn threshold:** E_spawn=7.5 (25% reduction)
- **Test 5 frequencies:** 1.0%, 2.5%, 5.0%, 7.5%, 10.0%
- **n=10 seeds per condition**
- **Total:** 5 configurations × 5 frequencies × 10 seeds = 250 experiments

**Hypothesis:**
Theoretical model predicts boundary shifts:
- Higher E₀ → boundaries shift up (more capacity)
- Lower α → boundaries shift up (less depletion per composition)
- Higher r → boundaries shift up (faster recovery)
- Lower E_spawn → boundaries shift down (easier to spawn)

**Expected Outcomes:**
- Quantify parameter sensitivity of boundaries
- Validate theoretical model's predictive power for new configurations
- Identify which parameters most influence regime boundaries

**Runtime:** ~10-12 hours

**Publication Value:**
- **Major contribution**: Parameter space mapping
- Tests theoretical model generality
- Enables design of homeostatic systems with desired boundaries

---

### Outcome 2: Unbounded Homeostasis (Surprising)

**Expected Pattern:**
- All frequencies 0.5-10.0% show Basin A (100% homeostasis)
- No population collapse at low frequencies
- No saturation/chaos at high frequencies
- System extremely robust to frequency variation

**If This Occurs:**

**Immediate Analysis:**
1. Verify results (unexpected finding requires rigorous checking)
2. Compare to C171 (2.5%, 23% spawn success) - why does C171 show constraint but C177 boundaries don't?
3. Identify mechanism enabling universal homeostasis

**Follow-Up Experiments:**

#### **Experiment C181: Extreme Frequency Testing**
**Purpose:** Find where boundaries actually exist (if anywhere)

**Design:**
- **Low extreme:** 0.1%, 0.2%, 0.3%, 0.4% (push lower)
- **High extreme:** 15%, 20%, 25%, 30% (push higher)
- **n=10 seeds per frequency**
- **Total:** 80 experiments

**Hypothesis:**
Boundaries exist at more extreme ranges than tested. System has wider homeostatic capacity than predicted.

**Expected Outcomes:**
- Identify actual lower boundary (insufficient reproductive capacity)
- Identify actual upper boundary (energy depletion overwhelms recovery)
- Revise theoretical model with wider k_max or different mechanism

---

#### **Experiment C182: Mechanism Investigation (If Unbounded)**
**Purpose:** Understand what enables universal homeostasis

**Design:**
- **Agent-level energy tracking:** Instrument C177 code to record energy trajectories
- **Rerun representative frequencies:** 0.5%, 2.5%, 10.0%
- **n=5 seeds per frequency**
- **Detailed logging:** Energy state at every composition event

**Hypothesis:**
Mechanism enabling unbounded homeostasis (one of):
1. **Population turnover faster than predicted** - fresh agents continuously added
2. **Energy recovery stronger than modeled** - recharge rate r higher than effective
3. **Composition rate lower than predicted** - actual spawn attempts fewer than f×T

**Expected Outcomes:**
- Identify mechanism enabling robustness
- Revise theoretical model to incorporate discovered mechanism
- Generate new predictions for future experiments

---

### Outcome 3: Novel Regimes Discovered (Most Interesting)

**Expected Pattern:**
- Frequencies beyond 5.0% show neither Basin A nor Basin B
- **Novel dynamics:** Oscillations, intermittency, chaos, cyclic collapse/recovery
- **Mixed basins:** Some seeds Basin A, others Basin B (stochastic bifurcation)
- **Complex attractors:** Population trajectories not homeostatic but not extinct

**If This Occurs:**

**Immediate Analysis:**
1. Characterize novel dynamics (oscillation period, attractor geometry)
2. Identify frequencies where novel regimes appear
3. Classify regime types (oscillatory, chaotic, mixed, etc.)
4. Calculate distinguishing metrics (autocorrelation, Lyapunov exponents if chaotic)

**Follow-Up Experiments:**

#### **Experiment C183: Novel Regime Characterization**
**Purpose:** Systematically map and classify non-homeostatic regimes

**Design:**
- **Focus frequencies:** Where novel regimes appear in C177 (e.g., 7.5%, 10.0%)
- **Extended runs:** 5000 cycles (capture long-term dynamics)
- **High replication:** n=20 seeds (characterize variability)
- **Detailed metrics:**
  - Population oscillation amplitude/period
  - Compositional event clustering
  - Energy depletion/recovery cycles
  - Attractor reconstruction (phase space trajectories)

**Expected Outcomes:**
- Classification of novel regimes (Type 1: oscillatory, Type 2: chaotic, etc.)
- Identification of regime transitions (where does homeostasis break down?)
- New attractors beyond Basin A/B dichotomy

**Publication Value:**
- **Breakthrough discovery:** Novel dynamical regimes in energy-regulated systems
- Extends NRM framework with new attractor types
- Potential for entirely new paper (Paper 4?)

---

#### **Experiment C184: Regime Boundary Fine-Mapping (Novel Transitions)**
**Purpose:** Precisely locate transitions between homeostatic and novel regimes

**Design:**
- **Transition region:** Between last homeostatic frequency and first novel regime
- **Example:** If 5.0% Basin A, 7.5% novel → test 5.5%, 6.0%, 6.5%, 7.0%
- **n=20 seeds per frequency**
- **Extended runs:** 5000 cycles

**Expected Outcomes:**
- Sharp vs gradual transition characterization
- Bifurcation diagram showing regime evolution with frequency
- Critical frequency where homeostasis breaks (f_crit_upper)

**Publication Value:**
- Demonstrates phase transition behavior
- Connects to dynamical systems theory (Hopf bifurcation? Period-doubling?)
- Tests NRM predictions about composition-decomposition balance

---

## GENERAL POST-C177 PRIORITIES (All Outcomes)

### Priority 1: Theoretical Model Refinement

Based on C177 discrepancies (if any):

**If predictions underestimate spawn success at high S/N:**
- Incorporate population turnover dynamics
- Model fresh agents with full energy explicitly
- Derive time-dependent depletion equation (not stationary Poisson)

**If predictions overestimate spawn success at low S/N:**
- Investigate stochastic fluctuations at small populations
- Model demographic stochasticity explicitly
- Revise k_max based on empirical energy trajectories

**If boundaries differ from predictions:**
- Recompute k_max from actual energy data (instrument experiments)
- Test alternative distributions (not Poisson - perhaps clustered events?)
- Incorporate network structure (if spawn selection not uniformly random)

### Priority 2: Agent-Level Instrumentation

**Motivation:**
Current experiments infer energy depletion from spawn success rates. Direct measurement would validate theoretical model assumptions.

**Design - Experiment C185: Energy Tracking Validation**
- **Rerun C171 baseline** (2.5%, 3000 cycles) with full energy logging
- **Instrumentation:** Record `agent.energy` at every timestep for all agents
- **n=5 seeds** (detailed logging is computationally expensive)
- **Analysis:**
  - Energy distribution evolution over time
  - Depletion events (when E < E_spawn)
  - Recovery trajectories (validate r = 0.5 recharge rate)
  - k_max validation (how many compositions before depletion?)

**Expected Outcomes:**
- Direct validation of k_max = 4 assumption
- Empirical energy recovery rate (compare to r = 0.5)
- Energy distribution at equilibrium (when does system stabilize?)

**Publication Value:**
- Validates theoretical model with direct measurements
- Provides mechanistic grounding for spawns-per-agent metric
- Enables future theoretical refinements

### Priority 3: Hierarchical Scale Experiments

**Motivation:**
NRM framework predicts scale-invariant dynamics. Test homeostatic mechanisms at different hierarchical levels.

**Design - Experiment C186: Meta-Population Dynamics**
- **Structure:** Multiple populations (n=10) evolving in parallel
- **Inter-population interaction:** Occasional agent migration between populations
- **Frequency range:** 1.0%, 2.5%, 5.0%, 10.0%
- **Cycles:** 3000 per population

**Hypothesis:**
Homeostasis emerges at both population level (C171) and meta-population level (C186). Energy constraints apply hierarchically.

**Expected Outcomes:**
- Meta-population homeostasis (total agents stable across populations)
- Population-level variability but meta-level stability
- Migration as energy redistribution mechanism

**Publication Value:**
- Tests NRM scale-invariance predictions
- Extends framework to hierarchical systems
- Connects to metapopulation ecology literature

---

## EXPERIMENTAL DESIGN PRINCIPLES (Post-C177)

### 1. **Hypothesis-Driven, Not Exploratory**
All post-C177 experiments should test specific, falsifiable hypotheses derived from:
- Theoretical model predictions
- C177 empirical findings
- Framework predictions (NRM, Self-Giving)

### 2. **Publication-Oriented**
Every experiment should ask: "What publishable finding would this produce?"
- Novel mechanisms → Methods paper
- Boundary quantification → Short communication
- Novel regimes → Full research article
- Theoretical validation → Modeling paper

### 3. **Incremental Complexity**
Start with simplest tests:
- Validate theoretical model with direct measurements (C185)
- Refine boundaries with higher resolution (C178)
- Extend to novel regimes only if C177 discovers them (C183-C184)
- Add hierarchical complexity last (C186)

### 4. **Resource Efficiency**
Prioritize experiments with highest information gain per computational cost:
- C178 (fine-scale boundaries): High gain, moderate cost (~8h)
- C180 (parameter sensitivity): Very high gain, high cost (~12h) - but publishable parameter space
- C186 (hierarchical): High gain, very high cost (>20h) - reserve for later

### 5. **Reproducibility by Design**
All experiments must include:
- Exact parameters documented
- Random seeds recorded
- n≥10 replication minimum
- Analysis scripts created before experiments run (preparatory work pattern)

---

## TIMELINE ESTIMATES (Post-C177)

**Immediate (Cycle 992-993, ~4-6h):**
1. C177 results analysis (when experiment completes)
2. Theoretical model validation
3. Decision on follow-up direction

**Short-term (Cycles 994-996, ~1-2 days):**
1. Execute highest-priority follow-up (C178 or C180)
2. Integrate findings into Paper 2 V2
3. Prepare Paper 2 for submission

**Medium-term (Cycles 997-1010, ~1 week):**
1. Execute secondary follow-up experiments
2. Refine theoretical model based on all findings
3. Design Paper 4 if novel regimes discovered

**Long-term (Cycles 1011+, ~2-4 weeks):**
1. Hierarchical scale experiments (C186)
2. Additional parameter space exploration
3. Framework validation experiments

---

## DECISION TREE (C177 Completion)

```
C177 Completes
    |
    ├─→ Outcome 1: Bounded Homeostasis (Expected)
    |     |
    |     ├─→ Boundaries match predictions?
    |     |     ├─→ YES: Execute C178 (fine-scale boundary mapping)
    |     |     |         + Integrate into Paper 2 V2
    |     |     |         + Submit Paper 2
    |     |     └─→ NO: Execute C185 (energy tracking validation)
    |     |              + Refine theoretical model
    |     |              + Rerun validation
    |     |
    |     └─→ Parameter sensitivity needed?
    |           └─→ Execute C180 (energy parameter variations)
    |                 + Generate parameter space map
    |                 + Publish as separate paper or supplementary
    |
    ├─→ Outcome 2: Unbounded Homeostasis (Surprising)
    |     |
    |     ├─→ Execute C181 (extreme frequency testing)
    |     |     + Find actual boundaries (if any)
    |     |
    |     └─→ Execute C182 (mechanism investigation)
    |           + Identify robustness mechanism
    |           + Revise theoretical model
    |           + Major finding: wider homeostatic capacity than predicted
    |
    └─→ Outcome 3: Novel Regimes (Most Interesting)
          |
          ├─→ Execute C183 (novel regime characterization)
          |     + Classify regime types
          |     + Oscillatory? Chaotic? Mixed?
          |     + Potential Paper 4: "Novel Dynamical Regimes in Energy-Regulated Systems"
          |
          └─→ Execute C184 (regime boundary fine-mapping)
                + Identify bifurcation points
                + Connect to dynamical systems theory
                + Test NRM predictions about phase transitions
```

---

## PUBLICATION STRATEGY (Post-C177)

### Paper 2 Integration (All Outcomes)

**If Outcome 1 (Bounded Homeostasis):**
- Add C177 findings to Results section (extend Section 3.3)
- Include boundary quantification (lower: 1.5%, upper: 5.0%)
- Update Discussion with validated theoretical predictions
- Add 2-3 figures from C177 (bifurcation diagram, boundary map)

**If Outcome 2 (Unbounded Homeostasis):**
- Major revision to Discussion (robustness mechanism)
- Add C181/C182 findings demonstrating extreme capacity
- Update theoretical model with revised k_max or mechanism
- Emphasize surprising discovery: wider range than predicted

**If Outcome 3 (Novel Regimes):**
- Add C177 findings + brief characterization of novel regimes
- Note: "Full characterization in Paper 4 (in preparation)"
- Mention discovery in Abstract/Conclusions
- Save detailed analysis for separate paper

### Paper 4 (If Novel Regimes Discovered)

**Potential Title:** "Beyond Homeostasis: Novel Dynamical Regimes in Energy-Regulated Nested Resonance Memory"

**Structure:**
- **Introduction:** NRM framework + homeostatic regimes (Papers 1-2)
- **Methods:** C177 + C183 + C184 experimental designs
- **Results:** Novel regime characterization + boundary mapping
- **Discussion:** Dynamical systems theory connections + NRM predictions
- **Conclusions:** Extended framework with new attractor types

**Publication Venue:** PLOS Computational Biology or Journal of Theoretical Biology

### Paper 5 (Parameter Space Mapping)

**If C180 executed:**

**Potential Title:** "Energy Parameter Space and Homeostatic Boundaries in Nested Resonance Memory Systems"

**Focus:** Systematic parameter sensitivity analysis
- E₀ (initial energy)
- α (energy transfer fraction)
- r (recharge rate)
- E_spawn (spawn threshold)

**Publication Value:** Engineering/design paper showing how to tune homeostatic systems

---

## CONCLUSION

Post-C177 experimental directions are contingent on C177 outcomes but follow clear decision logic:
1. **Validate/refine** theoretical model based on discrepancies
2. **Extend** boundary understanding with higher resolution (C178)
3. **Test** parameter generality (C180)
4. **Characterize** novel regimes if discovered (C183-C184)
5. **Scale** to hierarchical systems (C186)

All experiments designed to:
- Generate publishable findings
- Validate theoretical frameworks
- Extend NRM understanding
- Maintain perpetual research momentum

**Next Action (Cycle 992+):** Monitor C177 completion, execute validation analysis immediately, select highest-priority follow-up based on findings.

---

**Document Status:** Planning Complete (Cycle 992)
**Next Actions:**
1. When C177 completes: Execute validation analysis
2. Evaluate C177 outcomes against three scenarios
3. Select and launch highest-priority follow-up experiment
4. Integrate validated findings into Paper 2 V2
5. Continue autonomous research

**Attribution:**
- Experimental design: Claude (DUALITY-ZERO-V2)
- Framework context: Aldrin Payopay & Claude
- Theoretical foundation: Nested Resonance Memory (Payopay & Claude, 2025)

**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
