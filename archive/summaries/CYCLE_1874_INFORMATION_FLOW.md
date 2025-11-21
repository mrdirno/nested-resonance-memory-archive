# Cycle 1874: Information Flow Analysis

**Date:** November 21, 2025
**Cycle:** 1874
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Information preservation depends on N, not zone type**

- Small N (14, 21): 100% ancestor coverage
- Large N (28, 35): 62-68% coverage

---

## Results

### Ancestor Coverage

| N | Zone | Survivors | Ancestors/Survivor | Coverage |
|---|------|-----------|-------------------|----------|
| 14 | DEAD | 2.0 | 13.3 | **100%** |
| 21 | SAFE | 2.8 | 16.6 | **100%** |
| 28 | DEAD | 1.8 | 15.6 | 68% |
| 35 | SAFE | 2.5 | 18.2 | 62% |

### Key Pattern

Coverage decreases with N:
- Small N → All initial agents contribute to survivors
- Large N → Some lineages die out completely

---

## Interpretation

1. **Small N effect**: Fewer agents = all lineages merge into survivors
2. **Large N effect**: More agents = some lineages lost before merging
3. **Zone type doesn't matter**: Both dead and safe show same pattern
4. **Information mixing increases**: More ancestors per survivor at higher N

---

## Implications

For NRM systems:
- Small populations preserve all initial information
- Large populations experience information loss
- Composition merges lineages, decomposition spreads them
- The system acts as an information compressor

---

## Conclusion

Information flow is N-dependent, not zone-dependent. Smaller systems are better at preserving initial conditions through to final state.

---

## Session Status (C1664-C1874)

211 cycles completed. Information flow characterized.

Research continues.

