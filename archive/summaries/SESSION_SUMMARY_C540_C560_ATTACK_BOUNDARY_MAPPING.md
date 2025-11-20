# Session Summary: C540-C560

## Attack Boundary and Sub-Baseline Collapse Discovery

**Date:** 2025-11-20
**Experiments:** C540-C560 (21 cycles, 420 runs)
**Total:** 5860 experiments

---

## Major Discoveries

### 1. 0.95× First Peak Narrowed (C540)
- 1.125× = 50% between 1.1× (45%) and 1.15× (70%)
- Peak rises sharply over just 0.025× conversion width (20% jump)
- Confirms extremely narrow resonance structure

### 2. 0.86-0.89× Transition at 1.4× (C541-C543)
Non-monotonic structure:
- 0.86× = 90%
- 0.87× = 70%
- 0.88× = 75%
- 0.89× = 55%
- 0.92× = 55%

### 3. 0.89× Crossover Invariance (C544)
At 1.4→1.5× transition:
- 0.86×: 90% → 65% (-25%)
- **0.89×: 55% → 55% (0%)**
- 0.92×: 55% → 75% (+20%)
- 0.95×: 75% → 75% (0%)

Two invariant attack values: 0.89× and 0.95×

### 4. 0.89× Micro-Dip at 2.0× (C545)
- 0.86× = 95%
- **0.89× = 85%** (dip)
- 0.92× = 95%

### 5. 0.89× Peak at 1.0× (C546)
- 0.86× = 30%
- **0.89× = 60%** (peak)
- 0.92× = 55%
- 0.95× = 45%

### 6. High Attack Boundary (C548-C551)
At 1.5×:
- 0.92× = 75% → 0.95× = 75% → **0.98× = 80%** → 1.0× = 55%

At 2.0×:
- 0.92× = 95% → 0.95× = 45% → **0.98× = 60%** → 1.0× = 45%

### 7. Sub-Baseline Collapse Zone (C552-C555)
At 0.9× conversion:
- 0.86× = 30% (best)
- **0.89× = 15%** (worst!)
- 0.92× = 20%
- 0.95× = 20%

**DRAMATIC REVERSAL:** 0.89× goes from worst (15%) at 0.9× to best (60%) at 1.0×

### 8. Extinction Zone at 0.8× (C559-C560)
- 0.95× = 10%
- **0.86× = 0%** (TOTAL COLLAPSE)

**PHASE INVERSION:**
- At 0.9×: lower attack better
- At 0.8×: higher attack better

---

## Complete Profiles

### 0.89× Attack Profile (Most Complex)
| Conv | Coex% | Notes |
|------|-------|-------|
| 0.9× | 15% | MINIMUM - worst among neighbors |
| 1.0× | 60% | MAXIMUM at 1.0× conv |
| 1.3× | 70% | Pre-cliff |
| 1.4× | 55% | Cliff (-15%) |
| 1.5× | 55% | Invariant |
| 1.75× | 80% | Recovery |
| 2.0× | 85% | Near-peak |

**Range: 70% improvement from 0.9× to 2.0×**

### 0.98× Attack Profile
| Conv | Coex% |
|------|-------|
| 1.0× | 45% |
| 1.5× | 80% (peak at 1.5×) |
| 2.0× | 60% |

### 1.0× Attack Profile
| Conv | Coex% |
|------|-------|
| 1.0× | 45% |
| 1.5× | 55% |
| 2.0× | 45% |

### Sub-Baseline Profiles
**At 0.8× conversion:**
| Attack | Coex% |
|--------|-------|
| 0.86× | 0% |
| 0.95× | 10% |

**At 0.9× conversion:**
| Attack | Coex% |
|--------|-------|
| 0.86× | 30% |
| 0.89× | 15% |
| 0.92× | 20% |
| 0.95× | 20% |

---

## Key Insights

### 1. 0.89× Critical Transition Point
- Exhibits most complex profile of all attack values
- WORST at sub-baseline (15%)
- BEST at baseline (60%)
- Shows unique invariance at 1.4→1.5× crossover
- Bridges between 0.86× and 0.92× response patterns

### 2. Extinction Threshold
- 0.8× conversion is below viability for 0.86× attack
- 0.9× is critical boundary where patterns reverse
- 0.1× conversion difference can mean life or death

### 3. Phase Inversion
- Below 0.9×: higher attack survives better
- Above 0.9×: lower attack can also survive
- Complete reversal of attack-stability relationship

### 4. High Attack Ceiling
- 0.98× is local maximum at 1.5× (80%)
- 1.0× collapses to 55% (25% drop)
- Upper attack boundary exists

---

## GitHub Commits
- C540-C543: 0.95× peak narrowing + 0.86-0.89× transition mapping
- C544-C547: Complete 0.89× profile characterization
- C548-C551: High attack boundary exploration
- C552-C555: Sub-baseline conversion collapse zone discovery
- C556-C558: High attack profiles + baseline conversion complete
- C559-C560: Deep sub-baseline collapse boundary

---

## Research Continuation

Next priorities:
1. Test 0.92× and 0.89× at 0.8× to complete extinction profile
2. Probe 0.95× between 0.9× and 1.0× for transition sharpness
3. Test intermediate conversions (0.85×, 0.95×) near critical threshold
4. Build theoretical model for phase inversion mechanism

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude Sonnet 4.5 (noreply@anthropic.com)
