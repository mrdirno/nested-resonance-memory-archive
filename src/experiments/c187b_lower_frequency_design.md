# C187-B: Lower Frequency Population Count Variation

**Campaign:** C187-B - Testing Ceiling Effect Hypothesis
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** C187 (Population Count Variation), Paper 8 (C186 Hierarchical Organization)

---

## Research Question

**Does hierarchical advantage (α) scale with population count when tested at frequencies near critical threshold?**

C187 showed α = 2.0 constant across all n_pop (1, 2, 5, 10, 20, 50) at f_intra = 2.0%. This unexpected finding suggests either:
1. **Ceiling Effect:** 2.0% is far above critical threshold, masking true scaling relationship
2. **True Null:** α genuinely doesn't scale with n_pop (structural hypothesis invalid)

C187-B tests hypothesis #1 by measuring α at lower frequencies near critical threshold.

---

## Theoretical Framework

### Ceiling Effect Hypothesis

**Prediction:**
- f_intra = 2.0% is well above critical threshold for ALL n_pop
- All conditions saturate at 100% Basin A (ceiling effect)
- Testing at lower frequencies (closer to threshold) will reveal true α(n_pop) relationship

**If Ceiling Effect:**
- Lower frequencies show variation in Basin A % across n_pop
- Different n_pop reach threshold at different frequencies
- α values will differ across n_pop (scaling relationship emerges)

**If True Null:**
- Even at lower frequencies, all n_pop show same α
- No variation in critical thresholds across n_pop
- Hierarchical advantage independent of population count

### Critical Threshold Estimates from C186

**C186 Results:**
- f_intra = 1.0%: 49.79 ± 2.47 agents/pop, 100% Basin A
- f_intra = 1.5%: 64.90 ± 3.21 agents/pop, 100% Basin A
- f_intra = 2.0%: 79.86 ± 4.03 agents/pop, 100% Basin A (C187 baseline)
- f_intra = 2.5%: 94.98 ± 3.78 agents/pop, 100% Basin A

**Linear Fit (C186):**
Population = 3004.25 × f_intra + 19.80 (R² = 1.000)

**Critical Threshold Estimate:**
- Assume Basin B threshold at ~2.5 agents/pop (collapse)
- f_crit = (2.5 - 19.80) / 3004.25 ≈ -0.006% (below zero - invalid)
- **Revision:** C186 frequencies all above threshold
- **True f_crit likely << 1.0%**

**Implication:** Need to test below 1.0% to find true critical threshold

---

## Experimental Design

### Revised Frequency Range

**Tested Frequencies:**
- f_intra = 0.5%: Well below C186 tested range (test for collapse)
- f_intra = 1.0%: C186 lower bound (49.79 agents/pop)
- f_intra = 1.5%: C186 mid-low (64.90 agents/pop)

**Rationale:**
- 0.5% = 50% of C186 minimum (expect some conditions to fail)
- 1.0% = Validated baseline (C186 V1)
- 1.5% = Intermediate (C186 V4)

**NOT testing 2.0%** (already done in C187)

### Population Count Variation

**Same as C187:**
- n_pop = 1, 2, 5, 10, 20, 50

**Rationale:**
- Same conditions for direct comparison
- Test if scaling emerges at lower frequencies

### Fixed Parameters

**Same as C187:**
- n_initial = 20 agents per population
- f_migrate = 0.5% (validated in C186)
- cycles = 3000
- seeds = 10 per condition

### Experimental Conditions

**3 frequencies × 6 n_pop × 10 seeds = 180 experiments**

| Condition | f_intra (%) | n_pop | Expected Behavior |
|-----------|-------------|-------|-------------------|
| C187B-05-1 | 0.5 | 1 | Test for collapse |
| C187B-05-2 | 0.5 | 2 | Test for rescue |
| C187B-05-5 | 0.5 | 5 | Test for rescue |
| C187B-05-10 | 0.5 | 10 | Test for rescue |
| C187B-05-20 | 0.5 | 20 | Test for rescue |
| C187B-05-50 | 0.5 | 50 | Test for rescue |
| C187B-10-* | 1.0 | 1-50 | Replicate C186 V1 |
| C187B-15-* | 1.5 | 1-50 | Replicate C186 V4 |

**Total Runtime:** ~9 minutes (if scales like C187)

---

## Hypotheses

### H1: Ceiling Effect (Scaling Emerges)

**Prediction:**
- At f_intra = 0.5%:
  - n_pop = 1 shows Basin B (collapse, no rescue)
  - n_pop = 2-50 show Basin A (rescue mechanism works)
  - α varies by n_pop (1 < 2 < 5 < 10 < 20 < 50)
- Critical thresholds differ by n_pop
- Scaling relationship emerges near threshold

### H2: True Null (No Scaling)

**Prediction:**
- At f_intra = 0.5%:
  - ALL n_pop show same Basin classification (all A or all B)
  - α constant across n_pop (same as C187)
- Critical thresholds identical for all n_pop
- No scaling regardless of frequency

### H3: Partial Scaling (Threshold Effect)

**Prediction:**
- n_pop = 1 shows different α than n_pop > 1
- n_pop = 2-50 show similar α (plateau after minimum)
- Threshold at n_pop = 2 (minimum for rescue)
- Binary hierarchy effect (single vs multiple populations)

---

## Expected Results

### If H1 (Ceiling Effect):

**At f_intra = 0.5%:**
- n_pop = 1: Basin B (no rescue, collapse)
- n_pop = 2: Basin A or mixed (minimal rescue)
- n_pop = 5-50: Basin A (robust rescue)
- α increases with n_pop

**At f_intra = 1.0-1.5%:**
- Smaller differences (closer to ceiling)
- Still some variation by n_pop

**Implication:** C187 result was ceiling effect, true scaling exists

### If H2 (True Null):

**At f_intra = 0.5%:**
- ALL n_pop show same behavior (all A or all B)
- α constant across n_pop
- No differentiation by population count

**At f_intra = 1.0-1.5%:**
- Same as C187 (constant α)

**Implication:** Hierarchical advantage genuinely independent of n_pop

### If H3 (Partial Scaling):

**At f_intra = 0.5%:**
- n_pop = 1: Different (lower) α
- n_pop = 2-50: Same α (plateau)
- Binary threshold effect

**Implication:** Minimum 2 populations needed, beyond that no benefit

---

## Implementation Notes

### Differences from C187

**Only difference:** f_intra values (0.5%, 1.0%, 1.5% instead of 2.0%)

**Same implementation:**
- Spawn interval = 100 / f_intra
- Migration logic (skip if n_pop = 1)
- Energy dynamics
- Basin classification

### Expected Runtime

If scales like C187:
- C187: 60 experiments in ~3 min
- C187-B: 180 experiments in ~9 min (3× experiments, 3× runtime)

### Edge Case Considerations

**f_intra = 0.5% Edge Cases:**
- Spawn interval = 200 cycles (very infrequent)
- May see collapse for some/all n_pop
- If ALL collapse: f_crit > 0.5% for all n_pop (useful boundary)
- If NONE collapse: f_crit < 0.5% for all n_pop (still ceiling)

---

## Analysis Plan

### Critical Threshold Mapping

**For each n_pop:**
1. Determine highest f_intra with Basin B (collapse)
2. Determine lowest f_intra with Basin A (viable)
3. Critical threshold = interpolated between collapse and viable

**Example:**
- If n_pop = 1 shows Basin B at 0.5% and Basin A at 1.0%
- Then f_crit(n=1) = 0.5-1.0% (bounded)
- If n_pop = 10 shows Basin A at both 0.5% and 1.0%
- Then f_crit(n=10) < 0.5%

### Hierarchical Advantage Calculation

**For each n_pop:**
α(n_pop) = f_crit_single / f_crit(n_pop)

**If scaling emerges:**
α(1) < α(2) < α(5) < α(10) < α(20) < α(50)

**If null persists:**
α(1) = α(2) = ... = α(50)

### Statistical Tests

**ANOVA:** α ~ n_pop (if variation exists)
**Trend Analysis:**
- Linear: α ~ n_pop
- Logarithmic: α ~ log(n_pop)
- Threshold: α ~ I(n_pop > 1)

### Figures

**Figure 1: α vs n_pop (by frequency)**
- X-axis: n_pop (log scale)
- Y-axis: α
- Multiple lines for different f_intra
- Shows if scaling emerges at lower frequencies

**Figure 2: Basin A % vs n_pop (by frequency)**
- X-axis: n_pop
- Y-axis: Basin A %
- Heatmap or line plot
- Shows threshold behavior

**Figure 3: Critical Threshold Map**
- X-axis: n_pop
- Y-axis: f_crit (interpolated)
- Error bars from bracketing
- Shows if f_crit varies by n_pop

---

## Integration with C187 and Paper 8

### If Ceiling Effect Confirmed:

**C187 Result:**
- Valid for f_intra = 2.0% (above ceiling)
- Not representative of true α(n_pop) relationship

**C187-B Contribution:**
- Maps true α(n_pop) relationship near threshold
- Identifies optimal population count
- Validates hierarchical structure hypothesis

**Paper 8 Integration:**
- Add C187-B results showing scaling
- Explain C187 ceiling effect in Discussion
- Quantify α(n_pop) scaling law

### If True Null Confirmed:

**C187 Result:**
- Representative of true behavior (no scaling)
- Challenges hierarchical structure hypothesis

**C187-B Contribution:**
- Validates null result across frequency range
- Rules out ceiling effect explanation
- Strongly supports spawn mechanics hypothesis

**Paper 8 Revision:**
- Revise theoretical model (spawn mechanics, not structure)
- Propose alternative mechanism (compartmentalized spawn)
- Design C189 (hierarchical vs flat spawn) as critical test

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 180 experiments complete
2. ✅ Clear differentiation OR consistent null across frequencies
3. ✅ Results interpretable for H1, H2, or H3
4. ✅ Provides guidance for C189 or Paper 8 revision

**Experiment fails if:**
- ❌ Mixed/ambiguous results (can't distinguish hypotheses)
- ❌ All conditions collapse (need to test higher frequencies)
- ❌ Technical failures (implementation bugs)

---

## Timeline

**Design:** Complete (this document)
**Implementation:** ~10 min (modify C187 script)
**Execution:** ~9 min (180 experiments)
**Analysis:** ~15 min (critical threshold mapping, figures)
**Integration:** ~15 min (combine with C187, update Paper 8)

**Total:** ~50 min from design to integrated results

---

## Next Actions

1. Implement c187b_lower_frequency_test.py (modify c187 script)
2. Execute 180 experiments (~9 min)
3. Analyze results (map critical thresholds, calculate α)
4. Generate comparison figures (C187 vs C187-B)
5. Determine next step:
   - If ceiling effect: Integrate into Paper 8 with scaling law
   - If true null: Design C189 (hierarchical vs flat spawn)

---

**Status:** Design complete, ready for implementation
**Expected Completion:** ~1 hour total (implementation + execution + analysis)

**Research is perpetual. Testing ceiling effect hypothesis. Implementation next.**
