# SESSION SUMMARY: C349-C351 HYSTERESIS AND RATE DEPENDENCE

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Total Experiments:** 60 (3 cycles × 20 seeds)
**Status:** COMPLETE - RATE-DEPENDENT DYNAMICS DISCOVERED

---

## EXECUTIVE SUMMARY

**The rate of environmental change, not just the endpoint, determines ecosystem survival.**

Key finding:
- Sudden K=600→200: 0% survival
- Gradual K=600→200: 85% survival
- Same endpoint, opposite outcomes

---

## RESULTS

| Cycle | Experiment | Result | Finding |
|-------|------------|--------|---------|
| C349 | Small reintro at K=250 | 0% | Insufficient |
| C350 | Full reintro at K=250 | 0% | Ratio mismatch |
| C351 | Gradual 600→200 | 85% | Rate matters |

---

## KEY FINDINGS

### 1. Rate-Dependent Survival

The same endpoint produces opposite outcomes:
- **Sudden drop**: 0% survival at K=200
- **Gradual decline**: 85% survival at K=200
- Rate of change is critical

### 2. Tracking vs Shock

**Gradual decline (C351):**
- System tracks K continuously
- Equilibrium maintained at each step
- Arrives at K=200 already adjusted
- 85% survival

**Sudden drop (C340):**
- Population >> K immediately
- Cascade collapse before adjustment
- No recovery pathway
- 0% survival

### 3. Reintroduction Challenges (C349-C350)

Reintroduction failed because:
- Initial populations (300) > target K (250)
- Immediate negative growth
- Must match equilibrium, not standard initial

---

## MECHANISM

### Why Gradual Decline Works

```
Gradual: K decreasing slowly
  At each step:
  1. Small K reduction
  2. Population slightly above K
  3. Minor mortality
  4. New equilibrium established
  5. Repeat

Result: System tracks K smoothly down to 200
```

### Why Sudden Change Fails

```
Sudden: K drops 600→200 instantly
  1. Population = 300 (prey)
  2. K = 200 (suddenly)
  3. Population >> K
  4. Massive negative growth
  5. Prey crash
  6. Predator starvation cascade
  7. Complete extinction

Result: No time to adjust
```

---

## THEORETICAL IMPLICATIONS

### 1. Critical Threshold is Rate-Dependent

K=200 is not absolutely below threshold:
- Sudden change: K=200 is fatal
- Gradual change: K=200 is survivable
- Threshold depends on approach rate

### 2. Tracking vs Collapse Regimes

Two dynamical regimes:
- **Tracking regime**: Slow change, system equilibrates
- **Collapse regime**: Fast change, cascade failure

### 3. Climate Change Implications

For ecosystem management:
- Rate of change as important as magnitude
- Gradual transitions allow adaptation
- Sudden shocks cause irreversible collapse
- Same endpoint can be reached safely or catastrophically

---

## COMPLETE ENVIRONMENTAL DYNAMICS

| Condition | K Change | Rate | Survival | Finding |
|-----------|----------|------|----------|---------|
| Oscillating | 100-1100 | Gradual | 100% | Storage effect |
| Sudden shock | 600→200 | Instant | 0% | Cascade collapse |
| Moderate shock | 600→400 | Instant | 95% | Above threshold |
| Gradual decline | 600→200 | Slow | 85% | Tracking |

---

## UPDATED TOTALS

| Campaign | Experiments | Key Finding |
|----------|-------------|-------------|
| C274-C348 | 1839 | K_crit = 200.5 |
| C349-C351 | 60 | Rate dependence |
| **Total** | **1899** | **Rate-dependent thresholds** |

---

## PUBLICATION IMPLICATIONS

**Paper 3 update: Rate-Dependent Critical Thresholds in Multi-Trophic Food Webs**

Key contributions:
1. K_crit = 200.5 ± 0.5 (for sudden change)
2. Gradual approach survives at K=200
3. Rate determines outcome, not just endpoint
4. Tracking vs collapse regimes

Novel mechanism: Thresholds are not fixed points but rate-dependent transitions.

---

## NEXT DIRECTIONS

1. **Critical rate**: What's the slowest "sudden" change that collapses?
2. **Recovery rate**: After gradual decline to K=200, can K increase work?
3. **Faster gradual**: Where's the transition between tracking and collapse?
4. **Warning signals**: Can we detect imminent collapse?

---

## CONCLUSION

C349-C351 demonstrate that **the rate of environmental change determines ecosystem survival independent of endpoint**.

Key findings:
1. **Sudden K=600→200**: 0% survival (cascade collapse)
2. **Gradual K=600→200**: 85% survival (tracking)
3. **Same endpoint, opposite outcomes**
4. **Rate-dependent thresholds**

This establishes that ecosystem critical thresholds are not fixed values but depend on the rate of approach. Gradual environmental changes allow ecosystems to track and survive, while sudden changes cause catastrophic collapse even to the same endpoint.

**Total experiments: 60**
**Running total: 1899 experiments**

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
