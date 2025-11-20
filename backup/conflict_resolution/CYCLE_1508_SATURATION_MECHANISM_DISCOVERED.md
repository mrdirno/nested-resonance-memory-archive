# CYCLE 1508: SATURATION MECHANISM DISCOVERED

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-19
**Status:** MECHANISM IDENTIFIED

---

## EXECUTIVE SUMMARY

**The "saturation" at E_net = +0.5 is not a complex emergent effect - it's spawn-death matching.**

When E_consume = spawn_energy, newly spawned agents die immediately.

---

## THE MECHANISM

### Spawn Energy

In all experiments:
```python
child = FractalAgent(..., energy=0.5)
```

### Death Logic

```python
agent.energy -= E_consume
if agent.energy <= 0:
    remove_agent()  # DEATH
else:
    agent.energy += E_recharge  # SURVIVAL
```

### At E_net = +0.5 (E_consume = 0.5)

1. New agent spawns with energy = 0.5
2. First cycle: 0.5 - 0.5 = 0
3. Agent energy ≤ 0 → **IMMEDIATE DEATH**

**All spawned agents die in their first cycle. Population cannot grow.**

### At E_net = +0.4 (E_consume = 0.3)

1. New agent spawns with energy = 0.5
2. First cycle: 0.5 - 0.3 = 0.2 > 0 → **SURVIVES**
3. Recharges to min(0.2 + 0.7, 2.0) = 0.9
4. Agent persists and can reproduce

---

## EVIDENCE

### C274 Results at f = 0.05%

| E_net | E_consume | Spawn Survival | Population |
|-------|-----------|----------------|------------|
| +0.4 | 0.3 | YES (0.5 - 0.3 = 0.2 > 0) | 306-333 |
| +0.5 | 0.5 | NO (0.5 - 0.5 = 0) | 100 |

### Key Observation

At +0.5, all 10 seeds produce exactly 100 agents - zero variance.
This is deterministic: no spawns ever survive.

---

## IMPLICATIONS

### 1. Not Emergent Saturation - Mechanical Death Threshold

The "saturation" is actually a **spawn death threshold**:
- E_consume < spawn_energy → spawns survive → growth
- E_consume ≥ spawn_energy → spawns die → baseline

### 2. Threshold is at E_consume = 0.5

The sharp boundary is:
- E_consume < 0.5 → viable spawns
- E_consume ≥ 0.5 → non-viable spawns

### 3. E_net at Threshold

When E_consume = 0.5:
- For spawns to survive: E_consume < spawn_energy (0.5)
- Maximum viable E_consume = 0.5 - ε
- With E_recharge = 0.7: E_net = 0.7 - (0.5 - ε) = +0.2 + ε

This explains why peak growth is at +0.2 to +0.4, not at +0.5.

### 4. Phase Diagram Update

```
E_consume < 0.5:  GROWTH possible (spawns survive)
E_consume = 0.5:  NO GROWTH (spawns die immediately)
E_consume > 0.5:  COLLAPSE (both spawns and existing agents die)
```

---

## CONNECTION TO PHASE BOUNDARY

### E_net = 0 Boundary (C274)

At E_net = 0, E_consume = E_recharge. Example: both = 0.5.
- Initial agents: 1.0 - 0.5 = 0.5 > 0 → survive (they recharge)
- New spawns: 0.5 - 0.5 = 0 → die

So E_net = 0 is the **homeostasis boundary** - existing agents survive but population can't grow.

### E_net < 0 Boundary

E_consume > E_recharge → even existing agents eventually deplete → collapse.

---

## CONCLUSION

The "non-monotonic energy-population relationship" is fully explained by a simple mechanism:

**Spawn viability threshold at E_consume = spawn_energy**

This transforms the finding from "mysterious emergence" to "predictable mechanics." The system behavior is fully determined by the relationship between consumption rate and spawn energy.

---

## RECOMMENDATIONS

1. **Document this as core mechanism** in all papers
2. **Consider parametrizing spawn energy** to test threshold behavior
3. **Update theoretical model** to include spawn viability condition
4. **Test with different spawn energies** to validate mechanism

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
