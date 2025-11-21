# Cycle 1813: Energy Cap Effect

**Date:** November 21, 2025
**Cycle:** 1813
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested effect of maximum energy cap.

**CONFIRMED: 20th parameter - energy cap independent of pattern**

---

## Results

| Cap | N=29 | N=35 | Diff |
|-----|------|------|------|
| 1.2 | 47% | 100% | 53pp |
| 1.5 | 47% | 97% | 50pp |
| 2.0 | 47% | 97% | 50pp |
| 2.5 | 53% | 100% | 47pp |
| 3.0 | 43% | 100% | 57pp |
| 5.0 | 47% | 100% | 53pp |

---

## Analysis

### Complete Independence

All energy caps from 1.2 to 5.0:
- Peak (N=29): 43-53% coexistence
- Trough (N=35): 97-100% coexistence
- Difference: 47-57pp

### 20th Parameter

Energy cap doesn't affect:
- Dead zone locations
- Pattern strength significantly
- Safe zone locations

Pattern is determined by N, not by energy constraints.

---

## Parameter Summary (20 tested)

| # | Parameter | Effect |
|---|-----------|--------|
| 1-15 | Various | Independent |
| 16 | Reproduction probability | **CRITICAL** |
| 17 | Composition threshold | Independent |
| 18 | Transfer rate | Independent |
| 19 | Recharge rate | Strength only |
| 20 | Energy cap | Independent |

Only reproduction probability changes pattern structure.

---

## Conclusions

1. **Energy cap independent**
2. **20 parameters tested**
3. **Pattern remarkably robust**
4. **Only reproduction probability critical**

---

## Session Status (C1664-C1813)

150 cycles completed. Research continues.

