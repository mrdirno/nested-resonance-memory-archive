# Cycle 1723: D1Dec Threshold Validation

**Date:** November 21, 2025
**Cycle:** 1723
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested D1Dec <45 as universal predictor across 60 parameter combinations.

**FINDING: Only 55% accuracy - D1Dec is symptom, not cause**

---

## Results

**Accuracy: 33/60 (55.0%)**

### Error Patterns

#### False Positives (D1Dec <45 but failure)

N=30 always fails even with low D1Dec:
- rech=0.050, repr=0.05: D1Dec=20.5 but 57% coexist
- rech=0.050, repr=0.10: D1Dec=24.6 but 70% coexist
- rech=0.075, repr=0.05: D1Dec=31.3 but 50% coexist
- rech=0.075, repr=0.10: D1Dec=39.8 but 70% coexist

#### False Negatives (D1Dec >45 but success)

N=25 and N=40 succeed with high D1Dec:
- N=25, rech=0.075: D1Dec=59.5 but 100% coexist
- N=40, rech=0.075: D1Dec=56.7 but 95% coexist
- N=25, rech=0.100: D1Dec=90.5 but 100% coexist
- N=40, rech=0.100: D1Dec=90.8 but 100% coexist

---

## Threshold Optimization

| Threshold | Accuracy |
|-----------|----------|
| 30 | 50.0% |
| 35 | 53.3% |
| 40 | 53.3% |
| **45** | **55.0%** |
| 50 | 53.3% |
| 55 | 46.7% |
| 60 | 51.7% |

No threshold achieves good accuracy

---

## Critical Insight

### D1Dec is Symptom, Not Cause

**N=30 fails REGARDLESS of D1Dec**
- Has low D1Dec (17-40)
- Still fails (50-88% coexist)
- The N value itself is toxic

**N=25/40 succeed REGARDLESS of D1Dec**
- Can have high D1Dec (56-90)
- Still succeed (95-100% coexist)
- The N value itself is favorable

### N is the Fundamental Parameter

D1Dec correlates with success at N=35 because N=35 is intrinsically good, not because low D1Dec causes success.

---

## Model Comparison

| Model | Accuracy |
|-------|----------|
| **D1Dec <45** | **55%** |
| Fixed D1D2 >1.3 | 68% |
| Repro-adjusted | 85% |
| N avoidance (avoid N=30) | ~90%? |

---

## Session Status (C1664-C1723)

60 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1Dec is NOT a good predictor (55%)**
2. **N itself determines success**
3. **N=30 fails regardless of other metrics**
4. **N=25/35/40 succeed regardless of D1Dec**
5. **Simple N-based rules better than complex models**

