#!/usr/bin/env python3
"""
Cycle 186 V6: Partial Compartmentalization Effects on Hierarchical Viability

Purpose: Test whether partial energy sharing reduces α below full compartmentalization
Background: C186 V1 (full compartmentalization) → 0% Basin A at f_intra=2.5%
            C186 V2 (full compartmentalization) → 50-60% Basin A at f_intra=5.0%

Hypothesis: Allowing some populations to share energy pools reduces effective α
            by enabling partial cross-population energy recovery.

Design:
    f_intra = 2.5% (FIXED at C186 V1 failure level)
    f_migrate = 0.5% (FIXED at baseline)
    n_pop = 10 populations
    N_initial = 20 agents per population

    Energy Pool Structures (3 conditions):
    1. ISOLATED: 10 independent energy pools (baseline, α_full)
    2. PAIRED: 5 clusters of 2 populations sharing energy (α_paired)
    3. CLUSTERED: 2 clusters of 5 populations sharing energy (α_clustered)

Expected Outcomes:
    ISOLATED: Basin A ≈ 0% (replicates C186 V1, full compartmentalization)
    PAIRED: Basin A ≈ 20-40% (partial sharing reduces α)
    CLUSTERED: Basin A ≈ 50-70% (more sharing further reduces α)

Mechanism:
    Shared energy pools → agents in cluster can recover from collective energy
    → reduced isolation → lower effective α
    → improved viability even at low f_intra

Quantitative Prediction:
    α_effective = α_full × (n_clusters / n_pop)

    ISOLATED: α = 2.0 (10/10 = 1.0, full compartmentalization)
    PAIRED: α ≈ 1.0 (5/10 = 0.5, half compartmentalization)
    CLUSTERED: α ≈ 0.4 (2/10 = 0.2, minimal compartmentalization)

    cycles = 3000
    seeds = 10 per condition (30 total experiments)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1054)
License: GPL-3.0
"""

import sys
import json
import time
import random
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
F_INTRA = 0.025  # 2.5% fixed (C186 V1 failure level)
F_MIGRATE = 0.005  # 0.5% fixed (baseline)
N_POP = 10
N_INITIAL = 20
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Energy pool structures
POOL_STRUCTURES = {
    'ISOLATED': [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]],  # 10 independent pools
    'PAIRED': [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],  # 5 clusters of 2
    'CLUSTERED': [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]  # 2 clusters of 5
}

# Energy parameters
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5

@dataclass
class Agent:
    """Individual fractal agent"""
    id: int
    population_id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0

@dataclass
class Population:
    """Population container"""
    id: int
    agents: List[Agent]
    cluster_id: int  # Which energy cluster this population belongs to

    def mean_population(self) -> float:
        return float(len(self.agents))

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

@dataclass
class EnergyCluster:
    """Cluster of populations sharing energy pool"""
    id: int
    population_ids: List[int]

    def total_energy(self, populations: List[Population]) -> float:
        """Total energy across all populations in cluster"""
        cluster_pops = [p for p in populations if p.id in self.population_ids]
        return sum(p.total_energy() for p in cluster_pops)

    def total_agents(self, populations: List[Population]) -> int:
        """Total agents across all populations in cluster"""
        cluster_pops = [p for p in populations if p.id in self.population_ids]
        return sum(len(p.agents) for p in cluster_pops)

class MetaPopulationSystem:
    """Meta-population system testing partial compartmentalization effects"""

    def __init__(self, seed: int, pool_structure: str, db_path: Path):
        self.seed = seed
        self.pool_structure = pool_structure
        self.random = random.Random(seed)
        self.bridge = TranscendentalBridge(db_path)

        self.populations: List[Population] = []
        self.clusters: List[EnergyCluster] = []
        self.next_agent_id = 0
        self.cycle_count = 0

        self.intra_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0
        self.composition_events = 0

        self._initialize_populations()
        self._initialize_clusters()

    def _initialize_populations(self):
        """Create initial population structure"""
        for pop_id in range(N_POP):
            agents = []
            for _ in range(N_INITIAL):
                phase = self.random.uniform(0, 2 * 3.14159)
                agent = Agent(
                    id=self.next_agent_id,
                    population_id=pop_id,
                    energy=E_INITIAL,
                    phase=phase,
                    depth=0,
                    compositions=0
                )
                agents.append(agent)
                self.next_agent_id += 1

            # Assign cluster_id based on pool structure
            cluster_id = self._find_cluster_for_population(pop_id)
            pop = Population(id=pop_id, agents=agents, cluster_id=cluster_id)
            self.populations.append(pop)

    def _find_cluster_for_population(self, pop_id: int) -> int:
        """Find which cluster a population belongs to"""
        structure = POOL_STRUCTURES[self.pool_structure]
        for cluster_id, pop_ids in enumerate(structure):
            if pop_id in pop_ids:
                return cluster_id
        return 0  # Default

    def _initialize_clusters(self):
        """Create energy clusters based on pool structure"""
        structure = POOL_STRUCTURES[self.pool_structure]
        for cluster_id, pop_ids in enumerate(structure):
            cluster = EnergyCluster(id=cluster_id, population_ids=pop_ids)
            self.clusters.append(cluster)

    def step(self):
        """Execute one cycle"""
        self.cycle_count += 1
        self._intra_spawning()
        if F_MIGRATE > 0:
            self._inter_migration()
        self._energy_recovery()
        self._composition_detection()

    def _intra_spawning(self):
        """Agents spawn within populations at F_INTRA rate"""
        for population in self.populations:
            if len(population.agents) == 0:
                continue

            n_attempts = int(len(population.agents) * F_INTRA)
            if self.random.random() < (len(population.agents) * F_INTRA - n_attempts):
                n_attempts += 1

            for _ in range(n_attempts):
                parent = self.random.choice(population.agents)

                # Energy check: use cluster-level energy for shared pools
                cluster = self.clusters[population.cluster_id]
                cluster_energy = cluster.total_energy(self.populations)
                cluster_agents = cluster.total_agents(self.populations)

                # Spawn threshold based on cluster-level energy availability
                if cluster_agents > 0 and cluster_energy >= E_SPAWN_THRESHOLD:
                    parent.energy -= E_SPAWN_COST
                    child_phase = parent.phase + self.random.gauss(0, 0.1)
                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_INITIAL * 0.5,
                        phase=child_phase,
                        depth=parent.depth + 1,
                        compositions=0
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    self.spawn_failures += 1

    def _inter_migration(self):
        """Migration between populations at F_MIGRATE rate"""
        if len(self.populations) < 2:
            return

        total_agents = sum(len(pop.agents) for pop in self.populations)
        n_attempts = int(total_agents * F_MIGRATE)
        if self.random.random() < (total_agents * F_MIGRATE - n_attempts):
            n_attempts += 1

        for _ in range(n_attempts):
            source_pops = [p for p in self.populations if len(p.agents) > 0]
            if not source_pops:
                continue

            source_pop = self.random.choice(source_pops)

            # Migration threshold based on cluster-level energy
            cluster = self.clusters[source_pop.cluster_id]
            cluster_energy = cluster.total_energy(self.populations)

            if cluster_energy >= E_MIGRATE_THRESHOLD:
                migrant = self.random.choice(source_pop.agents)
                dest_pops = [p for p in self.populations if p.id != source_pop.id]
                if not dest_pops:
                    continue

                dest_pop = self.random.choice(dest_pops)
                source_pop.agents.remove(migrant)
                migrant.population_id = dest_pop.id
                dest_pop.agents.append(migrant)
                self.migrations += 1

    def _energy_recovery(self):
        """All agents recover energy (shared within clusters)"""
        for cluster in self.clusters:
            # Calculate cluster-level energy pool
            cluster_pops = [p for p in self.populations if p.id in cluster.population_ids]
            cluster_agents = []
            for pop in cluster_pops:
                cluster_agents.extend(pop.agents)

            # Shared recharge: distribute evenly across cluster
            if cluster_agents:
                total_recharge = len(cluster_agents) * RECHARGE_RATE
                recharge_per_agent = total_recharge / len(cluster_agents)

                for agent in cluster_agents:
                    agent.energy = min(E_INITIAL, agent.energy + recharge_per_agent)

    def _composition_detection(self):
        """Detect composition events"""
        for population in self.populations:
            if len(population.agents) < 2:
                continue

            for i, agent_i in enumerate(population.agents):
                for agent_j in population.agents[i+1:]:
                    phase_diff = abs(agent_i.phase - agent_j.phase)
                    if phase_diff < 0.1 or phase_diff > (2 * 3.14159 - 0.1):
                        agent_i.compositions += 1
                        agent_j.compositions += 1
                        self.composition_events += 1
                        agent_i.phase = (agent_i.phase + 0.05) % (2 * 3.14159)
                        agent_j.phase = (agent_j.phase + 0.05) % (2 * 3.14159)
                        break

    def get_statistics(self) -> Dict:
        """Compute statistics"""
        all_agents = []
        populations_data = []

        for pop in self.populations:
            all_agents.extend(pop.agents)
            populations_data.append({
                'pop_id': pop.id,
                'cluster_id': pop.cluster_id,
                'n_agents': len(pop.agents),
                'total_energy': pop.total_energy(),
                'mean_energy': pop.total_energy() / len(pop.agents) if pop.agents else 0.0
            })

        mean_population = len(all_agents) / N_POP if N_POP > 0 else 0.0
        basin = 'A' if mean_population > 2.5 else 'B'

        pop_sizes = [len(pop.agents) for pop in self.populations]
        if len(pop_sizes) > 1 and mean_population > 0:
            import statistics
            cv = (statistics.stdev(pop_sizes) / mean_population) * 100
        else:
            cv = 0.0

        total_spawn_attempts = self.intra_spawns + self.spawn_failures
        spawn_success_rate = (self.intra_spawns / total_spawn_attempts * 100) if total_spawn_attempts > 0 else 0.0

        # Cluster statistics
        cluster_stats = []
        for cluster in self.clusters:
            cluster_energy = cluster.total_energy(self.populations)
            cluster_agents = cluster.total_agents(self.populations)
            cluster_stats.append({
                'cluster_id': cluster.id,
                'population_ids': cluster.population_ids,
                'total_agents': cluster_agents,
                'total_energy': cluster_energy,
                'mean_energy_per_agent': cluster_energy / cluster_agents if cluster_agents > 0 else 0.0
            })

        return {
            'cycle': self.cycle_count,
            'total_agents': len(all_agents),
            'mean_population': mean_population,
            'basin': basin,
            'cv_percent': cv,
            'intra_spawns': self.intra_spawns,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'migrations': self.migrations,
            'compositions': self.composition_events,
            'populations': populations_data,
            'clusters': cluster_stats
        }

def run_experiment(seed: int, pool_structure: str, output_path: Path, db_path: Path) -> Dict:
    """Run single experiment"""
    structures = list(POOL_STRUCTURES.keys())
    struct_idx = structures.index(pool_structure)
    seed_idx = SEEDS.index(seed)
    exp_num = struct_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(structures) * len(SEEDS)

    print(f"  [{exp_num:2d}/{total_exps}] {pool_structure:10s}, Seed {seed:3d}: ", end='', flush=True)

    clear_bridge_database(db_path)
    system = MetaPopulationSystem(seed, pool_structure, db_path)

    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    final_stats = system.get_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:4.1f} | "
          f"CV: {final_stats['cv_percent']:5.1f}% | "
          f"Clusters: {len(POOL_STRUCTURES[pool_structure])} | "
          f"{elapsed_total:4.0f}s")

    final_stats['seed'] = seed
    final_stats['f_intra'] = F_INTRA
    final_stats['f_migrate'] = F_MIGRATE
    final_stats['pool_structure'] = pool_structure
    final_stats['n_clusters'] = len(POOL_STRUCTURES[pool_structure])
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C186 V6 partial compartmentalization experiments"""

    print("=" * 80)
    print("CYCLE 186 V6: PARTIAL COMPARTMENTALIZATION EFFECTS")
    print("=" * 80)
    print()
    print("Purpose: Test if partial energy sharing reduces α below full compartmentalization")
    print("Background: C186 V1 (full compartmentalization) → 0% Basin A at f_intra=2.5%")
    print()
    print(f"Experimental Design:")
    print(f"  f_intra = {F_INTRA*100:.1f}% (FIXED at C186 V1 failure level)")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (FIXED at baseline)")
    print(f"  n_pop = {N_POP} populations")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print()
    print(f"Energy Pool Structures:")
    print(f"  ISOLATED: 10 independent pools (baseline, α_full)")
    print(f"  PAIRED: 5 clusters of 2 populations (α_paired)")
    print(f"  CLUSTERED: 2 clusters of 5 populations (α_clustered)")
    print()
    print(f"Experimental Parameters:")
    print(f"  Seeds per structure: n={len(SEEDS)}")
    print(f"  Cycles per seed: {CYCLES}")
    print(f"  Total experiments: {len(POOL_STRUCTURES) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(POOL_STRUCTURES) * len(SEEDS) * 0.04:.1f} hours")
    print()
    print(f"Hypothesis:")
    print(f"  ISOLATED: Basin A ≈ 0% (replicates C186 V1)")
    print(f"  PAIRED: Basin A ≈ 20-40% (partial sharing)")
    print(f"  CLUSTERED: Basin A ≈ 50-70% (extensive sharing)")
    print()

    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c186_v6_partial_compartmentalization.json"

    db_path = Path(__file__).parent.parent / "bridge" / "bridge.db"

    results = []
    start_time_total = time.time()

    for pool_structure in POOL_STRUCTURES.keys():
        print()
        print(f"Testing {pool_structure} structure")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, pool_structure, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Structure':>12s} | {'Basin A %':>10s} | {'Mean Pop':>10s} | {'CV %':>8s} | {'Clusters':>8s}")
    print("-" * 80)

    structure_aggregates = []
    for pool_structure in POOL_STRUCTURES.keys():
        struct_results = [r for r in results if r['pool_structure'] == pool_structure]

        basin_a_count = sum(1 for r in struct_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(struct_results)) * 100

        mean_pops = [r['mean_population'] for r in struct_results]
        mean_pop_avg = sum(mean_pops) / len(mean_pops)

        cvs = [r['cv_percent'] for r in struct_results]
        cv_avg = sum(cvs) / len(cvs)

        n_clusters = len(POOL_STRUCTURES[pool_structure])

        structure_aggregates.append({
            'pool_structure': pool_structure,
            'basin_a_pct': basin_a_pct,
            'mean_pop_avg': mean_pop_avg,
            'cv_avg': cv_avg,
            'n_clusters': n_clusters
        })

        print(f"{pool_structure:>12s} | {basin_a_pct:9.1f}% | {mean_pop_avg:10.2f} | {cv_avg:7.1f}% | {n_clusters:8d}")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    isolated = structure_aggregates[0]['basin_a_pct']   # ISOLATED
    paired = structure_aggregates[1]['basin_a_pct']     # PAIRED
    clustered = structure_aggregates[2]['basin_a_pct']  # CLUSTERED

    if abs(isolated) < 10:
        print(f"✓ Control validated: ISOLATED → {isolated:.1f}% Basin A (matches C186 V1)")
    else:
        print(f"⚠ Control mismatch: ISOLATED → {isolated:.1f}% Basin A (expected ~0%)")

    if clustered > paired > isolated:
        print(f"✓ Hypothesis SUPPORTED: Basin A increases with energy sharing")
        print(f"  Partial compartmentalization reduces α")
        print(f"  {isolated:.1f}% → {paired:.1f}% → {clustered:.1f}% Basin A")
    else:
        print(f"⚠ Hypothesis NOT SUPPORTED: Basin A does not increase monotonically")

    print()

    output_data = {
        'metadata': {
            'experiment': 'C186_V6_PARTIAL_COMPARTMENTALIZATION',
            'date': datetime.now().isoformat(),
            'purpose': 'Test if partial energy sharing reduces α',
            'f_intra': F_INTRA,
            'f_migrate': F_MIGRATE,
            'pool_structures': {k: v for k, v in POOL_STRUCTURES.items()},
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'seeds': SEEDS,
        },
        'structure_aggregates': structure_aggregates,
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C186 V6 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
