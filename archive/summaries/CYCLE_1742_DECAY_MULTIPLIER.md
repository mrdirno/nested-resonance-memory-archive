# Cycle 1742: Decay Multiplier Effect

**Date:** November 21, 2025
**Cycle:** 1742
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if decay multiplier affects dead zone locations.

**FINDING: Minimal effect - Zone 3 perfectly stable**

---

## Results

| Decay Mult | Zone 1 | Zone 3 | Interval |
|------------|--------|--------|----------|
| 0.05 | 30 (43%) | 59 (50%) | 29 |
| 0.10 | 30 (43%) | 59 (63%) | 29 |
| 0.15 | 30 (43%) | 59 (53%) | 29 |
| 0.20 | 30 (43%) | 59 (53%) | 29 |
| 0.25 | 29 (47%) | 59 (50%) | 30 |

---

## Analysis

### Stability

- **Zone 1**: 29-30 (shift: 1)
- **Zone 3**: 59 (no shift)
- **Interval**: 29-30 (very stable)

### Severity

Coexistence varies more (43-63%) than location.
Optimal decay: 0.10 (highest coexistence at Zone 3).

---

## Parameter Sensitivity Summary (C1737-C1742)

| Parameter | Zone 1 Shift | Zone 3 Shift | Interval Var |
|-----------|--------------|--------------|--------------|
| **Decomp threshold** | **0** | **0** | **0** |
| **Decay mult** | **1** | **0** | **1** |
| Resonance thresh | 1 | 2 | 1 |
| Recharge rate | 0 | 2 | 2 |
| **Transfer rate** | **0** | **4** | **4** |
| **Repro rate** | **3** | **5** | **3** |

### Hierarchy

**Most stable**: Decomp threshold, decay mult
**Moderate**: Resonance thresh, recharge rate
**Most variable**: Transfer rate, repro rate

---

## Session Status (C1664-C1742)

79 cycles investigating NRM dynamics.

---

## Conclusions

1. **Decay multiplier ≈ stable** (shift ≤1)
2. **Zone 3 perfectly stable** at 59
3. **Confirms phase space origin**
4. **Complete parameter sweep done**

