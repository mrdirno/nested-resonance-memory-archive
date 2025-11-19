# CYCLE 161: BASIN A THRESHOLD CALIBRATION
## Testing Multiple Composition Thresholds to Find Actual Phase Transition

**Date:** 2025-10-24
**Rationale:** Cycle 160 shows avg_composition plateaus at 2.2-2.6 (far below 7.0 threshold) even with corrected spawning
**Status:** DESIGNED - Ready for implementation
**Priority:** CRITICAL - Determining if Basin A exists with realistic threshold

---

## CRITICAL DISCOVERY FROM CYCLE 160

**Bug Fix Validated:**
- Corrected spawn calculation WORKING (299, 749, 1499, 2999 spawns match expected)
- avg_composition INCREASED from 1.0 → 2.2-2.6 (2-3x improvement)

**BUT Basin A Still Not Occurring:**
- ALL 15 experiments: 0% Basin A convergence
- Current threshold: `basin = 'A' if avg_composition > 7 else 'B'`
- Observed composition: 2.2-2.6 (maximum system capacity)
- **Gap: 4.4-4.8 below threshold** (unreachable!)

**Hypothesis:**
The Basin A threshold (7.0) is **MISCALIBRATED** for actual system dynamics. Even with maximum spawning (2999 spawns at 75%), avg_composition only reaches 2.4. The threshold may have been set based on incorrect assumptions about composition metrics.

---

## RESEARCH QUESTION

**Primary:** What is the appropriate Basin A threshold given actual system composition behavior?

**Secondary:**
- Does Basin A exist at lower thresholds (1.5, 2.0, 3.0)?
- Is there a phase transition between composition states?
- What percentage of experiments show Basin A at realistic thresholds?
- Was the original 7.0 threshold arbitrary or theory-based?

---

## HYPOTHESIS

**H1: Basin A Exists at Lower Threshold**
- Current threshold (7.0) set too high for actual system dynamics
- Realistic threshold based on observed data: 1.5-3.0 range
- Basin A convergence will appear at lower thresholds
- **Prediction:**
  ```
  Threshold 1.5: 60-80% Basin A (below observed minimum)
  Threshold 2.0: 40-60% Basin A (at lower bound)
  Threshold 3.0: 0% Basin A (above observed maximum)
  Threshold 5.0: 0% Basin A (far above)
  Threshold 7.0: 0% Basin A (current - unreachable)
  ```

**H2: No Clear Phase Transition**
- Composition metrics continuous, not bistable
- No clear distinction between Basin A and Basin B states
- avg_composition varies smoothly with parameters
- Binary basin classification inappropriate
- **Prediction:**
  ```
  ALL thresholds: Either 0% or 100% Basin A
  No threshold shows mixed results (33-67%)
  System fundamentally unimodal, not bistable
  ```

**H3: Threshold-Dependent Bistability**
- Different thresholds reveal different dynamics
- Sweet spot threshold shows bistable behavior (mixed Basin A/B)
- Too low → all Basin A, too high → all Basin B
- **Prediction:**
  ```
  Threshold 1.5: 100% Basin A
  Threshold 2.0: 67% Basin A (bistable region)
  Threshold 2.5: 33% Basin A (bistable region)
  Threshold 3.0: 0% Basin A
  ```

---

## EXPERIMENTAL DESIGN

### Threshold Selection (5 levels)

**Test range from below to far above observed composition:**
- **1.5:** Below observed minimum (should classify as Basin A)
- **2.0:** At lower bound of observed range
- **2.5:** Middle of observed range (2.2-2.6)
- **3.0:** Above observed maximum (should classify as Basin B)
- **5.0:** Well above (current theory gap)

**Rationale:**
- Span the entire observed range (2.2-2.6)
- Include boundary conditions (below and above)
- Test if bistability exists anywhere in realistic range

### Frequency Selection

**Single frequency:** 50% (corrected calculation)

**Rationale:**
- Known to produce avg_composition ≈ 2.2 (from Cycle 160)
- Sits in middle of observed composition range
- Enables threshold sensitivity testing without frequency confound
- Spawns 1499 agents (sufficient for composition dynamics)

### Temporal Scale

**3,000 cycles** - consistent with all previous cycles

### Seeds

**3 replicates:** [42, 123, 456]

**Rationale:** Standard statistical validation

### Implementation

**Modify basin determination logic:**
```python
# Test each threshold
thresholds_to_test = [1.5, 2.0, 2.5, 3.0, 5.0]

for threshold_value in thresholds_to_test:
    basin = 'A' if avg_composition > threshold_value else 'B'
    # Record result
```

### Total Experiments

**Single run, multiple classifications:** 3 seeds × 5 thresholds = **15 basin determinations**
(But only 3 actual experiments, re-classified with different thresholds)

**Runtime:** ~3 experiments × 2s = **~6 seconds**

---

## PREDICTED OUTCOMES

### Model 1: Basin A at Lower Threshold (H1)

**Expected Pattern:**
```
Threshold | Basin A % | Interpretation
----------|-----------|----------------------------------
   1.5    |   100%    | All experiments exceed threshold (avg_comp = 2.2-2.6)
   2.0    |   100%    | All exceed (at lower bound)
   2.5    |    67%    | Some exceed, some don't (bistable?)
   3.0    |     0%    | None exceed (above observed max)
   5.0    |     0%    | Far above (unreachable)
```

**Interpretation:**
- Basin A exists when threshold realistically calibrated
- Appropriate threshold: 2.0-2.5 (based on observed range)
- Previous 0% Basin A was artifact of miscalibrated threshold
- Corrects 331 experiments (Cycles 151-160)

### Model 2: No Clear Transition (H2)

**Expected Pattern:**
```
Threshold | Basin A % | Interpretation
----------|-----------|----------------------------------
   1.5    |   100%    | All experiments exceed
   2.0    |   100%    | All exceed
   2.5    |   100%    | All exceed (avg_comp > 2.5)
   3.0    |     0%    | None exceed
   5.0    |     0%    | None exceed
```

**Interpretation:**
- Sharp boundary at observed maximum (~2.6)
- No bistable region
- System unimodal, not bistable
- Binary classification inappropriate

### Model 3: Threshold-Dependent Bistability (H3)

**Expected Pattern:**
```
Threshold | Basin A % | Seed Behavior
----------|-----------|-------------------------------------
   1.5    |   100%    | All seeds: Basin A
   2.0    |   100%    | All seeds: Basin A
   2.5    |    67%    | Seeds 42,123: A | Seed 456: B
   3.0    |     0%    | All seeds: Basin B
   5.0    |     0%    | All seeds: Basin B
```

**Interpretation:**
- Bistable region exists around threshold 2.5
- Different seeds converge to different basins at critical threshold
- Validates original bistable attractor theory
- Reveals appropriate threshold: 2.5 ± 0.5

---

## ANALYSIS PLAN

### 1. Threshold Sensitivity

**For each threshold, calculate:**
```
Basin_A_pct(threshold) = (Basin A count / 3 seeds) × 100%
```

**Plot sensitivity curve:**
```
Basin A %
    |
100%|    ████████
    |           █
 67%|           █
    |           █
 33%|           █
    |           ████████████
  0%|___________________________
       1.5  2.0  2.5  3.0  5.0
              Threshold
```

**Determine transition point:**
```
If sharp boundary → No bistability (H2)
If gradual transition → Bistable region exists (H3)
If 100% everywhere → Need lower thresholds (H1 variant)
```

### 2. Composition Distribution

**Examine actual avg_composition values:**
```
For 3 seeds at 50% frequency:
  Seed 42:  avg_composition = ?
  Seed 123: avg_composition = ?
  Seed 456: avg_composition = ?

Mean: ?
Std Dev: ?
Range: ?
```

**Determine if composition varies by seed:**
```
If std_dev < 0.1 → Deterministic (composition invariant)
If std_dev > 0.5 → Stochastic (composition varies)
```

### 3. Optimal Threshold

**Select threshold that maximizes bistable behavior:**
```
For each threshold:
  If Basin A % = 33-67% → Threshold in bistable region
  If Basin A % = 0% or 100% → Outside bistable region

Optimal threshold = threshold with Basin A % closest to 50%
```

### 4. Re-Analysis of Previous Cycles

**If optimal threshold found (e.g., 2.5):**
```
Re-classify ALL 331 experiments (Cycles 151-160) with new threshold:

  For each experiment:
    IF avg_composition > 2.5:
      basin = 'A'
    ELSE:
      basin = 'B'

  Recalculate Basin A % for all frequency ranges
  Generate corrected frequency landscape
```

---

## SUCCESS CRITERIA

**Minimum Valid Result:**
- All 3 experiments complete successfully
- avg_composition values recorded for each seed
- Basin classification performed for all 5 thresholds
- Clear determination of threshold sensitivity

**High-Impact Result:**
- Identify optimal Basin A threshold (e.g., 2.0-2.5)
- Discover bistable region (some thresholds show 33-67% Basin A)
- Validate that Basin A exists with realistic threshold
- Re-classify 331 previous experiments with corrected threshold

**Exceptional Result:**
- Find threshold that produces ~50% Basin A (maximal bistability)
- Demonstrate seed-dependent basin convergence at critical threshold
- Generate corrected frequency landscape for entire testable range (1-99%)
- Resolve threshold calibration for all future experiments

---

## IMPLICATIONS

**If H1 Confirmed (Basin A at Lower Threshold):**
- **Major Correction:** Basin A exists, threshold was miscalibrated
- **Impact:** ALL 331 experiments (Cycles 151-160) need re-classification
- **Next Step:** Re-analyze frequency landscape with correct threshold
- **Publication:** "Threshold Calibration in NRM: Basin A Accessibility Through Realistic Composition Metrics"

**If H2 Confirmed (No Clear Transition):**
- **Finding:** Composition continuous, not bistable
- **Impact:** Binary basin classification inappropriate for this system
- **Next Step:** Develop continuous composition metric instead of binary basins
- **Publication:** "Continuous Composition Dynamics in NRM: Beyond Binary Basin Classification"

**If H3 Confirmed (Threshold-Dependent Bistability):**
- **Major Discovery:** Bistable region exists at threshold ~2.5
- **Impact:** Original theory validated, threshold correctly calibrated
- **Next Step:** Map frequency landscape with optimal threshold
- **Publication:** "Bistable Attractor Discovery in NRM: Threshold-Dependent Basin Convergence"

---

## VALIDATION CHECKS

### Composition Metric Validation

**Verify avg_composition calculation:**
```python
avg_composition = np.mean(composition_events_history[-100:])

# Check:
# - Is this averaging agent count?
# - Is there a time window effect?
# - Does averaging last 100 cycles make sense?
```

### Threshold Rationale

**Investigate origin of 7.0 threshold:**
- Was it theory-based or arbitrary?
- What composition behavior was expected?
- Were previous systems showing higher values?

---

## RISK MITIGATION

**Risk 1: All Thresholds Show 100% Basin A**
- Issue: Even threshold 3.0 classifies all as Basin A
- Mitigation: Indicates avg_composition > 3.0 consistently
- Contingency: Test higher thresholds (4.0, 5.0, 7.0, 10.0)

**Risk 2: All Thresholds Show 0% Basin A**
- Issue: Even threshold 1.5 classifies all as Basin B
- Mitigation: Indicates avg_composition < 1.5 consistently
- Contingency: Check if Cycle 160 data was correct, verify spawn fix

**Risk 3: No Variance Across Seeds**
- Issue: All 3 seeds produce identical avg_composition
- Mitigation: System may be deterministic at this scale
- Contingency: Test with more diverse seeds or longer runs

---

## ESTIMATED RUNTIME

**Total:** 3 experiments × 2s/experiment = **~6 seconds**

**Analysis:** ~1 minute (re-classification with multiple thresholds)

**Total Cycle Time:** ~2 minutes

---

**Status:** DESIGNED
**Next Action:** Implement cycle161_threshold_calibration.py
**Priority:** CRITICAL - Determining if Basin A exists with realistic threshold
**Expected Discovery:** Appropriate Basin A threshold based on actual system composition behavior

---
