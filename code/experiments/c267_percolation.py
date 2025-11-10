#!/usr/bin/env python3
"""
Cycle 267: Percolation Dynamics in NRM Network Topology

Purpose: Test if NRM networks exhibit percolation phase transitions
MOG Resonance: α = 0.71 (Moderate-High Priority)

Hypothesis: NRM compositional networks show percolation at critical p_c
Predictions:
    1. Percolation threshold p_c ≈ 0.025-0.03
    2. Giant component scaling S_∞ ~ (p - p_c)^β where β ≈ 1.0
    3. Critical cluster distribution n_s ~ s^(-τ)

Cross-Domain Analogy:
    Domain A (NRM): Composition creates network edges, dynamic topology
    Domain B (Physics): Random graph percolation (Stauffer & Aharony 1994)
    Coupling: Composition rate ↔ Edge probability, Giant component ↔ System coordination

Design:
    f_spawn values: {0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.050} (9 levels)
    Seeds: n = 20 per condition (180 total experiments)
    Cycles: 5000
    Expected Runtime: ~3-4 hours

Falsification Criteria:
    - Reject if no threshold detected
    - Reject if scaling exponent β ≤ 0
    - Reject if critical point far from predicted p_c

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1384 Implementation)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
import networkx as nx
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
F_SPAWN_VALUES = [0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040, 0.050]  # 9 levels
SEEDS = list(range(42, 62))  # 20 seeds

# Fixed control parameters
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0

# Population parameters
N_INITIAL = 100

# Composition/decomposition thresholds
THETA_COMP = 0.85
THETA_DECOMP = 0.15

@dataclass
class Agent:
    """Fractal agent"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int

class PercolationSystem:
    """Population system with network percolation tracking"""

    def __init__(self, seed: int, f_spawn: float, db_path: Path):
        self.seed = seed
        self.f_spawn = f_spawn
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Compositional network
        self.composition_network = nx.Graph()

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.composition_count = 0
        self.decomposition_count = 0

        # Giant component tracking
        self.giant_component_history: List[float] = []

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self) -> Agent:
        """Create new agent"""
        depth = self.random.uniform(0.0, 1.0)
        agent = Agent(
            agent_id=self.next_agent_id,
            energy=E_MAX,
            depth=depth,
            birth_cycle=self.cycle_count
        )

        self.agents[agent.agent_id] = agent
        self.composition_network.add_node(agent.agent_id)
        self.next_agent_id += 1

        return agent

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Spawn attempt
        if self.random.random() < self.f_spawn:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check (create edges)
        if len(self.agents) >= 2:
            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i+1, len(agents_list)):
                    depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)

                    if depth_similarity >= THETA_COMP:
                        agents_list[i].energy -= 2.0
                        agents_list[j].energy -= 2.0
                        self.composition_count += 1

                        # Add edge to composition network
                        self.composition_network.add_edge(agents_list[i].agent_id, agents_list[j].agent_id)

        # Decomposition check
        if len(self.agents) >= 2:
            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i+1, len(agents_list)):
                    depth_distance = abs(agents_list[i].depth - agents_list[j].depth)

                    if depth_distance >= THETA_DECOMP:
                        agents_list[i].energy += 1.0
                        agents_list[j].energy += 1.0
                        self.decomposition_count += 1

        # Energy consumption and death
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            self._remove_agent(agent_id)

        # Measure giant component (every 100 cycles)
        if self.cycle_count % 100 == 0:
            self._measure_giant_component()

    def _attempt_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        if len(self.agents) == 0:
            return

        parent = self.random.choice(list(self.agents.values()))

        if parent.energy >= (E_THRESHOLD + SPAWN_COST):
            parent.energy -= SPAWN_COST
            self._create_agent()
            self.spawn_successes += 1

    def _remove_agent(self, agent_id: int):
        """Remove agent from population and network"""
        if agent_id in self.agents:
            del self.agents[agent_id]

        if self.composition_network.has_node(agent_id):
            self.composition_network.remove_node(agent_id)

    def _measure_giant_component(self):
        """Measure size of giant connected component"""
        if self.composition_network.number_of_nodes() == 0:
            self.giant_component_history.append(0.0)
            return

        # Find largest connected component
        components = list(nx.connected_components(self.composition_network))

        if len(components) == 0:
            giant_size = 0
        else:
            giant_size = max(len(c) for c in components)

        # Normalize by network size
        network_size = self.composition_network.number_of_nodes()
        s_infinity = giant_size / network_size if network_size > 0 else 0.0

        self.giant_component_history.append(s_infinity)

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for percolation analysis"""
        # Giant component metrics
        if len(self.giant_component_history) > 0:
            mean_s_infinity = float(np.mean(self.giant_component_history))
            final_s_infinity = float(self.giant_component_history[-1])
        else:
            mean_s_infinity = 0.0
            final_s_infinity = 0.0

        # Network metrics
        num_nodes = self.composition_network.number_of_nodes()
        num_edges = self.composition_network.number_of_edges()
        edge_density = (2 * num_edges / (num_nodes * (num_nodes - 1))) if num_nodes > 1 else 0.0

        # Cluster size distribution (for final network)
        components = list(nx.connected_components(self.composition_network))
        cluster_sizes = [len(c) for c in components]

        return {
            'mean_s_infinity': mean_s_infinity,
            'final_s_infinity': final_s_infinity,
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'edge_density': edge_density,
            'num_clusters': len(cluster_sizes),
            'largest_cluster': max(cluster_sizes) if len(cluster_sizes) > 0 else 0,
            'spawn_success_rate': (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0,
            'composition_count': self.composition_count,
            'decomposition_count': self.decomposition_count,
            'final_population': len(self.agents)
        }

def run_experiment(seed: int, f_spawn: float, output_path: Path, db_path: Path) -> Dict:
    """Run single percolation experiment"""
    f_spawn_idx = F_SPAWN_VALUES.index(f_spawn)
    seed_idx = SEEDS.index(seed)
    exp_num = f_spawn_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(F_SPAWN_VALUES) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] f={f_spawn:.3f}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = PercolationSystem(seed, f_spawn, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"S_∞={stats['final_s_infinity']:.3f} | "
          f"Edges={stats['num_edges']:4d} | "
          f"Clusters={stats['num_clusters']:3d} | "
          f"t={elapsed:4.1f}s")

    # Build result
    result = {
        'seed': seed,
        'f_spawn': f_spawn,
        **stats,
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full percolation experimental suite"""
    print("=" * 80)
    print("CYCLE 267: PERCOLATION DYNAMICS IN NRM NETWORK TOPOLOGY")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM networks exhibit percolation phase transitions")
    print("MOG Resonance: α = 0.71 (Moderate-High Priority)")
    print()
    print("Hypothesis: NRM compositional networks show percolation at critical p_c")
    print("Predictions:")
    print("  1. Percolation threshold p_c ≈ 0.025-0.03")
    print("  2. Giant component scaling S_∞ ~ (p - p_c)^β where β ≈ 1.0")
    print("  3. Critical cluster distribution n_s ~ s^(-τ)")
    print()
    print("Experimental Parameters:")
    print(f"  f_spawn values: {F_SPAWN_VALUES} (9 levels)")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(F_SPAWN_VALUES) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  Expected runtime: ~3-4 hours")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c267_percolation.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for f_spawn in F_SPAWN_VALUES:
        print()
        print(f"Testing f_spawn = {f_spawn}")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c267_fspawn{f_spawn}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, f_spawn, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'f_spawn':>10s} | {'Mean S_∞':>10s} | {'Mean Edges':>12s} | {'Mean Clusters':>14s}")
    print("-" * 80)

    for f_spawn in F_SPAWN_VALUES:
        condition_results = [r for r in results if r['f_spawn'] == f_spawn]

        mean_s_inf = np.mean([r['final_s_infinity'] for r in condition_results])
        mean_edges = np.mean([r['num_edges'] for r in condition_results])
        mean_clusters = np.mean([r['num_clusters'] for r in condition_results])

        print(f"{f_spawn:10.3f} | {mean_s_inf:10.3f} | {mean_edges:12.1f} | {mean_clusters:14.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C267_Percolation',
        'description': 'Test if NRM networks exhibit percolation phase transitions',
        'mog_resonance': 0.71,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'f_spawn_values': F_SPAWN_VALUES,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'total_experiments': len(results)
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c267_percolation.py")
    print()

if __name__ == '__main__':
    main()
