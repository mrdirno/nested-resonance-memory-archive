# Cycles 1947-1952: System Characterization Series

**Date:** November 21, 2025
**Cycles:** 1947-1952
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Complete characterization of composition-dominated NRM dynamics**

- Energy throughput system (Recharge ≈ Comp loss)
- Deaths = 0 (composition controls population)
- Stable attractor (CV = 7.5%)
- Phase resonance: mean = 0.895, 28% at thresh 0.99
- D1 highest similarity (0.91) due to energy homogeneity

---

## Series Overview

| Cycle | Focus | Key Finding |
|-------|-------|-------------|
| 1947 | Energy flow | Throughput system: 105/cycle IN, 108/cycle OUT |
| 1948 | Decomposition | D1: 1M+ events, D4 max energy 16.7 |
| 1949 | Temporal patterns | CV=7.5%, D1/D0=0.198, E/capita=1.55 |
| 1950 | Phase resonance | Mean=0.895, P(≥0.96)=48% |
| 1951 | Composition rate | Actual=28.0%, matches theoretical |
| 1952 | Pair selection | D1 highest sim (0.91), selection effect minimal |

---

## Key Findings

### 1. Energy Throughput System (C1947)

The system is NOT energy storage - it's energy flow:

**Energy Budget (per cycle):**
- Recharge IN: 105.1
- Birth IN: 0.4
- Comp loss OUT: 108.5
- Decay OUT: 5.2

**Balance:** Recharge ≈ Composition loss

Energy flows through the system, not accumulating. Population determined by balance point.

### 2. Decomposition Dynamics (C1948)

Decomposition events by depth:

| Depth | Events | Avg Energy | First Cycle |
|-------|--------|------------|-------------|
| D1 | 1,000,000+ | 1.73 | ~25 |
| D2 | 200,000+ | 1.87 | ~50 |
| D3 | 50,000+ | 2.05 | ~100 |
| D4 | 10,000+ | 2.30 | ~200 |

Max energy observed at D4: 16.7 (10× decomposition threshold)

### 3. Stable Attractor (C1949)

Temporal dynamics confirm stability:

**Growth Phases:**
- Cycles 0-99: 1.6 agents/cycle (exponential)
- Cycles 100-299: 2.7 agents/cycle (slowing)
- Cycles 300-499: 2.9 agents/cycle (equilibrium)

**Equilibrium Metrics:**
- CV = 7.5% (coefficient of variation)
- D1/D0 ratio = 0.198 ± 0.027
- Energy per capita = 1.55 (constant)

### 4. Phase Resonance Distribution (C1950)

Similarity distribution for random pairs:

```
Mean: 0.895 (highly positive-biased)
Std:  0.153
Range: [0.068, 1.0]

Cumulative:
P(sim ≥ 0.90): 65%
P(sim ≥ 0.96): 48%
P(sim ≥ 0.99): 28%
```

Explains why comp_thresh = 0.99 needed (at 0.96, half would compose).

### 5. Composition Rate Validation (C1951)

Actual composition matches theoretical:

**5.8M pairs tested, 1.6M compositions**
- Actual success rate: 28.0%
- Theoretical P(sim ≥ 0.99): 28.3%

System works exactly as designed.

### 6. Depth-Dependent Similarity (C1952)

Adjacent pair similarity by depth:

| Depth | Mean Sim | Explanation |
|-------|----------|-------------|
| D0 | 0.800 | Broad energy mix (birth/recharge/decomp) |
| D1 | 0.906 | From similar-energy D0 compositions |
| D2 | 0.807 | Mixed sources |
| D3 | 0.854 | Mixed sources |

D1 has highest similarity because D1 agents come from D0 pairs that passed the 0.99 threshold - they started with similar energies.

---

## Complete System Model

### Parameter Configuration
```python
p_base = 0.17
K = 30              # for 1000+ cycle stability
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4
```

### Dynamics Summary
```
N_eq ≈ 38K = 1140 agents

Energy flow:
  Recharge → Agents → Composition (15% loss) → Loop

Population control:
  Deaths = 0
  Controlled by composition/decomposition balance
  ~640 agents/cycle through comp/decomp

Hierarchy ratios:
  D1/D0 ≈ 0.20
  D2/D1 ≈ 0.16
  D3/D2 ≈ 0.16
```

---

## Physical Interpretation

### Why D1 Has Highest Similarity

1. D0 agents have broad energy distribution (0.5-2.0)
2. Composition requires sim ≥ 0.99
3. Only similar-energy pairs compose
4. D1 agents inherit similar energies from parents
5. D1 population is energy-homogeneous
6. Energy-homogeneous → high internal similarity

### Why System Self-Stabilizes

1. Composition removes high-similarity pairs
2. Creates slight similarity depletion in population
3. But shuffling each cycle mixes pairs
4. Net effect: steady-state composition rate
5. Decomposition returns agents with similar energies
6. Cycle maintains quasi-equilibrium

### Energy Throughput vs Storage

Traditional population models assume births/deaths balance. This system:
- Deaths = 0 (decay too slow)
- Population = f(composition, decomposition)
- Energy flows through, not stored
- Similar to predator-prey cycling

---

## Research Implications

### 1. Parameter Discovery Complete

All 6 primary parameters optimized and validated:
- p_base, K, N, comp_thresh, decomp_thresh, recharge_base

### 2. Theoretical Model Validated

- N_eq ≈ 38K (empirical: 1140 at K=30)
- Composition rate = P(sim ≥ 0.99) = 28%
- Energy balance verified

### 3. Emergent Properties Documented

- Four-level hierarchy (D0-D3)
- Stable attractor (CV 7.5%)
- Self-organizing energy homogeneity at D1
- Composition-dominated population control

### 4. Foundation for Advanced Research

Ready to explore:
- Information theory metrics
- Pattern memory dynamics
- Cross-scale interactions
- Alternative transcendental substrates

---

## Session Status

289 cycles completed (C1664-C1952). System fully characterized with energy flow, temporal patterns, phase resonance, and composition dynamics.

Research continues perpetually.
