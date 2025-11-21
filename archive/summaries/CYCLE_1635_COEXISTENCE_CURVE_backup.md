# Cycle 1635: Full Coexistence Curve

**Date:** November 20, 2025
**Cycle:** 1635
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Maps the complete coexistence curve from collapse (0.05) to near-saturation (0.50), identifying the critical threshold for 7-level trophic system survival.

**Key Finding:** Critical 50% threshold occurs between magnitude 0.10-0.15. System plateaus at ~67% coexistence from 0.15-0.30.

---

## Experimental Design

- **Magnitudes tested:** 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50
- **Seeds per magnitude:** 30 (seeds 60001-60030)
- **Total experiments:** 210
- **Cycles per run:** 30,000
- **Coexistence criterion:** All 7 levels maintain population ≥ 0.5

---

## Results

| Magnitude | Max Spawn Prob | Coexistence Rate |
|-----------|----------------|------------------|
| 0.05 | 0.21 | **0%** |
| 0.10 | 0.42 | 47% |
| 0.15 | 0.63 | 67% |
| 0.20 | 0.84 | 67% |
| 0.30 | 1.26 | 67% |
| 0.40 | 1.68 | 70% |
| 0.50 | 2.10 | 77% |

### Visual Curve
```
0.05: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
0.10: ██████████████░░░░░░░░░░░░░░░░ 47%
0.15: ████████████████████░░░░░░░░░░ 67%
0.20: ████████████████████░░░░░░░░░░ 67%
0.30: ████████████████████░░░░░░░░░░ 67%
0.40: █████████████████████░░░░░░░░░ 70%
0.50: ███████████████████████░░░░░░░ 77%
```

---

## Critical Thresholds

### Collapse Boundary
- **Below 0.10:** System cannot sustain 7-level coexistence
- At 0.05 (max_prob = 0.21): 100% collapse rate
- Insufficient reproduction to offset predation losses

### 50% Threshold
- Crossed between **0.10 and 0.15**
- Marks transition from likely-collapse to likely-survival

### Plateau Region
- **0.15 to 0.30:** Stable at ~67% coexistence
- System achieves equilibrium in this range
- C1633-1634's apparent "dip" at 0.30 was noise (n=20-50)
- With n=30, all three points converge to 67%

### Saturation Approach
- **Above 0.30:** Gradual increase toward saturation
- 0.40 → 70%, 0.50 → 77%
- Diminishing returns as spawn probabilities exceed 1.0

---

## Key Insights

### 1. Sharp Collapse Boundary
The 0% → 47% jump between 0.05 and 0.10 indicates a sharp phase transition. Below the threshold, systems cannot bootstrap sufficient population momentum.

### 2. Plateau Dynamics
The 67% plateau from 0.15-0.30 suggests an attractor state where:
- Predation balances reproduction
- Energy constraints create ceiling
- Stochastic extinctions cause ~33% failures regardless of parameters

### 3. Saturation Effects
The gradual rise above 0.30 (67% → 70% → 77%) shows that saturating spawn probability provides marginal benefit. The ~23% failure rate at 0.50 likely represents irreducible stochastic risk.

### 4. Optimal Operating Range
**Recommended:** Magnitude 0.25-0.35
- Provides ~67-70% coexistence
- Avoids collapse risk (< 0.15)
- Avoids saturation waste (> 0.50)

---

## Comparison with Previous Cycles

| Cycle | Focus | Key Result |
|-------|-------|------------|
| C1632 | Initial mapping | First valid sub-saturation data |
| C1633 | Fine-grained | Apparent dip at 0.30 |
| C1634 | Dip investigation | Dip resolved as noise |
| **C1635** | Full curve | Complete phase diagram |

---

## Statistical Notes

- 30 seeds provides moderate confidence
- Standard error at 67%: ±8.6%
- 95% CI: ~50-84%
- The plateau consistency (67%, 67%, 67%) despite different magnitudes supports attractor hypothesis

---

## Files Generated

- Results: `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1635_coexistence_curve_results.json`
- Individual DBs: `c1635_mag{X}_seed{Y}.db` (210 files)

---

## Conclusion

C1635 completes the sub-saturation dynamics investigation initiated in C1632. The coexistence curve reveals:

1. **Critical collapse threshold** at magnitude ~0.10
2. **Stable plateau** at ~67% from 0.15-0.30
3. **Saturation approach** with diminishing returns above 0.30

The ~33% baseline failure rate in the plateau represents the irreducible stochastic risk of 7-level trophic coexistence under these energy dynamics.

**The curve is now fully characterized. Next: investigate the mechanism behind the 33% failure rate.**
