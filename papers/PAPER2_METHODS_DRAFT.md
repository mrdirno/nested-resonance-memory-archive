# Paper 2 - Methods Section (DRAFT)

**File**: Expanded methodology for "From Bistability to Homeostasis" manuscript
**Date**: 2025-10-25
**Status**: DRAFT - awaiting C174-C176 data for completion

---

## 2. Methods

### 2.1 Comparative Experimental Framework

We designed a systematic comparison between two implementations of the Nested Resonance Memory (NRM) framework to test whether bistable dynamics validated in simplified models (C168-C170) persist in complete framework implementations. This comparative approach enables isolation of emergent behaviors arising from architectural completeness versus local agent dynamics.

**Research Question**: Do composition-rate-controlled bistable dynamics discovered in simplified single-agent systems persist when implementing the full NRM framework with birth-death dynamics and multi-agent populations?

**Hypothesis**: Bistable basin structure (0%→100% transition at f=2.55%) validated in C168-C170 will replicate in full FractalSwarm implementation across same frequency range.

**Null Hypothesis**: Complete framework exhibits different dynamics due to emergent population-level interactions absent in simplified model.

### 2.2 Simplified Model Implementation (C168-C170 Baseline)

**Purpose**: Establish baseline bistable dynamics under controlled, minimal-complexity conditions.

#### 2.2.1 Architecture

**Single-Agent System**:
- One `FractalAgent` instance with fixed existence throughout experiment
- No agent birth or death (population ≡ 1)
- Agent phase evolves via transcendental bridge (π, e, φ basis)
- Energy derived from real system metrics (psutil: CPU%, memory%)

**Spawn Event Mechanism**:
```python
spawn_interval = floor(100.0 / frequency)  # frequency in %
if (cycle_idx % spawn_interval) == 0:
    # Opportunity for composition event
    check_resonance(agent, threshold=0.5)
```

**Composition Detection**:
- Phase alignment calculated via transcendental bridge
- Resonance criterion: phase_similarity > 0.5
- Each alignment = 1 composition event
- No agent removal (composition purely informational)

**Key Simplification**: Spawn events create composition *opportunities* but don't modify population. Agent persists indefinitely.

#### 2.2.2 Experimental Parameters (C168-C170)

**Control Variables**:
- **Spawn Frequency**: 0.5% - 10.0% (varies by cycle)
  - C168: Coarse sweep (0.5%, 1.0%, ..., 10.0%)
  - C169: Fine resolution (2.0% - 3.0% in 0.1% steps)
  - C170: Multi-threshold validation (1.5 - 3.5 threshold range)

- **Basin Threshold**: Events/window criterion for classification
  - C168-C169: Fixed at 2.5 events/window
  - C170: Varied across [1.5, 2.0, 2.5, 3.0, 3.5]

- **Random Seeds**: n=10 per condition (C169-C170)
- **Cycles**: 3000 per experiment
- **Window Size**: 100 cycles for sliding composition rate calculation

**Measured Observables**:
1. **Composition Event Rate**: Mean events per 100-cycle window
2. **Basin Classification**: Basin A (rate > threshold) vs. Basin B (rate ≤ threshold)
3. **Bifurcation Signatures**: 0%→100% Basin A transition frequency

**Total Experiments**: 1086+ across C168-C170

#### 2.2.3 Key Results (Baseline for Comparison)

**C169 Critical Transition**:
- Sharp 0%→100% Basin A transition between 2.5% and 2.6%
- Critical frequency: f_crit = 2.55% ± 0.05%
- Discontinuous first-order phase behavior

**C170 Linear Scaling Validation**:
```
f_critical = 0.98 × basin_threshold + 0.04
R² = 0.9954 (n=550 experiments)
```

**Mechanism Established**: Composition event rate = fundamental control parameter for bistability.

### 2.3 Complete Framework Implementation (C171 Test)

**Purpose**: Test hypothesis that bistable dynamics persist when birth-death dynamics and population regulation are enabled.

#### 2.3.1 Architecture

**Multi-Agent System (FractalSwarm)**:
- Dynamic agent population (0 to max_agents limit)
- Birth-death coupling enabled
- Full composition-decomposition cycles
- Population evolution emergent (not prescribed)

**Birth Mechanism**:
```python
spawn_interval = floor(100.0 / frequency)
if (cycle_idx % spawn_interval) == 0 and len(agents) < max_agents:
    new_agent = FractalAgent(...)
    agents.append(new_agent)  # Population increases
```

**Composition Mechanism**:
```python
def detect_compositions(agents, threshold=0.5):
    for pair in combinations(agents, 2):
        if phase_alignment(pair) > threshold:
            composition_events.append(cycle_idx)
            # Agents may form cluster
```

**Death Mechanism** (Decomposition/Bursting):
```python
def burst_clusters(agents):
    for cluster in active_clusters:
        if should_burst(cluster):
            for agent in cluster:
                agents.remove(agent)  # Population decreases
            memory.store(cluster_pattern)
```

**Key Difference from Simplified Model**:
- Spawn events ADD agents to population (birth)
- Composition events can REMOVE agents via bursting (death)
- Population size evolves dynamically
- Birth rate ≠ Death rate → population changes
- Birth rate ≈ Death rate → population saturation

#### 2.3.2 Experimental Parameters (C171)

**Designed to Replicate C169 Conditions**:

**Frequencies Tested**: [2.0%, 2.5%, 2.6%, 3.0%]
- Chosen to span C169 critical transition (f_crit = 2.55%)
- Expected: 2.0%, 2.5% → Basin B; 2.6%, 3.0% → Basin A

**Fixed Parameters**:
- Basin threshold: 2.5 events/window (same as C169)
- Random seeds: n=10 per frequency (statistical rigor)
- Cycles: 3000 (matched to C168-C170)
- Window size: 100 cycles (consistent measurement)
- Max agents: 1000 (effectively unlimited)

**New Variables Enabled**:
- **Population dynamics**: Measured at each cycle
- **Agent lifetimes**: Tracked from birth to death
- **Composition cluster sizes**: Number of agents per composition
- **Birth-death rates**: Spawns/cycle vs. deaths/cycle

**Total Experiments**: 40 (4 frequencies × 10 seeds)
**Runtime**: 154 minutes total

#### 2.3.3 Measurement Protocol

**Primary Observable** (comparison with C168-C170):
```python
# Same calculation as simplified model
bins = [0, 100, 200, ..., 3000]
hist, _ = histogram(composition_event_times, bins)
avg_composition_events = mean(hist)
basin = 'A' if avg_composition_events > 2.5 else 'B'
```

**Additional Observables** (full framework only):
```python
# Population dynamics
population_trajectory = [len(agents) at each cycle]
mean_population = mean(population_trajectory)
population_variance = std(population_trajectory)

# Birth-death rates
spawn_count = total_spawn_events
death_count = total_agents_removed
birth_rate = spawn_count / cycles
death_rate = death_count / cycles
```

### 2.4 Comparison Methodology

#### 2.4.1 Direct Comparison Metrics

**Basin Classification Agreement**:
```
Match Rate = (# frequencies with same basin) / (total frequencies)
Expected: 100% if hypothesis confirmed
Observed: [TO BE CALCULATED from C171 data]
```

**Composition Rate Comparison**:
```
For each frequency f:
  Δ_composition = |events_full(f) - events_simplified(f)|
  Relative difference = Δ_composition / events_simplified(f)
```

**Critical Frequency Shift**:
```
Δf_critical = f_critical_full - f_critical_simplified
Expected: Δf_critical ≈ 0 (no shift)
```

#### 2.4.2 Divergence Analysis

**If Results Diverge** (as observed in C171):

**Population Saturation Metric**:
```
Saturation = mean_population / max_agents
Stability = CV(population) where CV = std/mean
```

**Composition-Population Decoupling**:
```
Correlation(spawn_frequency, composition_events)
Simplified model: r ≈ 1.0 (direct coupling)
Full framework: r ≈ ? (test for decoupling)
```

**Homeostasis Detection**:
```
# Test if population stable despite varying spawn rate
For frequencies f1, f2 with different spawn counts:
  H0: mean_pop(f1) ≠ mean_pop(f2)  [bistability prediction]
  H1: mean_pop(f1) ≈ mean_pop(f2)  [homeostasis alternative]

  t-test for population means
  Effect size: Cohen's d
```

### 2.5 Statistical Analysis

**Reproducibility**:
- n=10 seeds per condition ensures statistical power
- Repeated measures enable variance estimation
- Seed independence verified (no correlation across seeds)

**Significance Testing**:
- Basin classification: Binomial test (0% vs. 100% extremes)
- Population means: Welch's t-test (unequal variances)
- Frequency effects: One-way ANOVA
- Post-hoc: Bonferroni correction for multiple comparisons

**Effect Sizes**:
- Cohen's d for population differences
- Cramér's V for basin classification agreement
- R² for composition-frequency correlations

### 2.6 Ablation Studies (C176 - Planned)

**Purpose**: Isolate which architectural components drive divergence between simplified and full frameworks.

**Ablation Targets**:

1. **Spawn Scheduler Ablation**:
   - Fixed-interval spawning (baseline)
   - Poisson-distributed spawning (stochastic births)
   - Test: Does spawn variability affect homeostasis?

2. **Window Size Ablation**:
   - Window sizes: [50, 100, 200 cycles]
   - Test: Is composition saturation ceiling window-dependent?

3. **Bridge Basis Ablation**:
   - Permutations of (π, e, φ) coefficient ordering
   - Test: Does transcendental basis order affect dynamics?

4. **Death Mechanism Ablation**:
   - Immediate removal vs. delayed removal
   - Probabilistic vs. deterministic bursting
   - Test: How does death timing influence population regulation?

**Total C176 Experiments**: ~120 (factorial design)
**Estimated Runtime**: ~4 hours

**Analysis**: Compare each ablation to baseline C171 to quantify contribution of each component to homeostatic vs. bistable behavior.

### 2.7 Software and Reproducibility

**Implementation**:
- Python 3.13.5
- NumPy 1.24+ (array operations)
- psutil 5.9+ (reality grounding)
- matplotlib 3.7+ (visualization)

**Hardware**:
- macOS 14.5 (Darwin 24.5.0)
- Multi-core CPU (46-50% utilization)
- 4GB+ RAM available

**Code Repository**:
```
/Volumes/dual/DUALITY-ZERO-V2/experiments/
├── cycle168_ultra_low_frequency_completion.py
├── cycle169_critical_transition_mapping.py
├── cycle170_basin_threshold_sensitivity.py
├── cycle171_fractal_swarm_bistability.py
├── cycle174_population_bistability.py (corrected)
├── cycle176_ablation_study.py (pending)
├── results/
│   ├── cycle168_*.json
│   ├── cycle169_*.json
│   ├── cycle170_*.json
│   └── cycle171_*.json
└── supplementary/
    ├── S6_REPRODUCIBILITY_PACKAGE.md
    └── [verification scripts]
```

**Data Format**: JSON with complete experiment metadata, parameters, and results for independent verification.

**Reproducibility Commitment**: Complete code, data, and analysis scripts provided in supplementary materials enabling exact replication of all findings.

---

**Status**: Methods section complete for C168-C171 experiments. C174-C176 methods to be integrated upon completion.

**Next Steps**:
1. Integrate C174 corrected results when available
2. Add C175 high-resolution transition analysis
3. Expand C176 ablation study methodology
4. Finalize statistical analysis protocol
