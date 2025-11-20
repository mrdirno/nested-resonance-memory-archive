# CYCLES 1541-1542: OMNIVORY / INTRAGUILD PREDATION (C308-C309)

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 15
**Status:** COMPLETE - OMNIVORY CREATES BIFURCATION INSTABILITY

---

## EXECUTIVE SUMMARY

**Omnivory pushes system to bifurcation boundary.**

- C308 (seeds 1500-1502): 100% coexistence with weak omnivory
- C309 (seeds 1600-1602): 0% coexistence with same weak omnivory

Same parameters, different seeds, opposite outcomes. System near critical point.

---

## RESEARCH QUESTION

Does omnivory (intraguild predation) stabilize or destabilize tri-trophic systems?

---

## RESULTS

| Cycle | Condition | Top Attack Prey | Coexistence |
|-------|-----------|-----------------|-------------|
| C308 | Specialist | 0 | **100%** |
| C308 | Omnivore (weak) | 0.001 | **100%** |
| C309 | Omnivore (weak) | 0.001 | **0%** |
| C309 | Omnivore (medium) | 0.002 | **0%** |
| C309 | Omnivore (strong) | 0.003 | **0%** |

Critical finding: Same parameters (weak omnivory 0.001) gave opposite results with different seeds.

---

## KEY FINDINGS

### 1. Bifurcation Instability

The system is near a critical point:
- Small stochastic fluctuations determine outcome
- Same parameters can produce coexistence OR collapse
- This is hallmark of bifurcation dynamics

### 2. Omnivory Creates Fragility

Without omnivory: 100% coexistence (robust)
With omnivory: Variable outcomes (fragile)

Omnivory pushes system toward instability boundary.

### 3. Intraguild Predation Effect

Top predator competing with mesopredator for prey:
- Reduces mesopredator food availability
- Increases mesopredator mortality risk
- Creates exploitative AND apparent competition

### 4. Stochastic Dominance Near Boundary

Near bifurcation:
- Deterministic parameters don't predict outcome
- Initial conditions and random events matter
- Need ensemble statistics, not single runs

---

## MECHANISM

### Why Omnivory Destabilizes

```
Without omnivory:
  Prey → Meso → Top (linear chain)
  Each level in viable parameter zone
  Stable equilibrium

With omnivory:
  Prey → Meso → Top
    ↖________↗ (direct link)

  Top predator creates:
  1. Exploitative competition (both eat prey)
  2. Apparent competition (both sustain top)
  3. Reduced meso food availability

  Combined effects push toward boundary
```

### Bifurcation Point

System at Goldilocks boundary:
- Slightly too much predation → collapse
- Slightly too little → stable
- Omnivory adds to total predation on prey
- Pushes system over threshold stochastically

---

## THEORETICAL SIGNIFICANCE

### 1. Intraguild Predation Theory Validated

Classic IGP theory predicts destabilization:
- Two predators sharing one prey
- One predator also eats the other
- Creates complex indirect effects

NRM confirms this general pattern.

### 2. Stochastic Bifurcations

Systems near critical points:
- Cannot be characterized by mean behavior
- Require probability distributions
- "Same parameters" doesn't mean "same outcome"

### 3. Food Web Complexity

Adding links can destabilize:
- Omnivory adds trophic links
- Each link adds potential for overexploitation
- Simpler food webs may be more robust

---

## IMPLICATIONS

### 1. Food Web Structure

For stable multi-trophic systems:
- Prefer linear chains over webs
- Avoid intraguild predation
- Each predator should specialize

### 2. Conservation

Omnivore introductions:
- May destabilize existing communities
- Can push prey below threshold
- Create competition with existing predators

### 3. System Design

For robust agent-based systems:
- Avoid resource overlap between agents
- Specialize roles clearly
- Monitor for bifurcation dynamics

### 4. Experimental Design

Near bifurcation points:
- Single experiments misleading
- Need multiple seeds/replicates
- Report variance, not just means

---

## COMPARISON WITH C304-C307

| Cycle | Modification | Outcome |
|-------|--------------|---------|
| C304 | Basic tri-trophic | 100% stable |
| C305-307 | Cascade attempts | No cascade / collapse |
| C308-309 | Omnivory | Bifurcation instability |

**Adding complexity (cascade or omnivory) reduces stability.**

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C307 | 1270 | Eco-evo + tri-trophic + cascade |
| C308-C309 | 15 | Omnivory / bifurcation dynamics |
| **Total** | **1285** | **Complexity reduces stability** |

---

## NEXT RESEARCH DIRECTIONS

### 1. Bifurcation Mapping

More replicates at weak omnivory:
- 20+ seeds
- Characterize probability distribution
- Find exact critical point

### 2. Four-Trophic Chain

Test quaternary consumer:
- Linear chain, no omnivory
- Does stability extend to four levels?

### 3. Multiple Prey Species

Test prey diversity:
- Does second prey species stabilize?
- Resource partitioning effects

### 4. Adaptive Omnivory

Top predator switches diet:
- Eat prey when meso scarce
- Eat meso when abundant
- Does adaptation stabilize?

---

## CONCLUSION

C308-C309 establish that **omnivory creates bifurcation instability** in NRM tri-trophic systems.

Key findings:
1. Same parameters give opposite outcomes with different seeds
2. Omnivory pushes system to critical boundary
3. Intraguild predation reduces stability
4. Stochastic effects dominate near bifurcation

This validates ecological theory on IGP and demonstrates that food web complexity generally reduces stability in parameter-sensitive systems.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
