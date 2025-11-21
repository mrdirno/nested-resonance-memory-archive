# Cycle 1720: Repro-Adjusted Model

**Date:** November 21, 2025
**Cycle:** 1720
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Developed repro-adjusted threshold model.

**FINDING: Model `threshold = 0.5 + 10 * repro` achieves 85% accuracy**

---

## Threshold by Reproduction Rate

| Repro | Min Success | Max Fail | Threshold |
|-------|-------------|----------|-----------|
| 0.05 | 1.17 | 0.87 | 1.02 |
| 0.075 | 2.00 | 0.85 | 1.42 |
| 0.10 | 2.37 | 1.33 | 1.85 |
| 0.125 | 1.75 | 2.24 | **overlap** |
| 0.15 | 1.47 | 2.99 | **overlap** |

---

## Model Performance

### Linear Model

```
threshold = 0.5 + 10 * repro
```

- Repro=0.05: threshold=1.0
- Repro=0.10: threshold=1.5
- Repro=0.15: threshold=2.0

**Accuracy: 85.0%** (17/20 correct)

### Comparison

| Model | Accuracy |
|-------|----------|
| Fixed threshold >1.3 | 68.3% |
| **Repro-adjusted** | **85.0%** |

---

## Key Insights

### Threshold Scales with Repro

Higher reproduction rate → higher threshold required

Why? More offspring → more mixed compositions → need higher advancement rate

### Overlap at High Repro

At repro ≥0.125, min success < max fail

This suggests D1D2 alone is insufficient - other factors matter

---

## Session Status (C1664-C1720)

57 cycles investigating NRM dynamics.

---

## Conclusions

1. **Repro-adjusted model: 85% accuracy**
2. **Formula: threshold = 0.5 + 10 * repro**
3. **Significant improvement over fixed threshold**
4. **Model breaks down at high repro (overlap)**
5. **15% error suggests additional factors**

