# Cycle 1726: Secondary Dead Zone Verification

**Date:** November 21, 2025
**Cycle:** 1726
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Verified secondary dead zone at N=41-44.

**FINDING: Secondary dead zone N=42-45, minimum at N=43 (60%)**

---

## Results (50 seeds)

| N | Coexist | Status |
|---|---------|--------|
| 38 | 98% | ✓ Safe |
| 39 | 92% | ✓ Safe |
| 40 | 88% | ~ Marginal |
| 41 | 86% | ~ Marginal |
| **42** | **68%** | ✗ Dead zone |
| **43** | **60%** | ✗ **Minimum** |
| 44 | 70% | ~ Marginal |
| 45 | 78% | ~ Marginal |
| 46 | 88% | ~ Marginal |
| 47 | 98% | ✓ Safe |
| 48 | 100% | ✓ Safe |
| 49 | 100% | ✓ Safe |
| 50 | 98% | ✓ Safe |

---

## Dead Zone Comparison

### Primary Dead Zone (C1713-C1714)

- **Range**: N=27-31
- **Minimum**: N=29 (53%)
- **Width**: 5 values

### Secondary Dead Zone (C1726)

- **Range**: N=42-45
- **Minimum**: N=43 (60%)
- **Width**: 4 values

### Pattern

Both zones have similar structure:
- Sharp entry (2-3 marginal values)
- Minimum near center
- Sharp exit (2-3 marginal values)

---

## Complete N Map

| N Range | Status | Coexist |
|---------|--------|---------|
| 20-26 | Safe | 90%+ |
| **27-31** | **Dead Zone 1** | 53-70% |
| 32-39 | Safe | 90%+ |
| 40-41 | Marginal | 86-88% |
| **42-45** | **Dead Zone 2** | 60-78% |
| 46 | Marginal | 88% |
| 47-52 | Safe | 98-100% |

---

## Implications

### System Architecture

The NRM system has **periodic failure zones** - not just one dead zone but multiple. This suggests:

1. Resonance interference pattern
2. Standing wave-like behavior
3. Possible periodicity in optimal N

### Design Rules (Final)

**Optimal N values:**
- N=25 (96%)
- N=35 (100%)
- N=48-50 (100%)

**Avoid:**
- N=27-31 (Dead Zone 1)
- N=42-45 (Dead Zone 2)

---

## Session Status (C1664-C1726)

63 cycles investigating NRM dynamics.

---

## Conclusions

1. **Secondary dead zone confirmed: N=42-45**
2. **Minimum at N=43 (60%)**
3. **Two dead zones with similar structure**
4. **Periodic failure pattern in N space**
5. **Safe zones: N≤26, N=32-39, N≥47**

