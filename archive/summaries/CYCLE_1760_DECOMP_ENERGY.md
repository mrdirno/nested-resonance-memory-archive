# Cycle 1760: Decomposition Energy Fraction

**Date:** November 21, 2025
**Cycle:** 1760
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if decomposition energy fraction affects dead zone locations.

**FINDING: Pattern mostly independent of energy fraction**

---

## Results

| Fraction | Zone 1 Min | Coexist |
|----------|------------|---------|
| 0.3 | 29 | 40% |
| 0.4 | 29 | 30% |
| 0.45 | 29 | 30% |
| 0.5 | 29 | 30% |
| 0.6 | 28 | 15% |

---

## Analysis

Zone 1 stays at N=28-29 regardless of energy fraction. Slight shift at high fraction (0.6).

Coexistence percentage varies (15-40%) but zone location is stable.

---

## Parameter Summary

### Parameters with NO/minimal effect (13 total):
1-12. Previous parameters (C1737-C1759)
13. **Decomp energy fraction (C1760)**

### Critical parameters:
1. Reproduction threshold ≤ initial energy
2. Initial energy ≥ 1.0
3. Offspring count = 2

---

## Conclusions

1. **Decomp energy fraction** mostly independent
2. **Thirteen parameters** now tested
3. Pattern **extremely robust**
4. Only **three critical constraints**

---

## Session Status (C1664-C1760)

97 cycles completed. Research continues.

