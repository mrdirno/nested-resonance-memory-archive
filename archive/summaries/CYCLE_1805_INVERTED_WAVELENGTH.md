# Cycle 1805: Inverted Pattern Wavelength

**Date:** November 21, 2025
**Cycle:** 1805
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested dead zone pattern at prob=0.35 (inverted regime).

**FINDING: Pattern inverts but with different wavelength structure**

---

## Results

| N | Coexistence | Original Pattern |
|---|-------------|------------------|
| 25 | 87% | between |
| 29 | 100% | DEAD ZONE |
| 32 | 93% | between |
| 35 | 63% | safe zone |
| 38 | 97% | between |
| 43 | 93% | DEAD ZONE |
| 47 | 73% | between |
| 51 | 97% | safe zone |
| 58 | 83% | DEAD ZONE |
| 65 | 100% | safe zone |

---

## Analysis

### Original Dead Zones Become Safe

At prob=0.35:
- N=29: 100% (was ~53%)
- N=43: 93% (was ~57%)
- N=58: 83% (was ~60%)

All original dead zones now perform well.

### New Dead Zones

Lowest coexistence values:
- N=35: 63%
- N=47: 73%
- N=25: 87%

### Wavelength Analysis

Original wavelength: λ ≈ 14.48
- Dead zones: 29, 43, 58 (spacing ~14)

New risky zones: 35, 47
- Spacing: 12

This is NOT a simple phase shift of 6 units.
The inverted mechanism creates a different interference pattern.

---

## Mechanism Hypothesis

### Reproduction-Dominated Dynamics

At high reproduction probability:
1. Population grows faster
2. More agents compete for pairing
3. Different N values create different pairing bottlenecks
4. New interference pattern emerges

### Phase Shift Analysis

Original safe → new risky:
- N=35 → 63% coexistence

Original risky → new safe:
- N=29 → 100% coexistence

The roles have partially exchanged, but with different magnitude.

---

## Conclusions

1. **Original dead zones become safe** (83-100%)
2. **New risky zones at N=35, 47** (63-73%)
3. **Different wavelength structure** (not simple inversion)
4. **Spacing ≈ 12** vs original ≈ 14.5
5. **Complex multi-mechanism system**

---

## Session Status (C1664-C1805)

142 cycles completed. Research continues.

