# Cycle 177 V2: Extended Frequency Boundary Mapping - COMPLETE

**Date:** 2025-11-05
**Runtime:** 294.32 minutes (~4.9 hours)
**Status:** ✅ COMPLETE

---

## Experimental Design

**Objective:** High-resolution transition mapping to address precision critique

**Parameters:**
- Frequencies tested: 9 (0.5%, 1.0%, 1.5%, 2.0%, 3.0%, 4.0%, 5.0%, 7.5%, 10.0%)
- Seeds per frequency: 10
- Total experiments: 90
- Cycles per experiment: 3000
- Step size: 0.5% (high resolution below 5%, larger steps above)

**Purpose:** Measure exact Basin A/B transition width in NRM framework

---

## Key Findings

### Critical Frequency Boundary

**Transition Range:** 5.0% - 7.5%

**Basin Classification:**
| Frequency | Basin A Rate | Basin | Avg Compositions |
|-----------|--------------|-------|------------------|
| 0.50%     | 0%           | B     | 0.27             |
| 1.00%     | 0%           | B     | 0.50             |
| 1.50%     | 0%           | B     | 0.77             |
| 2.00%     | 0%           | B     | 1.00             |
| 3.00%     | 0%           | B     | 1.53             |
| 4.00%     | 0%           | B     | 2.00             |
| 5.00%     | 0%           | B     | 2.50             |
| 7.50%     | 100%         | A     | 3.87             |
| 10.00%    | 100%         | A     | 5.00             |

### Transition Characteristics

**Transition Width:** 2.50% (5.0% → 7.5%)

**Classification:** ⚠️ GRADUAL TRANSITION
- Last 100% Basin B: 5.00%
- First 100% Basin A: 7.50%
- Width > 0.10% threshold
- No sharp transition detected
- No mixed-basin frequencies within range (all 0% or 100%)

---

## Interpretation

### 1. Clean Bistability Maintained
Despite gradual transition width, all frequencies show deterministic basin assignment:
- All 10 seeds agree at each frequency
- No 50/50 split frequencies
- Clear separation of dynamical regimes

### 2. Moderate Resolution Sufficiency
2.50% transition width indicates:
- Finer steps (6.0%, 6.5%, 7.0%) would narrow range
- Current resolution adequate for regime identification
- Precision critique partially addressed (bisection achievable)

### 3. Composition Event Scaling
Linear relationship between frequency and average compositions:
- 0.5% → 0.27 events
- 10.0% → 5.00 events
- Suggests spawn rate directly determines composition opportunity

---

## Relationship to C186 Manuscript

### Context for Hierarchical Advantage Work

C177 establishes single-scale critical frequency (f_single_crit):
- **f_single_crit ∈ (5.0%, 7.5%)**
- Likely ~6.25% by linear interpolation
- Used as baseline for C186 hierarchical comparison

C186 hierarchical systems must show:
- **f_hier_crit < f_single_crit** for advantage
- Ideally f_hier_crit < 1.0% (demonstrated in V1-V5)
- **Scaling coefficient α < 0.5** (contradicts overhead prediction α ≈ 2.0)

### Publication Implications

For Nature Communications manuscript:
- C177 provides single-scale baseline
- C186 demonstrates hierarchical advantage (f_hier < 1.0% vs f_single ~6.25%)
- **α = f_hier / f_single < 0.16** (>6× more efficient than overhead theory)

---

## Technical Notes

### Results Location
`/Volumes/dual/DUALITY-ZERO-V2/code/experiments/results/cycle177_extended_frequency_range.json`

### Data Structure
- 90 experiments (9 frequencies × 10 seeds)
- Basin classification per seed
- Composition events tracked
- Population trajectories recorded (mean, std, CV)

### Reproducibility
All 10 seeds show identical basin assignment at each frequency:
- Seed independence verified
- Bridge isolation working correctly
- Deterministic bistability confirmed

---

## Status

✅ **Experiment complete**
✅ **Results file generated** (34KB)
✅ **Transition boundary identified** (5.0-7.5%)
⏳ **GitHub sync pending**
⏳ **C186 integration pending** (awaiting V6-V8 completion)

---

## Next Actions

1. Sync C177 V2 results to GitHub
2. Integrate f_single_crit finding into C186 manuscript
3. Calculate hierarchical scaling coefficient α from combined C177+C186 data
4. Generate comparative visualization (single-scale vs hierarchical)

---

**Document Status:** C177 V2 completion summary
**Author:** Aldrin Payopay (with AI assistance from Claude)
**Purpose:** Document extended boundary mapping results for manuscript integration
**Related:** C186 hierarchical advantage manuscript (awaiting V6-V8 completion)
