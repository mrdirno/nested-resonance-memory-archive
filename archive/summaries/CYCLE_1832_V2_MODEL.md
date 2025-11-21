# Cycle 1832: V2 Model with Attenuation

**Date:** November 21, 2025
**Cycle:** 1832
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**V2 model with attenuation: 56% accuracy, +33% from attenuation alone**

The attenuation factor correctly predicts safety for high |k| values (N=52, 72, 80), but N=65 remains anomalous.

---

## Results

| N | |k| | Prediction | Actual Dead | Result |
|---|-----|------------|-------------|--------|
| 17 | 0.83 | mid (0.20-0.50) | 0.80 | ✗ |
| 20 | 0.62 | safe or high | 0.60 | ✓ |
| 25 | 0.28 | mid (0.25-0.35) | 0.30 | ✓ |
| 37 | 0.55 | mid (0.25-0.35) | safe | ✗ |
| 40 | 0.76 | mid (0.20-0.50) | safe | ✗ |
| **52** | **1.59** | **safe (attenuated)** | **safe** | **✓ (v2)** |
| 65 | 2.49 | safe (attenuated) | 0.50 | ✗ |
| **72** | **2.97** | **safe (attenuated)** | **safe** | **✓ (v2)** |
| **80** | **3.52** | **safe (attenuated)** | **safe** | **✓ (v2)** |

---

## Model Performance

| Metric | V1 (no atten.) | V2 (with atten.) |
|--------|----------------|------------------|
| Correct | 2/9 | 5/9 |
| Accuracy | 22% | 56% |
| Improvement | - | +33% |

---

## Attenuation Analysis

### Successful Predictions

| N | |k| | Prediction | Outcome |
|---|-----|------------|---------|
| 52 | 1.59 | Safe (attenuated) | Safe ✓ |
| 72 | 2.97 | Safe (attenuated) | Safe ✓ |
| 80 | 3.52 | Safe (attenuated) | Safe ✓ |

### Failed Prediction

| N | |k| | Prediction | Actual | Issue |
|---|-----|------------|--------|-------|
| 65 | 2.49 | Safe (attenuated) | Dead at 0.50 | Anomalous |

### N=65 Anomaly

N=65 has:
- k = 2.49 (should be attenuated)
- k mod 1 = 0.49 (borderline safe/mid)
- Dead zone at prob=0.50

Possible explanations:
1. k mod 1 ≈ 0.5 creates resonance
2. Transition between attenuation regimes
3. Higher harmonic mode

---

## Model Refinement

### Current V2

```python
def predict_v2(n):
    k = (n - 29) / 14.48
    if abs(k) > 1.5:
        return "safe (attenuated)"
    # ... standard prediction
```

### Proposed V3

```python
def predict_v3(n):
    k = (n - 29) / 14.48
    k_frac = k % 1

    # Attenuation with k mod 1 check
    if abs(k) > 1.5:
        if 0.45 < k_frac < 0.55:
            return "possible mid prob dead"
        return "safe (attenuated)"

    # ... standard prediction
```

---

## Outstanding Issues

### Failures to Address

1. **N=17**: Very low N, different dynamics
2. **N=37**: Safe but predicted mid prob
3. **N=40**: Safe but predicted mid prob
4. **N=65**: High |k| but not fully attenuated

### Root Causes

- k mod 1 boundaries not precise
- Attenuation threshold may need tuning
- Some N values don't follow pattern

---

## Conclusions

1. **Attenuation improves accuracy** by +33%
2. **3/4 high |k| predictions correct** (75%)
3. **N=65 anomaly** suggests k mod 1 ≈ 0.5 special case
4. **Mid-range failures** (N=37, 40) need refinement
5. **56% overall accuracy** - useful but not reliable

---

## Model Status

| Version | Accuracy | Key Feature |
|---------|----------|-------------|
| V1 | 56% | k mod 1 only |
| V2 | 56% | + attenuation |
| V3 (proposed) | ? | + k mod 1 ≈ 0.5 check |

---

## Session Status (C1664-C1832)

169 cycles completed. V2 model implemented and tested.

Research continues.

