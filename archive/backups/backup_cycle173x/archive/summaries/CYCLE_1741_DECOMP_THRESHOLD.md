# Cycle 1741: Decomposition Threshold Effect

**Date:** November 21, 2025
**Cycle:** 1741
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if decomposition threshold affects dead zone locations.

**FINDING: NO effect - perfect stability across all thresholds**

---

## Results

| Threshold | Zone 1 | Zone 3 | Interval |
|-----------|--------|--------|----------|
| 1.1 | 29 (53%) | 59 (57%) | 30 |
| 1.2 | 29 (50%) | 59 (57%) | 30 |
| 1.3 | 29 (53%) | 59 (67%) | 30 |
| 1.4 | 29 (53%) | 59 (63%) | 30 |
| 1.5 | 29 (53%) | 59 (57%) | 30 |

---

## Analysis

### Complete Stability

- **Zone 1**: 29 (no variation)
- **Zone 3**: 59 (no variation)
- **Interval**: 30 (no variation)

This is the most stable parameter tested.

### Severity Variation

Coexistence varies only slightly (50-67%).
Pattern: Threshold 1.3 optimal for Zone 3.

---

## Implications

### Phase Space Independence

Dead zone locations determined by:
- π-e-φ resonance geometry
- NOT by decomposition dynamics

The decomposition threshold controls:
- When agents decompose
- NOT where interference nodes occur

### Parameter Hierarchy

Based on all tests (C1737-C1741):

**Most stable** (shift 0):
- Decomposition threshold

**Stable** (shift ≤2):
- Resonance threshold
- Recharge rate

**Moderate** (shift ≤4):
- Transfer rate
- Reproduction rate

---

## Session Status (C1664-C1741)

78 cycles investigating NRM dynamics.

---

## Conclusions

1. **Decomp threshold ≠ zone driver**
2. **Perfect stability** across 1.1-1.5
3. **Confirms phase space origin** of dead zones
4. **Wavelength truly fundamental**

