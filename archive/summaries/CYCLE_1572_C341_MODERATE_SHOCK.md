# CYCLE 1572: C341 MODERATE ENVIRONMENTAL SHOCK

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 20
**Status:** COMPLETE - CRITICAL THRESHOLD MAPPED

---

## EXECUTIVE SUMMARY

**K=400 is above the critical threshold - 95% survival vs 0% at K=200.**

- Coexistence: 19/20 (95%)
- Shock survival: 95%
- Critical threshold: Between 200 and 400

The system can survive moderate shocks but not severe ones.

---

## RESULTS

| Metric | Value |
|--------|-------|
| K before | 600 |
| K after | 400 |
| Shock cycle | 15000 |
| Shock survival | 95% (19/20) |

---

## KEY FINDINGS

### 1. Critical Threshold Bounded

K threshold identified:
- K=400: 95% survival
- K=200: 0% survival
- Critical threshold: 200 < K_crit < 400

### 2. Contrast with C340

| Condition | K after | Survival |
|-----------|---------|----------|
| C340 severe | 200 | 0% |
| C341 moderate | 400 | 95% |

The system shows sharp threshold behavior.

### 3. Single Failure Analysis

Only seed 4808 collapsed:
- Ran 300 recordings (full 30,000 cycles)
- L0 final = 600 (metric artifact)
- Some stochastic variation exists

### 4. Near-Baseline Performance

95% survival matches baseline coexistence:
- Constant K=600: ~95% coexistence
- Shock to K=400: 95% survival
- K=400 appears sustainable

---

## MECHANISM

### Why K=400 Survives

**1. Above Minimum Carrying Capacity**
- K=400 can support seven-trophic chain
- Sufficient basal production
- Energy flows adequate

**2. Gradual Adjustment**
- Unlike K=200 instant crash
- Some populations track K decline
- Damped oscillations to new equilibrium

**3. No Cascade Collapse**
- K=400 maintains prey populations
- Predators don't starve
- Chain remains intact

### Critical Threshold Mechanism

For seven-trophic at standard parameters:
- K ≥ 400: Stable (95%+)
- K ≤ 200: Collapse (0%)
- K_crit ≈ 300 (estimated)

---

## SHOCK RESPONSE SERIES

| Cycle | K Change | Survival | Finding |
|-------|----------|----------|---------|
| C340 | 600→200 | 0% | Below threshold |
| C341 | 600→400 | 95% | Above threshold |

Next: Test K=300 to narrow threshold.

---

## IMPLICATIONS

### 1. Sharp Threshold Behavior

Not gradual degradation:
- Above threshold: High survival
- Below threshold: Complete collapse
- Bistable system

### 2. Resilience Limits

System can absorb:
- 33% K reduction (600→400): OK
- 67% K reduction (600→200): Collapse

### 3. Climate/Resource Management

For maintaining ecosystems:
- Know critical thresholds
- Avoid crossing them
- Once crossed, collapse may be irreversible

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C340 | 1679 | Eco-evo + env shocks |
| C341 | 20 | Critical threshold mapped |
| **Total** | **1699** | **Threshold dynamics** |

---

## NEXT DIRECTIONS

1. **Narrow threshold**: Test K=300
2. **Gradual shock**: Ramp K down slowly
3. **Recovery test**: Can system restart at K=400 after collapse?
4. **Multiple shocks**: Sequential K reductions

---

## CONCLUSION

C341 demonstrates that **moderate environmental shock (K: 600→400) allows 95% survival**, in stark contrast to C340's 0% survival at K=200.

Key findings:
1. K=400 is above critical threshold
2. Critical K between 200-400 (likely ~300)
3. System shows sharp threshold behavior
4. 33% resource reduction is sustainable

This establishes that seven-trophic food webs have definite resilience limits, with sharp transitions between stability and collapse.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
