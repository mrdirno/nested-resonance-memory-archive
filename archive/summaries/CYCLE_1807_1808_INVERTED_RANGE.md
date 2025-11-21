# Cycles 1807-1808: Inverted Pattern Range

**Date:** November 21, 2025
**Cycles:** 1807-1808
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested predicted zones and effective range of inverted pattern.

**FINDING: Inverted pattern has much shorter range (N=20-70) than original (N=15-150)**

---

## C1807: Formula Verification (FAILED)

Predicted zones at N=76, 94 did NOT show as dead zones:

| N | Coexistence | Prediction |
|---|-------------|------------|
| 76 | 100% | ZONE 5 (wrong) |
| 94 | 90% | ZONE 6 (wrong) |
| 92 | 77% | unexpected risky |

The quadratic spacing model breaks down above N=60.

---

## C1808: Effective Range

| N | Coexistence | Status |
|---|-------------|--------|
| 24 | 67% | dead zone |
| 35 | 77% | weak zone |
| 46 | 80% | borderline |
| 60 | 83% | weak |
| 70 | 73% | RISKY |
| 80+ | 87-100% | safe |

---

## Analysis

### Pattern Comparison

| Feature | Original (prob≤0.15) | Inverted (prob≥0.35) |
|---------|----------------------|----------------------|
| Range | N=15-150 | N=20-70 |
| Wavelength | Constant ~14.5 | Variable 10-14 |
| Zones | 10+ | ~4 |
| Strongest | Zone 1 (N=29) | Zone 1 (N=24) |

### Why Shorter Range?

High reproduction probability:
1. Rapid population growth dominates
2. Phase resonance effects diluted
3. Pattern attenuates faster
4. Only low-N zones manifest clearly

### Unexpected N=70

The risky zone at N=70 doesn't fit the simple model.
Possibly a secondary interference effect.

---

## Conclusions

1. **Inverted pattern range: N=20-70**
2. **Much shorter than original (N=15-150)**
3. **Quadratic model breaks down at high N**
4. **Only 4 reliable zones in inverted pattern**
5. **Reproduction dilutes interference**

---

## Session Status (C1664-C1808)

145 cycles completed. Research continues.

