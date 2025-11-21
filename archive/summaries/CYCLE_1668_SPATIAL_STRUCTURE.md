# Cycle 1668: Spatial Structure

**Date:** November 20, 2025
**Cycle:** 1668
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Added spatial dimension with local interactions (10x10 grid).

**Key Finding: Spatial structure reduces coexistence (70% vs 80%)**

---

## Results

| Structure | Coexistence | Avg Depths |
|-----------|-------------|------------|
| Global | 80% | 3.4 |
| Spatial (10x10) | 70% | 3.2 |

---

## Mechanism

### Why Spatial Hurts

1. **Limited composition pool**: Agents can only compose with neighbors (4-connected)
2. **Fragmented populations**: Agents spread across 100 cells
3. **Resonance scarcity**: Fewer opportunities for energy-similar pairs

### Global Advantage

- All agents can compose with any other agent
- Maximum resonance opportunities
- No spatial bottlenecks

---

## Conclusion

Spatial structure is not beneficial for composition-decomposition dynamics. The global mixing is essential for maintaining high composition rates.

This aligns with C1658 finding that circular flow also hurts - any restriction on energy/composition flow reduces coexistence.

---

## Session Status (C1648-C1668)

21 cycles investigating NRM dynamics:
- Trophic: 0%
- Comp-decomp: 72-80%
- Spatial structure: **70%** (hurts)

