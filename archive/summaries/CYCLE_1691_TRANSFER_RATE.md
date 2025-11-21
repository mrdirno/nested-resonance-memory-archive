# Cycle 1691: Transfer Rate Effects

**Date:** November 21, 2025
**Cycle:** 1691
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested whether optimal N depends on composition transfer rate (standard = 0.85).

**Finding: n=25 optimal for transfer rates 0.7-0.9 (98%)**

---

## Results

| Transfer | Optimal N | Success |
|----------|-----------|---------|
| 0.70 | 25 | 98% |
| 0.80 | 25 | 98% |
| 0.85 | 25 | 98% |
| 0.90 | 25 | 98% |
| 0.95 | 25 | 82% |

---

## Analysis

### Robustness to Transfer Rate

n=25 achieves 98% for wide range of transfer rates:
- 0.7: 98%
- 0.8: 98%
- 0.85: 98%
- 0.9: 98%

Only at very high transfer (0.95) does performance drop to 82%.

### Why High Transfer Hurts

At transfer = 0.95:
- Composed energy = 2 × 1.1 × 0.95 = 2.09
- This exceeds threshold (1.3)
- Immediate decomposition

At transfer = 0.85:
- Composed energy = 2 × 1.1 × 0.85 = 1.87
- Still above threshold but manageable with decay

### Optimal Transfer Range

The system works best with transfer 0.7-0.9:
- Low enough to keep composed energy reasonable
- High enough to maintain energy flow

---

## Complete Parameter Space

### n=25 Optimum Robustness

| Parameter | Range Tested | n=25 Optimal? | Notes |
|-----------|--------------|---------------|-------|
| Threshold | 1.1-1.7 | Yes (all 98%) | Independent |
| Initial E | 0.5-1.25 | Yes at E≥1.0 | Varies with E |
| Recharge | 0.05-0.2 | Yes for 0.05-0.15 | Varies at high rate |
| Transfer | 0.7-0.95 | Yes for 0.7-0.9 | Drops at 0.95 |

### The Optimal Configuration

```python
E_INITIAL = 1.0
RECHARGE_RATE = 0.1
TRANSFER_RATE = 0.85
N_INITIAL = 25
DECOMP_THRESHOLD = 1.3
# → 96-98% coexistence
```

---

## Conclusion

**n=25 is robust to transfer rate variations (0.7-0.9).**

The standard transfer rate of 0.85 is well within the optimal range.

Complete parameter characterization now achieved.

---

## Session Status (C1648-C1691)

44 cycles investigating NRM dynamics:
- Complete characterization (C1664-1676)
- Theoretical validation (C1677-1678)
- Population optimization (C1679-1690)
- **Transfer rate: n=25 robust 0.7-0.9 (C1691)**

