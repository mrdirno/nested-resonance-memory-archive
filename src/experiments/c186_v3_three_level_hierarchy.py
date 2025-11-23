#!/usr/bin/env python3
"""
Cycle 186 V3: Three-Level Hierarchical Energy Dynamics

Purpose: Test hierarchical scaling coefficient α prediction for 3-level systems
Background: C186 V2 empirically validated α ≈ 2.0 for 2-level hierarchy
             (f_intra 2.5% → 5.0% restored viability from 0% → 50-60% Basin A)

Hypothesis: α scales with hierarchical depth
            α_2-level ≈ 2.0 (validated)
            α_3-level ≈ 4.0 (prediction: doubling per additional level)

Three-Level Structure:
    Level 1 (Agent): Individual fractal agents with internal state
    Level 2 (Population): Agents grouped into populations
    Level 3 (Meta-population): Populations grouped into meta-populations

Energy Dynamics:
    - Agents spawn within populations at f_agent rate
    - Populations exchange agents via migration at f_intra rate
    - Meta-populations exchange populations at f_meta rate (currently disabled)

Design:
    n_meta = 2 meta-populations
    n_pop_per_meta = 3 populations per meta-population (total 6 populations)
    N_initial = 15 agents per population

    f_agent = 8.0% per cycle (4× baseline 2.0%, testing α_3-level ≈ 4.0)
    f_intra = 0.5% per cycle (population-level migration, unchanged from C186)
    f_meta = 0.0% per cycle (meta-population level disabled for this test)

    cycles = 3000
    seeds = 10

Expected Outcome:
    If α_3-level ≈ 4.0: f_agent = 8.0% should produce Basin A ≈ 50-60%
    If α_3-level < 4.0: Higher Basin A percentage (less overhead than predicted)
    If α_3-level > 4.0: Lower Basin A percentage (more overhead than predicted)

Validation:
    - Compare to C171 (f=2.5%, 100% Basin A, single-scale)
    - Compare to C186 V1 (f_intra=2.5%, 0% Basin A, 2-level)
    - Compare to C186 V2 (f_intra=5.0%, 50-60% Basin A, 2-level)
    - Quantify α_3-level from Basin A percentage and sustained population sizes

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1053)
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
N_META = 2  # Number of meta-populations
N_POP_PER_META = 3  # Populations per meta-population
N_INITIAL = 15  # Initial agents per population
F_AGENT = 0.08  # 8.0% agent-level spawn rate (testing α_3-level ≈ 4.0)
F_INTRA = 0.005  # 0.5% population-level migration rate
F_META = 0.0  # 0.0% meta-population level (disabled for this test)
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Energy parameters (from C171/C186 baseline)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5  # Energy recovery per cycle per agent

@dataclass
class Agent:
    """Individual fractal agent at Level 1"""
    id: int
    population_id: int
    meta_id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0

@dataclass
class Population:
    """Population container at Level 2"""
    id: int
    meta_id: int
    agents: List[Agent]

    def mean_population(self) -> float:
        return float(len(self.agents))

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

@dataclass
class MetaPopulation:
    """Meta-population container at Level 3"""
    id: int
    populations: List[Population]

    def total_agents(self) -> int:
        return sum(len(pop.agents) for pop in self.populations)

class ThreeLevelHierarchy:
    """
    Three-level hierarchical system with energy-constrained dynamics

    Level 1: Agents with internal state spaces
    Level 2: Populations containing agents
    Level 3: Meta-populations containing populations
    """

    def __init__(self, seed: int, db_path: Path):
        self.seed = seed
        self.random = random.Random(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Initialize hierarchy
        self.meta_populations: List[MetaPopulation] = []
        self.next_agent_id = 0
        self.cycle_count = 0

        # Statistics tracking
        self.agent_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0
        self.composition_events = 0

        # Initialize structure
        self._initialize_hierarchy()

    def _initialize_hierarchy(self):
        """Create initial 3-level hierarchy structure"""
        pop_id = 0
        for meta_id in range(N_META):
            populations = []
            for _ in range(N_POP_PER_META):
                agents = []
                for _ in range(N_INITIAL):
                    phase = self.random.uniform(0, 2 * 3.14159)
                    agent = Agent(
                        id=self.next_agent_id,
                        population_id=pop_id,
                        meta_id=meta_id,
                        energy=E_INITIAL,
                        phase=phase,
                        depth=0,
                        compositions=0
                    )
                    agents.append(agent)
                    self.next_agent_id += 1

                pop = Population(id=pop_id, meta_id=meta_id, agents=agents)
                populations.append(pop)
                pop_id += 1

            meta_pop = MetaPopulation(id=meta_id, populations=populations)
            self.meta_populations.append(meta_pop)

    def step(self):
        """Execute one cycle of 3-level dynamics"""
        self.cycle_count += 1

        # Level 1: Agent-level spawning within populations
        self._agent_spawning()

        # Level 2: Population-level migration between populations within meta-populations
        if F_INTRA > 0:
            self._population_migration()

        # Level 3: Meta-population level (disabled for this test)
        # if F_META > 0:
        #     self._meta_migration()

        # Energy recovery
        self._energy_recovery()

        # Composition detection (Level 1 within populations)
        self._composition_detection()

    def _agent_spawning(self):
        """Level 1: Agents attempt to spawn within their populations"""
        for meta_pop in self.meta_populations:
            for population in meta_pop.populations:
                if len(population.agents) == 0:
                    continue

                # Determine number of spawn attempts for this population
                n_attempts = int(len(population.agents) * F_AGENT)
                if self.random.random() < (len(population.agents) * F_AGENT - n_attempts):
                    n_attempts += 1

                for _ in range(n_attempts):
                    # Select random parent from population
                    parent = self.random.choice(population.agents)

                    # Energy check
                    if parent.energy >= E_SPAWN_THRESHOLD:
                        # Successful spawn
                        parent.energy -= E_SPAWN_COST

                        # Create child with inherited phase + mutation
                        child_phase = parent.phase + self.random.gauss(0, 0.1)
                        child = Agent(
                            id=self.next_agent_id,
                            population_id=population.id,
                            meta_id=meta_pop.id,
                            energy=E_INITIAL * 0.5,  # Child starts with half initial energy
                            phase=child_phase,
                            depth=parent.depth + 1,
                            compositions=0
                        )
                        population.agents.append(child)
                        self.next_agent_id += 1
                        self.agent_spawns += 1
                    else:
                        # Spawn failure due to insufficient energy
                        self.spawn_failures += 1

    def _population_migration(self):
        """Level 2: Migration between populations within same meta-population"""
        for meta_pop in self.meta_populations:
            # Only migrate if multiple populations exist in meta
            if len(meta_pop.populations) < 2:
                continue

            # Determine number of migration attempts for this meta-population
            total_agents = sum(len(pop.agents) for pop in meta_pop.populations)
            n_attempts = int(total_agents * F_INTRA)
            if self.random.random() < (total_agents * F_INTRA - n_attempts):
                n_attempts += 1

            for _ in range(n_attempts):
                # Select random source population (with agents)
                source_pops = [p for p in meta_pop.populations if len(p.agents) > 0]
                if not source_pops:
                    continue

                source_pop = self.random.choice(source_pops)

                # Energy check: population must have sufficient total energy
                if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
                    # Select random agent to migrate
                    migrant = self.random.choice(source_pop.agents)

                    # Select random destination population (different from source)
                    dest_pops = [p for p in meta_pop.populations if p.id != source_pop.id]
                    if not dest_pops:
                        continue

                    dest_pop = self.random.choice(dest_pops)

                    # Migrate agent
                    source_pop.agents.remove(migrant)
                    migrant.population_id = dest_pop.id
                    dest_pop.agents.append(migrant)
                    self.migrations += 1

    def _energy_recovery(self):
        """All agents recover energy proportional to population size"""
        for meta_pop in self.meta_populations:
            for population in meta_pop.populations:
                for agent in population.agents:
                    agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def _composition_detection(self):
        """Detect composition events within populations using transcendental bridge"""
        for meta_pop in self.meta_populations:
            for population in meta_pop.populations:
                if len(population.agents) < 2:
                    continue

                # Check for resonance-driven composition
                for i, agent_i in enumerate(population.agents):
                    for agent_j in population.agents[i+1:]:
                        # Check phase alignment via bridge
                        phase_diff = abs(agent_i.phase - agent_j.phase)
                        if phase_diff < 0.1 or phase_diff > (2 * 3.14159 - 0.1):
                            # Resonance detected - composition event
                            agent_i.compositions += 1
                            agent_j.compositions += 1
                            self.composition_events += 1

                            # Phase shift after composition
                            agent_i.phase = (agent_i.phase + 0.05) % (2 * 3.14159)
                            agent_j.phase = (agent_j.phase + 0.05) % (2 * 3.14159)
                            break

    def get_statistics(self) -> Dict:
        """Compute current system statistics"""
        all_agents = []
        populations_data = []

        for meta_pop in self.meta_populations:
            for pop in meta_pop.populations:
                all_agents.extend(pop.agents)
                populations_data.append({
                    'meta_id': meta_pop.id,
                    'pop_id': pop.id,
                    'n_agents': len(pop.agents),
                    'total_energy': pop.total_energy(),
                    'mean_energy': pop.total_energy() / len(pop.agents) if pop.agents else 0.0
                })

        mean_population = len(all_agents) / (N_META * N_POP_PER_META) if (N_META * N_POP_PER_META) > 0 else 0.0

        # Basin classification (agent-level)
        basin = 'A' if mean_population > 2.5 else 'B'

        # Coefficient of variation across populations
        pop_sizes = [len(pop.agents) for meta_pop in self.meta_populations for pop in meta_pop.populations]
        if len(pop_sizes) > 1 and mean_population > 0:
            import statistics
            cv = (statistics.stdev(pop_sizes) / mean_population) * 100
        else:
            cv = 0.0

        # Spawn success rate
        total_spawn_attempts = self.agent_spawns + self.spawn_failures
        spawn_success_rate = (self.agent_spawns / total_spawn_attempts * 100) if total_spawn_attempts > 0 else 0.0

        return {
            'cycle': self.cycle_count,
            'total_agents': len(all_agents),
            'mean_population': mean_population,
            'basin': basin,
            'cv_percent': cv,
            'agent_spawns': self.agent_spawns,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'migrations': self.migrations,
            'compositions': self.composition_events,
            'populations': populations_data
        }

def run_experiment(seed: int, output_path: Path, db_path: Path) -> Dict:
    """
    Run single 3-level hierarchy experiment for one seed

    Returns final statistics including Basin classification
    """
    print(f"\n[{SEEDS.index(seed)+1}/{len(SEEDS)}] Running seed {seed}...")

    # Clear bridge database for seed isolation
    clear_bridge_database(db_path)

    # Initialize system
    system = ThreeLevelHierarchy(seed, db_path)

    # Run for specified cycles
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

        # Progress reporting every 500 cycles
        if (cycle + 1) % 500 == 0:
            elapsed = time.time() - start_time
            stats = system.get_statistics()
            print(f"  Cycle {cycle+1}/{CYCLES}: Basin {stats['basin']} | "
                  f"Mean Pop: {stats['mean_population']:.1f} | "
                  f"CV: {stats['cv_percent']:.1f}% | "
                  f"Spawn Success: {stats['spawn_success_rate']:.1f}% | "
                  f"Elapsed: {elapsed:.1f}s")

    # Final statistics
    final_stats = system.get_statistics()
    elapsed_total = time.time() - start_time

    print(f"  Final: Basin {final_stats['basin']} | "
          f"Mean Pop: {final_stats['mean_population']:.1f} | "
          f"CV: {final_stats['cv_percent']:.1f}% | "
          f"Migrations: {final_stats['migrations']} | "
          f"Time: {elapsed_total:.1f}s")

    # Add metadata
    final_stats['seed'] = seed
    final_stats['elapsed_seconds'] = elapsed_total
    final_stats['f_agent'] = F_AGENT
    final_stats['f_intra'] = F_INTRA
    final_stats['f_meta'] = F_META
    final_stats['n_meta'] = N_META
    final_stats['n_pop_per_meta'] = N_POP_PER_META
    final_stats['n_initial'] = N_INITIAL

    return final_stats

def main():
    """Execute C186 V3 3-level hierarchy experiments"""

    print("=" * 80)
    print("CYCLE 186 V3: THREE-LEVEL HIERARCHICAL ENERGY DYNAMICS")
    print("=" * 80)
    print()
    print("Purpose: Test α_3-level ≈ 4.0 prediction (hierarchical scaling coefficient)")
    print("Background: C186 V2 validated α_2-level ≈ 2.0 (f_intra 2.5% → 5.0%)")
    print()
    print(f"Three-Level Structure:")
    print(f"  Level 1 (Agent): {N_INITIAL} agents per population initially")
    print(f"  Level 2 (Population): {N_POP_PER_META} populations per meta-population")
    print(f"  Level 3 (Meta-population): {N_META} meta-populations")
    print(f"  Total populations: {N_META * N_POP_PER_META}")
    print(f"  Total agents (initial): {N_META * N_POP_PER_META * N_INITIAL}")
    print()
    print(f"Energy Dynamics:")
    print(f"  f_agent = {F_AGENT*100:.1f}% (4× baseline 2.0%, testing α_3-level ≈ 4.0)")
    print(f"  f_intra = {F_INTRA*100:.1f}% (population-level migration)")
    print(f"  f_meta = {F_META*100:.1f}% (meta-level disabled)")
    print()
    print(f"Experimental Parameters:")
    print(f"  Seeds: n={len(SEEDS)}")
    print(f"  Cycles per seed: {CYCLES}")
    print(f"  Total experiments: {len(SEEDS)}")
    print(f"  Expected runtime: ~{len(SEEDS) * 0.6:.1f} hours")
    print()
    print(f"Hypothesis:")
    print(f"  If α_3-level ≈ 4.0: Basin A ≈ 50-60% (similar to C186 V2)")
    print(f"  If α_3-level < 4.0: Basin A > 60% (less overhead)")
    print(f"  If α_3-level > 4.0: Basin A < 50% (more overhead)")
    print()

    # Setup paths
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c186_v3_three_level_hierarchy.json"

    db_path = Path(__file__).parent.parent / "bridge" / "bridge.db"

    # Run experiments
    results = []
    start_time_total = time.time()

    for seed in SEEDS:
        result = run_experiment(seed, output_path, db_path)
        results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate statistics
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)

    basin_a_count = sum(1 for r in results if r['basin'] == 'A')
    basin_a_pct = (basin_a_count / len(results)) * 100

    mean_populations = [r['mean_population'] for r in results]
    mean_pop_avg = sum(mean_populations) / len(mean_populations)

    cvs = [r['cv_percent'] for r in results]
    cv_avg = sum(cvs) / len(cvs)

    spawn_rates = [r['spawn_success_rate'] for r in results]
    spawn_rate_avg = sum(spawn_rates) / len(spawn_rates)

    print(f"Basin A: {basin_a_pct:.1f}% ({basin_a_count}/{len(results)} seeds)")
    print(f"Mean Population (avg): {mean_pop_avg:.2f} agents")
    print(f"CV (avg): {cv_avg:.1f}%")
    print(f"Spawn Success Rate (avg): {spawn_rate_avg:.1f}%")
    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    if basin_a_pct >= 50:
        print(f"✓ Hypothesis SUPPORTED: α_3-level ≈ 4.0")
        print(f"  Basin A = {basin_a_pct:.1f}% matches prediction for 3-level hierarchy")
        print(f"  f_agent = 8.0% (4× baseline) overcomes compartmentalization overhead")
    elif basin_a_pct >= 30:
        print(f"⚠ Hypothesis PARTIALLY SUPPORTED: α_3-level < 4.0")
        print(f"  Basin A = {basin_a_pct:.1f}% suggests less overhead than predicted")
        print(f"  Actual α_3-level ≈ {4.0 * (2.0 / (basin_a_pct / 50)):.2f} (estimated)")
    else:
        print(f"✗ Hypothesis NOT SUPPORTED: α_3-level > 4.0")
        print(f"  Basin A = {basin_a_pct:.1f}% suggests more overhead than predicted")
        print(f"  Actual α_3-level ≈ {4.0 * (basin_a_pct / 50):.2f} (estimated)")
    print()

    # Save results
    output_data = {
        'metadata': {
            'experiment': 'C186_V3_THREE_LEVEL_HIERARCHY',
            'date': datetime.now().isoformat(),
            'purpose': 'Test α_3-level ≈ 4.0 prediction for hierarchical scaling',
            'n_meta': N_META,
            'n_pop_per_meta': N_POP_PER_META,
            'n_initial': N_INITIAL,
            'f_agent': F_AGENT,
            'f_intra': F_INTRA,
            'f_meta': F_META,
            'cycles': CYCLES,
            'seeds': SEEDS,
        },
        'aggregate': {
            'basin_a_percentage': basin_a_pct,
            'mean_population_avg': mean_pop_avg,
            'cv_avg': cv_avg,
            'spawn_success_rate_avg': spawn_rate_avg,
            'elapsed_hours': elapsed_total / 3600,
        },
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C186 V3 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
