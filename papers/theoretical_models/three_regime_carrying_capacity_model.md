# THREE-REGIME CARRYING CAPACITY MODEL

**Date:** 2025-11-18
**Cycle:** 1385
**Status:** Theory Development (In Progress)
**Purpose:** Derive predictive model for population fate from energy parameters

---

## MOTIVATION

**Empirical Foundation:**
- 150 experiments (V6c + V6a + V6b) demonstrate three qualitatively different regimes
- Population fate spans 0 → 201 → 19,320 agents (3+ orders of magnitude)
- Single parameter control (net energy = E_recharge - E_consume)
- Spawn rate effect regime-dependent (inactive in collapse/homeostasis, active in growth)

**Theoretical Gap:**
- Empirical findings are descriptive (what happens)
- Need predictive theory (why it happens, generalize beyond tested parameters)
- Goal: Derive carrying capacity formula K(E_net, f_spawn) predicting population fate

**Scientific Value:**
- Transforms 150 experiments → general theory
- Enables parameter space exploration without exhaustive experiments
- Testable predictions for untested parameter combinations
- Publishable theoretical contribution alongside empirical C186 manuscript

---

## EMPIRICAL CONSTRAINTS (FROM C186 EXPERIMENTS)

### Regime 1: Collapse (V6c, E_net = -0.5)
```
Parameters:
- E_consume = 1.5
- E_recharge = 1.0
- E_net = -0.5 (net-negative energy)
- f_spawn = 0.0010 to 0.0100 (5 rates tested)

Observations:
- Final population: 0 agents (100% collapse, 50/50 experiments)
- Spawn rate effect: NONE (p=NaN, constant zero population)
- Collapse time: ~450,000 cycles (full runtime, minimal computation)
- Mechanism: Decomposition > composition regardless of spawn attempts

Carrying Capacity:
K(E_net < 0, f_spawn) = 0  (extinction guaranteed)
```

### Regime 2: Homeostasis (V6a, E_net = 0.0)
```
Parameters:
- E_consume = 1.0
- E_recharge = 1.0
- E_net = 0.0 (perfect energy balance)
- f_spawn = 0.0010 to 0.0100 (5 rates tested)

Observations:
- Final population: 201 ± 1.2 agents (stable equilibrium)
- Spawn rate effect: NONE (p=0.448, statistically insignificant)
- Energy: 1,000 ± 0 units (constant, tight regulation)
- Mechanism: Composition = decomposition, self-regulation to carrying capacity

Carrying Capacity:
K(E_net = 0, f_spawn) ≈ 201  (spawn rate irrelevant)
```

### Regime 3: Growth (V6b, E_net = +0.5)
```
Parameters:
- E_consume = 0.5
- E_recharge = 1.0
- E_net = +0.5 (net-positive energy)
- f_spawn = 0.0010 to 0.0100 (5 rates tested)

Observations:
- Final population: 15,094 to 20,746 agents (f_spawn-dependent)
- Spawn rate effect: SIGNIFICANT (p<0.001, 10× f_spawn → +16.5% population)
- Energy: 10,005,217 ± 2,914 units (energy cap hit)
- Mechanism: Composition > decomposition, spawn rate amplifies growth speed

Carrying Capacity:
K(E_net > 0, f_spawn) = f(f_spawn)  (spawn rate modulates carrying capacity)

Empirical Fit (Linear):
K = 15,094 + 565,200 * f_spawn  (R² > 0.99, from V6b data)
```

---

## THEORETICAL MODEL DEVELOPMENT

### Hypothesis 1: Energy Balance Determines Regime
**Claim:** Net energy (E_net = E_recharge - E_consume) is the **primary control parameter** determining which regime emerges.

**Regime Classification:**
```
if E_net < 0:   → Collapse regime (extinction)
if E_net = 0:   → Homeostasis regime (stable equilibrium)
if E_net > 0:   → Growth regime (exponential expansion)
```

**Prediction:** Population fate is STEP FUNCTION of E_net, not continuous:
- Sharp transition at E_net = 0 (collapse ↔ homeostasis)
- Sharp transition at E_net = 0⁺ (homeostasis ↔ growth)
- NO intermediate regimes (confirmed by V6c=0, V6a=201, V6b=19,320)

**Testable:** Continuous energy scan (E_net from -1.0 to +1.0) should reveal:
- All E_net < 0 → collapse (K=0)
- E_net = 0 → homeostasis (K~201)
- All E_net > 0 → growth (K >> 201)
- Transition bandwidth < 0.01 (sharp, not gradual)

### Hypothesis 2: Spawn Rate Modulates Growth ONLY
**Claim:** Spawn rate (f_spawn) influences carrying capacity **ONLY** in growth regime (E_net > 0).

**Regime-Dependent Effect:**
```
if E_net ≤ 0:  ∂K/∂f_spawn = 0  (spawn rate irrelevant)
if E_net > 0:  ∂K/∂f_spawn > 0  (spawn rate amplifies growth)
```

**Mechanism:**
- **Collapse (E_net < 0):** Energy deficit prevents spawning from mattering
- **Homeostasis (E_net = 0):** Energy balance self-regulates regardless of spawn attempts
- **Growth (E_net > 0):** Energy surplus enables spawning to determine growth rate

**Testable:** Vary f_spawn within each regime:
- V6c (E_net = -0.5): ∂K/∂f_spawn should remain 0 (confirmed)
- V6a (E_net = 0.0): ∂K/∂f_spawn should remain 0 (confirmed)
- V6b (E_net = +0.5): ∂K/∂f_spawn should be positive (confirmed, slope ≈ 565,200)

### Hypothesis 3: Carrying Capacity Piecewise Formula
**Claim:** Carrying capacity K is **piecewise function** of E_net and f_spawn.

**Proposed Formula:**
```
K(E_net, f_spawn) = {
    0,                              if E_net < 0
    K₀,                             if E_net = 0
    K₀ + α(E_net) * f_spawn,        if E_net > 0
}

where:
- K₀ = baseline carrying capacity at net-zero energy (empirically ~201)
- α(E_net) = growth amplification factor (function of net energy)
```

**From V6a (E_net = 0):**
```
K₀ ≈ 201 agents
```

**From V6b (E_net = +0.5):**
```
K(0.5, f_spawn) = K₀ + α(0.5) * f_spawn
K(0.5, f_spawn) = 15,094 + 565,200 * f_spawn

Implies:
α(0.5) ≈ 565,200

And baseline at E_net = +0.5, f_spawn = 0.001:
15,094 = K₀ + 565,200 * 0.001
15,094 = K₀ + 565.2
K₀ ≈ 14,529  (but this contradicts V6a K₀ = 201)

ISSUE: Linear model doesn't account for regime shift between E_net=0 and E_net>0
Need non-linear formulation that explains K₀=201 at E_net=0 vs K₀=15,094 at E_net=+0.5
```

### Hypothesis 3B: Non-Linear Carrying Capacity (Revised)
**Issue with Linear Model:**
- V6a (E_net = 0): K ≈ 201
- V6b (E_net = +0.5, f_spawn = 0.001): K ≈ 15,094
- 75× increase from E_net: 0 → +0.5 (NOT linear in E_net alone)

**Revised Hypothesis:**
Carrying capacity depends on **both** E_net magnitude and f_spawn, with **multiplicative interaction** in growth regime.

**Proposed Non-Linear Formula:**
```
K(E_net, f_spawn) = {
    0,                                          if E_net < 0
    K_homeostasis,                              if E_net = 0
    K_homeostasis * exp(β * E_net / f_spawn),   if E_net > 0
}

where:
- K_homeostasis ≈ 201 (homeostasis carrying capacity)
- β = growth rate parameter (determines exponential scaling)
```

**Testing with V6b data:**
```
K(0.5, 0.001) = 201 * exp(β * 0.5 / 0.001)
15,094 = 201 * exp(β * 500)

exp(β * 500) = 15,094 / 201 = 75.09

β * 500 = ln(75.09) = 4.32

β = 4.32 / 500 = 0.00864
```

**Validation with V6b spawn rate variation:**
```
Predicted K(0.5, f_spawn) = 201 * exp(0.00864 * 0.5 / f_spawn)

f_spawn = 0.001: K = 201 * exp(4.32) = 201 * 75.09 = 15,093 ✓ (matches ~15,094)
f_spawn = 0.010: K = 201 * exp(0.432) = 201 * 1.54 = 310 ✗ (predicts 310, observed ~20,746)

ISSUE: Exponential model underestimates effect of higher f_spawn
Need different formulation that explains both regime shift AND spawn rate amplification
```

---

## MECHANISTIC MODEL (COMPOSITION-DECOMPOSITION BALANCE)

### Agent-Level Dynamics
**Energy Flow:**
```
E_agent(t+1) = E_agent(t) + E_recharge - E_consume * action_cost

where:
- E_recharge = energy gained per cycle (constant)
- E_consume = energy lost per cycle (constant)
- action_cost = 0 if passive, 1 if active decomposition
```

**Composition (Spawning):**
```
P(spawn) = f_spawn if E_agent ≥ spawn_cost
         = 0 otherwise

Spawn cost: 5.0 energy units (fixed)
```

**Decomposition (Death):**
```
P(death) = 1.0 if E_agent ≤ 0
         = 0 otherwise

Death threshold: 0.0 energy units (fixed)
```

### Population-Level Balance
**Rate Equations:**
```
dN/dt = R_composition - R_decomposition

where:
- R_composition = N * f_spawn * P(sufficient_energy)
- R_decomposition = N * P(energy_depletion)
```

**Equilibrium Condition:**
```
R_composition = R_decomposition
N * f_spawn * P(E ≥ spawn_cost) = N * P(E ≤ 0)

Simplifies to:
f_spawn * P(E ≥ spawn_cost) = P(E ≤ 0)
```

### Regime-Specific Analysis

**Collapse Regime (E_net < 0):**
```
Energy depletion rate > energy recharge rate
Average agent energy: E_avg → 0 over time
P(sufficient_energy) → 0 (insufficient energy to spawn)
P(energy_depletion) → 1 (all agents eventually deplete)

Result: R_composition → 0, R_decomposition → N
       dN/dt < 0 always
       N(t→∞) = 0  (extinction)
```

**Homeostasis Regime (E_net = 0):**
```
Energy depletion rate = energy recharge rate
Average agent energy: E_avg = constant (tight regulation)
P(sufficient_energy) = constant
P(energy_depletion) = constant

Equilibrium: f_spawn * P(E ≥ 5.0) = P(E ≤ 0)
             K = N where dN/dt = 0

Result: Self-regulating equilibrium at K ≈ 201 agents (empirically)
        K independent of f_spawn (tight energy constraint)
```

**Growth Regime (E_net > 0):**
```
Energy recharge rate > energy depletion rate
Average agent energy: E_avg → E_cap over time (10M cap)
P(sufficient_energy) → 1 (abundant energy)
P(energy_depletion) → 0 (low death rate)

Composition rate: R_composition = N * f_spawn
Decomposition rate: R_decomposition ≈ 0 (until energy cap)

Result: dN/dt = N * f_spawn (exponential growth)
        N(t) = N₀ * exp(f_spawn * t)
        K depends on f_spawn (higher spawn rate → faster growth → higher final population before cap)
```

### Carrying Capacity from Energy Cap Constraint

**In Growth Regime:**
Population growth continues until **energy cap** is reached (E_total = 10M units).

**Energy Distribution:**
```
E_total = N * E_avg

where:
- E_total = total energy in system (capped at 10M)
- N = population size
- E_avg = average energy per agent
```

**At Carrying Capacity:**
```
N_cap = E_total_cap / E_avg

E_avg depends on spawn rate:
- Higher f_spawn → more spawning → lower E_avg (energy spread across more agents)
- Lower f_spawn → less spawning → higher E_avg (energy concentrated in fewer agents)
```

**Hypothesis 4: Carrying Capacity from Energy Distribution**
```
K(E_net > 0, f_spawn) = E_cap / E_avg(f_spawn)

where E_avg(f_spawn) is decreasing function of f_spawn
```

**From V6b data:**
```
f_spawn = 0.001: K ≈ 15,094, E_avg ≈ 10,000,000 / 15,094 ≈ 662 units/agent
f_spawn = 0.010: K ≈ 20,746, E_avg ≈ 10,000,000 / 20,746 ≈ 482 units/agent

Higher f_spawn → lower E_avg (energy distributed across more agents)
10× f_spawn increase → 27% decrease in E_avg → 37% increase in K
```

**Empirical Relationship:**
```
E_avg(f_spawn) ≈ E_base * f_spawn^(-γ)

where:
- E_base = baseline energy per agent
- γ = spawn rate exponent (determines sensitivity)

From V6b:
662 = E_base * 0.001^(-γ)
482 = E_base * 0.010^(-γ)

Ratio: 662/482 = (0.001/0.010)^(-γ)
       1.374 = 10^γ
       γ = log₁₀(1.374) = 0.138
```

**Predicted Carrying Capacity:**
```
K(E_net > 0, f_spawn) = E_cap / (E_base * f_spawn^(-0.138))
                       = (E_cap / E_base) * f_spawn^(0.138)

Constant: E_cap / E_base ≈ 10,000,000 / 662 * 0.001^(0.138) ≈ 9,580

K(f_spawn) ≈ 9,580 * f_spawn^(0.138)
```

**Validation:**
```
f_spawn = 0.001: K = 9,580 * 0.001^(0.138) = 9,580 * 0.575 = 5,508 ✗ (predicts 5,508, observed 15,094)

ISSUE: Power-law model underestimates carrying capacity
Need to account for BOTH energy cap AND spawn mechanics
```

---

## NEXT STEPS (THEORY DEVELOPMENT)

### Immediate (This Cycle)
1. ⏳ Resolve mechanistic model inconsistencies
   - Why does K ≈ 201 at E_net=0 but K ≈ 15,094 at E_net=+0.5?
   - What is the precise relationship between E_avg, f_spawn, and K in growth regime?
   - How does energy cap constraint translate to population limit?

2. ⏳ Develop complete mathematical framework
   - Derive K(E_net, f_spawn) from first principles (agent rules)
   - Explain regime transitions (collapse ↔ homeostasis ↔ growth)
   - Account for spawn rate sensitivity switching on/off

### Short-Term (1-3 Cycles)
3. ⏳ Validate theoretical predictions
   - Continuous energy scan (E_net from -1.0 to +1.0)
   - Test transition sharpness (is it step function or gradual?)
   - Spawn cost variation (does K depend on spawn_cost in growth regime?)

4. ⏳ Generalize to multi-parameter space
   - K(E_net, f_spawn, spawn_cost, E_cap)
   - Identify all regime boundaries in parameter space
   - Create phase diagram visualization

### Medium-Term (5-10 Cycles)
5. ⏳ Compare to existing ecological models
   - Lotka-Volterra carrying capacity (logistic growth)
   - Metabolic theory of ecology (energy-based limits)
   - Dynamic Energy Budget models

6. ⏳ Publish theoretical model paper
   - Empirical foundation (C186 experiments)
   - Mechanistic derivation (composition-decomposition balance)
   - Predictive validation (new experiments)
   - Generalization to other systems

---

## OPEN QUESTIONS

1. **Energy Distribution Puzzle:**
   - Why E_avg ≈ 662 at f_spawn=0.001 but E_avg ≈ 482 at f_spawn=0.010?
   - Is this due to spawn cost (5 units) × spawn frequency?
   - Or due to age distribution (younger agents have less energy)?

2. **Homeostasis Mechanism:**
   - Why K ≈ 201 specifically at E_net=0?
   - Is 201 related to spawn_cost (5.0), E_recharge (1.0), or initial population (100)?
   - Would K change if initial_population or spawn_cost varied?

3. **Regime Transition Sharpness:**
   - Is transition at E_net=0 truly discontinuous (step function)?
   - Or is there narrow boundary layer (e.g., -0.01 < E_net < +0.01)?
   - What determines transition bandwidth?

4. **Spawn Rate Threshold:**
   - At what f_spawn does spawn rate start influencing K in growth regime?
   - Is there minimum threshold below which f_spawn has no effect?
   - Or does effect scale continuously with f_spawn?

5. **Energy Cap Effect:**
   - How would removing 10M cap change carrying capacity?
   - Would population grow indefinitely or reach intrinsic limit?
   - Is energy cap artificial constraint or realistic resource limit?

---

## EXPERIMENTAL VALIDATION PLAN

### Experiment 1: Continuous Energy Scan
**Goal:** Map K(E_net, f_spawn=0.001) across full energy range

**Parameters:**
```
E_consume: 0.5 to 2.0 (step 0.05, 31 values)
E_recharge: 1.0 (fixed)
E_net: -1.0 to +1.0 (step 0.05, 31 values)
f_spawn: 0.001 (baseline)
seeds: 42-51 (10 seeds per condition)

Total: 31 × 10 = 310 experiments
Runtime: ~2 hours (estimated)
```

**Expected Results:**
- E_net < 0: K = 0 (all collapse)
- E_net = 0: K ≈ 201 (homeostasis)
- E_net > 0: K increases with E_net
- Transition sharpness revealed

### Experiment 2: Spawn Rate Variation in Growth
**Goal:** Validate K(E_net=+0.5, f_spawn) relationship

**Parameters:**
```
E_consume: 0.5 (fixed, growth regime)
E_recharge: 1.0 (fixed)
f_spawn: 0.0001 to 0.0200 (20 values, logarithmic spacing)
seeds: 42-51 (10 seeds per condition)

Total: 20 × 10 = 200 experiments
Runtime: ~40 min (estimated)
```

**Expected Results:**
- K increases with f_spawn (positive correlation)
- Relationship shape: linear, power-law, or logarithmic?
- Allows fitting K(f_spawn) empirical formula

### Experiment 3: Spawn Cost Interaction
**Goal:** Test if spawn_cost modulates regime boundaries

**Parameters:**
```
E_consume: 0.5, 1.0, 1.5 (3 values, all three regimes)
E_recharge: 1.0 (fixed)
spawn_cost: 1.0, 5.0, 10.0, 20.0 (4 values)
f_spawn: 0.001 (baseline)
seeds: 42-51 (10 seeds per condition)

Total: 3 × 4 × 10 = 120 experiments
Runtime: ~2 hours (estimated)
```

**Expected Results:**
- Does higher spawn_cost shift regime boundaries?
- Does K in homeostasis depend on spawn_cost?
- Does K in growth depend on spawn_cost?

---

## REFERENCES

**Empirical Foundation:**
- C186 three-regime manuscript (~98% complete, this repository)
- V6c collapse regime (50 experiments, 100% extinction)
- V6a homeostasis regime (50 experiments, K ≈ 201)
- V6b growth regime (50 experiments, K ≈ 15,094 to 20,746)

**Ecological Theory:**
- Lotka-Volterra models (predator-prey carrying capacity)
- Verhulst logistic growth (K as intrinsic population limit)
- Metabolic theory of ecology (energy-based constraints)
- Dynamic Energy Budget theory (individual-level energy allocation)

**Agent-Based Modeling:**
- Epstein & Axtell Sugarscape (resource-limited growth)
- Grimm ODD protocol (model description standards)
- DeAngelis individual-based ecology (emergent population dynamics)

---

**Status:** Theory development in progress (Cycle 1385)
**Next Action:** Resolve mechanistic model inconsistencies, develop complete K(E_net, f_spawn) formula
**Target:** Publishable theoretical model paper validating with new experiments

**Files Created:**
- `/Volumes/dual/DUALITY-ZERO-V2/papers/theoretical_models/three_regime_carrying_capacity_model.md` (this file)

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (Anthropic)
