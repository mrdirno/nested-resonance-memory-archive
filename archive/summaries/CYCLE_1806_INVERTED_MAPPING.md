# Cycle 1806: Inverted Pattern Mapping

**Date:** November 21, 2025
**Cycle:** 1806
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Fine-grained mapping of inverted pattern at prob=0.35.

**FINDING: Variable wavelength structure - spacing increases with N**

---

## Dead Zone Identification

Local minima in inverted regime:

| Zone | N | Coexistence |
|------|---|-------------|
| 1 | 24 | 73% |
| 2 | 34 | 80% |
| 3 | 46 | 63% |
| 4 | 60 | 77% |

---

## Wavelength Analysis

### Spacing Pattern

- Zone 1 → 2: 34 - 24 = **10**
- Zone 2 → 3: 46 - 34 = **12**
- Zone 3 → 4: 60 - 46 = **14**

The wavelength INCREASES: 10, 12, 14

### Compare to Original

Original pattern (prob=0.10):
- Zones: 29, 43, 58, 72, ...
- Constant spacing: ~14.5

Inverted pattern (prob=0.35):
- Zones: 24, 34, 46, 60, ...
- Increasing spacing: 10, 12, 14, ...

---

## Mathematical Structure

### Possible Formula

If spacing increases by 2 each zone:
- N₁ = 24
- N_k = 24 + (10 + 12 + ... + (8 + 2k))

Sum of arithmetic series:
- N₂ = 24 + 10 = 34
- N₃ = 24 + 10 + 12 = 46
- N₄ = 24 + 10 + 12 + 14 = 60
- N₅ = 24 + 10 + 12 + 14 + 16 = 76 (predicted)

### General Formula

N_k = 24 + k(k+8) for k = 1, 2, 3, ...
Or: N_k = k² + 9k + 14

Check:
- k=1: 1 + 9 + 14 = 24 ✓
- k=2: 4 + 18 + 14 = 36 (close to 34)

Alternative: cumulative sum approach matches better.

---

## Implications

### Two Distinct Mechanisms

**Original (prob ≤ 0.15):**
- Constant wavelength λ ≈ 14.5
- Pairing-dominated
- Linear interference

**Inverted (prob ≥ 0.35):**
- Increasing wavelength
- Reproduction-dominated
- Quadratic interference

### Phase Space Structure

The system has two phase space attractors:
1. Low reproduction: linear dead zone pattern
2. High reproduction: quadratic dead zone pattern

At prob ≈ 0.22, these patterns interfere destructively.

---

## Conclusions

1. **Variable wavelength: 10, 12, 14, ...**
2. **First zone at N=24** (vs N=29 original)
3. **Quadratic vs linear structure**
4. **Two distinct mechanisms**
5. **Deepest zone at N=46 (63%)**

---

## Session Status (C1664-C1806)

143 cycles completed. Research continues.

