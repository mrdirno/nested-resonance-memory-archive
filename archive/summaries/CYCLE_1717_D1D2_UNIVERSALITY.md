# Cycle 1717: D1D2 Ratio Universality

**Date:** November 21, 2025
**Cycle:** 1717
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if D1D2 >3 is a universal success threshold across parameters.

**FINDING: D1D2 >3 is NOT universal - threshold is parameter-dependent**

---

## Results

### Standard (recharge=0.1, repro=0.1)

| N | D1D2 | Coex | Pass |
|---|------|------|------|
| 25 | 3.78 | 97% | ✓ |
| 30 | 0.86 | 70% | ✓ |
| 35 | 2.13 | 100% | ✗ |

### Low recharge (0.05)

| N | D1D2 | Coex | Pass |
|---|------|------|------|
| 25 | 1.72 | 93% | ✗ |
| 30 | 0.88 | 80% | ✓ |
| 35 | 1.39 | 100% | ✗ |

### High recharge (0.15)

| N | D1D2 | Coex | Pass |
|---|------|------|------|
| 25 | 5.74 | 93% | ✓ |
| 30 | 1.38 | 70% | ✓ |
| 35 | 2.95 | 93% | ✗ |

### Low repro (0.05)

| N | D1D2 | Coex | Pass |
|---|------|------|------|
| 25 | **0.79** | **100%** | ✗ |
| 30 | 0.91 | 37% | ✓ |
| 35 | 4.09 | 100% | ✓ |

### High repro (0.15)

| N | D1D2 | Coex | Pass |
|---|------|------|------|
| 25 | 2.89 | 77% | ✓ |
| 30 | 2.26 | 90% | ✗ |
| 35 | 1.84 | 100% | ✗ |

---

## Key Violations

### Low D1D2 but High Coexistence

- Low repro, N=25: D1D2=0.79 but 100% coexist
- Low recharge, N=35: D1D2=1.39 but 100% coexist
- High repro, N=35: D1D2=1.84 but 100% coexist

### High D1D2 but Lower Coexistence

- High recharge, N=25: D1D2=5.74 but only 93% coexist

---

## Implications

### Multiple Success Pathways

1. **High D1D2 path**: Standard config at N=25
2. **Low D1D2 path**: Low repro at N=25 (different mechanism)

### Parameter-Specific Thresholds

The "optimal" D1D2 threshold shifts with parameters:
- Low repro: Success possible with D1D2 <1
- Standard: Need D1D2 >3
- High recharge: Need D1D2 >5

---

## Session Status (C1664-C1717)

54 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1D2 >3 is NOT universal**
2. **Multiple success pathways exist**
3. **Threshold is parameter-dependent**
4. **Need different predictive metric**

