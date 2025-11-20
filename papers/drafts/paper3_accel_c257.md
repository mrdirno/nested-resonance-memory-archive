# Paper 3 (C257): H1 x H5 Interaction (Pilot-Accelerated)

**Status:** ✅ SUPERSEDED (Pilot-Accelerated)
**Date:** 2025-11-19
**Cycle:** 14

## Abstract
We utilized the Pilot-Accelerated method to investigate the interaction between Energy Pooling (H1) and Energy Recovery/Efficiency (H5). Pilot simulations (100 cycles) reveal a **SYNERGISTIC** interaction (Synergy: +2.66).

## Results
- **Synergy Score:** +2.66 (Synergistic)
- **Mechanism:** **Safety Net Synergism**.
    - **H5 (Recovery):** Provides a boost to agents when they fall below critical energy levels (emergency recovery).
    - **H1 (Pooling):** Redistributes energy, keeping the population tighter around the mean.
    - **Interaction:** Pooling prevents agents from dying instantly, keeping them in the "recovery zone" long enough for H5 to kick in. Conversely, H5 injects new energy into the bottom of the distribution, which H1 then redistributes to the rest of the population. The two mechanisms cover each other's weaknesses: H1 handles variance, H5 handles absolute deficits.
    
## Conclusion
The interaction is **SYNERGISTIC**. Collective redistribution amplifies the benefit of individual recovery mechanisms.
