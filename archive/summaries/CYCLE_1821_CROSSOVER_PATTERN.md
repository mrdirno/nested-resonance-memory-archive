# Cycle 1821: Crossover Pattern Analysis

**Date:** November 21, 2025
**Cycle:** 1821
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested for additional dead zones in the crossover regime (prob=0.22).

**FINDING: Crossover has only one dead zone at N=12, not a repeating pattern**

---

## Results

Local minima at crossover (prob=0.22):
- **N=12: 48%** (only clear dead zone)

Other notable points:
- N=14: 72%
- N=24: 80%
- N=26: 70%

But only N=12 is a definitive dead zone.

---

## Analysis

### Not a Third Pattern

The crossover regime does NOT have:
- Multiple dead zones
- Repeating wavelength
- Pattern structure

Instead, it appears to be:
- Residual interference at low N
- Single dead zone around N=12-13
- General weakening of both patterns

### Mechanism

At the crossover probability:
1. Original pattern (pairing) weakens
2. Inverted pattern (reproduction) weakens
3. Patterns partially cancel
4. Small residual effect at low N remains

### Comparison

| Feature | Original | Inverted | Crossover |
|---------|----------|----------|-----------|
| Dead zones | Multiple | Multiple | Single |
| Wavelength | λ=14.48 | Variable | None |
| Range | N=14-190 | N=11-60 | N≈12-13 |

---

## Revised Model

**Two-pattern system** (not three):
1. Original (prob ≤ 0.15)
2. Inverted (prob ≥ 0.35)
3. Crossover (prob ≈ 0.22): Residual, not a full pattern

---

## Design Guidelines

At crossover probability (0.22):
- Avoid N=12-13
- Most other N values safe
- Less predictable than pure regimes

---

## Conclusions

1. **Crossover has single dead zone at N=12**
2. **Not a third pattern** (no wavelength)
3. **Residual interference effect**
4. **Two-pattern model remains valid**

---

## Session Status (C1664-C1821)

158 cycles completed. Research continues.

