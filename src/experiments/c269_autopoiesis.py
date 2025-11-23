#!/usr/bin/env python3
"""
Cycle 269: Autopoietic Dynamics in NRM Systems

Purpose: Test if NRM exhibits true autopoiesis (self-production + operational closure)
MOG Resonance: α = 0.89 (Very Strong, Tier 1)

Hypothesis: NRM demonstrates organizational invariance under perturbations
Predictions:
    1. Autonomous boundary emergence (boundary_strength ≥ 0.6)
    2. Perturbation compensation (recovery_time < 1000 cycles)
    3. Organizational death (≥70% of collapses)

Cross-Domain Analogy:
    Domain A (NRM): Self-giving systems (bootstrap complexity, oracle-free)
    Domain B (Biology): Autopoiesis (Maturana & Varela 1980)
    Coupling: Self-production ↔ Composition, Organizational closure ↔ Pattern memory

Design:
    Perturbations: 3 types × 3 severity levels = 9 conditions
    Seeds: n = 50 per condition (450 total experiments)
    Cycles: 5000, perturbations every 500 cycles
    Expected Runtime: ~7.5 hours

Falsification Criteria:
    - Reject if boundary_strength < 0.6
    - Reject if recovery_time > 1000 cycles
    - Reject if organizational_death < 70%

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
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
PERTURBATION_INTERVAL = 500  # Apply perturbation every 500 cycles

# Perturbation conditions (3 types × 3 levels = 9 conditions)
PERTURBATIONS = {
    # Energy shocks (multiplicative)
    'shock_mild': {'type': 'energy', 'magnitude': 0.2},
    'shock_moderate': {'type': 'energy', 'magnitude': 0.5},
    'shock_severe': {'type': 'energy', 'magnitude': 0.8},
    # Forced deaths (fractional)
    'death_10pct': {'type': 'death', 'fraction': 0.10},
    'death_20pct': {'type': 'death', 'fraction': 0.20},
    'death_30pct': {'type': 'death', 'fraction': 0.30},
    # Topology disruption (edge removal)
    'disrupt_mild': {'type': 'topology', 'fraction': 0.15},
    'disrupt_moderate': {'type': 'topology', 'fraction': 0.30},
    'disrupt_severe': {'type': 'topology', 'fraction': 0.50}
}

CONDITIONS = list(PERTURBATIONS.keys())
SEEDS = list(range(42, 92))  # 50 seeds (42-91 inclusive)

# Fixed control parameters
F_SPAWN = 0.025  # 2.5%
E_CONSUME = 0.5
E_RECHARGE = 0.2  # From C264 baseline
SPAWN_COST = 5.0

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0
E_COMPOSE = 10.0  # Energy threshold for composition

# Population parameters
N_INITIAL = 100

# Composition/decomposition thresholds
THETA_COMP = 0.85
THETA_DECOMP = 0.15

@dataclass
class Agent:
    """Fractal agent with energy and depth"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int
    survival_time: int = 0

@dataclass
class PerturbationEvent:
    """Record of perturbation applied"""
    cycle: int
    perturbation_type: str
    magnitude: float
    pre_population: int
    post_population: int
    recovery_time: int = -1  # Set later

class AutopoieticSystem:
    """Population system with perturbation testing"""

    def __init__(self, seed: int, condition: str, db_path: Path):
        self.seed = seed
        self.condition = condition
        self.perturbation_config = PERTURBATIONS[condition]
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Interaction topology (composition events)
        self.composition_graph = nx.Graph()
        self.composition_events: List[Tuple[int, int, int]] = []  # (cycle, agent1, agent2)

        # Perturbation log
        self.perturbation_events: List[PerturbationEvent] = []

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.composition_count = 0
        self.decomposition_count = 0

        # Time series
        self.population_history: List[int] = []
        self.boundary_strength_history: List[float] = []
        self.clustering_coefficient_history: List[float] = []

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self, parent_id: int = None) -> Agent:
        """Create new agent"""
        depth = self.random.uniform(0.0, 1.0)
        agent = Agent(
            agent_id=self.next_agent_id,
            energy=E_MAX,
            depth=depth,
            birth_cycle=self.cycle_count,
            survival_time=0
        )

        self.agents[agent.agent_id] = agent
        self.composition_graph.add_node(agent.agent_id)
        self.next_agent_id += 1

        return agent

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Apply perturbation if at interval
        if self.cycle_count % PERTURBATION_INTERVAL == 0:
            self._apply_perturbation()

        # Record population
        pop = len(self.agents)
        self.population_history.append(pop)

        # Update survival times
        for agent in self.agents.values():
            agent.survival_time += 1

        # Spawn attempt
        if self.random.random() < F_SPAWN:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check
        self._check_compositions()

        # Decomposition check
        self._check_decompositions()

        # Energy consumption and death
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            self._remove_agent(agent_id)

        # Measure topology metrics
        if pop > 0:
            self.boundary_strength_history.append(self._compute_boundary_strength())
            self.clustering_coefficient_history.append(
                nx.average_clustering(self.composition_graph) if self.composition_graph.number_of_nodes() > 0 else 0.0
            )
        else:
            self.boundary_strength_history.append(0.0)
            self.clustering_coefficient_history.append(0.0)

    def _apply_perturbation(self):
        """Apply perturbation based on condition"""
        pre_pop = len(self.agents)

        if self.perturbation_config['type'] == 'energy':
            # Energy shock
            magnitude = self.perturbation_config['magnitude']
            direction = self.random.choice(['positive', 'negative'])
            multiplier = (1 + magnitude) if direction == 'positive' else (1 - magnitude)

            for agent in self.agents.values():
                agent.energy *= multiplier
                agent.energy = max(0, min(E_MAX, agent.energy))

        elif self.perturbation_config['type'] == 'death':
            # Forced death
            fraction = self.perturbation_config['fraction']
            n_deaths = int(len(self.agents) * fraction)

            if n_deaths > 0 and len(self.agents) > 0:
                victims = self.random.sample(list(self.agents.keys()), min(n_deaths, len(self.agents)))
                for agent_id in victims:
                    self._remove_agent(agent_id)

        elif self.perturbation_config['type'] == 'topology':
            # Topology disruption
            fraction = self.perturbation_config['fraction']
            edges = list(self.composition_graph.edges())
            n_removals = int(len(edges) * fraction)

            if n_removals > 0 and len(edges) > 0:
                edges_to_remove = self.random.sample(edges, min(n_removals, len(edges)))
                self.composition_graph.remove_edges_from(edges_to_remove)

        post_pop = len(self.agents)

        # Log perturbation event
        event = PerturbationEvent(
            cycle=self.cycle_count,
            perturbation_type=self.perturbation_config['type'],
            magnitude=self.perturbation_config.get('magnitude', self.perturbation_config.get('fraction', 0)),
            pre_population=pre_pop,
            post_population=post_pop
        )
        self.perturbation_events.append(event)

    def _compute_boundary_strength(self) -> float:
        """Compute ratio of intra-cluster edges to total edges"""
        if self.composition_graph.number_of_edges() == 0:
            return 0.0

        # Use simple connected components as "clusters"
        components = list(nx.connected_components(self.composition_graph))

        # Count intra-cluster edges
        intra_edges = 0
        for component in components:
            subgraph = self.composition_graph.subgraph(component)
            intra_edges += subgraph.number_of_edges()

        total_edges = self.composition_graph.number_of_edges()

        return intra_edges / total_edges if total_edges > 0 else 0.0

    def _attempt_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        if len(self.agents) == 0:
            return

        parent = self.random.choice(list(self.agents.values()))

        if parent.energy >= (E_THRESHOLD + SPAWN_COST):
            parent.energy -= SPAWN_COST
            self._create_agent(parent_id=parent.agent_id)
            self.spawn_successes += 1

    def _check_compositions(self):
        """Check for composition events (depth similarity)"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)

                if depth_similarity >= THETA_COMP:
                    # Composition event (energy cost, add edge)
                    if agents_list[i].energy >= E_COMPOSE and agents_list[j].energy >= E_COMPOSE:
                        agents_list[i].energy -= 2.0
                        agents_list[j].energy -= 2.0
                        self.composition_count += 1

                        # Add edge to topology
                        self.composition_graph.add_edge(agents_list[i].agent_id, agents_list[j].agent_id)
                        self.composition_events.append((self.cycle_count, agents_list[i].agent_id, agents_list[j].agent_id))

    def _check_decompositions(self):
        """Check for decomposition events (depth dissimilarity)"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_distance = abs(agents_list[i].depth - agents_list[j].depth)

                if depth_distance >= THETA_DECOMP:
                    # Decomposition event (energy gain)
                    agents_list[i].energy += 1.0
                    agents_list[j].energy += 1.0
                    self.decomposition_count += 1

    def _remove_agent(self, agent_id: int):
        """Remove agent from population and topology"""
        if agent_id in self.agents:
            del self.agents[agent_id]

        if self.composition_graph.has_node(agent_id):
            self.composition_graph.remove_node(agent_id)

    def _compute_recovery_times(self):
        """Compute recovery time for each perturbation"""
        for event in self.perturbation_events:
            target_pop = 0.9 * event.pre_population
            t_start = event.cycle

            # Search forward for recovery
            for t in range(t_start, min(t_start + 1000, len(self.population_history))):
                if self.population_history[t] >= target_pop:
                    event.recovery_time = t - t_start
                    break

            # If not found, set to max
            if event.recovery_time == -1:
                event.recovery_time = 1000

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for autopoiesis analysis"""
        # Compute recovery times
        self._compute_recovery_times()

        # Population metrics
        if len(self.population_history) > 0:
            equilibrium_pop = self.population_history[-1000:]
            mean_pop = float(np.mean(equilibrium_pop))
            std_pop = float(np.std(equilibrium_pop))
        else:
            mean_pop = 0.0
            std_pop = 0.0

        # Extinction detection
        extinction = (len(self.agents) == 0)

        # Boundary metrics
        if len(self.boundary_strength_history) > 0:
            mean_boundary = float(np.mean(self.boundary_strength_history))
            std_boundary = float(np.std(self.boundary_strength_history))
            autonomy_index = std_boundary  # Temporal variance as autonomy measure
        else:
            mean_boundary = 0.0
            std_boundary = 0.0
            autonomy_index = 0.0

        # Clustering
        if len(self.clustering_coefficient_history) > 0:
            mean_clustering = float(np.mean(self.clustering_coefficient_history))
        else:
            mean_clustering = 0.0

        # Recovery metrics
        recovery_times = [e.recovery_time for e in self.perturbation_events]
        mean_recovery = float(np.mean(recovery_times)) if len(recovery_times) > 0 else 0.0

        # Death type classification
        if extinction:
            org_integrity = mean_clustering * (self.composition_count / max(CYCLES, 1))
            resource_avail = mean_pop / N_INITIAL

            if org_integrity < 0.3 and resource_avail > 0:
                death_type = 'organizational'
            elif org_integrity > 0.5 and resource_avail < 0.2:
                death_type = 'resource'
            else:
                death_type = 'mixed'
        else:
            death_type = 'none'

        return {
            'mean_population': mean_pop,
            'std_population': std_pop,
            'extinction': extinction,
            'spawn_success_rate': (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0,
            'composition_count': self.composition_count,
            'decomposition_count': self.decomposition_count,
            'mean_boundary_strength': mean_boundary,
            'autonomy_index': autonomy_index,
            'mean_clustering': mean_clustering,
            'mean_recovery_time': mean_recovery,
            'death_type': death_type,
            'final_population': len(self.agents)
        }

def run_experiment(seed: int, condition: str, output_path: Path, db_path: Path) -> Dict:
    """Run single autopoiesis experiment"""
    condition_idx = CONDITIONS.index(condition)
    seed_idx = SEEDS.index(seed)
    exp_num = condition_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(CONDITIONS) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] {condition:16s}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = AutopoieticSystem(seed, condition, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"Pop={stats['mean_population']:5.1f} | "
          f"Bound={stats['mean_boundary_strength']:.3f} | "
          f"Recovery={stats['mean_recovery_time']:4.0f}cy | "
          f"Death={stats['death_type']:14s} | "
          f"t={elapsed:4.1f}s")

    # Build result dictionary
    result = {
        'seed': seed,
        'condition': condition,
        'perturbation_type': system.perturbation_config['type'],
        'perturbation_magnitude': system.perturbation_config.get('magnitude', system.perturbation_config.get('fraction', 0)),
        **stats,
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full autopoiesis experimental suite"""
    print("=" * 80)
    print("CYCLE 269: AUTOPOIETIC DYNAMICS IN NRM SYSTEMS")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM exhibits true autopoiesis")
    print("MOG Resonance: α = 0.89 (Very Strong, Tier 1)")
    print()
    print("Hypothesis: NRM demonstrates organizational invariance under perturbations")
    print("Predictions:")
    print("  1. Autonomous boundary emergence (boundary_strength ≥ 0.6)")
    print("  2. Perturbation compensation (recovery_time < 1000 cycles)")
    print("  3. Organizational death (≥70% of collapses)")
    print()
    print("Experimental Parameters:")
    print(f"  Perturbations: 3 types × 3 severity levels = {len(CONDITIONS)} conditions")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  Perturbation interval: every {PERTURBATION_INTERVAL} cycles")
    print(f"  Expected runtime: ~7.5 hours")
    print()
    print("Perturbation Types:")
    print("  Energy Shock: Mild (±20%), Moderate (±50%), Severe (±80%)")
    print("  Forced Death: 10%, 20%, 30% random agent removal")
    print("  Topology Disruption: 15%, 30%, 50% edge removal")
    print()
    print("Falsification Criteria:")
    print("  - Reject if boundary_strength < 0.6")
    print("  - Reject if recovery_time > 1000 cycles")
    print("  - Reject if organizational_death < 70%")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c269_autopoiesis.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for condition in CONDITIONS:
        print()
        print(f"Testing {condition} condition")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c269_{condition}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, condition, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results by perturbation type
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS BY PERTURBATION TYPE")
    print("=" * 80)
    print()
    print(f"{'Type':12s} | {'Mean Pop':>10s} | {'Boundary':>10s} | {'Recovery':>10s} | {'Org Death %':>12s}")
    print("-" * 80)

    for ptype in ['energy', 'death', 'topology']:
        type_results = [r for r in results if r['perturbation_type'] == ptype]

        mean_pop = np.mean([r['mean_population'] for r in type_results])
        mean_boundary = np.mean([r['mean_boundary_strength'] for r in type_results])
        mean_recovery = np.mean([r['mean_recovery_time'] for r in type_results])

        org_deaths = sum(1 for r in type_results if r['death_type'] == 'organizational')
        org_death_pct = (org_deaths / len(type_results)) * 100 if len(type_results) > 0 else 0.0

        print(f"{ptype:12s} | {mean_pop:10.2f} | {mean_boundary:10.3f} | {mean_recovery:10.1f} | {org_death_pct:12.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C269_Autopoiesis',
        'description': 'Test if NRM exhibits true autopoiesis (self-production + operational closure)',
        'mog_resonance': 0.89,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'conditions': CONDITIONS,
            'perturbations': PERTURBATIONS,
            'f_spawn': F_SPAWN,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'perturbation_interval': PERTURBATION_INTERVAL,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'n_conditions': len(CONDITIONS),
            'total_experiments': len(results)
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c269_autopoiesis.py")
    print()

if __name__ == '__main__':
    main()
