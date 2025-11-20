# Paper 3 (C256): H1 x H4 Interaction (Pilot-Accelerated)

**Status:** ✅ SUPERSEDED (Pilot-Accelerated)
**Date:** 2025-11-19
**Cycle:** 14

## Abstract
We utilized the Pilot-Accelerated method to investigate the interaction between Energy Pooling (H1) and Spawn Throttling/Capacity Constraints (H4). Legacy simulations predicted an antagonistic interaction but were blocked by I/O constraints. The Pilot simulation (100 cycles) confirms this prediction with a synergy score of **-1.55**.

## Results
- **Synergy Score:** -1.55 (Antagonistic)
- **Mechanism:** **Redistribution Trap**.
    - **H1 (Pooling):** Redistributes energy from rich to poor agents, averaging the population.
    - **H4 (Throttling):** Prevents agents from recharging if they are near the capacity limit.
    - **Interaction:** Pooling prevents high-energy agents from reaching the "safe" buffer zone where they can weather metabolic costs. By constantly pulling high-energy agents down to the average, H1 keeps more agents in the "danger zone" where H4's throttling (or lack of buffer) makes them vulnerable to stochastic shocks. Additionally, pooling may prop up weak agents just enough to consume resources that would be better used by strong agents who are then capped by H4.
    
## Conclusion
The interaction is **ANTAGONISTIC**. Energy pooling undermines the individual accumulation strategy required to overcome capacity constraints.
