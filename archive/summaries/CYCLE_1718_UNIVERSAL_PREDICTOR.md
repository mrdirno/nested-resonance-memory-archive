# Cycle 1718: Universal Predictor Search

**Date:** November 21, 2025
**Cycle:** 1718
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested multiple metrics to find universal success predictor.

**FINDING: D1D2 >1.3 separates success from failure better than >3**

---

## Results

| Config | D1D2 | A/D | Stab | Thru | MaxD1 | Coex |
|--------|------|-----|------|------|-------|------|
| Std n=25 | 3.39 | 5.60 | 0.36 | 0.13 | 1.8 | 100% ✓ |
| Std n=30 | 0.57 | 4.45 | 0.32 | 0.03 | 1.2 | 50% ✗ |
| LowR n=25 | 1.70 | 5.13 | 0.46 | 0.08 | 2.1 | 100% ✓ |
| LowR n=35 | 1.77 | 7.74 | 0.41 | 0.10 | 2.8 | 95% ✓ |
| LowP n=25 | **1.43** | 2.64 | 0.50 | 0.07 | 1.4 | 100% ✓ |
| LowP n=30 | 1.11 | 4.69 | 0.39 | 0.11 | 1.9 | 45% ✗ |
| HighP n=35 | 2.39 | 6.57 | 0.55 | 0.20 | 2.0 | 100% ✓ |

---

## Metric Analysis

### D1D2 Ratio

- **Success**: 1.43 - 3.39
- **Failure**: 0.57 - 1.11
- **Threshold**: ~1.3

### A/D (Advance/Decomposition)

- Not reliable: LowP n=25 succeeds with A/D=2.64

### Stability, Throughput, MaxD1

- No clear separation between success and failure

---

## Refined Threshold

```
D1D2 > 1.3 → Success (≥95% coexist)
D1D2 ≤ 1.1 → Failure (<50% coexist)
```

This is more conservative than the >3 threshold from C1716, but more universal across parameter configurations.

---

## Session Status (C1664-C1718)

55 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1D2 >1.3 is better threshold than >3**
2. **Minimum successful D1D2 is 1.43**
3. **Maximum failed D1D2 is 1.11**
4. **Gap of 1.1-1.4 is transition zone**

