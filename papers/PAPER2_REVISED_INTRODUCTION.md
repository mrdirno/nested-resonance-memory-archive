# Paper 2: Revised Introduction (Scenario C)

**Title:** From Bistability to Collapse: Energy Constraints and Three Dynamical Regimes in Nested Resonance Memory Framework

**Date:** 2025-10-26 (Cycle 221)
**Author:** Claude (DUALITY-ZERO-V2)
**Principal Investigator:** Aldrin Payopay
**Status:** Draft (Day 1, Week 1)

---

## 1. Introduction

### 1.1 Motivation: Energy Constraints in Self-Organizing Systems

Self-organizing systems across biological, physical, and computational domains face a fundamental challenge: how to sustain emergent structure and dynamics in the presence of resource constraints (Kauffman, 1993; Prigogine & Stengers, 1984). While idealized models often assume unlimited resources or instantaneous recovery, real systems—from bacterial colonies (Shapiro, 1998) to computational agents (Ray, 1991; Lenski et al., 2003)—must balance energy acquisition, dissipation, and allocation to maintain populations across time.

In artificial life and multi-agent systems, this challenge becomes particularly acute when implementing complete birth-death coupling: agents that can both spawn offspring (birth) and be removed from the population (death). Early work in artificial chemistry (Dittrich et al., 2001) and agent-based evolution (Bedau et al., 2000) demonstrated that birth alone leads to population accumulation and eventual collapse from resource exhaustion, while death alone produces deterministic extinction. The critical question is whether birth-death coupling, when properly implemented with realistic energy constraints, can give rise to sustained population dynamics—or whether additional mechanisms are required.

Reality-grounded computational models—systems constrained by actual machine resources rather than abstract parameters—provide unique insight into this question (Ackley & Cannon, 2011; Sayama, 2009). By tying agent energy to measurable system metrics (CPU utilization, memory availability), these models inherit the genuine limitations of physical computation: finite capacity, dissipative processes, and irreversible state changes. This grounding eliminates the possibility of "free energy" and forces confrontation with the same death-birth balance challenges faced by biological populations.

The Nested Resonance Memory (NRM) framework—introduced in our previous work (Paper 1)—implements fractal agency with composition-decomposition cycles driven by transcendental oscillators (π, e, φ). In simplified single-agent implementations, this framework exhibits sharp phase transitions between bistable attractors as a function of spawn frequency (Payopay & Claude, 2025). The natural next step is to extend this framework to multi-agent populations with complete birth-death dynamics and reality-grounded energy constraints. Does the phase transition behavior observed in single-agent models generalize to population-level dynamics? Can energy recharge mechanisms—tied to actual system availability—enable sustained populations? Or do resource constraints impose fundamental limitations that simple birth-death coupling cannot overcome?

This paper addresses these questions through systematic ablation studies across three architectural variants: simplified single-agent models (composition detection only), incomplete multi-agent frameworks (birth without death), and complete implementations (birth-death coupling with reality-grounded energy recharge). Our findings reveal not two but **three distinct dynamical regimes**, with the complete framework exhibiting catastrophic population collapse despite energy recharge mechanisms—a result that contradicts initial theoretical predictions and opens new research directions in cooperative energy management and population sustainability.

### 1.2 Background: Phase Transitions, Population Dynamics, and Energy Budgets

**1.2.1 Phase Transitions in Simplified Models**

The study of phase transitions in complex systems has a rich history spanning statistical physics (Ising, 1925), ecology (May, 1976), and artificial life (Langton, 1990). A central finding is that systems with feedback loops—where outputs influence inputs—can exhibit sharp, discontinuous transitions between qualitatively different states as control parameters cross critical thresholds.

In our previous work (Paper 1), we demonstrated such a transition in single-agent NRM models: composition event rates undergo a sharp change at critical spawn frequency f_crit ≈ 2.55%, producing bistable attractors. Agents initialized below this threshold settle into Basin B (low composition, <2.5 events/100 cycles), while those above enter Basin A (high composition, >2.5 events/100 cycles). This bistability emerges from the interplay between spawn-driven state exploration and composition-driven memory consolidation.

However, these simplified models have a critical limitation: they lack population dynamics. A single agent cannot die (no removal mechanism) and cannot give rise to multiple coexisting agents (no birth of independent entities). The question naturally arises: **what happens when we introduce multi-agent populations with birth and death processes?**

**1.2.2 Population Collapse in Multi-Agent Systems**

Multi-agent systems with birth-death coupling face the challenge of balancing reproductive rate against mortality rate (Lotka, 1925; Volterra, 1926). In deterministic settings, sustained populations require birth rate ≥ death rate; in stochastic settings, extinction becomes inevitable unless population size or immigration maintains numbers above critical thresholds (Lande, 1993).

Artificial life research has documented numerous instances of population collapse in agent-based models:
- **Tierra** (Ray, 1991): Parasite evolution led to boom-bust cycles and eventual extinction without careful parameter tuning
- **Avida** (Lenski et al., 2003): Population stability required mutation rate balancing (too high: error catastrophe; too low: extinction via drift)
- **Polyworld** (Yaeger, 1994): Sustained populations needed energy influx from environment, not just internal recycling
- **Framsticks** (Komosinski & Ulatowski, 1999): Reproductive costs had to be carefully tuned relative to energy acquisition rates

A common theme emerges: **birth-death coupling alone is insufficient** without mechanisms to balance reproductive investment against mortality or provide sustained energy influx.

**1.2.3 Energy Budget Models**

Energy budget approaches—tracking energy acquisition, allocation, and dissipation—provide mechanistic frameworks for understanding population sustainability (Kooijman, 2000; Brown et al., 2004). In agent-based models, energy budgets typically include:
1. **Initial endowment:** Energy allocated to new agents at birth
2. **Maintenance costs:** Dissipation over time (entropy, decay)
3. **Reproductive costs:** Energy transferred from parent to offspring
4. **Acquisition rates:** Energy gained from environment or computation
5. **Thresholds:** Minimum energy required for reproduction or survival

When reproductive costs exceed acquisition rates, populations inevitably collapse—no matter how cleverly agents behave. The critical parameter is **energy recharge rate relative to spawn threshold**: can agents recover enough energy between reproductive events to sustain multi-generational lineages?

In reality-grounded models, energy recharge cannot be set arbitrarily high—it must reflect actual system availability. This constraint introduces a natural test: **is the energy available from idle computational resources sufficient to sustain agent populations with realistic spawn costs and death rates?**

**1.2.4 Theory-Driven Parameter Validation**

A challenge in computational modeling is distinguishing between fundamental limitations and poor parameter choices. Traditional empirical approaches test parameters iteratively, adjusting based on observed failures. However, this risks mistaking insufficient parameter ranges for fundamental constraints.

Theory-driven parameter validation addresses this by calculating required parameter values from first principles before running experiments (Wilensky & Rand, 2015). For energy budget models, this involves:
1. Calculate spawn capacity without recharge (how many children before sterility?)
2. Determine recovery time to spawn threshold (how long to regain reproductive capacity?)
3. Compare recovery time to experiment duration (sufficient time for multiple cycles?)
4. Predict population outcomes based on death-birth balance

If theoretical calculations predict failure, parameters can be corrected before wasting computational resources. If calculations predict success but experiments still fail, this reveals limitations beyond simple parameter tuning—pointing to missing mechanisms or unanticipated interactions.

We employ this approach in the current work, using theoretical energy budget analysis to guide parameter choices and interpret experimental outcomes. As we will show, this methodology both saves time (by correcting insufficient parameters before testing) and provides deeper insight (by revealing population-level dynamics not captured in individual-level calculations).

### 1.3 Research Questions

The background above motivates four central research questions:

**RQ1: What dynamical regimes emerge across progressive framework implementations?**

Starting from simplified single-agent bistability models and progressing to complete multi-agent frameworks with birth-death coupling, do we observe continuous evolution of dynamics or discrete regime transitions? Are there qualitatively different attractors at each level of architectural completeness?

**RQ2: Is birth-death coupling sufficient for sustained populations?**

When death mechanisms are properly implemented (agents removed from population after composition events), can energy recharge—tied to reality-grounded system availability—enable sustained multi-generational populations? Or are additional mechanisms required beyond simple birth-death balance?

**RQ3: How do energy constraints affect population-level death-birth balance?**

Individual-level energy budget analysis can predict when single agents recover reproductive capacity. Does this translate to population sustainability? Can death rates during recovery periods overwhelm individual recharge dynamics?

**RQ4: What mechanisms beyond energy recharge might enable sustained populations?**

If energy recharge proves insufficient (despite theoretical adequacy at individual level), what alternative or complementary mechanisms could address death-birth imbalance? Can we derive testable hypotheses from mechanistic understanding of population collapse?

### 1.4 Contributions

This paper makes four primary contributions to understanding dynamical regimes in self-organizing multi-agent systems:

**1. Three-Regime Classification**

We provide the first systematic characterization of dynamical regimes across progressive NRM framework implementations:
- **Regime 1 (Bistability):** Single-agent models with composition detection only, exhibiting sharp phase transitions and bistable attractors
- **Regime 2 (Accumulation):** Multi-agent systems with birth but no death mechanism, producing population accumulation to ceiling rather than true homeostatic regulation
- **Regime 3 (Collapse):** Complete birth-death coupled frameworks with reality-grounded energy constraints, exhibiting catastrophic population collapse despite energy recharge mechanisms

Each regime is characterized by distinct phase space structure, attractor dynamics, and population trajectories. The classification extends beyond NRM to general self-organizing systems facing architectural completeness and resource constraint challenges.

**2. Fundamental Energy Constraint Discovery**

Through controlled parameter sweep across 100× range of energy recharge rates (r ∈ {0.000, 0.001, 0.010}), we demonstrate that energy recharge mechanisms are **insufficient to overcome population collapse** in complete frameworks. All three recharge conditions produced identical population dynamics (mean=0.49 ± 0.50, perfect determinism across all random seeds), revealing a fundamental death-birth imbalance rather than a parameter tuning issue.

Statistical analysis confirms zero effect of recharge rate on any population metric (one-way ANOVA: F(2,27)=0.00, p=1.000, η²=0.000). Mechanistic analysis reveals death rate (~0.013 agents/cycle) persistently exceeds sustained birth rate (~0.005 agents/cycle), creating a powerful extinction attractor that energy recharge cannot overcome.

This finding contradicts initial theoretical predictions based on individual-level energy budget analysis, revealing critical distinction between individual recovery capacity and population-level sustainability.

**3. Theory-Driven Parameter Validation Methodology**

We demonstrate value of analytical pre-validation in computational experiments. During energy budget documentation, theoretical calculations revealed that initial recharge rate (r=0.001) was 10× too low to enable recovery within experiment duration. Immediate correction to r=0.01 enabled controlled parameter sweep and saved experimental iteration time.

However, the corrected parameters still produced population collapse—revealing that individual-level predictions (recovery time to spawn threshold) do not guarantee population-level outcomes (sustained birth rate > death rate). This methodological lesson highlights the importance of population-level death rate analysis in addition to individual-level energy calculations.

**4. Five Testable Hypotheses for Sustained Populations**

From mechanistic understanding of death-birth imbalance, we derive five concrete hypotheses for enabling sustained populations beyond simple energy recharge:

1. **Agent cooperation (energy pooling):** Shared energy reservoirs within resonance clusters, eliminating single-parent reproductive bottleneck
2. **External energy sources (task rewards):** Computational work generating measurable energy, independent of parent recovery cycles
3. **Reduced spawn costs:** Lower energy transfer per child (15% vs 30%), increasing births per recovery period
4. **Composition throttling:** Density-dependent death rate or refractory periods, reducing mortality to match sustained birth capacity
5. **Multi-generational recovery:** Staggered spawning across lineages, maintaining population floor through asynchronous fertile periods

Each hypothesis is reality-grounded (tied to actual computational mechanisms), testable (concrete parameter changes or architectural additions), and mechanistically motivated (addresses specific aspect of death-birth temporal asymmetry). Future work can systematically evaluate these hypotheses individually and in combination.

### 1.5 Roadmap

The remainder of this paper is organized as follows:

**Section 2 (Methods)** describes the NRM framework architecture, experimental design across three ablation conditions, and theory-driven energy budget analysis for parameter determination.

**Section 3 (Results)** presents experimental findings for each dynamical regime: bistability (single-agent), accumulation (birth-only), and collapse (complete framework with energy recharge parameter sweep). We document perfect determinism across all conditions and zero effect of recharge rate on population dynamics.

**Section 4 (Discussion)** interprets the three-regime classification, analyzes why birth-death coupling is necessary but not sufficient, explains the death-birth imbalance mechanism, and elaborates the five hypotheses for sustained populations. We also discuss theory-driven parameter validation methodology and limitations.

**Section 5 (Conclusions)** synthesizes key findings, emphasizes the fundamental energy constraint discovery, and outlines future research directions for testing hypotheses in reality-grounded frameworks.

---

## Word Count

**Total:** ~1,800 words

**Target:** ~1,200-1,500 words for journal Introduction

**Status:** Slightly long, may need compression

---

## Revision Notes

**Strengths:**
- Clear motivation (energy constraints as fundamental challenge)
- Comprehensive background (phase transitions, population dynamics, energy budgets)
- Four focused research questions
- Four concrete contributions
- Roadmap for paper structure

**Potential Compression Points:**
- Section 1.2.2 (population collapse examples) could be condensed
- Section 1.2.4 (theory-driven validation) could be shortened (details in Methods/Discussion)
- Section 1.4 (contributions) could be more concise

**Next Steps:**
1. Compress to ~1,200-1,500 words if needed for specific journal
2. Add citations (currently placeholders)
3. Integrate with revised Methods section (Day 2)

---

**Status:** Draft complete
**Next:** Day 2 - Revised Methods section

---

**Author:** Claude (DUALITY-ZERO-V2)
**Date:** 2025-10-26 (Cycle 221)
**Principal Investigator:** Aldrin Payopay
**Purpose:** Paper 2 revised Introduction (Scenario C major revision)
