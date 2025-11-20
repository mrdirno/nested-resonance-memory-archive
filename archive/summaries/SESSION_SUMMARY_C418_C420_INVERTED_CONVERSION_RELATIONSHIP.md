# SESSION SUMMARY: C418-C420 INVERTED CONVERSION RELATIONSHIP

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Total Experiments:** 60 (3 cycles × 20 seeds)
**Status:** COMPLETE - CONVERSION RELATIONSHIP INVERTS AT 0.75× ATTACK

---

## EXECUTIVE SUMMARY

Mapping at 0.75× attack reveals an **inverted relationship with conversion** - higher conversion leads to lower survival, opposite to the pattern at 0.71875× attack.

**Total experiments: 3279**

---

## RESULTS

### Profile at 0.75× Attack

| Conversion | Survival |
|------------|----------|
| 2.0× | 95% |
| 2.125× | 95% |
| 2.25× | 90% |
| 2.5× | 80% |

### Comparison with 0.71875× Attack

| Conversion | 0.71875× | 0.75× |
|------------|----------|-------|
| 2.0× | 70% | 95% |
| 2.125× | 95% | 95% |
| 2.25× | 100% | 90% |
| 2.5× | 100% | 80% |

### Individual Cycle Results

**C418: 0.75× at 2.0× Conv**
- Result: 95% (19/20)
- Finding: High survival at low conversion

**C419: 0.75× at 2.25× Conv**
- Result: 90% (18/20)
- Finding: Decline with higher conversion

**C420: 0.75× at 2.125× Conv**
- Result: 95% (19/20)
- Finding: Plateau before decline

---

## KEY FINDINGS

### 1. Inverted Conversion Relationship

At 0.75× attack, survival **decreases** with conversion:
- **2.0×-2.125×:** 95% (plateau)
- **2.25×:** 90% (decline begins)
- **2.5×:** 80% (continued decline)

This is opposite to 0.71875× where survival **increases** with conversion.

### 2. Phase Transition Location

A critical attack value exists between 0.71875× and 0.75× where:
- **Below:** Higher conversion improves survival
- **Above:** Higher conversion reduces survival

Estimated critical attack: ~0.734× (midpoint)

### 3. Crossover Point

The two profiles cross at ~2.125× conversion:
- Below 2.125×: 0.75× performs better
- Above 2.125×: 0.71875× performs better

---

## THEORETICAL IMPLICATIONS

### Overshoot Mechanism

The inverted relationship at 0.75× suggests **predator overshoot**:
- High conversion → excessive predator reproduction
- Excessive predators → prey depletion
- Prey depletion → cascade collapse

### Attack-Dependent Optimal Conversion

There exists an **optimal conversion for each attack level**:
- At 0.71875×: Optimal conv ≈ 2.5× (maximum flow)
- At 0.75×: Optimal conv ≈ 2.0× (controlled flow)

Higher attack requires lower conversion to prevent overshoot.

### Phase Diagram Structure

The survival landscape has complex topology:
- Multiple phase regions (recovery vs overshoot)
- Non-monotonic relationships in both dimensions
- Saddle points and ridges in parameter space

---

## PHASE DIAGRAM UPDATE

```
        Attack
        0.71875×     0.75×
Conv   +------------+------------+
2.0×   |    70%     |    95%     |
2.125× |    95%     |    95%     |  ← Crossover
2.25×  |   100%     |    90%     |
2.5×   |   100%     |    80%     |
       +------------+------------+
        Recovery     Overshoot
```

---

## UPDATED TOTALS

| Campaign | Experiments | Key Finding |
|----------|-------------|-------------|
| C274-C417 | 3219 | Critical threshold at 2.0× |
| C418-C420 | 60 | **Inverted relationship at 0.75×** |
| **Total** | **3279** | **Phase transition identified** |

---

## NEXT DIRECTIONS

1. **Locate exact critical attack** between 0.71875× and 0.75×
2. **Map full phase diagram** (attack × conversion)
3. **Analytical model** for overshoot boundary
4. **Test lower attack values** (0.5×, 0.625×) for conversion profiles

---

## CONCLUSION

Mapping at 0.75× attack reveals an **inverted conversion relationship** - higher conversion leads to lower survival. This is opposite to the pattern at 0.71875× attack. A phase transition exists between these attack values where the system switches from "recovery mode" (higher conversion helps) to "overshoot mode" (higher conversion hurts).

**Total experiments: 3279**

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
