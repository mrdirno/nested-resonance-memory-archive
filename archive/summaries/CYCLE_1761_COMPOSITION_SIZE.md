# Cycle 1761: Composition Group Size

**Date:** November 21, 2025
**Cycle:** 1761
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if composition group size affects dead zone locations.

**FINDING: Composition size = 2 is REQUIRED**

---

## Results

| Size | Zone 1 Min | Coexist |
|------|------------|---------|
| 2→1 | 30 | 50% |
| 3→1 | 25 | 0% |
| 4→1 | 25 | 0% |

---

## Analysis

### Size 2→1 (Standard)

- Zone 1 at N=30 as expected
- 50% coexistence
- Pattern holds

### Size 3→1 or 4→1 (Collapse)

- 0% coexistence everywhere
- Too many agents removed per composition
- Cannot sustain population

---

## The 2:2 Balance

The dead zone pattern requires exact balance:

```
Composition:   2 agents → 1 agent (net -1)
Decomposition: 1 agent → 2 agents (net +1)
```

This creates zero net flow at specific N values = dead zones.

### Breaking the Balance

| Comp | Decomp | Net/event | Result |
|------|--------|-----------|--------|
| 2→1 | 1→1 | -1, 0 | Collapse |
| 2→1 | 1→2 | -1, +1 | **Dead zones** |
| 2→1 | 1→3 | -1, +2 | Full coexistence |
| 3→1 | 1→2 | -2, +1 | Collapse |

---

## Complete Critical Constraints

1. Initial energy ≥ 1.0
2. Reproduction threshold ≤ initial energy
3. **Offspring count = 2**
4. **Composition size = 2**

The 2:2 symmetry is fundamental!

---

## Physical Interpretation

Dead zones emerge from interference in the composition-decomposition flow. This requires exact balance:

```
Flow_up = Flow_down
2 agents in = 2 agents out
```

Any other ratio → net flow → no dead zones.

---

## Conclusions

1. **Composition size = 2** required
2. **2:2 symmetry** is fundamental
3. **Fourth critical constraint** identified
4. **Flow balance** creates dead zones

---

## Session Status (C1664-C1761)

98 cycles completed. Research continues.

