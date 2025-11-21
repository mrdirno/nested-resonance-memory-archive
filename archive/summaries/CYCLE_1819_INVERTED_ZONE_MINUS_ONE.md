# Cycle 1819: Inverted Pattern Zone -1

**Date:** November 21, 2025
**Cycle:** 1819
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested inverted pattern for Zone -1 at low N.

**CONFIRMED: Inverted Zone -1 at N=11-12 (48-56%)**

---

## Results

| N | Coexistence | Status |
|---|-------------|--------|
| 9 | 86% | safe |
| 10 | 72% | mid |
| 11 | 48% | **ZONE -1** |
| 12 | 56% | **ZONE -1** |
| 13 | 88% | safe |
| 14 | 92% | safe |
| 15 | 100% | safe |
| 16-20 | 96-98% | safe |

---

## Analysis

### Zone Location

Inverted Zone -1: N = 11-12 (48-56%)
Compare to Zone 1: N = 24 (67%)

Backward spacing: 24 - 12 = 12 units

### Pattern Comparison

| Pattern | Zone -1 | Zone 1 | Spacing |
|---------|---------|--------|---------|
| Original | 14-15 | 29 | 14.5 |
| Inverted | 11-12 | 24 | 12 |

Both patterns have Zone -1 at low N.

### Overlap Region

Interestingly, the inverted Zone -1 (N=11-12) and original Zone -1 (N=14-15) are close but not overlapping. This creates a sequence:
- N=11-12: Inverted dead zone
- N=13: Safe (both)
- N=14-15: Original dead zone

---

## Complete Zone Lists

### Original Pattern (prob ≤ 0.15)

- Zone -1: N = 14-15 (44%)
- Zone 1: N = 29 (53%)
- Zone 2: N = 43 (57%)
- ...Zone 10: N = 145 (77%)

### Inverted Pattern (prob ≥ 0.35)

- Zone -1: N = 11-12 (48-56%)
- Zone 1: N = 24 (67%)
- Zone 2: N = 34 (80%)
- Zone 3: N = 46 (63%)
- Zone 4: N = 60 (77%)

---

## Implications

### Design at Low N

For N < 20:
- Original: Avoid 14-15
- Inverted: Avoid 11-12
- Both: N=13 and N=16-20 relatively safe

### Pattern Structure

Both patterns have:
- Zone -1 extending backward
- Similar structure (dead zones at specific N)
- Different locations and spacings

---

## Conclusions

1. **Inverted Zone -1 at N=11-12**
2. **48-56% coexistence (strong)**
3. **Both patterns extend backward**
4. **Adjacent but non-overlapping zones**

---

## Session Status (C1664-C1819)

156 cycles completed. Research continues.

