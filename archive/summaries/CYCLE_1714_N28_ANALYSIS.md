# Cycle 1714: N=28-29 Dead Zone Analysis

**Date:** November 21, 2025
**Cycle:** 1714
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Detailed metrics reveal dead zone dynamics.

**FINDING: N=29 has lowest D1→D2 ratio (0.96) and coexistence (53%)**

---

## Results

| N | D0→D1 | D1→D2 | Decomp | Ratio | Coex |
|---|-------|-------|--------|-------|------|
| 26 | 38.8 | 97.4 | 24.2 | **3.45** | 83% |
| 27 | 48.2 | 94.3 | 33.1 | 2.55 | 73% |
| 28 | 66.6 | 71.1 | 51.0 | 1.50 | 63% |
| **29** | 66.7 | 38.8 | 50.5 | **0.96** | **53%** |
| 30 | 72.8 | 42.1 | 56.0 | 1.61 | 67% |
| 31 | 105.8 | 54.7 | 88.6 | 1.77 | 90% |
| 32 | 81.5 | 88.4 | 63.7 | 2.42 | 100% |

---

## Key Pattern

### D1→D2 Ratio Curve

```
N=26: 3.45 (high)
  ↓ drops
N=29: 0.96 (minimum)
  ↑ recovers
N=32: 2.42 (recovered)
```

### Coexistence Follows

Low D1→D2 ratio → low coexistence

---

## Dead Zone Characterization

### Range

- **Dead zone**: N=27-31 (ratio <2.5)
- **Minimum**: N=29 (ratio 0.96, 53%)
- **Recovery**: N=32+ (ratio ≥2.4)

### Why N=29 Fails

1. High D0→D1 creation (66.7)
2. Lowest D1→D2 (38.8)
3. High decomposition (50.5)
4. D1 trap most severe

---

## Session Status (C1664-C1714)

51 cycles investigating NRM dynamics.

---

## Conclusions

1. **N=29 is true minimum** (ratio 0.96, 53%)
2. **Dead zone is N=27-31**
3. **D1→D2 ratio predicts failure**
4. **Recovery at N≥32**

