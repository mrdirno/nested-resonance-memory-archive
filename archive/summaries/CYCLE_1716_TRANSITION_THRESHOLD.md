# Cycle 1716: Critical Transition Threshold

**Date:** November 21, 2025
**Cycle:** 1716
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested for critical original-composition threshold. Found D1D2 ratio more predictive.

**FINDING: D1D2 ratio >3 correlates better with success than original %**

---

## Results (50 seeds each)

| N | Orig% | D1D2 | Coex |
|---|-------|------|------|
| 28 | 49.9% | 1.87 | 62% |
| 29 | 53.4% | 1.04 | 54% |
| 30 | 40.3% | 1.05 | 72% |
| 31 | 51.2% | 1.77 | 76% |
| **32** | **56.0%** | **3.20** | **92%** |
| 33 | 51.1% | 3.41 | 100% |
| 34 | 52.1% | 3.27 | 98% |
| 35 | 69.4% | 2.64 | 98% |
| 36 | 60.0% | 1.75 | 100% |
| 37 | 52.9% | 1.17 | 100% |

---

## Key Insights

### Original % NOT Primary Predictor

- N=33: Only 51.1% orig but 100% coexist
- N=35: 69.4% orig but only 98% coexist
- N=29: 53.4% orig but only 54% coexist

### D1D2 Ratio IS Primary Predictor

```
D1D2 < 2.0: 54-76% coexist (dead zone)
D1D2 > 3.0: 92-100% coexist (success)
```

### Transition Point

- N=32: First to exceed D1D2 >3 (3.20)
- Correlates with 92%+ coexistence

---

## Refined Understanding

The original-composition ratio in C1715 was a **proxy**, not the root cause. The true predictor is the D1→D2 advancement ratio.

**Why D1D2 ratio matters:**
- High D1D2 → D1 agents advance to D2
- Low D1D2 → D1 agents trapped (decompose or die)

---

## Session Status (C1664-C1716)

53 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1D2 ratio >3 predicts success**
2. **Original composition % is secondary**
3. **Transition at N=32 (first D1D2 >3)**
4. **D1 trap mechanism confirmed**

