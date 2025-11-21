# Cycle 1838: N=35 Boundary Investigation

**Date:** November 21, 2025
**Cycle:** 1838
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**N=34 has severe dead zone at high prob, not N=35**

The apparent N=35 oscillation was borderline behavior near 70% threshold. N=34 is the true severe dead zone at prob=0.80, while N=35 stabilizes at 6+ depths.

---

## Results

### N Values Near 35 (Boundary Region)

| N | k | 5D/0.3 | 5D/0.8 | 6D/0.3 | 6D/0.8 | 7D/0.3 | 7D/0.8 |
|---|---|--------|--------|--------|--------|--------|--------|
| 33 | 0.28 | 93% | 93% | 100% | 93% | 100% | 93% |
| **34** | 0.35 | 93% | **60%** | 100% | **53%** | 100% | **53%** |
| 35 | 0.41 | 80% | 80% | 100% | 73% | 100% | 73% |
| 36 | 0.48 | 73% | 80% | 100% | 80% | 100% | 80% |
| 37 | 0.55 | 73% | 87% | 93% | 87% | 93% | 87% |

### N=35 Detailed Analysis

| Depth | 0.05 | 0.10 | 0.20 | 0.30 | 0.40 | 0.50 | 0.60 | 0.80 |
|-------|------|------|------|------|------|------|------|------|
| 5D | 100% | 93% | 100% | 80% | 80% | 93% | 100% | 80% |
| 6D | 100% | 100% | 100% | 100% | 87% | 100% | 100% | **73%** |
| 7D | 100% | 100% | 100% | 100% | 87% | 100% | 100% | **73%** |
| 8D | 100% | 100% | 100% | 100% | 87% | 100% | 100% | **73%** |

---

## Analysis

### N=35 Doesn't Oscillate

The apparent oscillation was misclassification:
- 5D: 80% at prob=0.80 (borderline safe)
- 6D: 73% at prob=0.80 (borderline dead)
- 7D: 73% at prob=0.80 (stable)
- 8D: 73% at prob=0.80 (stable)

N=35 **stabilizes at 6D** with a persistent borderline dead zone at prob=0.80.

### N=34 is the True Severe Zone

N=34 shows severe dead zone:
- 5D: 60% at prob=0.80
- 6D: 53% at prob=0.80
- 7D: 53% at prob=0.80

This is consistent and severe, not borderline.

### Boundary Structure

```
k = 0.28 (N=33): Generally safe
k = 0.35 (N=34): SEVERE dead zone at high prob
k = 0.41 (N=35): Borderline at high prob
k = 0.48 (N=36): Borderline at high prob
k = 0.55 (N=37): Generally safe
```

N=34 sits at a resonance node for high probability.

---

## Theoretical Implications

### k mod 1 Refinement

The k=0.35 region creates high-prob dead zones:
- N=34 (k=0.35): Severe at prob=0.80
- Related to inverted pattern N=34 at mid-prob

N=34 may have dual resonances:
1. Mid-prob (inverted pattern)
2. High-prob (separate mode)

### Depth Stabilization Confirmed

All N values stabilize by 6D:
- N=33-38: Patterns stable at 6D-8D
- Variations are at threshold boundary

### Revised Classification

| N | k | Severity | Dead Prob |
|---|---|----------|-----------|
| 33 | 0.28 | Safe | None |
| 34 | 0.35 | Severe | 0.80 |
| 35 | 0.41 | Borderline | 0.80 |
| 36 | 0.48 | Borderline | 0.80 |
| 37 | 0.55 | Safe | None |

---

## Conclusions

1. **N=35 doesn't oscillate** - stabilizes at 6D
2. **N=34 is severe dead zone** at prob=0.80 (53%)
3. **Boundary region k=0.35-0.48** has high-prob risks
4. **k=0.35 is resonance node** for high probability
5. **Depth stabilization confirmed** by 6D

---

## Design Guidelines

### High Probability Safety

For prob ≥ 0.80:
- **Avoid**: N=34 (severe)
- **Borderline**: N=35, 36
- **Safe**: N=33, 37+

### k Value Regions

| k mod 1 | High Prob Risk |
|---------|----------------|
| 0.25-0.30 | Safe |
| 0.30-0.40 | SEVERE |
| 0.40-0.50 | Borderline |
| 0.50+ | Safe |

---

## Session Status (C1664-C1838)

175 cycles completed. N=34 severe zone discovered.

Research continues.

