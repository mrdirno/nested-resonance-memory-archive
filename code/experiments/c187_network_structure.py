#!/usr/bin/env python3
"""
Cycle 187: Network Structure Effects on Energy Regulation

Purpose: Test whether network topology affects spawn success via degree-dependent selection
Background: Papers 1-2 used uniform random selection (all agents equally likely).
            Real systems exhibit spatial/topological structure (social, neural, ecological networks).

Hypothesis: Topology matters via degree-dependent selection:
            - Hubs (high degree) → selected frequently → energy depletion → bottleneck
            - Periphery (low degree) → selected rarely → underutilization

Design:
    Three Canonical Topologies (all with ⟨k⟩ ≈ 4):
    1. Scale-Free (Barabási-Albert): Power-law P(k) ~ k^(-γ), hubs + periphery
    2. Random (Erdős-Rényi): Poisson P(k), homogeneous degree distribution
    3. Lattice (2D Grid): Delta function P(k), all k=4 (maximum homogeneity)

    Selection Method: Degree-weighted (P_i ~ k_i, not uniform random)

Expected Outcomes:
    H2.1 (Hub Depletion): Spawn success ranking: Lattice > Random > Scale-Free
    H2.2 (Spawn Success Ranking): T-tests confirm ordered differences
    H2.3 (Degree-Weighted Selection): High-degree agents selected more frequently

Mechanism:
    Scale-free hubs experience 10-20× compositional load of periphery
    → λ_hub > λ_crit → chronic energy depletion → bottleneck
    → reduced spawn success compared to homogeneous topologies

Theoretical Prediction:
    λ_crit = α_recharge · (E_max - E_threshold) / E_cost
           = 0.5 · (50 - 20) / 10 = 1.5 compositions/cycle

    If λ_hub > 1.5, hub depletion occurs → spawn success drops

Parameters:
    cycles = 3000
    N = 100 nodes (match network size)
    ⟨k⟩ ≈ 4 (controlled across topologies)
    f_spawn = 2.5% (validated homeostasis frequency)
    seeds = 10 per topology (30 total experiments)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1295)
License: GPL-3.0
"""

import sys
import json
import time
import random
import sqlite3
import numpy as np
import networkx as nx
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 3000
N_NODES = 100
MEAN_DEGREE = 4
F_SPAWN = 0.025  # 2.5% (validated homeostasis frequency from Paper 2)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Network topology parameters
TOPOLOGIES = {
    'scale_free': {'type': 'barabasi_albert', 'n': N_NODES, 'm': 2},  # m=2 → ⟨k⟩≈4
    'random': {'type': 'erdos_renyi', 'n': N_NODES, 'p': 0.04},       # p=0.04 → ⟨k⟩≈4
    'lattice': {'type': 'grid_2d', 'rows': 10, 'cols': 10}            # 10×10 grid, k=4
}

# Energy parameters
E_INITIAL = 50.0
E_MAX = 50.0
E_THRESHOLD = 20.0
E_COST = 10.0
RECHARGE_RATE = 0.5

# Composition parameters
THETA_COMP = 0.85
THETA_DECOMP = 10.0

# Population parameters
N_INITIAL_MIN = 10
N_INITIAL_MAX = 20
BASIN_A_THRESHOLD = 2.5

@dataclass
class Agent:
    """Individual fractal agent in network"""
    id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0
    times_selected: int = 0  # Track selection frequency
    total_energy_at_selection: float = 0.0  # For mean energy when selected

@dataclass
class NetworkMetrics:
    """Network-level metrics for degree-stratified analysis"""
    degree_distribution: Dict[int, int]  # k → count
    mean_degree: float
    degree_variance: float
    hub_agents: List[int]      # Agent IDs with k ≥ ⟨k⟩ + 2σ_k
    core_agents: List[int]     # Agent IDs with ⟨k⟩ - σ_k ≤ k < ⟨k⟩ + 2σ_k
    periphery_agents: List[int]  # Agent IDs with k < ⟨k⟩ - σ_k

class NetworkedPopulationSystem:
    """Single population with network structure and degree-weighted selection"""

    def __init__(self, seed: int, topology: str, db_path: Path):
        self.seed = seed
        self.topology = topology
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Generate network
        self.network = self._generate_network()

        # Agent population
        self.agents: Dict[int, Agent] = {}  # agent_id → Agent
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0
        self.composition_events = 0
        self.decomposition_events = 0

        # Degree-stratified metrics
        self.selection_by_stratum = defaultdict(int)  # 'hub'/'core'/'periphery' → count
        self.spawn_by_stratum = defaultdict(int)

        # Network state history (sample every 100 cycles to reduce memory)
        self.network_history = []

        self._initialize_agents()

    def _generate_network(self) -> nx.Graph:
        """Generate network topology based on type"""
        topo_params = TOPOLOGIES[self.topology]
        topo_type = topo_params['type']

        if topo_type == 'barabasi_albert':
            # Scale-free network (preferential attachment)
            G = nx.barabasi_albert_graph(n=topo_params['n'], m=topo_params['m'], seed=self.seed)

        elif topo_type == 'erdos_renyi':
            # Random network (independent edge probability)
            G = nx.erdos_renyi_graph(n=topo_params['n'], p=topo_params['p'], seed=self.seed)

        elif topo_type == 'grid_2d':
            # 2D lattice (regular grid)
            G = nx.grid_2d_graph(rows=topo_params['rows'], cols=topo_params['cols'])
            # Relabel nodes from (i,j) tuples to integers 0..99
            mapping = {node: i for i, node in enumerate(G.nodes())}
            G = nx.relabel_nodes(G, mapping)

        else:
            raise ValueError(f"Unknown topology type: {topo_type}")

        return G

    def _initialize_agents(self):
        """Create initial population on network nodes"""
        n_initial = self.random.randint(N_INITIAL_MIN, N_INITIAL_MAX)

        # Randomly select initial nodes to populate
        initial_nodes = self.random.sample(list(self.network.nodes()), n_initial)

        for node_id in initial_nodes:
            phase = self.bridge.get_phase(np.pi)  # Initialize with π phase
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL,
                phase=phase,
                depth=0,
                compositions=0
            )
            self.agents[self.next_agent_id] = agent
            self.next_agent_id += 1

    def _get_network_metrics(self) -> NetworkMetrics:
        """Calculate degree-stratified network metrics"""
        # Degree distribution
        degrees = dict(self.network.degree())
        degree_values = list(degrees.values())

        degree_dist = defaultdict(int)
        for k in degree_values:
            degree_dist[k] += 1

        mean_k = np.mean(degree_values)
        var_k = np.var(degree_values)
        std_k = np.sqrt(var_k)

        # Stratify agents by degree
        hub_threshold = mean_k + 2 * std_k
        periphery_threshold = mean_k - std_k

        hubs = []
        core = []
        periphery = []

        for agent_id in self.agents.keys():
            if agent_id in degrees:
                k = degrees[agent_id]
                if k >= hub_threshold:
                    hubs.append(agent_id)
                elif k < periphery_threshold:
                    periphery.append(agent_id)
                else:
                    core.append(agent_id)

        return NetworkMetrics(
            degree_distribution=dict(degree_dist),
            mean_degree=mean_k,
            degree_variance=var_k,
            hub_agents=hubs,
            core_agents=core,
            periphery_agents=periphery
        )

    def _select_parent_degree_weighted(self) -> Optional[Agent]:
        """Select parent with probability proportional to degree (P_i ~ k_i)"""
        if not self.agents:
            return None

        # Get degrees for all agents
        degrees = dict(self.network.degree())
        agent_ids = list(self.agents.keys())

        # Filter agents that exist in network
        valid_agent_ids = [aid for aid in agent_ids if aid in degrees]
        if not valid_agent_ids:
            return None

        # Degree-weighted probabilities
        agent_degrees = np.array([degrees[aid] for aid in valid_agent_ids])

        # Handle case where all degrees are 0 (shouldn't happen in connected graphs)
        if agent_degrees.sum() == 0:
            # Fallback to uniform random
            selected_id = self.random.choice(valid_agent_ids)
        else:
            probabilities = agent_degrees / agent_degrees.sum()
            selected_id = self.np_random.choice(valid_agent_ids, p=probabilities)

        return self.agents[selected_id]

    def _try_spawn(self):
        """Attempt to spawn new agent (degree-weighted parent selection)"""
        self.spawn_attempts += 1

        parent = self._select_parent_degree_weighted()
        if parent is None:
            self.spawn_failures += 1
            return

        # Track selection
        parent.times_selected += 1
        parent.total_energy_at_selection += parent.energy

        # Check energy threshold
        if parent.energy < E_THRESHOLD:
            self.spawn_failures += 1
            return

        # Spawn succeeds
        parent.energy -= E_COST
        parent.compositions += 1
        self.spawn_successes += 1

        # Create child agent
        phase = self.bridge.get_phase(np.e)  # Use e for child phase
        child = Agent(
            id=self.next_agent_id,
            energy=E_INITIAL,
            phase=phase,
            depth=parent.depth + 1,
            compositions=0
        )
        self.agents[self.next_agent_id] = child
        self.next_agent_id += 1

        # Add child to network (connect to parent's neighbors or parent itself)
        # Simple strategy: connect child to parent and inherit one random neighbor
        self.network.add_node(child.id)
        self.network.add_edge(parent.id, child.id)

        parent_neighbors = list(self.network.neighbors(parent.id))
        if parent_neighbors:
            random_neighbor = self.random.choice(parent_neighbors)
            self.network.add_edge(child.id, random_neighbor)

    def _recharge_energy(self):
        """Recharge all agents' energy"""
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + RECHARGE_RATE)

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Spawn attempts (Poisson with mean = f_spawn * N)
        n_agents = len(self.agents)
        n_spawn_attempts = self.np_random.poisson(F_SPAWN * n_agents)

        for _ in range(n_spawn_attempts):
            self._try_spawn()

        # Energy recharge
        self._recharge_energy()

        # Sample network state every 100 cycles
        if self.cycle_count % 100 == 0:
            self._record_network_state()

    def _record_network_state(self):
        """Record network metrics for degree-stratified analysis"""
        metrics = self._get_network_metrics()

        # Calculate stratum-specific metrics
        hub_energies = [self.agents[aid].energy for aid in metrics.hub_agents if aid in self.agents]
        core_energies = [self.agents[aid].energy for aid in metrics.core_agents if aid in self.agents]
        periphery_energies = [self.agents[aid].energy for aid in metrics.periphery_agents if aid in self.agents]

        state = {
            'cycle': self.cycle_count,
            'n_agents': len(self.agents),
            'mean_degree': metrics.mean_degree,
            'degree_variance': metrics.degree_variance,
            'n_hubs': len(metrics.hub_agents),
            'n_core': len(metrics.core_agents),
            'n_periphery': len(metrics.periphery_agents),
            'hub_mean_energy': np.mean(hub_energies) if hub_energies else 0.0,
            'core_mean_energy': np.mean(core_energies) if core_energies else 0.0,
            'periphery_mean_energy': np.mean(periphery_energies) if periphery_energies else 0.0,
        }

        self.network_history.append(state)

    def get_final_statistics(self) -> Dict:
        """Calculate final experiment statistics"""
        mean_population = len(self.agents)
        basin = 'A' if mean_population > BASIN_A_THRESHOLD else 'B'

        spawn_success_rate = (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0

        # Final network metrics
        final_metrics = self._get_network_metrics()

        # Degree distribution summary
        degrees = dict(self.network.degree())
        degree_values = [degrees[aid] for aid in self.agents.keys() if aid in degrees]

        # Agent-level metrics for degree-stratified analysis
        agent_data = []
        for aid, agent in self.agents.items():
            if aid in degrees:
                agent_data.append({
                    'agent_id': aid,
                    'degree': degrees[aid],
                    'final_energy': agent.energy,
                    'depth': agent.depth,
                    'compositions': agent.compositions,
                    'times_selected': agent.times_selected,
                    'mean_energy_at_selection': (agent.total_energy_at_selection / agent.times_selected)
                                                if agent.times_selected > 0 else 0.0,
                })

        # Gini coefficient for energy inequality
        energies = [agent.energy for agent in self.agents.values()]
        gini = self._calculate_gini(energies) if energies else 0.0

        return {
            'cycle': self.cycle_count,
            'topology': self.topology,
            'final_agents': len(self.agents),
            'mean_population': mean_population,
            'basin': basin,
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'composition_events': self.spawn_successes,  # Each spawn is a composition
            'network_metrics': {
                'degree_distribution': final_metrics.degree_distribution,
                'mean_degree': final_metrics.mean_degree,
                'degree_variance': final_metrics.degree_variance,
                'degree_std': np.sqrt(final_metrics.degree_variance),
                'n_hubs': len(final_metrics.hub_agents),
                'n_core': len(final_metrics.core_agents),
                'n_periphery': len(final_metrics.periphery_agents),
            },
            'energy_inequality': {
                'gini_coefficient': gini,
                'mean_energy': np.mean(energies) if energies else 0.0,
                'energy_variance': np.var(energies) if energies else 0.0,
            },
            'agent_data': agent_data,
            'network_history': self.network_history,
        }

    def _calculate_gini(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        if not values or len(values) == 0:
            return 0.0

        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)

        # Gini = (2 * Σ(i * x_i)) / (n * Σx_i) - (n+1)/n
        numerator = 2 * np.sum((np.arange(1, n+1) * sorted_values))
        denominator = n * cumsum[-1]

        if denominator == 0:
            return 0.0

        gini = (numerator / denominator) - (n + 1) / n
        return gini

def run_experiment(seed: int, topology: str, output_path: Path, db_path: Path) -> Dict:
    """Run single network structure experiment"""
    topologies = list(TOPOLOGIES.keys())
    topo_idx = topologies.index(topology)
    seed_idx = SEEDS.index(seed)
    exp_num = topo_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(topologies) * len(SEEDS)

    print(f"  [{exp_num:2d}/{total_exps}] {topology:12s}, Seed {seed:3d}: ", end='', flush=True)

    clear_bridge_database(db_path)
    system = NetworkedPopulationSystem(seed, topology, db_path)

    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    final_stats = system.get_final_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:5.1f} | "
          f"η: {final_stats['spawn_success_rate']:5.1f}% | "
          f"⟨k⟩: {final_stats['network_metrics']['mean_degree']:4.1f} | "
          f"G: {final_stats['energy_inequality']['gini_coefficient']:.3f} | "
          f"{elapsed_total:4.0f}s")

    final_stats['seed'] = seed
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C187 network structure experiments"""

    print("=" * 80)
    print("CYCLE 187: NETWORK STRUCTURE EFFECTS ON ENERGY REGULATION")
    print("=" * 80)
    print()
    print("Purpose: Test if network topology affects spawn success via degree-dependent selection")
    print("Background: Papers 1-2 used uniform random selection.")
    print("            C187 tests degree-weighted selection (P_i ~ k_i)")
    print()
    print(f"Network Topologies (all with ⟨k⟩ ≈ 4):")
    print(f"  Scale-Free (Barabási-Albert): Power-law P(k) ~ k^(-γ), hubs + periphery")
    print(f"  Random (Erdős-Rényi): Poisson P(k), homogeneous degree distribution")
    print(f"  Lattice (2D Grid): Delta P(k), all k=4 (maximum homogeneity)")
    print()
    print(f"Experimental Parameters:")
    print(f"  f_spawn = {F_SPAWN*100:.1f}% (validated homeostasis frequency)")
    print(f"  N = {N_NODES} nodes")
    print(f"  Cycles = {CYCLES}")
    print(f"  Seeds per topology: n={len(SEEDS)}")
    print(f"  Total experiments: {len(TOPOLOGIES) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(TOPOLOGIES) * len(SEEDS) * 0.06:.1f} hours")
    print()
    print(f"Hypothesis H2.1 (Hub Depletion):")
    print(f"  Spawn success ranking: Lattice > Random > Scale-Free")
    print(f"  Mechanism: Hubs experience excessive compositional load → energy depletion")
    print()
    print(f"Hypothesis H2.2 (Spawn Success Ranking):")
    print(f"  T-tests confirm ordered differences (all pairwise p < 0.05)")
    print()
    print(f"Hypothesis H2.3 (Degree-Weighted Selection):")
    print(f"  High-degree agents selected more frequently (positive correlation r > 0.7)")
    print()

    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c187_network_structure.json"

    db_path = Path(__file__).parent.parent / "bridge" / "bridge.db"

    results = []
    start_time_total = time.time()

    for topology in TOPOLOGIES.keys():
        print()
        print(f"Testing {topology.upper()} topology")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, topology, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Topology':>12s} | {'Basin A %':>10s} | {'Mean η %':>10s} | {'Mean ⟨k⟩':>10s} | {'Mean G':>8s}")
    print("-" * 80)

    topology_aggregates = []
    for topology in TOPOLOGIES.keys():
        topo_results = [r for r in results if r['topology'] == topology]

        basin_a_count = sum(1 for r in topo_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(topo_results)) * 100

        spawn_rates = [r['spawn_success_rate'] for r in topo_results]
        mean_spawn_rate = np.mean(spawn_rates)

        mean_degrees = [r['network_metrics']['mean_degree'] for r in topo_results]
        mean_k_avg = np.mean(mean_degrees)

        ginis = [r['energy_inequality']['gini_coefficient'] for r in topo_results]
        gini_avg = np.mean(ginis)

        topology_aggregates.append({
            'topology': topology,
            'basin_a_pct': basin_a_pct,
            'mean_spawn_rate': mean_spawn_rate,
            'spawn_rate_values': spawn_rates,  # For statistical tests
            'mean_k_avg': mean_k_avg,
            'gini_avg': gini_avg
        })

        print(f"{topology:>12s} | {basin_a_pct:9.1f}% | {mean_spawn_rate:9.1f}% | {mean_k_avg:10.2f} | {gini_avg:8.3f}")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    print("=" * 80)
    print("HYPOTHESIS TESTING")
    print("=" * 80)
    print()

    # H2.1: Spawn success ranking
    sf_rate = topology_aggregates[0]['mean_spawn_rate']  # scale_free
    rand_rate = topology_aggregates[1]['mean_spawn_rate']  # random
    latt_rate = topology_aggregates[2]['mean_spawn_rate']  # lattice

    print("H2.1 (Hub Depletion Effect):")
    print(f"  Lattice: η = {latt_rate:.1f}%")
    print(f"  Random:  η = {rand_rate:.1f}%")
    print(f"  Scale-Free: η = {sf_rate:.1f}%")

    if latt_rate > rand_rate > sf_rate:
        print(f"  ✓ Ordering CONFIRMED: Lattice > Random > Scale-Free")
        h21_result = "SUPPORTED"
    else:
        print(f"  ⚠ Ordering NOT CONFIRMED")
        h21_result = "NOT_SUPPORTED"
    print()

    print("H2.3 (Energy Inequality):")
    sf_gini = topology_aggregates[0]['gini_avg']
    rand_gini = topology_aggregates[1]['gini_avg']
    latt_gini = topology_aggregates[2]['gini_avg']

    print(f"  Scale-Free: G = {sf_gini:.3f}")
    print(f"  Random:     G = {rand_gini:.3f}")
    print(f"  Lattice:    G = {latt_gini:.3f}")

    if sf_gini > rand_gini > latt_gini:
        print(f"  ✓ Inequality ranking CONFIRMED: Scale-Free > Random > Lattice")
        h23_result = "SUPPORTED"
    else:
        print(f"  ⚠ Inequality ranking NOT CONFIRMED")
        h23_result = "NOT_SUPPORTED"
    print()

    print(f"Note: Detailed statistical tests (t-tests, correlations) will be performed by")
    print(f"      analysis pipeline (analyze_c187_network_structure.py)")
    print()

    output_data = {
        'metadata': {
            'experiment': 'C187_NETWORK_STRUCTURE',
            'date': datetime.now().isoformat(),
            'purpose': 'Test network topology effects on spawn success via degree-weighted selection',
            'topologies': {k: v for k, v in TOPOLOGIES.items()},
            'f_spawn': F_SPAWN,
            'n_nodes': N_NODES,
            'mean_degree_target': MEAN_DEGREE,
            'cycles': CYCLES,
            'seeds': SEEDS,
            'hypotheses': {
                'H2.1': 'Spawn success ranking: Lattice > Random > Scale-Free',
                'H2.2': 'T-tests confirm ordered differences',
                'H2.3': 'Energy inequality (Gini) increases with degree variance',
            }
        },
        'topology_aggregates': topology_aggregates,
        'hypothesis_results': {
            'H2.1': h21_result,
            'H2.3': h23_result,
        },
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C187 COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Run analysis pipeline: python code/analysis/analyze_c187_network_structure.py")
    print("  2. Generate publication figures (degree distributions, η vs. topology, etc.)")
    print("  3. Perform statistical tests (ANOVA, t-tests, correlations)")
    print("  4. Update Paper 4 Section 3.1 with empirical results")

if __name__ == "__main__":
    main()
