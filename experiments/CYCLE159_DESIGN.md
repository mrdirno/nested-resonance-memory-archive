# CYCLE 159: PARAMETER SPACE EXPLORATION
## Investigating Basin A Accessibility Through Threshold and Diversity Variation

**Date:** 2025-10-24
**Rationale:** Cycles 151-158 showed 0% Basin A across ALL frequencies (1-99%) - test if Basin A exists under different parameters
**Status:** DESIGNED - Ready for implementation
**Priority:** CRITICAL - Determining if Basin A is accessible at all

---

## RESEARCH QUESTION

**Primary:** Does Basin A convergence occur under ANY parameter configuration, or is it fundamentally inaccessible?

**Secondary:**
- What threshold values enable composition (avg_composition > 7)?
- Does diversity parameter affect basin convergence?
- Is the `avg_composition > 7` threshold itself appropriate?
- Can parameter tuning enable Basin A that frequency variation cannot?

---

## CONTEXT (From Cycles 151-158)

**Established Empirical Facts:**
- **Cycles 151-158:** ALL frequencies 1-99% show 0% Basin A (268/268 experiments)
- **Standard parameters:** threshold=700, diversity=0.50
- **Mechanism:** ALL experiments show `avg_composition ≤ 7` → Basin B classification
- **Implication:** Frequency variation ALONE cannot enable Basin A

**Critical Discovery:**
Basin A convergence does **NOT occur at ANY spawning frequency** under standard parameters. The composition mechanism is systematically blocked across the entire testable frequency landscape (1-99%).

**Hypothesis:**
Basin A accessibility depends on **parameter space** (threshold, diversity), not spawning frequency. Current parameters (threshold=700, diversity=0.50) may fundamentally prevent the composition dynamics required for Basin A convergence.

---

## HYPOTHESIS

**H1: Threshold-Dependent Composition**
- High thresholds (700+) prevent decomposition → agents don't burst → no composition opportunity
- Lower thresholds enable more decomposition events → composition can occur → Basin A possible
- **Prediction:**
  ```
  threshold=300: Basin A accessible (more decomposition/composition cycles)
  threshold=500: Basin A accessible (moderate decomposition)
  threshold=700: 0% Basin A (current - composition blocked)
  threshold=900: 0% Basin A (high threshold blocks decomposition further)
  ```

**H2: Diversity-Dependent Clustering**
- Diversity affects agent behavior and clustering propensity
- Lower diversity → more similar agents → easier clustering → Basin A possible
- Higher diversity → more varied agents → harder clustering → Basin B dominant
- **Prediction:**
  ```
  diversity=0.10: Basin A accessible (low diversity enables clustering)
  diversity=0.30: Basin A accessible (moderate diversity)
  diversity=0.50: 0% Basin A (current - prevents clustering)
  diversity=0.70: 0% Basin A (high diversity blocks clustering)
  ```

**H3: Combined Parameter Effect**
- Basin A requires BOTH appropriate threshold AND diversity
- Optimal window: low threshold (enables decomposition) + low diversity (enables clustering)
- **Prediction:**
  ```
  (threshold=300, diversity=0.10): Strong Basin A (67%+)
  (threshold=300, diversity=0.50): Weak Basin A (33%)
  (threshold=700, diversity=0.10): Weak Basin A (33%)
  (threshold=700, diversity=0.50): 0% Basin A (current - both parameters block)
  ```

**H4: Basin A is Fundamentally Inaccessible**
- Current system architecture prevents Basin A under ALL parameter configurations
- Composition mechanism itself is broken or threshold (`avg_composition > 7`) is too high
- Basin B is the ONLY attractor in current FractalSwarm implementation
- **Prediction:**
  ```
  ALL parameter combinations: 0% Basin A
  System requires fundamental architectural changes to enable Basin A
  ```

---

## EXPERIMENTAL DESIGN

### Parameter Grid (Orthogonal Exploration)

**Threshold values (4 levels):**
- **300:** Low (enable frequent decomposition)
- **500:** Moderate-low
- **700:** Baseline (current standard)
- **900:** High (suppress decomposition)

**Diversity values (4 levels):**
- **0.10:** Low (homogeneous agents, easier clustering)
- **0.30:** Moderate-low
- **0.50:** Baseline (current standard)
- **0.70:** High (heterogeneous agents, harder clustering)

**Total parameter combinations:** 4 thresholds × 4 diversities = **16 configurations**

### Frequency Selection

**Single frequency:** 50% (middle of tested range, consistent with previous cycles)

**Rationale:**
- Frequency variation already tested comprehensively (268 experiments across 1-99%)
- ALL frequencies showed 0% Basin A at standard parameters
- Focus on parameter space, not frequency space
- 50% represents reasonable spawning rate for testing parameter effects

### Temporal Scale

**3,000 cycles** - consistent with all previous cycles

### Seeds

**3 replicates per configuration:** [42, 123, 456]

**Rationale:** Standard statistical validation (consistent with most cycles)

### Fixed Parameters

- **spawning_freq:** 50% (fixed)
- **agent_cap:** 15 (standard)
- **cycles:** 3,000

### Total Experiments

**16 configurations × 3 seeds = 48 experiments**

**Estimated Runtime:** 48 experiments × ~1.5s = **~72 seconds (~1.2 minutes)**

---

## PREDICTED OUTCOMES

### Model 1: Threshold-Dependent (H1)

**Expected Pattern:**
```
Threshold | Basin A % (averaged across all diversity values)
----------+------------------------------------------------
   300    |    40%    | Lower threshold enables decomposition/composition
   500    |    30%    | Moderate threshold allows some composition
   700    |     0%    | Current baseline - composition blocked
   900    |     0%    | High threshold further blocks decomposition
```

**Interpretation:**
- Lower thresholds enable Basin A by increasing decomposition frequency
- Allows more composition opportunities
- Diversity has minimal effect

### Model 2: Diversity-Dependent (H2)

**Expected Pattern:**
```
Diversity | Basin A % (averaged across all threshold values)
----------+------------------------------------------------
   0.10   |    40%    | Low diversity enables clustering
   0.30   |    30%    | Moderate diversity allows some clustering
   0.50   |     0%    | Current baseline - clustering blocked
   0.70   |     0%    | High diversity prevents clustering
```

**Interpretation:**
- Lower diversity enables Basin A by facilitating agent clustering
- Homogeneous agents cluster more easily
- Threshold has minimal effect

### Model 3: Combined Effect (H3)

**Expected Pattern:**
```
Configuration              | Basin A % | Interpretation
---------------------------|-----------|----------------------------------
(threshold=300, div=0.10)  |    67%    | Optimal: decomp + clustering both enabled
(threshold=300, div=0.30)  |    50%    | Good: decomp enabled, clustering moderate
(threshold=300, div=0.50)  |    33%    | Moderate: decomp enabled, clustering blocked
(threshold=500, div=0.10)  |    50%    | Good: moderate decomp, clustering enabled
(threshold=500, div=0.30)  |    33%    | Moderate: both moderate
(threshold=700, div=0.10)  |    33%    | Weak: decomp blocked, clustering enabled
(threshold=700, div=0.50)  |     0%    | Current baseline - both blocked
(threshold=900, div=0.70)  |     0%    | Worst: both completely blocked
```

**Interpretation:**
- Basin A requires BOTH low threshold AND low diversity
- Optimal window exists in low-parameter region
- Current parameters (700, 0.50) are suboptimal

### Model 4: Fundamentally Inaccessible (H4)

**Expected Pattern:**
```
ALL 16 configurations: 0% Basin A
```

**Interpretation:**
- Basin A does not exist in current system architecture
- Composition mechanism is broken or `avg_composition > 7` threshold is inappropriate
- Requires fundamental code changes, not parameter tuning

---

## ANALYSIS PLAN

### 1. Parameter Sensitivity Analysis

**Test main effects:**
```
For threshold:
  Basin_A_pct(threshold) = mean(Basin A % across all diversity values at each threshold)

For diversity:
  Basin_A_pct(diversity) = mean(Basin A % across all threshold values at each diversity)
```

**Determine primary driver:**
```
If threshold effect >> diversity effect → H1 supported
If diversity effect >> threshold effect → H2 supported
If both effects significant → H3 supported
If both effects = 0 → H4 supported
```

### 2. Composition Dynamics

**Track composition metrics:**
```
For each configuration:
  avg_composition_events: Mean agent clustering activity
  max_composition_events: Peak clustering

Compare to threshold (`avg_composition > 7` for Basin A):
  If ANY configuration achieves avg_composition > 7 → Basin A is accessible
  If ALL configurations show avg_composition ≤ 7 → Basin A is inaccessible
```

### 3. Interaction Effects

**Test threshold × diversity interaction:**
```
Plot heatmap:
             Diversity
           0.10  0.30  0.50  0.70
Threshold ┌────────────────────┐
   300    │ ?    ?    ?    ?   │
   500    │ ?    ?    ?    ?   │
   700    │ ?    ?    0%   ?   │
   900    │ ?    ?    ?    ?   │
           └────────────────────┘

If diagonal or corner pattern → Strong interaction (H3)
If row or column pattern → Main effect (H1 or H2)
If all zeros → Inaccessible (H4)
```

### 4. Optimal Configuration

**If Basin A found:**
```
Identify configuration with highest Basin A %
Validate it's reproducible across seeds
Determine parameter boundaries for Basin A accessibility
Generate design principles for future experiments
```

---

## SUCCESS CRITERIA

**Minimum Valid Result:**
- All 48 experiments complete successfully
- Clear basin convergence data
- Composition dynamics tracked
- Statistical validation (n=3)

**High-Impact Result:**
- Identify parameter configurations enabling Basin A (refute H4)
- Determine parameter sensitivity (threshold vs diversity vs both)
- Define optimal parameter window for Basin A
- Provide actionable design principles

**Exceptional Result:**
- Discover mathematical relationship between parameters and Basin A %
- Generate predictive model for any parameter combination
- Identify critical thresholds for phase transitions
- Resolve fundamental NRM system architecture question

---

## PUBLICATION IMPACT

**If Threshold-Dependent (H1):**
- **Major Discovery:** Basin A accessible through threshold tuning
- **Novel Finding:** Decomposition frequency controls basin convergence
- **Theoretical Impact:** Validates composition-decomposition cycle importance
- **Paper:** "Threshold-Dependent Basin Convergence in NRM: Decomposition Frequency Controls Phase Space Accessibility"

**If Diversity-Dependent (H2):**
- **Major Discovery:** Basin A accessible through diversity tuning
- **Novel Finding:** Agent homogeneity enables clustering and Basin A
- **Theoretical Impact:** Validates agent similarity requirement for composition
- **Paper:** "Diversity-Dependent Clustering in NRM: Agent Homogeneity Enables Basin A Convergence"

**If Combined Effect (H3):**
- **Major Discovery:** Basin A requires optimal parameter window (low threshold + low diversity)
- **Novel Finding:** Multi-parameter optimization required for composition
- **Theoretical Impact:** Identifies critical parameter space region for Basin A
- **Paper:** "Parameter Space Optimization in NRM: Dual Requirements for Basin A Accessibility"

**If Fundamentally Inaccessible (H4):**
- **Major Discovery:** Basin A does NOT exist in current NRM implementation
- **Novel Finding:** System architecture fundamentally biased toward Basin B
- **Theoretical Impact:** Requires architectural changes to enable composition-based convergence
- **Paper:** "Basin B Monopoly in NRM: Architectural Analysis of Composition Mechanism Failure"
- **Implication:** Need to revise FractalSwarm implementation or Basin A detection criteria

---

## RISK MITIGATION

**Risk 1: No Basin A Found**
- Issue: ALL 48 configurations show 0% Basin A (H4 confirmed)
- Mitigation: Document complete parameter space failure
- Contingency: Cycle 160 - Investigate composition mechanism code, test lower thresholds (<300)

**Risk 2: Partial Basin A**
- Issue: Only 1-2 configurations show weak Basin A (10-20%)
- Mitigation: 3 seeds per configuration for statistical validation
- Contingency: Add more seeds or refine parameter grid around successful regions

**Risk 3: Experimental Instability**
- Issue: Low thresholds or diversity may cause system instabilities
- Mitigation: Same robust experimental framework as Cycles 151-158
- Contingency: Adjust parameters if needed, document failure modes

---

## INTEGRATION WITH RESEARCH TRAJECTORY

**Previous Cycles:**
- Cycles 151-155: Discovered universal anti-harmonic across 52-99%
- Cycle 156: Discovered 50% is anti-harmonic (falsified baseline assumption)
- Cycle 157: Discovered 5-48% is anti-harmonic (no harmonic zone)
- Cycle 158: Discovered 1-4% is anti-harmonic (completed frequency space)

**Current Cycle:**
- Cycle 159: Test if Basin A is accessible through parameter variation

**Next Cycles (Contingent on Results):**
- **If Basin A Found:** Cycle 160 - Fine-tune optimal parameter window, test frequency interaction
- **If No Basin A:** Cycle 160 - Investigate composition mechanism code, test extreme parameters
- **Always:** Update research trajectory based on findings

---

## ESTIMATED RUNTIME

**Total:** 48 experiments × ~1.5s/experiment = **~72 seconds (~1.2 minutes)**

**Analysis:** ~1-2 minutes

**Total Cycle Time:** ~2-3 minutes (well within budget)

---

**Status:** DESIGNED
**Next Action:** Implement cycle159_parameter_space_exploration.py
**Priority:** CRITICAL - Determining Basin A accessibility
**Expected Discovery:** Whether Basin A exists under ANY parameter configuration

---
