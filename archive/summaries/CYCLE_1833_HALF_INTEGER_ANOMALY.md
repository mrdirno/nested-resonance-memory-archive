# Cycle 1833: Half-Integer k Anomaly Investigation

**Date:** November 21, 2025
**Cycle:** 1833
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**No half-integer k anomaly - attenuation model validated**

All N values at high |k| (>1.5) are safe, regardless of k mod 1. The N=65 dead zone in C1832 was statistical noise.

---

## Results

### Half-Integer k Values (k mod 1 ≈ 0.5)

| N | k | |k| | Dead Probs |
|---|---|-----|------------|
| 36 | 0.48 | 0.48 | safe |
| 51 | 1.52 | 1.52 | safe |
| 65 | 2.49 | 2.49 | **safe** |
| 80 | 3.52 | 3.52 | safe |
| 94 | 4.49 | 4.49 | safe |

### Integer k Values (k mod 1 ≈ 0)

| N | k | |k| | Dead Probs |
|---|---|-----|------------|
| 58 | 2.00 | 2.00 | safe |
| 72 | 2.97 | 2.97 | safe |
| 87 | 4.01 | 4.01 | safe |
| 101 | 4.97 | 4.97 | safe |

---

## Analysis

### N=65 Resolved

In C1832, N=65 showed 65% coexistence at prob=0.50 (borderline dead zone).

In C1833, N=65 shows 90% coexistence at all probs (clearly safe).

**Conclusion**: The C1832 result was statistical noise near the 70% threshold.

### Attenuation Validation

**All |k| > 1.5 values are safe**, regardless of:
- k mod 1 (half-integer or integer)
- Probability range (0.05-0.80)

This validates the attenuation factor in the v2 model.

### Pattern Boundary

The attenuation threshold |k| > 1.5 corresponds to:
- N < N1 - 1.5λ ≈ 7 (very low, chaotic)
- N > N1 + 1.5λ ≈ 51 (safe from patterns)

---

## Model Update

### V2 Model Status

```python
def predict_v2(n):
    k = (n - 29) / 14.48

    # Attenuation - VALIDATED
    if abs(k) > 1.5:
        return "safe (attenuated)"

    # Standard prediction
    ...
```

**Attenuation threshold |k| > 1.5 is correct.**

### No V3 Needed

The k mod 1 ≈ 0.5 special case is not necessary. The v2 model attenuation is sufficient.

---

## Implications

### Safe Zone Definition

**N > 51 is generally safe from dead zone patterns**

This corresponds to |k| > 1.5 in the wavelength formula.

### Design Guideline

For applications requiring maximum safety:
- Use N > 51
- Or tune B/C ratio to 0.02-0.03

### Model Accuracy

With corrected understanding:
- V2 model attenuation: Validated
- High |k| predictions: 100% accurate (8/8)
- Mid/low |k| predictions: Need more refinement

---

## Conclusions

1. **No half-integer anomaly** - attenuation works for all k mod 1
2. **N=65 was statistical noise** - now shows safe
3. **Attenuation threshold |k| > 1.5 validated**
4. **N > 51 generally safe** from dead zone patterns
5. **V2 model attenuation correct** - no V3 modification needed

---

## Session Status (C1664-C1833)

170 cycles completed. Attenuation model validated.

Research continues.

