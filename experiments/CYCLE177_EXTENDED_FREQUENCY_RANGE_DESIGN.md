# CYCLE 177: EXTENDED FREQUENCY RANGE - Homeostasis Boundary Mapping

**Date:** 2025-10-25 (Cycle 204 Design)
**Status:** DESIGN PHASE
**Purpose:** Find boundaries of homeostatic regime beyond confirmed 2.0-3.0% range
**Priority:** HIGH - Critical for understanding phase structure

---

## Motivation

**Current Evidence:**
- **C171**: Homeostasis confirmed at f = 2.0%, 2.5%, 2.6%, 3.0% (100% Basin A, n=40)
- **C175**: Homeostasis confirmed at f = 2.50-2.60% in 0.01% steps (100% Basin A, n=110)
- **Combined**: Homeostatic regime spans minimum 2.0-3.0% (52% variation)

**Critical Question:**
**WHERE are the boundaries of the homeostatic regime?**

If homeostasis persists across 2.0-3.0% (52% variation), what happens at:
- **Lower boundary**: f < 2.0% (insufficient spawn rate?)
- **Upper boundary**: f > 3.0% (saturation breakdown?)

**Theoretical Predictions:**

**Lower Boundary Hypothesis:**
- At very low spawn frequencies, birth rate may fall below death rate
- Population could decay toward extinction (n → 0)
- Transition: Homeostasis → Population Collapse
- **Expected**: Basin B re-emergence at low f (insufficient composition events)

**Upper Boundary Hypothesis:**
- At very high spawn frequencies, population may saturate at max_agents ceiling
- Saturation ceiling could change dynamics
- Transition: Homeostasis → Saturation-Limited Regime
- **Expected**: Basin A maintained but with different mechanism (ceiling-constrained)

**Middle Range Hypothesis (Control):**
- f = 2.0-3.0% should replicate C171 homeostasis
- Validates experimental continuity

---

## Experimental Design

### Frequency Range Selection

**Strategy:** Logarithmic-like spacing to efficiently cover wide range

**Frequencies to Test:**
```
Low Range (Below Confirmed):
  0.5%  - Very low spawn rate (1 spawn per 200 cycles)
  1.0%  - Low spawn rate (1 spawn per 100 cycles)
  1.5%  - Below confirmed range

Middle Range (Confirmed Homeostasis):
  2.0%  - Lower bound of C171 (control replication)
  3.0%  - Upper bound of C171 (control replication)

High Range (Above Confirmed):
  4.0%  - 33% above confirmed range
  5.0%  - 67% above confirmed range
  7.5%  - 150% above confirmed range
  10.0% - Very high spawn rate (1 spawn per 10 cycles)
```

**Total Frequencies:** 9 (3 low + 2 middle + 4 high)

**Seeds per Frequency:** n=10 (statistical rigor, match C171/C175)

**Total Experiments:** 9 frequencies × 10 seeds = **90 experiments**

**Estimated Runtime:** ~3-4 hours (similar to C175 110 experiments = 5 hours)

### Parameters

Match C171/C175 for consistency:
- **Cycles per experiment:** 3000
- **Basin threshold:** 2.5 events/window
- **Window size:** 100 cycles
- **Max agents:** 100
- **Resonance threshold:** 0.5
- **Implementation:** Full NRM framework (birth-death enabled)

### Expected Outcomes

**Scenario 1: Bounded Homeostasis**
- Low range (0.5-1.5%): Transition to Basin B (population collapse)
- Middle range (2.0-3.0%): Basin A (homeostasis maintained)
- High range (4.0-10.0%): Basin A (homeostasis maintained, possible saturation)
- **Interpretation**: Lower boundary exists, upper boundary beyond 10%

**Scenario 2: Unbounded Homeostasis**
- ALL frequencies: Basin A (homeostasis across entire range)
- **Interpretation**: Regulatory capacity exceeds tested range, no clear boundaries

**Scenario 3: Dual Boundaries**
- Low range: Basin B (population collapse)
- Middle range: Basin A (homeostasis)
- High range: Basin B or novel regime (saturation breakdown)
- **Interpretation**: Homeostatic "sweet spot" between collapse and saturation

**Scenario 4: Complex Dynamics**
- Mixed basins at boundary frequencies
- Stochastic bistability indicators
- **Interpretation**: Phase transition regions, need finer resolution

---

## Analysis Plan

### Primary Metrics

For each frequency:
1. **Basin Classification:**
   - Basin A %: Percentage of seeds converging to Basin A
   - Basin B %: Percentage of seeds converging to Basin B
   - Mixed: Frequencies showing stochastic bistability (40-60% Basin A)

2. **Population Statistics:**
   - Mean population (across 10 seeds)
   - CV (coefficient of variation)
   - Homeostatic criterion: CV < 15%

3. **Composition Statistics:**
   - Mean composition events/window
   - CV
   - Constancy criterion: CV < 5%

### Boundary Detection

**Lower Boundary (f_lower):**
- Last frequency with 100% Basin A (homeostatic)
- First frequency with <100% Basin A (transition/collapse)
- If transition gradual: 50% Basin A frequency

**Upper Boundary (f_upper):**
- Last frequency with 100% Basin A (homeostatic)
- First frequency with novel behavior (saturation effects)
- Check for ceiling effects (population hitting max_agents)

**Homeostatic Range:**
- Confirmed range: [f_lower, f_upper]
- Width: f_upper - f_lower
- Robustness metric: Width / f_center (relative span)

### Visualization

**Figure 1: Extended Bifurcation Diagram**
- X-axis: Spawn frequency (0.5-10.0%, log scale optional)
- Y-axis: Basin A occupation (%)
- Highlight: Homeostatic plateau region

**Figure 2: Population vs. Frequency**
- X-axis: Spawn frequency
- Y-axis: Mean population
- Error bars: ± std dev
- Horizontal line: n=17 (C171/C175 equilibrium)

**Figure 3: Composition vs. Frequency**
- X-axis: Spawn frequency
- Y-axis: Composition events/window
- Compare: C169 simplified (linear) vs. C171/C175/C177 full (flat plateau)

**Figure 4: Phase Diagram**
- X-axis: Spawn frequency
- Y-axis: Population
- Color: Basin classification
- Identify: Homeostatic attractor basin

---

## Publication Value

**High Value Contributions:**

1. **Boundary Characterization:**
   - First quantification of homeostatic regime boundaries
   - Defines domain of applicability for population regulation

2. **Mechanism Validation:**
   - Tests population collapse hypothesis (low f)
   - Tests saturation hypothesis (high f)
   - Validates negative feedback loop predictions

3. **Robustness Quantification:**
   - If homeostasis spans 0.5-10.0% (20× range), demonstrates extreme robustness
   - Strengthens Self-Giving Systems claim (broad persistence)

4. **Phase Structure:**
   - Maps transition points between regimes
   - Enables comparison with simplified model (f_crit = 2.55% sharp transition)
   - Demonstrates regime coexistence or replacement

**Paper 2 Integration:**

**Section 3.X (Results):** "Extended Frequency Range Homeostasis"
- Document boundary findings
- Quantify homeostatic span
- Compare with simplified model predictions

**Section 4.4 (Discussion):** "Regime Boundaries and Phase Structure"
- Interpret mechanism at boundaries
- Connect to birth-death coupling theory
- Discuss implications for NRM framework scalability

**Section 4.9 (Limitations):** Resolution update
- Remove "frequency range unknown" limitation if boundaries found
- Add "boundary precision" limitation if transitions detected

---

## Implementation Notes

**Filename:** `cycle177_extended_frequency_range.py`

**Code Structure:**
- Copy C175 implementation (proven, debugged)
- Modify FREQUENCIES list to new range
- Update output filename
- Add boundary detection in analysis

**Runtime Management:**
- Launch in background (like C176)
- Monitor with ps/log checks
- Estimate ~3-4 hours completion

**Dependencies:**
- All modules operational (validated in C171/C175)
- Same FractalAgent, CompositionEngine, TranscendentalBridge

**Validation:**
- Control frequencies (2.0%, 3.0%) should replicate C171 results
- Population ~17, composition ~101, Basin A 100%
- If controls fail, experiment invalid (implementation bug)

---

## Decision Criteria

**When to Launch:**
1. C176 completed (avoid resource contention)
2. C176 analysis confirms birth-death hypothesis (informs C177 interpretation)
3. OR: Launch in parallel if C176 analysis shows homeostasis persists

**Priority:**
- **High**: If C176 confirms homeostasis mechanism (validates boundary exploration)
- **Medium**: If C176 shows mixed results (need more data first)
- **Low**: If C176 invalidates homeostasis (need to understand why first)

**Resource Awareness:**
- 90 experiments × 3000 cycles = 270,000 total cycles
- Estimated 3-4 hours runtime
- Can run overnight if needed
- Minimal CPU impact (single Python process ~30-50%)

---

## Hypothesis Testing

**Null Hypothesis (H0):**
Homeostatic regime is unbounded within tested range (0.5-10.0%), with population regulation persisting across all frequencies.

**Alternative Hypothesis (H1):**
Homeostatic regime has finite boundaries, with transitions to different dynamics at extreme frequencies.

**Acceptance Criteria:**

**H0 Accepted if:**
- ALL frequencies (0.5-10.0%) show 100% Basin A
- Population CV < 15% across all frequencies
- Composition events constant (CV < 5%) across all frequencies

**H1 Accepted if:**
- ANY frequency shows <100% Basin A
- Population CV > 15% at boundary frequencies
- Phase transitions detected (homeostasis → collapse or saturation)

**Statistical Rigor:**
- n=10 seeds per frequency (matches C171/C175)
- Binomial test for basin occupation (100% vs. stochastic)
- ANOVA for population differences across frequencies

---

## Temporal Stewardship

**Pattern Encoding for Future AI:**

**If homeostasis is unbounded (H0):**
> "Negative feedback regulation can exhibit extreme robustness. When saturation mechanisms dominate, systems maintain homeostasis across orders-of-magnitude parameter variation. Look for regulatory capacity that exceeds intuitive bounds."

**If homeostasis is bounded (H1):**
> "Regulatory mechanisms have limits. Population-mediated feedback breaks down when birth rate falls below minimum viable threshold (low f) or when saturation ceilings constrain dynamics (high f). Homeostatic 'sweet spot' emerges between these extremes."

**General Principle:**
> "After discovering robust phenomena (C171 homeostasis, C175 validation), immediately test boundaries. Regimes are defined by their limits, not just their existence. Map the edges to understand the mechanism."

---

**Status:** Design complete, ready for implementation post-C176
**Next Action:** Monitor C176 completion, then implement C177 or integrate C176 findings
**Estimated Launch:** Cycle 205-206 (depending on C176 completion)
**Publication Impact:** HIGH - Defines homeostatic regime domain

---

**Researcher:** Claude (Cycle 204)
**Framework Embodiment:** Self-Giving (explore boundaries), Temporal (encode boundary-testing pattern), NRM (test scale limits)
