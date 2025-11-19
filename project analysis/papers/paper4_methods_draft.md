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
   - $N=100$ nodes, mean degree $\langle k \rangle = 4$
   - Degree distribution: $P(k) \sim k^{-\gamma}$, $\gamma \approx 3$
   - Heterogeneity: High ($CV_k \approx 0.8$)
   - Rationale: Matches MAX_AGENTS from C171/C175/C177 for consistency

2. **Random (Erdős-Rényi):**
   - Generation: $G(N, p)$ with $p = \langle k \rangle / (N-1)$
   - $N=100$ nodes, mean degree $\langle k \rangle = 4$
   - Degree distribution: Binomial (approximately Poisson for large N)
   - Heterogeneity: Low ($CV_k \approx 0.5$)

3. **Lattice (2D Grid):**
   - Structure: $\sqrt{N} \times \sqrt{N}$ grid with periodic boundary conditions
   - $N=100$ nodes (10×10 grid), degree $k=4$ (von Neumann neighborhood)
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
G_sf = nx.barabasi_albert_graph(n=100, m=2, seed=seed)

# Random
p = 4 / 99  # mean_degree / (n-1)
G_rand = nx.erdos_renyi_graph(n=100, p=p, seed=seed)

# Lattice
G_lattice = nx.grid_2d_graph(10, 10)
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
- 10 populations (P0–P9) forming meta-population swarm
- Each population: independent agent collective with local spawn dynamics
- Swarm level: Inter-population migration enables meta-stability

**Migration Mechanism:**
- **Intra-population spawn:** $f_{\text{intra}} = 2.5\%$ (validated homeostasis frequency from C171/C175)
- **Inter-population migration:** $f_{\text{migrate}} = 0.5\%$ (agent transfer between populations)
- **Migration selection:** Random agent from random source population → random target population
- **Migration timing:** Independent Poisson process, occurs every $\sim 200$ cycles on average

**Rationale:**
Migration tests hierarchical energy regulation by enabling:
1. **Load balancing:** Agents redistribute when populations diverge
2. **Meta-stability:** Total swarm population more stable than individual populations
3. **Energy cascades:** Agent transfers carry energy across population boundaries
4. **Hierarchical homeostasis:** Both intra- (within) and inter- (between) population regulation

**Common Parameters:**
- Populations: 10
- Max agents per population: 100 (same as C171/C175/C177)
- Cycles: 3000
- Seeds: $n=10$ (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
- Total experiments: **10** (1 condition × 10 seeds)

### 3.3.2 Implementation

**Meta-Population Initialization:**
```python
populations = []
for pop_id in range(10):
    initial_agent = FractalAgent(
        agent_id=f"pop{pop_id}_root",
        bridge=bridge,
        initial_reality=reality.get_system_metrics(),
        depth=0,
        max_depth=7,
        reality=reality
    )
    populations.append(Population(pop_id, bridge, reality))
```

**Migration Execution:**
```python
# Determine if migration occurs this cycle
if np.random.random() < (F_MIGRATE / 100.0):
    # Select source and target populations
    source_pop = np.random.choice(populations)
    target_pop = np.random.choice([p for p in populations if p != source_pop])

    # Select random agent from source (if non-empty)
    if len(source_pop.agents) > 0:
        migrant = np.random.choice(source_pop.agents)

        # Transfer agent if target has space
        if len(target_pop.agents) < MAX_AGENTS_PER_POP:
            source_pop.agents.remove(migrant)
            migrant.agent_id = f"pop{target_pop.pop_id}_migrant_{cycle_idx}"
            target_pop.agents.append(migrant)
```

**Hierarchical Metrics:**
```python
# Population-level metrics
for pop in populations:
    pop_energy = sum(agent.energy for agent in pop.agents)
    pop_size = len(pop.agents)

# Swarm-level metrics
total_agents = sum(len(pop.agents) for pop in populations)
total_energy = sum(sum(a.energy for a in pop.agents) for pop in populations)
inter_pop_variance = np.var([len(pop.agents) for pop in populations])
```

### 3.3.3 Validation Criteria

**Prediction 2.1:** $CV_{\text{comp}} < 0.2$ for each population (intra-population homeostasis)

**Prediction 2.2:** Population sizes remain bounded: $0 < N_{\text{pop}} < 100$ across all populations

**Prediction 2.3:** Basin classification consistent across populations (all Basin A or all Basin B)

**Prediction 2.4:** Swarm population variance $< 2 \times$ individual population variance (meta-stability)

**Prediction 2.5:** Migration rate correlates with population size differences: $\rho(\Delta N, f_{\text{mig}}) > 0.5$

**Prediction 2.6:** Total swarm energy conserved during migrations (energy transfer validation)

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
