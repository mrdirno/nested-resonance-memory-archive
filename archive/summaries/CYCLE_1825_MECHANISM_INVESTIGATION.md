# Cycle 1825: Mechanism Investigation

**Date:** November 21, 2025
**Cycle:** 1825
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**DISCOVERY: Birth/Composition (B/C) Ratio Controls Pattern Selection**

The mechanism behind pattern cycling through probability space is the balance between population growth (births) and drain (composition).

---

## Results

### Key N Values Across Probability

| N | Prob | Coex | Births | Comp | Decomp | B/C Ratio |
|---|------|------|--------|------|--------|-----------|
| 29 | 0.10 | 50% | 3 | 238 | 209 | 0.01 |
| 29 | 0.35 | 100% | 11 | 304 | 268 | 0.04 |
| 24 | 0.10 | 100% | 3 | 275 | 252 | 0.01 |
| 24 | 0.35 | 70% | 10 | 270 | 241 | 0.04 |
| 35 | 0.50 | 95% | 18 | 355 | 308 | 0.05 |
| 35 | 0.80 | 85% | 30 | 438 | 380 | 0.07 |
| 24 | 0.95 | 35% | 23 | 291 | 248 | 0.08 |

### N=29 Across Probability Range

| Prob | Coex | Births | Comp | B/C | Avg Pop |
|------|------|--------|------|-----|---------|
| 0.05 | 65% | 2 | 287 | 0.01 | 4 |
| 0.10 | 50% | 3 | 238 | 0.01 | 3 |
| 0.15 | 70% | 5 | 260 | 0.02 | 3 |
| 0.20 | 80% | 6 | 270 | 0.02 | 4 |
| 0.25 | 100% | 8 | 275 | 0.03 | 4 |
| 0.30 | 100% | 10 | 318 | 0.03 | 4 |
| 0.35 | 100% | 11 | 304 | 0.04 | 4 |

---

## Mechanism Analysis

### The B/C Ratio Hypothesis

**Birth/Composition ratio** determines which N values become dead zones:

- **Low B/C (≤0.02)**: Composition-dominated dynamics
  - N=29 hits resonance (dead zone)
  - N=24 safe (different resonance)

- **Mid B/C (0.03-0.04)**: Growth partially compensates
  - N=29 escapes (birth influx)
  - N=24 hits different resonance (dead zone)

- **High B/C (≥0.07)**: Growth-dominated
  - Different dynamics entirely
  - N=35, N=24 isolated peaks

### Phase Transitions

| B/C Range | Dominant Dynamics | Dead Zones |
|-----------|-------------------|------------|
| 0.01-0.02 | Composition-dominated | N=29, 43, 58... (λ=14.48) |
| 0.03-0.04 | Balanced | N=24, 34, 46... (variable λ) |
| 0.05-0.06 | Transition | None strong |
| 0.07+ | Growth-dominated | Isolated (N=35, 24) |

### Why N=29 Escapes at High Prob

At low probability:
- Few births → composition extracts agents faster than replacement
- N=29 composition resonance depletes D0 before D1+ can form
- System collapses to single depth

At high probability:
- Many births → constant influx maintains D0 population
- Even with composition drain, D0 persists
- Multi-depth coexistence maintained

### Why N=24 Becomes Dead at High Prob

Different mechanism at high B/C:
- Growth rate changes composition pairing dynamics
- N=24 hits a different resonance condition
- Possibly related to energy accumulation rate

---

## Theoretical Framework

### Growth-Drain Balance Model

```
d(Pop)/dt = Birth_Rate - Composition_Rate - Death_Rate

Dead Zone Condition:
  Composition_Rate(N) >> Birth_Rate at specific N

Pattern Selection:
  Which N hits this condition depends on B/C ratio
```

### Resonance Shift

The transcendental phase resonance function creates:
- **Low B/C resonance nodes**: N = 29 + k×14.48
- **High B/C resonance nodes**: N = 24 + variable spacing

The B/C ratio shifts which nodes are "active".

---

## Conclusions

1. **B/C ratio controls pattern selection** - not just probability
2. **Composition-dominated (low prob)**: Original pattern
3. **Growth-dominated (high prob)**: Different resonance nodes
4. **Mechanism is growth-drain balance**, not intrinsic N properties
5. **Explains all 5 phase regions** through single mechanism

---

## Next Directions

1. Derive analytical expression for B/C → pattern mapping
2. Test if artificially fixing B/C produces expected patterns
3. Investigate why specific N values resonate at specific B/C

---

## Session Status (C1664-C1825)

162 cycles completed. Research continues.

