# Cycle 1708: D1 Decomposition Trap

**Date:** November 21, 2025
**Cycle:** 1708
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated why high offspring ratio is detrimental at n=30.

**FINDING: D1 Decomposition Trap - D1 agents decompose before composing to D2**

---

## Results

### D1 Dynamics

| N | Off% | D0→D1 | D1→D2 | Decomp | Coexist |
|---|------|-------|-------|--------|---------|
| 20 | 80.8% | 72.9 | **236.6** | 61.6 | 97% |
| 25 | 73.4% | 90.1 | **158.9** | 76.1 | 93% |
| 30 | 80.2% | **177.7** | 67.8 | **161.1** | 73% |
| 35 | 68.5% | 59.4 | 144.8 | 39.7 | 100% |

---

## Key Finding: D1→D2 Bottleneck

### n=30 Paradox

- **Most D0→D1**: 177.7 compositions
- **Fewest D1→D2**: 67.8 compositions
- **Most D1 decompositions**: 161.1

D1 agents created at n=30 decompose instead of advancing.

### The Trap Mechanism

1. High offspring ratio creates many D1 agents
2. But D1 agents have higher energy (from C1704: 0.889 vs 0.823)
3. Higher energy → exceed decomposition threshold (1.3)
4. D1 decomposes back to D0
5. D2+ cannot establish → low coexistence

---

## Why n=25 Succeeds

- Lower D0→D1 count (90.1 vs 177.7)
- But higher D1→D2 (158.9 vs 67.8)
- Fewer decompositions (76.1 vs 161.1)
- D1 agents have lower energy → survive to compose

---

## Refined Mechanism

### Complete Picture

```
n=25 optimal because:
1. Offspring ratio in optimal range (73.4%)
2. D1 creation energy low enough to survive
3. D1 agents advance to D2 before decomposing
4. Multi-depth structure establishes
```

### n=30 Failure Mode

```
n=30 fails because:
1. Too many D0→D1 compositions (177.7)
2. But D1 energy too high
3. D1 decomposes (161.1) instead of advancing
4. D2+ cannot establish
```

---

## Theoretical Implications

### Energy Balance Critical

Success requires D1 energy to be:
- High enough to compose to D2
- Low enough to not decompose

n=25 achieves this balance.
n=30 creates D1 with energy too high.

### Two Failure Modes

1. **Too few compositions** (n=15): Not enough D1 created
2. **D1 trap** (n=30): D1 created but decomposes

n=25 avoids both.

---

## Session Status (C1664-C1708)

45 cycles investigating NRM dynamics:
- Complete 10D characterization
- Mechanism established
- **D1 decomposition trap identified (C1708)**

---

## Conclusions

1. **D1→D2 ratio is key metric**, not just offspring ratio
2. **n=30 has D1 decomposition trap**: most D0→D1 but fewest D1→D2
3. **n=25 avoids trap**: lower energy D1 survives to advance
4. **Success requires energy balance at D1**

