# Cycle 1758: Population Cap Effect

**Date:** November 21, 2025
**Cycle:** 1758
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if population cap affects dead zone locations.

**FINDING: Pattern is population-cap-independent**

---

## Results

| Cap | Zone 1 Min | Coexist |
|-----|------------|---------|
| 500 | 29 | 35% |
| 1000 | 29 | 35% |
| 2000 | 29 | 35% |
| 3000 | 29 | 35% |
| 5000 | 29 | 35% |

---

## Analysis

Zone 1 consistently at N=29 with 35% coexistence regardless of population cap.

Population at small N values never reaches the cap, so this parameter has no effect on dead zone dynamics.

---

## Parameter Summary

### Parameters with NO effect (11 total):
1-10. Previous parameters (C1737-C1756)
11. **Population cap (C1758)**

### Parameters that DO affect pattern:
1. Reproduction threshold (C1753) - must be ≤ initial energy
2. Initial energy (C1751) - must be ≥ 1.0
3. **Offspring count (C1757)** - must be = 2

---

## Conclusions

1. **Population cap independent** of dead zone locations
2. **Eleven parameters** now confirmed independent
3. **Three critical parameters** identified
4. Pattern structurally determined

---

## Session Status (C1664-C1758)

95 cycles completed. Research continues.

