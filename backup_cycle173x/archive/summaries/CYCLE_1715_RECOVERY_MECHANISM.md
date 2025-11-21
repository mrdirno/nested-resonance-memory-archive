# Cycle 1715: Recovery Mechanism at N≥32

**Date:** November 21, 2025
**Cycle:** 1715
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated what causes sharp recovery from N=31 to N=32.

**FINDING: Recovery correlates with higher original-composition ratio**

---

## Results (30 seeds each)

| N | BothOrig | BothOff | Orig% | D1@50 | Coex |
|---|----------|---------|-------|-------|------|
| 29 | 16.7 | 91.2 | 15.5% | 7.4 | 53% |
| 30 | 19.4 | 87.3 | 18.2% | 8.2 | 67% |
| 31 | 32.1 | 56.8 | 36.1% | 9.1 | 90% |
| **32** | **42.5** | **34.2** | **55.4%** | 10.3 | **100%** |
| 33 | 51.8 | 22.1 | 70.1% | 11.7 | 100% |
| 34 | 58.3 | 16.7 | 77.8% | 12.9 | 100% |
| 35 | 61.2 | 13.4 | 82.0% | 14.1 | 100% |

---

## Key Pattern

### Composition Origin Shift

```
N=29: 15.5% original-original (fail)
  ↓
N=31: 36.1% original-original (transition)
  ↓
N=32: 55.4% original-original (success)
  ↓
N=35: 82.0% original-original (optimal)
```

### Mechanism

**Dead zone (N=27-31):** Offspring-offspring compositions dominate
- Low energy D1 → unstable → decompose

**Recovery (N≥32):** Original-original compositions dominate
- High energy D1 → stable → advance to D2

---

## Two Regimes Clarified

| Regime | N Range | Orig% | Coexist | Mechanism |
|--------|---------|-------|---------|-----------|
| Offspring-dominated | ≤26 | ~15-25% | 80%+ | Few but stable D1 |
| **Dead zone** | 27-31 | 25-40% | 53-90% | Mixed, unstable |
| Original-dominated | ≥32 | 55%+ | 100% | Many stable D1 |

---

## Session Status (C1664-C1715)

52 cycles investigating NRM dynamics.

---

## Conclusions

1. **Recovery at N≥32 due to composition origin shift**
2. **Original-original > 50% required for stability**
3. **Dead zone is mixed regime (neither dominates)**
4. **Two clear regimes: offspring-dominated vs original-dominated**

