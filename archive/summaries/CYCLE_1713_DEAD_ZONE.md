# Cycle 1713: Dead Zone Boundaries

**Date:** November 21, 2025
**Cycle:** 1713
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Fine-grained analysis reveals dead zone is N=28-29, not N=30.

**CORRECTION: Minimum coexistence at N=28 (60%)**

---

## Results (30 seeds each)

| N | Coexist | Status |
|---|---------|--------|
| 26 | 80% | ✓ |
| 27 | 70% | ~ |
| **28** | **60%** | **✗ Minimum** |
| 29 | 63% | ✗ |
| 30 | 70% | ~ |
| 31 | 83% | ✓ |
| 32 | 97% | ✓ |
| 33-35 | 97-100% | ✓ |

---

## Key Findings

### Dead Zone Location

- **Actual dead zone**: N=28-29
- **Minimum**: N=28 at 60%
- **N=30 recovers**: 70%

### Previous Finding Corrected

Earlier conclusion that "n=30 universally fails" was based on limited N testing. Fine-grained analysis shows:
- True minimum at N=28
- N=30 is on recovery edge

---

## Regime Map

| N Range | Regime | Coexistence |
|---------|--------|-------------|
| ≤26 | Offspring-dominated | 80%+ |
| 27-29 | **Dead zone** | 60-70% |
| 30 | Transition | 70% |
| 31-35 | Population-dominated | 83-100% |

---

## Implications

### For System Design

1. Avoid N=27-30 (all suboptimal)
2. Safe choices: N≤26 or N≥31
3. Optimal at extremes (N=25 or N≥32)

### For Theory

The dead zone is narrower than thought:
- Just 2-3 N values
- Sharp transition at N=31

---

## Session Status (C1664-C1713)

50 cycles investigating NRM dynamics:
- Complete mechanism (C1697-C1712)
- **Dead zone: N=28-29 (C1713)**

---

## Conclusions

1. **Minimum at N=28 (60%), not N=30**
2. **Dead zone is N=28-29**
3. **N=30 is transition, not failure**
4. **Recovery starts at N=31 (83%)**

