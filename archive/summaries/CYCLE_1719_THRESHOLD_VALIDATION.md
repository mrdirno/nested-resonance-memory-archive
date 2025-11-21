# Cycle 1719: Threshold Validation

**Date:** November 21, 2025
**Cycle:** 1719
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested D1D2 >1.3 threshold across 60 parameter combinations.

**FINDING: 68.3% accuracy - threshold is repro-dependent**

---

## Results

**Accuracy: 41/60 (68.3%)**

### Error Patterns

#### False Negatives (D1D2 <1.3 but success)

All at **low repro (0.05)**:
- N=25, rech=0.050: D1D2=0.71 but 98% coexist
- N=25, rech=0.075: D1D2=0.95 but 98% coexist
- N=25, rech=0.100: D1D2=1.20 but 100% coexist
- N=35, rech=0.050, repro=0.15: D1D2=1.12 but 100% coexist

#### False Positives (D1D2 >1.3 but failure)

All at **high repro (0.15)**:
- N=25, rech=0.050: D1D2=1.37 but 84% coexist
- N=30, rech=0.050: D1D2=1.36 but 78% coexist
- N=25, rech=0.075: D1D2=1.72 but 86% coexist
- N=25, rech=0.100: D1D2=2.81 but 88% coexist

---

## Key Insight

### Repro-Dependent Threshold

```
Low repro (0.05): Success with D1D2 >0.7
Standard repro (0.10): Success with D1D2 >1.3
High repro (0.15): Success needs D1D2 >3.0?
```

### Why?

- **Low repro**: Fewer offspring → compositions mostly original-original → stable D1
- **High repro**: Many offspring → compositions mixed → higher D1D2 needed to overcome

---

## Session Status (C1664-C1719)

56 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1D2 >1.3 not universal (68.3% accuracy)**
2. **Threshold depends on reproduction rate**
3. **Low repro: lower threshold sufficient**
4. **High repro: higher threshold required**
5. **Need repro-adjusted predictive model**

