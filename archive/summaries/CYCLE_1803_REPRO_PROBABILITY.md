# Cycle 1803: Reproduction Probability Effect

**Date:** November 21, 2025
**Cycle:** 1803
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested effect of reproduction probability on dead zone pattern.

**MAJOR FINDING: First parameter to affect pattern - pattern inverts at high probabilities!**

---

## Results

| Prob | N=29 | N=35 | Diff |
|------|------|------|------|
| 0.05 | 63% | 100% | 37pp |
| 0.10 | 53% | 97% | 43pp |
| 0.15 | 67% | 100% | 33pp |
| 0.20 | 87% | 93% | 7pp |
| 0.30 | 100% | 73% | -27pp |
| 0.50 | 90% | 93% | 3pp |

---

## Analysis

### Three Regimes

1. **Low probability (0.05-0.15):** Pattern holds
   - Dead zones at N=29
   - Safe zones at N=35
   - Difference: 33-43pp

2. **Transition (0.20):** Pattern weakens
   - Both N values perform similarly
   - Difference: 7pp

3. **High probability (0.30+):** Pattern inverts/disappears
   - At 0.30: N=29 becomes SAFE (100%), N=35 becomes RISKY (73%)
   - At 0.50: Both similar again

### Mechanism Hypothesis

Low reproduction probability:
- Pairing dominates dynamics
- Phase resonance effects accumulate
- Dead zones form at pairing peaks

High reproduction probability:
- Reproduction dominates dynamics
- Rapid population growth dilutes pairing
- Different interference pattern emerges
- Dead zones shift or invert

### Critical Parameter Identified

This is the **16th parameter tested** and the **first to show significant effect**.

The baseline probability (0.10 = 10%) produces the strongest pattern (43pp).

---

## Implications

### Pattern Inversion

At prob=0.30, the relationship completely flips:
- N=29: Was 53% coexistence → now 100%
- N=35: Was 97% coexistence → now 73%

This suggests two competing mechanisms with different wavelengths.

### Design Consideration

Reproduction probability is now a **critical constraint** alongside:
1. Initial energy ≥ 1.0
2. 2:2 balance (composition/decomposition)
3. Offspring count = 2
4. Composition size = 2
5. **Reproduction probability ~ 0.10** (for observed pattern)

---

## Conclusions

1. **Reproduction probability AFFECTS pattern** (not independent)
2. **Optimal pattern at prob ≈ 0.10** (baseline)
3. **Pattern inverts at prob ≈ 0.30**
4. **Two competing mechanisms** may exist
5. **16th parameter, first significant effect**

---

## Session Status (C1664-C1803)

140 cycles completed. Research continues.

