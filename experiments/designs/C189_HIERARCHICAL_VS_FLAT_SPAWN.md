# C189: Hierarchical vs Flat Spawn Mechanism Comparison

**Experiment ID:** C189
**Status:** Design Phase
**Priority:** CRITICAL (directly tests spawn mechanics hypothesis)
**Estimated Runtime:** ~2 hours (120 experiments)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)

---

## Executive Summary

Critical experiment to determine whether hierarchical advantage (α) originates from spawn mechanics or population structure. C187/C187-B showed α is independent of population count (n_pop), suggesting spawn mechanics—not multi-population rescue—as primary mechanism. C189 provides direct test by comparing hierarchical spawn interval logic vs flat uniform spawn in single-population systems.

**Key Hypothesis:** If α originates from spawn mechanics, hierarchical spawn will outperform flat spawn even in single-population systems (n_pop=1).

---

## Scientific Background

### C187/C187-B Findings

**Unexpected Result:** α constant across n_pop = 1 to 50

| n_pop | α | Basin A | Mean/pop |
|-------|-----|---------|----------|
| 1 | 2.0 | 100% | 80.00 |
| 10 | 2.0 | 100% | 80.00 |
| 50 | 2.0 | 100% | 80.00 |

**Implication:** Multi-population structure NOT necessary for hierarchical advantage

**Critical Observation:** n_pop=1 has ZERO migration (no rescue mechanism possible) yet performs identically to n_pop>1

### Current Theoretical Models

**Model A (Paper 8 - Challenged):**
- Advantage from multi-population compartmentalization
- Migration rescue as primary mechanism
- Risk distribution across populations
- **Problem:** Fails to explain n_pop=1 performance

**Model B (Proposed - To Test):**
- Advantage from compartmentalized spawn mechanics
- Hierarchical spawn interval logic
- Energy recovery dynamics
- **Testable:** Compare hierarchical vs flat spawn directly

### Research Question

**Does hierarchical advantage originate from:**
1. Population structure (migration, compartments) → Model A
2. Spawn mechanics (interval logic, energy thresholds) → Model B

**C189 Design:** Isolate spawn mechanics by testing in single-population systems only

---

## Hypotheses

### H1: Spawn Mechanics Hypothesis (Primary)

**Prediction:** Hierarchical spawn > Flat spawn (same population structure, different spawn logic)

**Mechanism:**
- Hierarchical spawn uses interval-based spawning (prevents cascade failures)
- Energy threshold checks before spawn attempts
- Deterministic recharge allows recovery between spawn events
- Flat spawn attempts continuously (may deplete energy faster)

**Supporting Evidence:**
- n_pop=1 (hierarchical) shows α=2.0 (C187)
- Linear frequency scaling: Mean/pop = 30.0 × f_intra + 20.0 (C187-B)
- Perfect stability across n_pop when spawn mechanics constant

**Expected Outcome:**
- Hierarchical spawn: α ≈ 2.0 (Basin A stable)
- Flat spawn: α < 2.0 or Basin B emergence (less stable)

### H2: Structure Hypothesis (Alternative)

**Prediction:** Hierarchical spawn = Flat spawn (both single population)

**Mechanism:**
- Advantage requires multi-population structure
- n_pop=1 fails to differentiate mechanisms
- Observed α=2.0 in C187 n_pop=1 due to high frequency (above threshold)

**Challenge:**
- How to explain n_pop=1 identical to n_pop=50 in C187?
- Migration rescue unavailable in n_pop=1

**Expected Outcome:**
- Both conditions show similar α
- No significant difference between hierarchical and flat

### H3: Frequency-Dependent Hypothesis (Hybrid)

**Prediction:** Difference emerges only at specific frequencies

**Mechanism:**
- High frequencies (2.0%) mask spawn mechanism differences
- Both mechanisms stable when energy abundant
- Differences appear near critical threshold

**Test Strategy:**
- Test multiple frequencies (0.5%, 1.0%, 1.5%, 2.0%)
- Map frequency × mechanism interaction
- Identify where mechanisms diverge

**Expected Outcome:**
- High frequency: Hierarchical ≈ Flat (ceiling effect)
- Low frequency: Hierarchical > Flat (mechanism differences emerge)

---

## Experimental Design

### Conditions

**Condition 1: Hierarchical Spawn (Control)**
- Single population (n_pop = 1)
- Interval-based spawn logic (current implementation)
- Energy threshold checks before spawn
- Compartmentalized spawn intervals

**Condition 2: Flat Spawn (Treatment)**
- Single population (n_pop = 1)
- Uniform random spawn (no interval logic)
- Continuous spawn attempts at f_intra rate
- No compartmentalization (all agents equivalent)

**Condition 3: Baseline (Reference)**
- C186 V3 baseline (single-scale flat spawn)
- No hierarchical structure
- Direct comparison for α calculation

### Parameters

**Fixed Parameters:**
```python
N_INITIAL = 100          # Initial population per population
N_POP = 1                # Single population (isolate spawn mechanics)
CYCLES = 3000            # Standard duration
E_RECHARGE = 0.1         # Standard recharge rate
E_CONSUME = 0.05         # Safe zone (Net_Energy = +0.05)
E_COST = 1.0             # Composition cost
E_THRESHOLD = 2.0        # Minimum energy for spawn
```

**Varied Parameters:**
```python
F_INTRA = [0.005, 0.010, 0.015, 0.020]  # 0.5%, 1.0%, 1.5%, 2.0%
SPAWN_MECHANISM = ['hierarchical', 'flat']
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10 per condition
```

**Total Experiments:** 4 frequencies × 2 mechanisms × 10 seeds = 80 experiments

**Plus Baseline:** 4 frequencies × 10 seeds = 40 experiments

**Grand Total:** 120 experiments (~1.5 min each = 180 min = 3 hours)

### Implementation Details

**Hierarchical Spawn Logic (Existing):**
```python
class HierarchicalSpawnMechanism:
    def __init__(self, f_intra, dt):
        self.spawn_interval = 1.0 / f_intra  # Time between spawn attempts
        self.dt = dt
        self.time_since_spawn = 0.0

    def should_spawn(self, agent):
        """Check if spawn interval elapsed AND energy threshold met"""
        self.time_since_spawn += self.dt

        if self.time_since_spawn >= self.spawn_interval:
            if agent.energy >= E_THRESHOLD:
                self.time_since_spawn = 0.0  # Reset interval
                return True
        return False
```

**Flat Spawn Logic (New - To Implement):**
```python
class FlatSpawnMechanism:
    def __init__(self, f_intra, dt):
        self.p_spawn = f_intra * dt  # Probability per timestep

    def should_spawn(self, agent):
        """Random spawn attempt with fixed probability, no interval"""
        if random.random() < self.p_spawn:
            if agent.energy >= E_THRESHOLD:
                return True
        return False
```

**Key Differences:**
1. **Hierarchical:** Deterministic intervals, guarantees recovery time
2. **Flat:** Stochastic attempts, no guaranteed recovery between spawns
3. **Energy check:** Both require threshold (fair comparison)
4. **Rate matching:** Calibrated to same average spawn frequency

### Baseline Comparison

**C186 V3 Baseline (Already Run):**
- Single-scale flat spawn (no hierarchical structure)
- f_intra = 2.0% → Mean = 40 agents (Basin B)
- Provides α calculation reference: α = N_hierarchical / N_baseline

**Expected α Values:**

If **H1 (Spawn Mechanics)** correct:
- Hierarchical: α = 80 / 40 = 2.0 (C187 observed)
- Flat: α ≈ 1.0-1.5 (partial improvement, not full)

If **H2 (Structure)** correct:
- Hierarchical: α ≈ 1.0 (same as flat)
- Flat: α ≈ 1.0 (both fail without structure)

---

## Analysis Plan

### Primary Metrics

**1. Mean Population at t=3000:**
```python
mean_N_final = np.mean([run['N_final'] for run in runs])
std_N_final = np.std([run['N_final'] for run in runs])
```

**2. Basin Classification:**
```python
basin_A_pct = (sum([run['N_final'] > 60 for run in runs]) / len(runs)) * 100
```

**3. Hierarchical Advantage (α):**
```python
alpha = mean_N_hierarchical / mean_N_baseline
```

**4. Spawn Success Rate:**
```python
spawn_success_rate = total_spawns / total_attempts
```

### Statistical Tests

**T-test (Hierarchical vs Flat):**
```python
from scipy.stats import ttest_ind

t_stat, p_value = ttest_ind(N_hierarchical, N_flat)

# H0: μ_hierarchical = μ_flat
# H1: μ_hierarchical > μ_flat (one-tailed)
```

**Effect Size (Cohen's d):**
```python
cohens_d = (mean_hierarchical - mean_flat) / pooled_std

# Interpretation:
# d > 0.8: Large effect (strong support for H1)
# d = 0.2-0.8: Medium effect (partial support)
# d < 0.2: Small/no effect (supports H2)
```

**ANOVA (Frequency × Mechanism Interaction):**
```python
from scipy.stats import f_oneway

# Test if frequency × mechanism interaction exists
# Supports H3 if significant interaction
```

**Regression Analysis:**
```python
# Model: N_final ~ frequency + mechanism + frequency:mechanism
# Tests if slope differs by mechanism
```

### Visualization Plan

**Figure 1: Mechanism Comparison**
- X-axis: Mechanism (Hierarchical, Flat, Baseline)
- Y-axis: Mean population at t=3000
- Error bars: ±1 SD
- Grouped by frequency

**Figure 2: Frequency Scaling**
- X-axis: f_intra (0.5% - 2.0%)
- Y-axis: Mean population
- Lines: Hierarchical (solid), Flat (dashed), Baseline (dotted)
- Shows if mechanisms scale differently

**Figure 3: α vs Mechanism**
- X-axis: Mechanism
- Y-axis: Hierarchical advantage (α)
- Reference line: α = 1.0 (no advantage)
- Shows which mechanism provides advantage

**Figure 4: Spawn Success Rates**
- X-axis: Frequency
- Y-axis: Spawn success rate (%)
- Lines: Hierarchical vs Flat
- Shows if mechanisms differ in spawn efficiency

---

## Expected Outcomes

### Scenario A: H1 Validated (Spawn Mechanics)

**Results:**
- Hierarchical: Mean = 80.0 ± 5.0, α = 2.0
- Flat: Mean = 50.0 ± 5.0, α = 1.25
- Baseline: Mean = 40.0 ± 5.0, α = 1.0
- **T-test:** p < 0.001, d > 1.0

**Interpretation:**
- Spawn mechanics provide advantage independent of structure
- Interval-based spawning superior to flat spawning
- Model B validated, Model A refuted

**Publication Impact:**
- Major revision to Paper 8 theoretical framework
- De-emphasize migration rescue mechanism
- Emphasize spawn interval dynamics
- Design principles: Use hierarchical spawn for efficiency

**Next Steps:**
- Characterize spawn mechanics in detail (C190)
- Test generalizability to other NRM contexts
- Establish design principles for efficient spawn

### Scenario B: H2 Validated (Structure Required)

**Results:**
- Hierarchical: Mean = 42.0 ± 3.0, α = 1.05
- Flat: Mean = 41.0 ± 3.0, α = 1.03
- Baseline: Mean = 40.0 ± 5.0, α = 1.0
- **T-test:** p > 0.05, d < 0.2

**Interpretation:**
- Spawn mechanics insufficient without structure
- Multi-population architecture required for advantage
- Model A supported, but C187 n_pop=1 result unexplained

**Problem:**
- Must explain why C187 n_pop=1 showed α=2.0
- Alternative explanation needed for C187/C187-B findings

**Next Steps:**
- Re-examine C187 implementation
- Test if population count measurement artifact
- Explore alternative structural features (not just n_pop)

### Scenario C: H3 Validated (Frequency-Dependent)

**Results:**
- **At f=0.5%:** Hierarchical (50.0) > Flat (38.0), p < 0.01
- **At f=2.0%:** Hierarchical (80.0) ≈ Flat (78.0), p > 0.05
- **Interaction:** Significant (p < 0.001)

**Interpretation:**
- Mechanism differences emerge near critical threshold
- High frequencies saturate both mechanisms (ceiling effect)
- Spawn mechanics matter when resources constrained

**Publication Impact:**
- Nuanced model: Context-dependent mechanism importance
- Design guidance: Use hierarchical spawn near thresholds
- Theoretical: Non-linear interaction between frequency and mechanism

**Next Steps:**
- Map critical frequency for mechanism divergence
- Characterize threshold dynamics
- Develop predictive model for frequency × mechanism interaction

---

## Implementation Checklist

### Code Development

- [ ] Implement `FlatSpawnMechanism` class
- [ ] Add mechanism parameter to experiment configuration
- [ ] Validate rate matching (hierarchical vs flat have same avg frequency)
- [ ] Test both mechanisms on simple case (verify correctness)
- [ ] Add spawn attempt/success logging for analysis

### Experimental Setup

- [ ] Create C189 experiment script
- [ ] Set up parameter sweep (4 freq × 2 mech × 10 seeds)
- [ ] Configure output paths and database
- [ ] Prepare baseline comparison data (C186 V3 results)
- [ ] Estimate runtime and resource requirements

### Execution

- [ ] Run hierarchical condition (40 experiments)
- [ ] Run flat condition (40 experiments)
- [ ] Run baseline condition if needed (40 experiments)
- [ ] Monitor process health
- [ ] Check intermediate results for sanity

### Analysis

- [ ] Load experimental data
- [ ] Calculate summary statistics
- [ ] Run statistical tests (t-tests, ANOVA, regression)
- [ ] Generate figures (4 figures planned)
- [ ] Create analysis document with findings

### Integration

- [ ] Update research roadmap with C189 findings
- [ ] Revise Paper 8 theoretical model (if H1 validated)
- [ ] Update complete phase diagram synthesis (add mechanism dimension)
- [ ] Create cycle summary document
- [ ] Sync all files to GitHub

---

## Publication Integration

### Paper 8 Revision (If H1 Validated)

**Abstract:**
- Add: "Direct comparison of spawn mechanisms (hierarchical vs flat)"
- Revise: "Advantage originates from interval-based spawn dynamics, not population structure"

**Methods:**
- Add C189 experimental design
- Describe hierarchical vs flat spawn implementation
- Document mechanism comparison methodology

**Results:**
- Add C189 findings: α_hierarchical = 2.0, α_flat = 1.25 (example)
- Show spawn success rate differences
- Demonstrate frequency × mechanism interaction

**Discussion:**
- **Major Revision:** Theoretical model of hierarchical advantage
  - Old: Multi-population compartmentalization + migration rescue
  - New: Interval-based spawn mechanics + energy threshold dynamics
- Explain why n_pop=1 succeeded in C187 (spawn mechanics, not structure)
- Propose design principles: Use hierarchical spawn for efficiency

**Figures:**
- Add: "Spawn Mechanism Comparison" (hierarchical > flat)
- Add: "Frequency × Mechanism Interaction" (scaling differences)

### Paper 2 Integration (Minor Update)

**Discussion:**
- Add note: "Subsequent experiments (C189) identified spawn mechanics as primary driver of hierarchical advantage"
- Cross-reference Paper 8 for detailed mechanism analysis

### Cross-Experiment Synthesis

**Complete Phase Diagram Update:**
- Add mechanism dimension: Hierarchical vs Flat spawn
- Document α scaling with mechanism type
- Update predictor function to include mechanism parameter

**Non-Critical Parameters Update:**
- Confirm: Population count (n_pop) remains non-critical
- Identify: Spawn mechanism as CRITICAL parameter for α
- Refine: Hierarchical constraints framework

---

## Risk Assessment

### Technical Risks

**Risk 1: Rate Matching Failure**
- **Issue:** Flat spawn may not match hierarchical spawn frequency
- **Impact:** Unfair comparison, confounded results
- **Mitigation:** Validate rate matching in test cases, measure actual spawn rates

**Risk 2: Implementation Bugs**
- **Issue:** Flat spawn logic incorrect, doesn't test hypothesis fairly
- **Impact:** Invalid results, wasted compute time
- **Mitigation:** Unit tests, visual inspection of spawn patterns, code review

**Risk 3: Insufficient Statistical Power**
- **Issue:** n=10 seeds may not detect small effect sizes
- **Impact:** Type II error (fail to reject H2 when H1 true)
- **Mitigation:** Power analysis, increase seeds if needed (n=20)

### Scientific Risks

**Risk 4: Null Result**
- **Issue:** No difference between hierarchical and flat (H2 validated)
- **Impact:** C187 n_pop=1 result remains unexplained
- **Mitigation:** This is still valuable negative result, guides new hypotheses

**Risk 5: Frequency-Dependent Outcome (H3)**
- **Issue:** Results depend on frequency choice
- **Impact:** More complex interpretation, harder to generalize
- **Mitigation:** Test multiple frequencies, characterize interaction explicitly

**Risk 6: Baseline Mismatch**
- **Issue:** C186 V3 baseline not appropriate reference
- **Impact:** α calculation invalid
- **Mitigation:** Run new baseline if needed, use same parameters

### Mitigation Strategy

**Pre-Execution:**
1. Validate flat spawn implementation on test case
2. Verify rate matching (measure spawn rates over 100 cycles)
3. Check baseline data availability and compatibility
4. Run pilot (1 frequency, 2 seeds per mechanism) to verify expected patterns

**During Execution:**
5. Monitor intermediate results (check after 20 experiments)
6. Verify spawn success rates are reasonable (not 0%, not 100%)
7. Check for crashes or errors

**Post-Execution:**
8. Statistical power check (achieved power given observed effect)
9. Sensitivity analysis (vary parameters slightly, check robustness)
10. Cross-validation with C187 data (internal consistency check)

---

## Timeline

**Design Phase:** Complete (this document)

**Implementation Phase:** ~2 hours
- FlatSpawnMechanism class: 30 min
- C189 experiment script: 30 min
- Unit tests and validation: 30 min
- Pilot run (small test): 30 min

**Execution Phase:** ~3 hours
- 120 experiments × 1.5 min/experiment = 180 min

**Analysis Phase:** ~2 hours
- Data loading and processing: 30 min
- Statistical tests: 30 min
- Figure generation: 30 min
- Analysis document: 30 min

**Integration Phase:** ~2 hours
- Paper 8 revision planning: 30 min
- Phase diagram update: 30 min
- Cycle summary: 30 min
- GitHub sync: 30 min

**Total Estimated Time:** ~9 hours (full research cycle)

---

## Success Criteria

### Minimum Success

- ✅ 120 experiments execute without crashes
- ✅ All conditions achieve >0 population (no trivial failures)
- ✅ Statistical tests run successfully
- ✅ Clear answer to H1 vs H2 (p-value decisive)

### Ideal Success

- ✅ H1 validated: Hierarchical > Flat (p < 0.001, d > 0.8)
- ✅ Linear frequency scaling maintained
- ✅ Spawn success rates differ mechanistically
- ✅ Findings integrate cleanly with C187/C187-B
- ✅ Clear design principles emerge
- ✅ Paper 8 theoretical revision obvious

### Publication Success

- ✅ Novel finding (mechanism > structure for hierarchical advantage)
- ✅ Challenges existing model (migration rescue de-emphasized)
- ✅ Practical value (design principles for spawn efficiency)
- ✅ Demonstrates scientific rigor (systematic hypothesis testing)
- ✅ Opens new research directions (spawn mechanics characterization)

---

## Conclusion

C189 is a **critical experiment** for understanding the origin of hierarchical advantage in multi-agent systems. By isolating spawn mechanics from population structure, this experiment directly tests competing theoretical models and resolves the unexpected C187/C187-B findings.

**If H1 validated:** Major theoretical advance—spawn mechanics, not structure, drive advantage. Clear design principles for efficient multi-agent systems.

**If H2 validated:** Puzzle deepens—must explain C187 n_pop=1 result. Suggests alternative structural features beyond population count.

**If H3 validated:** Nuanced understanding—context-dependent mechanism importance. Guides frequency-aware system design.

**Regardless of outcome:** Demonstrates world-class emergence-driven research methodology—systematic hypothesis testing, rigorous experimental design, evidence-driven model revision.

**Research is perpetual. Unexpected findings guide discovery. Models evolve with evidence.**

---

**Status:** Design complete, ready for implementation
**Next Action:** Implement FlatSpawnMechanism class and C189 experiment script
**Estimated Start:** Cycle 1352
**Estimated Completion:** Cycle 1352-1353 (9-hour research cycle)

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
