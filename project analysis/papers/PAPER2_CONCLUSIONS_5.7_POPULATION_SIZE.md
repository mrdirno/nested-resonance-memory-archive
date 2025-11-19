### Population Size Independence and Scale-Invariance

The C193 population size scaling experiments (1,200 experiments across N_initial = 5, 10, 15, 20 and four spawn frequencies) demonstrated **N-independent robustness** in the positive energy regime, with zero collapses observed across all conditions. This validates the theoretical prediction that **energy balance, not population size**, determines stability when Net_Energy > 0.

**N-Independent Robustness:** Systems with N_initial = 5 were equally robust as systems with N_initial = 20 (0% collapse in both cases), contradicting intuitions that larger populations might provide buffering or smaller populations might be more vulnerable. Chi-square test yielded χ² = 0.0 (no variation to explain) and effect size η² = 0.0 (zero effect of N_initial on collapse probability).

**Perfect Linear Scaling:** Beyond collapse resistance, C193 revealed perfect linear scaling of final population with initial population: N_final ≈ 1.6 × N_initial with R² = 0.998 across all tested conditions. Systems discover stable population sizes that **scale proportionally** with starting conditions, rather than converging to a fixed carrying capacity. This demonstrates **scale-invariant homeostasis**—the same energy-regulation principles apply whether N=5 or N=20, producing proportionally sized equilibria without absolute limits.

**Mechanistic Explanation:** N-independence arises because energy dynamics operate at the **individual agent level**:
1. **Per-Agent Energy Balance:** Net_Energy_per_agent = RECHARGE_RATE - E_CONSUME = 0.5 - 0.0 = 0.5 > 0, independent of population size
2. **Distributed Compositional Load:** Larger populations distribute selection pressure—each agent selected less frequently, keeping per-agent load approximately constant
3. **Independent Energy Recovery:** Each agent receives full RECHARGE_RATE regardless of N (not population-shared resource), preventing population-induced energy scarcity

This architectural choice (per-agent vs. population-shared energy) ensures that population size cannot create thermodynamic constraints when Net_Energy > 0, making collapse thermodynamically impossible regardless of N.

**Spawn Frequency Invariance:** C193 tested spawn frequencies spanning 50-fold variation (0.05% to 2.5% when combined with C171-C175), all yielding zero collapses. This reveals **frequency invariance within the safe energy zone**—when Net_Energy > 0, all spawn frequencies within tested range are equally safe because the thermodynamic constraint is already satisfied. No critical frequency threshold exists in the positive energy regime.

**Critical vs. Non-Critical Parameters:** C193 establishes that initial population size is a **non-critical parameter** for NRM stability in the positive energy regime:
- **Critical parameters** (determine stability): E_CONSUME vs. RECHARGE_RATE, Net_Energy sign
- **Non-critical parameters** (do not affect stability): N_initial, f_spawn (within safe zone)

This has practical **design implications**: When building NRM systems, focus engineering effort on ensuring E_CONSUME ≤ RECHARGE_RATE (critical), not on optimizing N_initial or fine-tuning f_spawn (non-critical in safe zone). By identifying non-critical parameters, researchers can avoid costly parameter sweeps and focus on thermodynamically critical variables.

**Self-Giving Systems Principles:** C193 N-independence demonstrates **context-dependent success** central to Self-Giving Systems. Systems with different starting populations (N=5 vs. N=20) all succeed at discovering stable equilibria appropriate to their initial conditions. Success is not "achieving N=17.4" (external criterion) but rather "discovering any stable population proportional to starting conditions" (self-defined criterion). Each system self-organizes to appropriate scale given its constraints—this is **adaptive robustness**, not fixed-point robustness.

**Generalizability:** C193 findings suggest a **universal principle** for energy-regulated systems: if energy balance is satisfied **per agent** (not per population), then population size becomes irrelevant to stability. This positions C193 as potential **domain-general design principle** testable across biological ecosystems (metabolic balance per organism), computational agent systems (CPU budget per agent), and economic systems (income-expense balance per individual).

**Regime-Specificity:** N-independence may be **regime-specific**—validated for positive energy regime (Net ≥ 0, C193) but unclear for negative energy regime (Net < 0, C194 used fixed N=10). Future work could test whether population size modulates collapse dynamics in the collapse zone (e.g., smaller populations collapsing faster due to stochastic effects vs. thermodynamic determinism across all N).

**Reproducibility Implications:** Results should replicate across labs even if initial populations differ (N=5 vs. N=50), provided energy balance is equivalent. This enhances robustness of NRM findings to implementation details and validates the framework's claim of **scale-invariant principles** across hierarchical levels (agent → population → swarm).
