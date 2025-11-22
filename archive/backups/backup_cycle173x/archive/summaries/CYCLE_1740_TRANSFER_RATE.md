# Cycle 1740: Transfer Rate Effect

**Date:** November 21, 2025
**Cycle:** 1740
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if energy transfer rate affects dead zone locations.

**FINDING: Moderate effect - Zone 1 stable, Zone 3 shifts ±4**

---

## Results

| Rate | Zone 1 | Zone 3 | Interval |
|------|--------|--------|----------|
| 0.70 | 29 (50%) | 60 (70%) | 31 |
| 0.80 | 29 (53%) | 56 (70%) | 27 |
| 0.85 | 29 (47%) | 59 (67%) | 30 |
| 0.90 | 29 (47%) | 56 (67%) | 27 |
| 0.95 | 29 (50%) | 56 (67%) | 27 |

---

## Analysis

### Zone Stability

- **Zone 1**: Completely stable at 29
- **Zone 3**: 56-60 (shift: 4)

### Interval Variance

- **Range**: 27-31
- **Mean**: 28.4
- **Expected**: 30

Higher variance than resonance threshold (28-29).

### Cumulative Effect

Transfer rate affects energy accumulation:
- Low rate (0.70): Less energy transferred → later composition
- High rate (0.95): More energy → earlier composition

Effect compounds with depth, explaining Zone 3 shift.

---

## Implications

### Wavelength Stability

Despite Zone 3 shift, wavelength remains ~14.5:
- Mean interval: 28.4/2 = 14.2
- Within tolerance of 14.5 ± 1

### Design Guidance

For stable dead zone locations:
- Maintain transfer rate near 0.85
- Higher rates shift zones down
- Lower rates shift zones up (at higher N)

---

## Session Status (C1664-C1740)

77 cycles investigating NRM dynamics.

---

## Conclusions

1. **Zone 1 stable** at N=29 (fundamental)
2. **Zone 3 shifts ±4** with transfer rate
3. **Wavelength ~14.5** still holds (mean 14.2)
4. **Effect cumulative** with depth

