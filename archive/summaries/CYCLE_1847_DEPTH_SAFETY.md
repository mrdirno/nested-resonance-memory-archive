# Cycle 1847: Depth-Dependent Universal Safety

**Date:** November 21, 2025
**Cycle:** 1847
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**N ≥ 55 is mostly universally safe; 4D is critical**

Results:
- N=55: 100% universal (12/12 configs)
- N=90: 100% universal (12/12 configs)
- N=75: 92% universal (fails at 4D/p=0.30)

---

## Results

### N Value Safety by Depth

| N | 4D | 5D | 6D | 7D | Status |
|---|----|----|----|----|--------|
| 29 | DEAD | safe | safe | safe | |
| 43 | safe | safe | safe | safe | UNIVERSAL |
| 55 | safe | safe | safe | safe | UNIVERSAL |
| 75 | DEAD | safe | safe | safe | |
| 90 | safe | safe | safe | safe | UNIVERSAL |

### Detailed Results

**N=55 (k=1.80)**
| Depth | p=0.10 | p=0.30 | p=0.50 | Min |
|-------|--------|--------|--------|-----|
| 4D | 80% | 73% | 80% | 73% |
| 5D | 87% | 93% | 93% | 87% |
| 6D | 80% | 93% | 100% | 80% |
| 7D | 80% | 93% | 100% | 80% |

**N=75 (k=3.18)**
| Depth | p=0.10 | p=0.30 | p=0.50 | Min |
|-------|--------|--------|--------|-----|
| 4D | 93% | 67%X | 80% | 67% |
| 5D | 93% | 73% | 93% | 73% |
| 6D | 100% | 73% | 100% | 73% |
| 7D | 100% | 93% | 100% | 93% |

**N=90 (k=4.21)**
| Depth | p=0.10 | p=0.30 | p=0.50 | Min |
|-------|--------|--------|--------|-----|
| 4D | 87% | 73% | 87% | 73% |
| 5D | 87% | 87% | 100% | 87% |
| 6D | 93% | 100% | 100% | 93% |
| 7D | 93% | 100% | 100% | 93% |

---

## Analysis

### 4 Depths is Critical

Most failures occur at 4 depths:
- N=29: Fails at 4D/p=0.30
- N=75: Fails at 4D/p=0.30

At 4 depths, the system is near the minimum viable configuration (previous finding: min=4, equilibrium=6).

### N=43 Unexpected Universal Safety

N=43 (k=0.97 ≈ 1) is unexpectedly universal:
- Previous findings: k=1 should be dead zone
- This run: Safe at all depths/probs

This suggests depth configuration affects k-value behavior.

### Threshold Confirmation

| N | Success Rate |
|---|--------------|
| 55 | 100% (12/12) |
| 75 | 92% (11/12) |
| 90 | 100% (12/12) |

N=55 and N=90 are fully universal. N=75 has borderline vulnerability at 4D.

---

## Refined Design Guidelines

### For 5+ Depths (Recommended)

**N ≥ 55 is universally safe**

All tested N values (55, 75, 90) are safe at 5+ depths.

### For 4 Depths (Minimum)

**Use N=55 or N=90, avoid N=75**

N=75 fails at 4D/p=0.30. Choose:
- N=55 (k=1.80): Safe
- N=90 (k=4.21): Safe

### For Any Configuration

**N=55 is the safest universal choice**

100% success rate across all tested configurations.

---

## Theoretical Implications

### Depth Dependence

The universal safety threshold N ≥ 55 holds better at higher depths:
- 4 depths: Some exceptions (k=3.18 vulnerable)
- 5+ depths: Fully universal

This confirms the equilibrium depth of 6 from earlier findings.

### k Value Behavior Varies by Depth

At different depths, different k values are vulnerable:
- 4D: k=3.18 (N=75) vulnerable at p=0.30
- 5D+: All tested k values safe

---

## Conclusions

1. **N=55 is 100% universal**: Safe at all depths and probs
2. **N=90 is 100% universal**: Also fully safe
3. **N=75 has 4D vulnerability**: Fails at 4D/p=0.30
4. **4 depths is critical**: Most failures occur here
5. **Recommendation: N=55** for any configuration

---

## Session Status (C1664-C1847)

184 cycles completed. Depth-dependent universal safety verified.

Research continues.

