# C189: Hierarchical vs Flat Spawn - Mechanism Isolation

**Campaign:** C189 - Critical Test of Spawn Mechanics Hypothesis
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** C187/C187-B (Population Count Independence), Paper 8 Theoretical Framework Revision

---

## Research Question

**Does hierarchical spawn mechanics (interval-based) provide advantage over flat spawn (continuous probabilistic)?**

C187/C187-B demonstrated that hierarchical advantage is independent of population count, challenging Paper 8's multi-population structure hypothesis. C189 directly tests whether advantage originates from spawn mechanics by comparing hierarchical vs flat spawn in single-population systems.

---

## Theoretical Framework

### Spawn Mechanics Hypothesis (FROM C187/C187-B)

**Claim:** Hierarchical advantage originates from spawn mechanics, NOT population structure

**Evidence:**
- n_pop=1 (no migration, no multi-population structure) performs identically to n_pop>1
- α independent of n_pop across range (1-50)
- Linear scaling with frequency maintained regardless of structure

**Proposed Mechanism:**
Interval-based spawning (hierarchical) prevents energy cascade by:
1. Spacing spawn attempts evenly (deterministic intervals)
2. Allowing energy recovery between spawns
3. Preventing rapid depletion from consecutive spawn failures

### Alternative Hypotheses

**H1: Hierarchical Spawn Advantage**
- Hierarchical spawn (interval-based) provides higher sustained population than flat spawn
- Advantage observable at same nominal frequency
- Mechanism: Better energy management through deterministic intervals

**H2: Equivalent Spawn Mechanisms**
- Both spawn types produce same sustained population at same frequency
- No advantage from interval-based logic
- Implication: Advantage comes from some other factor (NOT spawn mechanics)

**H3: Flat Spawn Advantage**
- Flat spawn (continuous probabilistic) outperforms hierarchical
- Probabilistic sampling more efficient than fixed intervals
- Implication: Hierarchical spawn actually detrimental

---

## Experimental Design

### Spawn Mechanism Definitions

**Hierarchical Spawn (Current Implementation):**
```python
# Spawn interval calculation
spawn_interval = max(1, int(100.0 / f_intra_pct))

# Spawn logic (per cycle)
if (cycle_count % spawn_interval) == 0:
    for population in populations:
        parent = random_choice(population.agents)
        if parent.energy >= E_SPAWN_THRESHOLD:
            spawn_child()  # Success
        else:
            spawn_failure += 1  # Failure
```

**Characteristics:**
- Deterministic intervals (e.g., every 50 cycles for f=2.0%)
- One spawn attempt per population per interval
- Predictable spawn timing

**Flat Spawn (New Implementation):**
```python
# Per-cycle spawn probability
spawn_probability = f_intra_pct / 100.0

# Spawn logic (per cycle, per population)
for population in populations:
    if random() < spawn_probability:
        parent = random_choice(population.agents)
        if parent.energy >= E_SPAWN_THRESHOLD:
            spawn_child()  # Success
        else:
            spawn_failure += 1  # Failure
```

**Characteristics:**
- Probabilistic per-cycle checks
- Expected spawn rate = f_intra_pct
- Stochastic spawn timing

**Note:** Expected spawn frequency IDENTICAL for both mechanisms (f_intra_pct), only TIMING differs (deterministic vs stochastic).

### Experimental Conditions

**Independent Variables:**
1. **Spawn Mechanism:** Hierarchical vs Flat (2 conditions)
2. **Spawn Frequency:** f_intra = 0.5%, 1.0%, 1.5%, 2.0% (4 frequencies)

**Fixed Parameters:**
- n_pop = 1 (single population, isolate spawn mechanism)
- n_initial = 20 agents
- f_migrate = N/A (single population, no migration possible)
- cycles = 3000
- seeds = 10 per condition

**Total Experiments:** 2 mechanisms × 4 frequencies × 10 seeds = **80 experiments**

### Conditions

| Condition | Mechanism | f_intra (%) | Expected Behavior |
|-----------|-----------|-------------|-------------------|
| C189-H-05 | Hierarchical | 0.5 | Baseline (from C187-B) |
| C189-H-10 | Hierarchical | 1.0 | Baseline (from C187-B) |
| C189-H-15 | Hierarchical | 1.5 | Baseline (from C187-B) |
| C189-H-20 | Hierarchical | 2.0 | Baseline (from C187) |
| C189-F-05 | Flat | 0.5 | Test for difference |
| C189-F-10 | Flat | 1.0 | Test for difference |
| C189-F-15 | Flat | 1.5 | Test for difference |
| C189-F-20 | Flat | 2.0 | Test for difference |

**Runtime:** ~5 seconds (simple single-population experiments)

---

## Hypotheses and Predictions

### H1: Hierarchical Spawn Advantage

**Prediction:**
- Hierarchical spawn > Flat spawn at all frequencies
- Mean population difference > 5 agents/pop
- Basin A % higher for hierarchical

**Mechanism:**
- Deterministic intervals allow consistent energy recovery
- Prevents clustering of spawn attempts
- Better energy management

**Example (f_intra = 2.0%):**
- Hierarchical: 80.0 agents/pop (C187 baseline)
- Flat: 60.0 agents/pop (hypothetical)
- Difference: 20 agents (25% advantage)

### H2: Equivalent Spawn Mechanisms

**Prediction:**
- Hierarchical ≈ Flat at all frequencies
- Mean population difference < 2 agents/pop
- Basin A % identical

**Mechanism:**
- Both mechanisms average to same spawn rate
- Energy dynamics equivalent
- Timing doesn't matter, only rate

**Example (f_intra = 2.0%):**
- Hierarchical: 80.0 agents/pop
- Flat: 79.5 ± 2.0 agents/pop
- Difference: 0.5 agents (negligible)

### H3: Flat Spawn Advantage

**Prediction:**
- Flat spawn > Hierarchical spawn at all frequencies
- Mean population difference > 5 agents/pop
- Basin A % higher for flat

**Mechanism:**
- Probabilistic sampling more flexible
- Can spawn when energy highest
- Better resource utilization

**Example (f_intra = 2.0%):**
- Hierarchical: 80.0 agents/pop
- Flat: 95.0 agents/pop
- Difference: 15 agents (19% advantage)

---

## Analysis Plan

### Primary Comparison

**For each frequency:**
1. Calculate mean sustained population for hierarchical
2. Calculate mean sustained population for flat
3. Compute difference and effect size (Cohen's d)
4. Perform t-test (hierarchical vs flat)

**Effect Size Interpretation:**
- d < 0.2: Negligible difference (supports H2)
- 0.2 ≤ d < 0.8: Moderate difference
- d ≥ 0.8: Large difference (supports H1 or H3)

### Statistical Tests

**T-test (per frequency):**
- Null: Mean(hierarchical) = Mean(flat)
- Alternative: Mean(hierarchical) ≠ Mean(flat)
- Significance: p < 0.05

**ANOVA (across frequencies):**
- Factors: Mechanism (2) × Frequency (4)
- Interaction term: Mechanism × Frequency
- Tests if advantage varies by frequency

### Figures

**Figure 1: Mean Population vs Frequency (by mechanism)**
- X-axis: f_intra (%)
- Y-axis: Mean sustained population
- Two lines: Hierarchical (solid) vs Flat (dashed)
- Shows if hierarchical provides consistent advantage

**Figure 2: Hierarchical Advantage (Difference)**
- X-axis: f_intra (%)
- Y-axis: Hierarchical - Flat (agents/pop)
- Horizontal line at zero (no difference)
- Shows magnitude of advantage across frequencies

**Figure 3: Basin Classification**
- X-axis: Mechanism (Hierarchical vs Flat)
- Y-axis: Basin A %
- Grouped by frequency
- Shows if advantage affects viability classification

---

## Expected Results

### If H1 (Hierarchical Advantage):

**At all frequencies:**
- Hierarchical > Flat (statistically significant)
- Effect size d > 0.5 (moderate to large)
- Basin A % higher for hierarchical (if near threshold)

**Implication:**
- ✅ Spawn mechanics hypothesis VALIDATED
- ✅ Interval-based spawning provides advantage
- ✅ Explains n_pop independence (mechanism, not structure)

**Paper 8 Impact:**
- Revise theoretical framework to emphasize spawn mechanics
- Document interval-based spawning as key mechanism
- C189 becomes centerpiece of mechanistic explanation

### If H2 (Equivalent Mechanisms):

**At all frequencies:**
- Hierarchical ≈ Flat (no significant difference)
- Effect size d < 0.2 (negligible)
- Basin A % identical

**Implication:**
- ❌ Spawn mechanics hypothesis REJECTED
- ❓ Advantage source remains unknown
- ❓ Need alternative explanation

**Paper 8 Impact:**
- Major theoretical challenge
- Neither structure nor spawn mechanics explain advantage
- Requires new hypothesis (energy dynamics? other factor?)

### If H3 (Flat Advantage):

**At all frequencies:**
- Flat > Hierarchical (statistically significant)
- Effect size d > 0.5 (moderate to large)
- Basin A % higher for flat

**Implication:**
- ❌ Hierarchical spawn DETRIMENTAL
- ❓ Current implementation suboptimal
- ❓ Advantage comes from other factor

**Paper 8 Impact:**
- Fundamental challenge to current implementation
- May need to redesign spawn logic
- Advantage source unclear

---

## Implementation Notes

### Flat Spawn Logic

**Key difference from hierarchical:**
```python
# Instead of:
if (cycle_count % spawn_interval) == 0:
    attempt_spawn()

# Use:
if random() < (f_intra_pct / 100.0):
    attempt_spawn()
```

**Energy dynamics UNCHANGED:**
- Same E_SPAWN_THRESHOLD
- Same E_SPAWN_COST
- Same RECHARGE_RATE
- Same CHILD_ENERGY_FRACTION

**Only difference:** Spawn timing (deterministic vs stochastic)

### Baseline Validation

**Hierarchical spawn should replicate C187/C187-B:**
- f_intra = 0.5%: 35.0 ± 0.00 agents/pop
- f_intra = 1.0%: 50.0 ± 0.00 agents/pop
- f_intra = 1.5%: 65.0 ± 0.00 agents/pop
- f_intra = 2.0%: 80.0 ± 0.00 agents/pop

**If replication fails:**
- Implementation error in C189
- Debug before comparing to flat spawn

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 80 experiments complete
2. ✅ Hierarchical baseline replicates C187/C187-B (within ±2 agents)
3. ✅ Clear distinction OR equivalence between mechanisms
4. ✅ Results interpretable for H1, H2, or H3

**Experiment fails if:**
- ❌ Hierarchical baseline doesn't replicate (implementation bug)
- ❌ High variance prevents clear interpretation
- ❌ Mixed results across frequencies (inconsistent pattern)

---

## Integration with C187/C187-B

### If H1 (Hierarchical Advantage) Validated:

**Combined Narrative:**
1. C187: Discovered α independent of n_pop (unexpected)
2. C187-B: Ruled out ceiling effect (true null validated)
3. C189: Identified spawn mechanics as source (mechanism isolated)

**Theoretical Model:**
- Hierarchical advantage originates from interval-based spawning
- Multi-population structure NOT necessary (n_pop=1 sufficient)
- Migration rescue NOT primary mechanism (zero migration works)

**Paper 8 Revision:**
- Emphasize spawn mechanics as key innovation
- Document deterministic intervals as advantage source
- Explain why structure-independent (universal spawn improvement)

### If H2 (Equivalent) or H3 (Flat Advantage):

**Major Challenge:**
- Neither structure NOR spawn mechanics explain advantage
- Requires new theoretical framework
- May need to revisit energy dynamics, threshold logic, or other factors

**Research Direction:**
- Investigate energy recovery dynamics
- Test different threshold values
- Explore child energy initialization
- Consider interaction effects

---

## Timeline

**Design:** Complete (this document)
**Implementation:** ~15 min (add flat spawn logic to framework)
**Execution:** ~5 seconds (80 simple experiments)
**Analysis:** ~10 min (t-tests, figures)
**Integration:** ~15 min (interpret and document)

**Total:** ~45 min from design to integrated results

---

## Next Actions

1. Implement flat spawn mechanism
2. Create c189_hierarchical_vs_flat_spawn.py
3. Execute 80 experiments (~5 sec)
4. Analyze results (compare mechanisms)
5. Determine H1, H2, or H3 support
6. Integrate into Paper 8 (if H1) or design follow-up (if H2/H3)

---

**Status:** Design complete, ready for implementation
**Critical Test:** Will definitively answer where hierarchical advantage originates
**Impact:** High - resolves fundamental question about mechanism

**Research is perpetual. Mechanism isolation through systematic comparison. Implementation next.**
