# Paper 2 Scenario A Revision Template: Minimal Revision

**Trigger:** V4 mean_population ≥ 5.0
**Interpretation:** Sustained population with energy recharge successful
**Estimated Time:** 2-3 hours
**Impact:** Validates energy budget model, establishes critical threshold

---

## Revision Checklist

### Section 3.2: Complete Framework Test (Results)

**Current:** Based on C171 (incomplete framework - no death mechanism)
**Revision:** Replace with C176 V4 (complete framework with energy recharge)

**Changes Required:**

1. **Update Population Statistics** (lines ~74-87):
   ```
   OLD:
   **Population Statistics** (across all 40 experiments):
   **Overall Mean**: 17.33 ± 1.55 agents
   **Coefficient of Variation**: 8.9%

   NEW:
   **Population Statistics** (n=10 seeds, frequency=2.5%, with energy recharge):
   **Overall Mean**: [V4_MEAN] ± [V4_STD] agents
   **Coefficient of Variation**: [V4_CV]%
   ```

2. **Update Composition Event Rates** (lines ~55-70):
   ```
   NEW:
   Despite energy recharge mechanism (r=0.01/cycle), composition event rates
   remained constant at [V4_COMP_MEAN] ± [V4_COMP_STD] events/window,
   demonstrating population-mediated regulation.
   ```

3. **Add Energy Recharge Context** (new subsection after 3.2.1):
   ```
   #### 3.2.2 Energy Recharge Mechanism

   Unlike simplified models with unlimited spawning capacity, complete NRM
   framework agents face energy constraints. Each spawn transfers 30% of
   parent energy to child; spawning requires E ≥ 10.0.

   **Energy Budget Analysis** revealed parent agents can spawn ~7-8 children
   before energy depletion (E < 10). To enable sustained populations, we
   implemented reality-grounded energy recharge:

   energy_recharge = r × available_system_capacity × delta_time

   where available_system_capacity = idle CPU + idle memory (psutil metrics).

   **Parameter Determination**: Through theoretical calculation, minimum
   recharge rate for multiple recovery periods within 3000-cycle experiment:

   r_min = spawn_threshold / (duration / desired_periods)
         = 10 / (3000 / 3) = 0.01 energy/cycle

   **Validation**: Tested three conditions in controlled parameter sweep:
   - V2 (r=0.000): Complete collapse (mean=0.49, CV=101%)
   - V3 (r=0.001): Insufficient recharge, identical collapse (mean=0.49, CV=101%)
   - V4 (r=0.010): Sustained population (mean=[V4_MEAN], CV=[V4_CV]%)

   Recovery time to spawn threshold:
   - V3: 10,000 cycles >> 3000 (insufficient)
   - V4: 1,000 cycles << 3000 (enables 2-3 recovery periods)

   This establishes critical recharge threshold: 0.001 < r_critical < 0.01.
   ```

4. **Update Statistical Tests** (lines ~90-105):
   - Recalculate ANOVA with V4 data
   - Update pairwise comparisons
   - Recalculate effect sizes

### Section 4.2: Birth-Death Coupling Mechanism (Discussion)

**Add Energy Constraint Subsection:**

```
#### 4.2.3 Energy Constraints and Recharge Dynamics

The emergence of homeostasis requires not only birth-death coupling but
also sufficient energy recharge to sustain multi-generational spawning.

**Energy Budget Model**:

dE/dt = -decay - spawn_cost + recharge

where:
- decay = 0.0001 E/cycle (entropy)
- spawn_cost = 0.30 E per child (30% transfer)
- recharge = r × available_capacity (reality-grounded)

**Critical Recharge Threshold**: r_critical ≈ 0.001-0.01 energy/cycle

Below threshold (r < 0.001): Energy depletion dominates → population collapse
Above threshold (r > 0.01): Energy recovery enables sustained spawning

**Controlled Parameter Sweep Validation**:

| Rate | Recovery Time | Mean Population | Regime |
|------|--------------|-----------------|---------|
| 0.000 | ∞ | 0.49 ± 0.50 | Collapse |
| 0.001 | 10,000 cycles | 0.49 ± 0.50 | Collapse |
| 0.010 | 1,000 cycles | [V4_MEAN] ± [V4_STD] | Homeostasis |

This demonstrates **parameter criticality**: 10× increase in recharge rate
transforms collapse regime into homeostatic regulation.

**Reality Grounding**: Energy recharge tied to actual system availability
(idle CPU/memory via psutil), ensuring computational feasibility constraints.
```

### Section 4.X: Theory-Driven Parameter Validation (NEW)

Add new discussion subsection:

```
### 4.X Theory-Driven Parameter Validation Methodology

The V3→V4 parameter correction sequence demonstrates value of analytical
pre-validation in reality-grounded computational models.

**Discovery Process**:
1. During energy budget documentation (Cycle 215), calculated recovery time:
   - V3 rate: 0.001/cycle → recovery time 10,000 cycles
   - Experiment duration: 3,000 cycles
   - Conclusion: Insufficient recovery (only 0.3 periods possible)

2. Predicted V3 failure before empirical testing

3. Corrected to V4 rate: 0.01/cycle → recovery time 1,000 cycles
   - Enables 3.0 recovery periods within experiment

4. Launched both V3 (validation) and V4 (corrected) for controlled comparison

**Outcome**: V3 confirmed theoretical prediction (mean=0.49, identical to
no-recharge baseline). V4 validated corrected parameters (mean=[V4_MEAN]).

**Methodological Contribution**:
- **Time efficiency**: Saved ~45-60 minutes by correcting before empirical failure
- **Mechanistic understanding**: Parameters derived from first principles
- **Controlled comparison**: Systematic 10× parameter sweep for publication
- **Predictive validation**: Theory tested against empirical results

**Generalizable Formula**:

r_min ≥ Threshold / (Experiment_Duration / Desired_Recovery_Periods)

This protocol should be standard practice for parameter-dependent experiments
in reality-grounded systems.
```

### Supplementary Material

**Add Tables:**
- **Table S1**: Energy Budget Calculations (spawn capacity without recharge)
- **Table S2**: Parameter Sweep Results (V2/V3/V4 comparison)
- **Table S3**: Recovery Time Analysis

**Add Figures:**
- **Figure S1**: Energy trajectory over time (V3 vs V4)
- **Figure S2**: Population time series (V2/V3/V4 overlay)
- **Figure S3**: Parameter sensitivity curve (recharge rate vs mean population)

---

## Files to Update

### Primary Manuscript Sections

1. **PAPER2_RESULTS_DRAFT.md**
   - Section 3.2: Replace C171 with V4
   - Update all statistics, tables, figures
   - Add energy recharge subsection

2. **PAPER2_DISCUSSION_DRAFT.md**
   - Section 4.2: Add energy constraints
   - Section 4.X: Add theory-driven validation methodology
   - Update population saturation model

3. **PAPER2_METHODS_DRAFT.md**
   - Add energy recharge implementation details
   - Add parameter determination protocol
   - Add V2/V3/V4 experimental design

### Supporting Files

4. **Generate updated figures**:
   - Run `generate_paper2_figures.py` with V4 data
   - Create new energy trajectory plots
   - Update all population time series

5. **Update supplementary material**:
   - Add energy budget tables
   - Add parameter sweep analysis
   - Add recovery time calculations

---

## Execution Steps (2-3 hours)

### Hour 1: Data Integration

1. **Extract V4 metrics from JSON** (10 min)
   - Mean population, std, CV
   - Spawn counts, composition events
   - Basin classification
   - Per-seed breakdown

2. **Update Results section 3.2** (30 min)
   - Replace all C171 statistics with V4
   - Add energy recharge subsection
   - Update tables and inline numbers

3. **Recalculate statistical tests** (20 min)
   - ANOVA (if multiple frequencies tested)
   - Pairwise comparisons
   - Effect sizes

### Hour 2: Discussion Updates

4. **Add energy constraints to Discussion 4.2** (40 min)
   - Energy budget model equations
   - Critical threshold analysis
   - Parameter sweep table
   - Reality grounding explanation

5. **Add theory-driven validation section 4.X** (20 min)
   - Discovery process narrative
   - Methodological contribution
   - Generalizable formula

### Hour 3: Figures and Finalization

6. **Generate updated figures** (30 min)
   - Population time series with V4
   - Energy trajectory plots (new)
   - Parameter sensitivity curve (new)
   - Update all figure captions

7. **Update Methods section** (20 min)
   - Energy recharge implementation
   - Parameter determination
   - Experimental design (V2/V3/V4)

8. **Final review and commit** (10 min)
   - Check all inline numbers match
   - Verify figure/table references
   - Commit to repository

---

## Expected Outcome

**Paper 2 Status:** Ready for submission with minor polishing

**Key Narrative:**
- Bistability → Homeostasis transition validated
- Energy recharge critical for sustained populations
- Theory-driven parameter validation demonstrated
- Controlled parameter sweep establishes critical threshold

**Scientific Contribution:**
- Confirms birth-death coupling + energy recharge = homeostasis
- Establishes quantitative parameter boundaries
- Demonstrates analytical pre-validation methodology
- Provides generalizable energy budget framework

**Impact:** Moderate (validates hypothesis, adds methodological contribution)

---

**Author:** Claude (DUALITY-ZERO-V2)
**Date:** 2025-10-26 (Cycle 219)
**Principal Investigator:** Aldrin Payopay
**Purpose:** Template for immediate Scenario A revision upon V4 completion

