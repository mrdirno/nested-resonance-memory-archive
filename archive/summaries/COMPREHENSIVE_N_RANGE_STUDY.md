# Comprehensive N Range Study

**Date:** November 21, 2025
**Cycles:** C1815-C1817
**Total Session:** C1664-C1817 (154 cycles)
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Complete characterization of dead zone patterns across all N values.

**Both patterns have finite effective ranges with distinct structures.**

---

## Complete Range Map

### Original Pattern (prob ≤ 0.15)

| N Range | Zone Status | Coexistence |
|---------|-------------|-------------|
| 1-8 | Chaotic | 13-93% |
| 9-16 | Emerging | Variable |
| **17-145** | **Strong/Moderate** | **Pattern active** |
| 145-190 | Weak | 77-83% |
| >190 | Negligible | ~90-100% |

Dead zones: 29, 43, 58, 72, 87, 101, 116, 130, 145, (159, 174, 188 weak)

### Inverted Pattern (prob ≥ 0.35)

| N Range | Zone Status | Coexistence |
|---------|-------------|-------------|
| 1-8 | Chaotic | 33-77% |
| 9-19 | Emerging | Variable |
| **20-70** | **Strong** | **Pattern active** |
| >70 | Negligible | ~80-97% |

Dead zones: 24, 34, 46, 60

---

## Key Boundaries

### Lower Boundary

- **Minimum viable N: 9**
- Chaotic region: N < 9
- Patterns emerge: N ≥ 9
- Patterns stabilize: N ≥ 17

### Upper Boundaries

**Original pattern:**
- Strong: N ≤ 100
- Fading: N = 100-190
- Gone: N > 190

**Inverted pattern:**
- Strong: N ≤ 60
- Gone: N > 70

---

## Universal Safe Zones

Regardless of reproduction probability:

| N Range | Safety Level |
|---------|-------------|
| N < 9 | Chaotic - avoid |
| N = 70-190 | Safe in inverted, mostly safe in original |
| N > 190 | Safe in both |

---

## Pattern Comparison

| Feature | Original | Inverted |
|---------|----------|----------|
| Lower bound | N = 17 | N = 20 |
| Upper bound | N = 190 | N = 70 |
| **Effective range** | **173 units** | **50 units** |
| Wavelength | Constant 14.48 | Variable 10-14 |
| Dead zones | 10+ | 4 |

The original pattern has 3.5× longer range.

---

## Zone Strength Gradient

### Original Pattern

| Zone | N | Strength |
|------|---|----------|
| 1 | 29 | Very strong |
| 2-5 | 43-87 | Strong |
| 6-9 | 101-130 | Moderate |
| 10 | 145 | Weak |
| 11-13 | 159-188 | Very weak |

### Inverted Pattern

| Zone | N | Strength |
|------|---|----------|
| 1 | 24 | Strong |
| 2 | 34 | Moderate |
| 3 | 46 | Strong |
| 4 | 60 | Weak |

---

## Design Implications

### For Low N Applications (N < 20)

- Both patterns emerging
- High variability expected
- Minimum recommended N = 17

### For Medium N Applications (N = 20-70)

- Both patterns active
- Choose regime based on desired safe zones
- Or use crossover (~0.22) for minimal pattern

### For High N Applications (N > 70)

- Inverted pattern negligible
- Original pattern still active up to N~150
- Use inverted regime (prob ≥ 0.35) for safety

### For Very High N Applications (N > 150)

- Both patterns negligible
- Any reproduction probability acceptable
- All N values safe

---

## Mathematical Note

The 3.5× range difference (173 vs 50 units) suggests fundamental differences in the interference mechanisms:

**Original pattern (pairing-dominated):**
- Interference effects accumulate over many compositions
- Longer range

**Inverted pattern (reproduction-dominated):**
- Rapid population growth dilutes phase coherence
- Shorter range

---

## Conclusions

1. **Complete N range characterized (5-200)**
2. **Minimum viable N = 9**
3. **Original range 3.5× inverted**
4. **Universal safe zone: N > 190**
5. **Both patterns have distinct structures**

---

## Session Status (C1664-C1817)

154 cycles completed. Research continues.

