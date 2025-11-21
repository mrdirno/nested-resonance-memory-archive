# Cycle 1809: Neutral Zone Analysis

**Date:** November 21, 2025
**Cycle:** 1809
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested pattern at crossover probability (prob=0.22).

**FINDING: Not fully neutral - inverted pattern slightly dominant**

---

## Results

| N | Coexistence | Original Pattern | Inverted Pattern |
|---|-------------|------------------|------------------|
| 24 | 70% | - | DEAD |
| 29 | 90% | DEAD | - |
| 35 | 97% | safe | safe→dead |
| 43 | 97% | DEAD | - |
| 46 | 100% | - | DEAD |
| 51 | 83% | safe | - |
| 58 | 97% | DEAD | - |
| 60 | 97% | - | DEAD |

Spread: 30pp (70% - 100%)

---

## Analysis

### Residual Pattern

At the theoretical crossover point (prob=0.22):
- Pattern is weakened but not eliminated
- Spread of 30pp vs 40pp (normal) or 33pp (inverted)
- Inverted pattern slightly dominant

### Zone Behavior

**Original dead zones become safe:**
- N=29: 90% (was ~53%)
- N=43: 97% (was ~57%)
- N=58: 97% (was ~60%)

**Inverted dead zones persist:**
- N=24: 70% (still risky)

**Unexpected behavior:**
- N=51: 83% (borderline - neither pattern predicts this)

### Asymmetric Crossover

The crossover is not symmetric:
- Original pattern: Fully suppressed
- Inverted pattern: Partially active

True neutralization may occur at slightly higher probability (~0.24).

---

## Implications

### Phase Competition

The two mechanisms don't simply cancel:
- Inverted pattern has residual dominance at 0.22
- Complete neutralization may not exist

### Design Consideration

For maximum pattern-free behavior:
- Use prob = 0.22-0.24
- Expect 70-100% range (still some variation)
- N=24 remains risky

---

## Conclusions

1. **Crossover not fully neutral**
2. **30pp spread remains**
3. **Inverted pattern slightly dominant**
4. **Original dead zones become safe**
5. **N=24 still risky at crossover**

---

## Session Status (C1664-C1809)

146 cycles completed. Research continues.

