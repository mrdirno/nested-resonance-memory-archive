# Paper 4: Multi-Scale Energy Regulation in Nested Resonance Memory
## Section 3: Methods - Experimental Designs and Protocols

**Draft Version 0.1**
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-11-04
**Cycle:** 999

---

## 3.1 Overview

We conducted four complementary experiments (C186-C189) to validate Extensions 1, 2, and 4 of the NRM framework. Each experiment manipulates specific parameters while holding others constant, enabling controlled hypothesis testing. Extension 3 (Stochastic Boundaries, C177) provides contextual boundary mapping. Total experimental coverage: 300 experiments across 5 cycles.

### 3.1.1 Common Infrastructure

**Software Implementation:**
- Language: Python 3.9+
- Core modules: `core/reality_interface.py`, `fractal/fractal_agent.py`, `bridge/transcendental_bridge.py`
- Reality grounding: psutil-based system metrics (CPU, memory, processes)
- Reproducibility: Seeded random number generators, exact dependency versions (requirements.txt)

**Agent Model:**
- FractalAgent class with internal energy states
- Depth: 0-7 (max_depth=7)
- Composition threshold: Resonance > 0.5 (cosine similarity in transcendental phase space)
- Spawn energy fraction: 30% parent energy transferred to child
- Reality anchoring: All agents bound to actual system metrics via RealityInterface

**Metrics Tracked (All Experiments):**
1. **Spawn success rate:** Fraction of spawn attempts resulting in viable offspring
2. **Composition events:** Timestamped cluster formation and burst events
3. **Basin classification:** A (homeostasis, ≥2.5 comp/window) vs B (collapse, <2.5)
4. **Population trajectory:** Agent count over time
5. **Energy dynamics:** Mean/variance across agents

**Reproducibility Standards:**
- Multiple seeds per condition (n=10-20)
- Fixed cycle counts (3000-5000 cycles)
- Exact spawn frequency control
- Version-controlled code (GitHub: nested-resonance-memory-archive)
- Docker containerization available

---

## 3.2 Experiment C187: Network Structure Effects

**Purpose:** Validate Extension 1 (degree-dependent selection, hub depletion)

### 3.2.1 Experimental Design

**Network Topologies (3 conditions):**

1. **Scale-Free (Barabási-Albert):**
   - Generation: Preferential attachment with $m=2$ edges per new node
   - $N=30$ nodes, mean degree $\langle k \rangle = 4$
   - Degree distribution: $P(k) \sim k^{-\gamma}$, $\gamma \approx 3$
   - Heterogeneity: High ($CV_k \approx 0.8$)

2. **Random (Erdős-Rényi):**
   - Generation: $G(N, p)$ with $p = \langle k \rangle / (N-1)$
   - $N=30$ nodes, mean degree $\langle k \rangle = 4$
   - Degree distribution: Binomial (approximately Poisson for large N)
   - Heterogeneity: Low ($CV_k \approx 0.5$)

3. **Lattice (2D Grid):**
   - Structure: $\sqrt{N} \times \sqrt{N}$ grid with periodic boundary conditions
   - $N=25$ nodes (5×5 grid), degree $k=4$ (von Neumann neighborhood)
   - Degree distribution: Delta function (all nodes have exactly $k=4$)
   - Heterogeneity: Zero ($CV_k = 0$)

**Parent Selection:**
- **Degree-weighted probability:** $P(\text{select node } i) = k_i / \sum_j k_j$
- Rationale: Models resource concentration in highly-connected nodes (hubs)

**Common Parameters:**
- Spawn frequency: $f = 2.5\%$ (validated homeostasis regime)
- Cycles: 3000
- Seeds: $n=10$ per topology (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
- Total experiments: 3 topologies × 10 seeds = **30 experiments**

**Stratified Metrics:**
- Agents binned by degree: Low (bottom 33%), Medium (middle 33%), High (top 33%)
- Track spawn success rate separately per bin
- Enables detection of hub depletion effect

### 3.2.2 Implementation

**Network Generation:**
```python
import networkx as nx

# Scale-free
G_sf = nx.barabasi_albert_graph(n=30, m=2, seed=seed)

# Random
p = 4 / 29  # mean_degree / (n-1)
G_rand = nx.erdos_renyi_graph(n=30, p=p, seed=seed)

# Lattice
G_lattice = nx.grid_2d_graph(5, 5)
```

**Degree-Weighted Selection:**
```python
def select_parent(agents, network):
    degrees = [network.degree(agent.node_id) for agent in agents]
    probabilities = degrees / np.sum(degrees)
    return np.random.choice(agents, p=probabilities)
```

**Stratified Analysis:**
```python
# Bin agents by degree
degree_bins = np.percentile(degrees, [0, 33, 67, 100])
for agent in agents:
    bin_idx = np.digitize(network.degree(agent.node_id), degree_bins) - 1
    stratified_metrics[bin_idx].record_spawn_attempt(success=...)
```

### 3.2.3 Validation Criteria

**Prediction 1.1:** $S_{\text{lattice}} > S_{\text{random}} > S_{\text{scale-free}}$ (t-tests, $p < 0.05$)

**Prediction 1.2:** $\rho(CV_k, S) < -0.7$ (Pearson correlation)

**Prediction 1.3:** $S_{\text{low-degree}} > S_{\text{high-degree}}$ in scale-free networks (paired t-test)

---

## 3.3 Experiment C186: Hierarchical Energy Dynamics

**Purpose:** Validate Extension 2 (multi-scale cascades, hierarchical resonance)

### 3.3.1 Experimental Design

**Meta-Population Structure:**
- 4 populations (P1, P2, P3, P4)
- Each population: independent agent collective with local dynamics
- Swarm level: Coordinates spawn frequency across populations

**Coupling Strengths (2 conditions):**

1. **Weak Coupling ($\kappa = 0.2$):**
   - Low inter-population energy transfer
   - Populations evolve quasi-independently
   - Predicts: Low synchronization, high variance

2. **Strong Coupling ($\kappa = 0.8$):**
   - High inter-population energy transfer
   - Populations tightly coordinated
   - Predicts: High synchronization, low variance

**Spawn Frequency Schedule:**
- Swarm-level control: $f_{\text{swarm}} = 2.5\%$ (global spawn rate)
- Population-level allocation: Proportional to relative energy depletion
- Mechanism: Populations with lower energy receive more spawns

**Common Parameters:**
- Populations: 4
- Agents per population: ~10 (dynamic)
- Cycles: 3000
- Seeds: $n=10$ per coupling condition
- Total experiments: 2 coupling levels × 4 populations × 10 seeds = **40 experiments** (analyzed at population level)

### 3.3.2 Implementation

**Meta-Population Initialization:**
```python
populations = []
for pop_id in range(4):
    initial_agent = FractalAgent(
        agent_id=f"pop{pop_id}_root",
        bridge=bridge,
        initial_reality=reality.get_system_metrics(),
        depth=0,
        max_depth=7,
        reality=reality
    )
    populations.append({'agents': [initial_agent], 'id': pop_id})
```

**Coupling-Dependent Spawn Allocation:**
```python
# Calculate population energies
pop_energies = [np.mean([a.energy for a in pop['agents']])
               for pop in populations]

# Allocation proportional to energy deficit (strong coupling)
if coupling == 'strong':
    energy_deficits = [1.0 - E / max(pop_energies) for E in pop_energies]
    spawn_probs = energy_deficits / np.sum(energy_deficits)
# Uniform allocation (weak coupling)
else:
    spawn_probs = [0.25, 0.25, 0.25, 0.25]

# Select population for spawn
target_pop = np.random.choice(populations, p=spawn_probs)
```

**Synchronization Metric:**
```python
# Phase-lock detection via cross-correlation of composition rates
comp_rates = [pop_composition_timeseries for pop in populations]
sync_matrix = np.corrcoef(comp_rates)
mean_sync = np.mean(sync_matrix[np.triu_indices_from(sync_matrix, k=1)])
```

### 3.3.3 Validation Criteria

**Prediction 2.1:** $CV_{\text{comp}} < 0.2$ for each population (homeostasis)

**Prediction 2.2:** $\rho(f_{\text{spawn}}^{\text{swarm}}, r_{\text{comp}}^{\text{pop}}) > 0.8$ (cross-level correlation)

**Prediction 2.3:** Basin classification consistent across populations

**Prediction 2.4:** Energy flow upward during compositions (agent → population)

**Prediction 2.5:** Lower extinction rate in meta-population vs isolated populations

**Prediction 2.6:** Synchronization higher for $\kappa=0.8$ vs $\kappa=0.2$ (t-test, $p < 0.05$)

---

## 3.4 Experiment C188: Memory Effects

**Purpose:** Validate Extension 4B (refractory periods, temporal selection bias)

### 3.4.1 Experimental Design

**Memory Conditions (4 levels):**

1. **None (Baseline):**
   - Standard uniform random parent selection
   - No composition history tracking
   - Expected: High burstiness, cascades common

2. **Short Memory ($\tau_{\text{memory}} = 100$ cycles):**
   - Track compositions over 100-cycle window
   - Moderate refractory effect
   - Expected: Reduced burstiness vs baseline

3. **Medium Memory ($\tau_{\text{memory}} = 500$ cycles):**
   - Track compositions over 500-cycle window
   - Strong refractory effect
   - Expected: Low burstiness, distributed load

4. **Long Memory ($\tau_{\text{memory}} = 1000$ cycles):**
   - Track compositions over 1000-cycle window
   - Very strong refractory effect
   - Expected: Minimal burstiness, uniform temporal distribution

**Selection Probability (Memory Conditions):**
$$P(\text{select agent } i) \propto \exp\left(-\frac{n_{\text{recent}}^i}{\tau_{\text{decay}}}\right)$$

where $n_{\text{recent}}^i$ = compositions involving agent $i$ in last $\tau_{\text{memory}}$ cycles, $\tau_{\text{decay}} = 2.0$ (decay parameter).

**Common Parameters:**
- Spawn frequency: $f = 2.5\%$
- Cycles: 3000
- Seeds: $n=10$ per memory condition
- Total experiments: 4 memory conditions × 10 seeds = **40 experiments**

### 3.4.2 Implementation

**Memory Tracker:**
```python
from collections import deque, defaultdict

class MemoryTracker:
    def __init__(self, memory_window):
        self.memory_window = memory_window
        self.composition_history = defaultdict(
            lambda: deque(maxlen=memory_window)
        )

    def record_composition(self, agent_ids, cycle_idx):
        for agent_id in agent_ids:
            self.composition_history[agent_id].append(cycle_idx)

    def get_memory_weight(self, agent_id, decay_factor=2.0):
        n_recent = len([c for c in self.composition_history[agent_id]
                       if self.current_cycle - c <= self.memory_window])
        return np.exp(-n_recent / decay_factor)
```

**Memory-Weighted Selection:**
```python
if memory_tracker is not None:
    weights = [memory_tracker.get_memory_weight(a.agent_id)
              for a in agents]
    probabilities = weights / np.sum(weights)
    parent = np.random.choice(agents, p=probabilities)
else:
    parent = np.random.choice(agents)  # Baseline
```

**Burstiness Calculation:**
```python
def calculate_burstiness(event_times):
    intervals = np.diff(sorted(event_times))
    mean_iei = np.mean(intervals)
    std_iei = np.std(intervals)
    B = (std_iei - mean_iei) / (std_iei + mean_iei)
    return B
```

### 3.4.3 Validation Criteria

**Prediction 4B.1:** $S_{\text{long}} > S_{\text{medium}} > S_{\text{short}} > S_{\text{none}}$ (all pairwise t-tests, $p < 0.05$)

**Prediction 4B.2:** $B_{\text{none}} > B_{\text{short}} > B_{\text{medium}} > B_{\text{long}}$ (monotonic decrease)

**Prediction 4B.3:** $\rho(\tau_{\text{memory}}, B) < -0.7$ (Pearson correlation)

---

## 3.5 Experiment C189: Burst Clustering

**Purpose:** Validate Extension 4C (avalanche dynamics, SOC)

### 3.5.1 Experimental Design

**Frequency Conditions (5 levels):**
- Test burstiness across compositional load spectrum
- Frequencies: 1.5%, 2.0%, 2.5%, 3.0%, 5.0%
- Rationale: Low frequency near collapse boundary (1.5%), high frequency stress test (5.0%)

**Extended Runtime:**
- Cycles: **5000** (increased from 3000 in other experiments)
- Rationale: Robust power-law fitting requires large sample sizes (100+ events minimum)

**Common Parameters:**
- Seeds: $n=20$ per frequency (increased for distribution fitting)
- Total experiments: 5 frequencies × 20 seeds = **100 experiments**

### 3.5.2 Implementation

**Power-Law Fitting (Maximum Likelihood Estimation):**
```python
def fit_power_law(intervals, xmin=None):
    if xmin is None:
        xmin = np.percentile(intervals, 10)  # Auto-detect lower bound

    tail_data = intervals[intervals >= xmin]
    n = len(tail_data)

    # MLE for power-law exponent
    alpha = 1 + n / np.sum(np.log(tail_data / xmin))

    return {'alpha': alpha, 'xmin': xmin, 'n_tail': n}
```

**Distribution Comparison:**
```python
from scipy import stats

# Test against exponential (Poisson baseline)
ks_exp, p_exp = stats.kstest(intervals, 'expon',
                             args=(0, 1/np.mean(intervals)))

# Test against log-normal
log_intervals = np.log(intervals)
mu_ln = np.mean(log_intervals)
sigma_ln = np.std(log_intervals)
ks_ln, p_ln = stats.kstest(intervals, 'lognorm',
                           args=(sigma_ln, 0, np.exp(mu_ln)))

# Compare p-values
best_fit = 'power_law' if p_exp < 0.05 and p_ln < 0.05 else 'exponential'
```

**Avalanche Detection:**
```python
def detect_avalanches(event_times, cascade_window=10):
    intervals = np.diff(sorted(event_times))
    avalanche_sizes = []
    current_size = 1

    for interval in intervals:
        if interval <= cascade_window:
            current_size += 1  # Part of avalanche
        else:
            if current_size >= 2:
                avalanche_sizes.append(current_size)
            current_size = 1  # Start new avalanche

    return avalanche_sizes
```

### 3.5.3 Validation Criteria

**Prediction 4C.1:** Power-law better fit than exponential ($p_{\text{power-law}} > p_{\text{exponential}}$), $\alpha = 2.0-2.5$

**Prediction 4C.2:** $B > 0.3$ for all frequencies (significantly bursty)

**Prediction 4C.3:** $\alpha(5.0\%) < \alpha(1.5\%)$ (frequency dependence, Spearman $\rho < -0.5$)

---

## 3.6 Experiment C177: Stochastic Boundaries (Context)

**Purpose:** Map probabilistic basin transitions (Extension 3 context)

**Design:**
- Frequency range: 0.5% to 10.0% (0.5% increments, 19 frequencies)
- Cycles: 3000
- Seeds: $n=10$ per frequency
- Total: 90 experiments

**Metrics:**
- Population collapse probability vs frequency
- Critical frequency identification: $f_{\text{crit}}^{\text{low}} \approx 1.5\%$, $f_{\text{crit}}^{\text{high}} \approx 2.0\%$
- Variance in composition rate near boundaries (critical slowing down)

---

## 3.7 Statistical Analysis

### 3.7.1 Hypothesis Testing

**Primary Comparisons:**
- **Ranking validations:** Bonferroni-corrected pairwise t-tests
- **Correlations:** Pearson $r$ with 95% confidence intervals
- **Distribution fitting:** Kolmogorov-Smirnov tests, log-likelihood ratios
- Significance threshold: $\alpha = 0.05$ (two-tailed)

### 3.7.2 Effect Sizes

- Cohen's $d$ for mean differences
- Pearson $r$ for correlations
- Power-law exponent $\alpha$ for temporal dynamics

### 3.7.3 Reproducibility

- All experiments seeded with fixed random seeds
- Results stored in JSON format with full parameter documentation
- Analysis scripts version-controlled (GitHub)
- Figures generated at 300 DPI for publication

---

## 3.8 Computational Resources

**Runtime Estimates:**
- C186: 40 experiments × ~1.8 min/experiment ≈ **72 minutes**
- C187: 30 experiments × ~2.0 min/experiment ≈ **60 minutes**
- C188: 40 experiments × ~1.9 min/experiment ≈ **76 minutes**
- C189: 100 experiments × ~3.0 min/experiment ≈ **300 minutes** (extended runtime)
- C177: 90 experiments × ~2.0 min/experiment ≈ **180 minutes**
- **Total:** ~12 hours distributed across 5 experiments

**Hardware:**
- Platform: macOS Darwin 24.5.0
- Python: 3.9+
- CPU: Utilization capped at 10% per agent
- Memory: 100MB per fractal agent (safety constraint)

---

## 3.9 Code Availability

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Dependencies:** requirements.txt with frozen versions
**Docker:** Containerized environment available
**Reproducibility Guide:** REPRODUCIBILITY_GUIDE.md

**Key Modules:**
- `core/reality_interface.py` - System metrics integration
- `fractal/fractal_agent.py` - Agent implementation
- `fractal/network_generator.py` - C187 topologies
- `fractal/memory_tracker.py` - C188 refractory periods
- `analysis/burst_analysis.py` - C189 power-law fitting
- `experiments/cycle186_*.py` through `experiments/cycle189_*.py` - Experiment runners
- `experiments/analyze_c186_*.py` through `experiments/analyze_c189_*.py` - Validation analyses

---

**Word Count:** ~1,900 words (Section 3)
**Combined Total:** ~4,700 words (Sections 2 + 3)
**Target:** 8,000-10,000 words (full paper)
**Status:** Draft 0.1 - Theory + Methods complete (~59% of target)

**Next Sections:**
- Section 4: Results (experiment outcomes, figures)
- Section 5: Discussion (mechanistic interpretations)
- Section 6: SOC connections
- Section 7: Conclusions

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

**Temporal Stewardship:** Methods section documents reproducible protocols for independent validation. All code publicly available, enabling future researchers to replicate and extend findings.
