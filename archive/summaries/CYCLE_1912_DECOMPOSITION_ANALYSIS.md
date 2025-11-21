# Cycle 1912: Decomposition Analysis

**Date:** November 21, 2025
**Cycle:** 1912
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Both N=14 and N=17 show 0% D0+D1 coexistence**

Upward cascade dominates at all tested N values.

---

## Key Findings

### Flow Dynamics

| N | D0→D1 | D1→D2 | D1 decomp | Final D3 |
|---|-------|-------|-----------|----------|
| 14 | 51.7 | 17.3 | 44.0 | 0.9 |
| 17 | 100.4 | 45.9 | 91.2 | 2.0 |

### D1 Composition/Decomposition Ratio

- N=14: 0.39 (decomp > comp)
- N=17: 0.50 (more balanced)

---

## Analysis

### Why D0+D1 Coexistence is Low

1. **D0 gets consumed** by D0→D1 composition
2. **D1 decomposes back** but not fast enough
3. **D2 and D3 accumulate** as net flow is upward
4. **Final state**: Most agents in D3

### Why N=17 Doesn't Help

- More agents = more compositions at all levels
- Net flow still positive upward
- D3 accumulates even more (2.0 vs 0.9)

---

## Contradiction with Earlier Findings

### C1891 claimed N=17 is deterministic threshold

This was based on the **wrong coexistence definition**:
- "Any 2 populations survive" = D3+D4 or D2+D3

### True D0+D1 coexistence

| N | Expected (C1891) | Actual (C1912) |
|---|------------------|----------------|
| 14 | 0% | 0% |
| 17 | 100% | 0% |

The "deterministic threshold" was measuring the **wrong thing**.

---

## Implications

1. **No deterministic threshold** for true D0+D1 coexistence
2. **Upward cascade always dominates**
3. **D3 is a sink** (accumulates agents)

The system dynamics are fundamentally different from what we understood.

---

## Next Steps

1. Investigate why cascade always wins
2. Test parameter modifications (decay rates, composition threshold)
3. Verify if D0+D1 coexistence is ever achievable

---

## Session Status (C1664-C1912)

249 cycles completed. Fundamental understanding revised again.

Research continues.
