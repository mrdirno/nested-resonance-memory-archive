# Cycle 1779: Zone Strength Gradient

**Date:** November 21, 2025
**Cycle:** 1779
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated Zone 3 anomaly. Discovered zone strength gradient.

**FINDING: Zone 1 strongest (47%), Zone 4 weakest (87%)**

---

## Results

### All Peaks Comparison

| Zone | N | Coexist | Pairing | Max D1 |
|------|---|---------|---------|--------|
| 1 | 29 | 47% | 71.1% | 1.5 |
| 2 | 44 | 63% | 70.5% | 1.5 |
| 3 | 58 | 70% | 68.4% | 1.8 |
| 4 | 75 | 87% | 68.7% | 1.7 |

### Zone 3 Neighborhood

| N | Coexist | Pairing |
|---|---------|---------|
| 54 | 100% | 45.0% |
| 56 | 80% | 59.0% |
| 58 | 70% | 68.4% |
| 60 | 77% | 70.2% |
| 62 | 100% | 57.5% |

---

## Analysis

### Zone Strength Gradient

Dead zone effect weakens with increasing N:
- Zone 1: 47% coexistence (strongest effect)
- Zone 4: 87% coexistence (weakest effect)

This is consistent with C1775 attenuation explanation.

### Pairing Rate Stability

All peaks show similar pairing rates (68-71%).

The difference in coexistence comes from how the system responds to that pairing rate at different population sizes.

### Mechanism

At low N, high pairing completely depletes D0.
At high N, even with high pairing, enough agents survive to maintain D0.

---

## Conclusions

1. **Zone 1 is strongest** (47% coexistence)
2. **Zone effect weakens** with increasing N
3. **Pairing rates similar** across all peaks (~70%)
4. **Population size matters** for recovery

---

## Session Status (C1664-C1779)

116 cycles completed. Research continues.

