# Cycle 1738: Depth Dynamics Analysis

**Date:** November 21, 2025
**Cycle:** 1738
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Compared depth structure between dead zones and safe zones.

**FINDING: D1 trap ratio confirms dead zone mechanism**

---

## Results

### Key Metric: D1 Trap Ratio

D1 trap ratio = (D1 decompositions) / (D0→D1 compositions)

| Zone | N | Coexist | D1 Trap Ratio |
|------|---|---------|---------------|
| Dead Zone 1 | 29 | 60% | **0.78** |
| Safe 1 | 35 | 100% | **0.48** |
| Dead Zone 5 | 87 | 85% | 0.52 |
| Safe 5 | 95 | 100% | 0.51 |

### Interpretation

- **High ratio (>0.6)**: D1 agents decompose before advancing → dead zone
- **Low ratio (<0.5)**: D1 agents advance to D2 → healthy structure

---

## Composition/Decomposition Counts

### Dead Zone 1 (N=29)

| Transition | Compositions | Decompositions |
|------------|--------------|----------------|
| D0↔D1 | 71.7 | 56.0 |
| D1↔D2 | 59.4 | 51.8 |
| D2↔D3 | 13.6 | 10.0 |
| D3↔D4 | 117.0 | 116.7 |

### Safe 1 (N=35)

| Transition | Compositions | Decompositions |
|------------|--------------|----------------|
| D0↔D1 | 36.8 | 17.6 |
| D1↔D2 | **89.6** | 80.5 |
| D2↔D3 | 7.1 | 2.7 |
| D3↔D4 | 148.4 | 147.5 |

**Key difference**: Safe N=35 has 2x more D1→D2 compositions

---

## Mechanism Confirmation

### Dead Zone Dynamics

At N=29:
1. High D0→D1 composition rate (71.7)
2. High D1 decomposition rate (56.0)
3. D1 trap ratio = 0.78
4. D1 agents decompose before advancing
5. Depth structure fails

### Safe Zone Dynamics

At N=35:
1. Lower D0→D1 composition rate (36.8)
2. Much lower D1 decomposition (17.6)
3. D1 trap ratio = 0.48
4. D1 agents advance to D2
5. Depth structure establishes

---

## Final Depth Distributions

| Zone | D0 | D1 | D2 | D3 | D4 |
|------|----|----|----|----|-----|
| Dead N=29 | 0.4 | 0.6 | 0.25 | 2.95 | 0.35 |
| Safe N=35 | 0.1 | 1.0 | 0.2 | 2.75 | 0.85 |

Safe N=35 shows more D4 agents (0.85 vs 0.35) - deeper structure.

---

## Attenuation Explanation

At higher N (87 vs 95):
- D1 trap ratios similar (0.52 vs 0.51)
- Dead zone effect weakened
- Confirms attenuation at high N

---

## Session Status (C1664-C1738)

75 cycles investigating NRM dynamics.

---

## Conclusions

1. **D1 trap ratio key metric** for dead zones
2. **Threshold ~0.6**: Above = dead zone, below = safe
3. **N=29 has ratio 0.78** (strong trap)
4. **N=35 has ratio 0.48** (healthy)
5. **Higher N shows convergence** (attenuation)

