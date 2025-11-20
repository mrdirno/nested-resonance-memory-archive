# SESSION SUMMARY: C374-C375 PARAMETER INTERACTION ANALYSIS

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Total Experiments:** 40 (2 cycles × 20 seeds)
**Status:** COMPLETE - NEGATIVE INTERACTION CONFIRMED

---

## EXECUTIVE SUMMARY

**Critical finding: Parameters have negative interactions - individual optima don't combine additively.**

When conversion efficiency is already optimal (1.5×), increasing attack rate REDUCES survival.

---

## RESULTS

| Cycle | Attack | Conversion | Survival | Notes |
|-------|--------|------------|----------|-------|
| C371 | 1.0× | 1.5× | **80%** | Conversion optimum |
| C363 | 1.25× | 1.0× | 60% | Attack optimum |
| C374 | 1.25× | 1.5× | 55% | Combined (worse!) |
| C375 | 1.0× | 1.5× | **80%** | Baseline + optimal conv |

---

## KEY FINDINGS

### 1. Negative Parameter Interaction

```
Expected (if additive): 80% + (60% - 50%) = 90%
Actual: 55%
Deficit: 35 percentage points
```

High attack reduces survival when conversion is high:
- 1.0× attack + 1.5× conv: 80%
- 1.25× attack + 1.5× conv: 55%
- **Change: -25 percentage points**

### 2. Mechanism

**Why does high attack hurt with high conversion?**

With 1.5× conversion:
- Predators already reproduce efficiently
- Each prey consumed → high offspring probability
- Adding higher attack rate → more prey depletion
- Prey becomes the limiting resource
- Net negative effect

**Bottleneck shifts:**
- Baseline conversion → predator reproduction is limiting
- High conversion → prey availability is limiting
- High attack accelerates prey depletion → worse outcomes

### 3. Theoretical Implications

**Non-additive parameter effects** imply:
- Cannot optimize parameters independently
- Context-dependent optima
- Ecosystem management requires holistic approach
- Single-parameter interventions may fail

---

## PARAMETER INTERACTION MODEL

```
                    Attack Rate
                 Low (1.0×)  High (1.25×)
              ┌──────────┬──────────┐
Conversion    │          │          │
   Low        │   50%    │   60%    │ +10%
  (1.0×)      │          │          │
              ├──────────┼──────────┤
Conversion    │          │          │
  High        │   80%    │   55%    │ -25%
  (1.5×)      │          │          │
              └──────────┴──────────┘
                 +30%       -5%
```

- At baseline conversion: high attack helps (+10%)
- At high conversion: high attack hurts (-25%)
- **Interaction term: -35%**

---

## THEORETICAL FRAMEWORK

### Resource Limitation Switching

1. **Low conversion state:**
   - Reproductive efficiency is limiting
   - More predation → more reproduction opportunities
   - Higher attack helps

2. **High conversion state:**
   - Prey availability is limiting
   - More predation → faster prey depletion
   - Higher attack hurts

### Optimal Strategy

For maximum survival under K decline:
- **Increase conversion efficiency** (most impactful)
- **Keep attack at baseline** (avoid over-predation)
- **Keep handling at baseline** (minimal sensitivity)

---

## UPDATED TOTALS

| Campaign | Experiments | Key Finding |
|----------|-------------|-------------|
| C274-C368 | 2239 | Rate dynamics, parameter sensitivity |
| C369-C373 | 100 | All parameters dome-shaped |
| C374-C375 | 40 | **Negative parameter interaction** |
| **Total** | **2379** | **Non-additive parameter effects** |

---

## NEXT DIRECTIONS

1. **Full interaction matrix**: Test all attack × conversion combinations

2. **Three-way interactions**: Does handling affect the interaction?

3. **Mechanistic analysis**: Track prey density at failure point

4. **Optimal portfolio**: Find global optimum in parameter space

5. **Rate-dependence of interaction**: Does interaction vary with K decline rate?

---

## CONCLUSION

C374-C375 demonstrate that **parameter interactions are non-additive**. The optimal conversion efficiency (1.5×, 80% survival) is undermined by combining with optimal attack rate (1.25×), yielding only 55% survival.

**Key insight:** Optimal strategies cannot be derived from single-parameter optima. Holistic optimization across parameter space is required.

**Total experiments: 2379**

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
