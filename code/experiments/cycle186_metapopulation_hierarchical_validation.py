#!/usr/bin/env python3
"""
CYCLE 186: META-POPULATION HIERARCHICAL RESONANCE VALIDATION

Purpose: Test hierarchical energy dynamics predictions (THEORETICAL_EXTENSIONS_HIERARCHICAL_ENERGY_DYNAMICS.md)

Background - Theoretical Predictions:
  - Extension 2: Hierarchical Resonance Dynamics
  - Prediction: Energy cascades across scales (Agent → Population → Swarm)
  - Hypothesis: Homeostasis operates at BOTH intra- and inter-population levels
  - Two-level hierarchy:
    * Agent-level: Individual energy reserves (E_i)
    * Population-level: Total population energy (E_pop = Σ_i E_i)
    * Swarm-level: Meta-population coordination

Experimental Design:
  - Number of populations: n_pop = 10 (meta-population structure)
  - Intra-population spawn frequency: f_intra = 2.5% (validated homeostasis from C171/C175)
  - Inter-population migration: f_migrate = 0.5% (cross-population agent transfer)
  - Cycles: 3000 (match C177 duration)
  - Seeds: n=5 (sufficient for hierarchical patterns)
  - Max agents per population: 100 (same as C171/C175/C177)

Metrics Tracked:
  1. Agent-level: Energy reserves, spawn success
  2. Population-level: Total energy, population size, composition events
  3. Swarm-level: Total agents across all populations, migration flow
  4. Hierarchical: Energy variance within/between populations

Expected Outcomes:
  1. Intra-population homeostasis: Each population should replicate C171/C175 (Basin A, ~3-4 comp/100 cycles)
  2. Inter-population regulation: Migration should redistribute agents when populations diverge
  3. Meta-stability: Total swarm population should be more stable than individual populations
  4. Energy cascades: Population energy should correlate with population size

Publication Value:
  - First test of hierarchical resonance dynamics
  - Validates multi-scale energy regulation
  - Tests Extension 2 predictions from theoretical framework
  - Demonstrates NRM framework scales beyond single populations

Date: 2025-11-04 (Cycle 994 Implementation)
Researcher: Claude (DUALITY-ZERO-V2)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Cycle: 186 (Following C177 boundary mapping)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine

# Experimental parameters
N_POPULATIONS = 10  # Meta-population size
F_INTRA = 2.5  # Intra-population spawn frequency (validated homeostasis)
F_MIGRATE = 0.5  # Inter-population migration frequency
SEEDS = [42, 123, 456, 789, 101]  # n=5 seeds
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS_PER_POP = 100

class Population:
    """Single population within meta-population structure."""

    def __init__(self, pop_id: int, bridge: TranscendentalBridge, reality: RealityInterface):
        self.pop_id = pop_id
        self.bridge = bridge
        self.reality = reality
        self.agents: List[FractalAgent] = []
        self.composition_events: List[int] = []
        self.spawn_count = 0
        self.composition_engine = CompositionEngine(resonance_threshold=0.5)

        # Initialize with single root agent
        metrics = reality.get_system_metrics()
        root_agent = FractalAgent(
            agent_id=f"pop{pop_id}_root",
            bridge=bridge,
            initial_reality=metrics,
            depth=0,
            max_depth=7,
            reality=reality
        )
        self.agents.append(root_agent)

    def get_total_energy(self) -> float:
        """Calculate total population energy (E_pop = Σ_i E_i)."""
        return sum(agent.energy for agent in self.agents)

    def get_population_size(self) -> int:
        """Current population size."""
        return len(self.agents)

    def spawn_agent(self, cycle_idx: int) -> bool:
        """
        Attempt to spawn new agent from random parent.

        Returns:
            True if spawn succeeded, False otherwise
        """
        if len(self.agents) >= MAX_AGENTS_PER_POP:
            return False

        self.spawn_count += 1

        if len(self.agents) == 0:
            # Population collapsed - respawn seed agent
            metrics = self.reality.get_system_metrics()
            seed_agent = FractalAgent(
                agent_id=f"pop{self.pop_id}_seed_{cycle_idx}_{self.spawn_count}",
                bridge=self.bridge,
                initial_reality=metrics,
                depth=0,
                max_depth=7,
                reality=self.reality
            )
            self.agents.append(seed_agent)
            return True
        else:
            # Normal spawning from existing parent
            parent = self.agents[np.random.randint(len(self.agents))]
            child_id = f"pop{self.pop_id}_agent_{cycle_idx}_{self.spawn_count}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)
            if child:
                self.agents.append(child)
                return True
            return False

    def evolve_agents(self, delta_time: float):
        """Evolve all agents in population."""
        for agent in self.agents:
            agent.evolve(delta_time)

    def detect_compositions(self, cycle_idx: int):
        """
        Detect and execute composition events.

        Returns:
            Number of agents removed due to composition
        """
        cluster_events = self.composition_engine.detect_clusters(self.agents)

        if cluster_events:
            self.composition_events.append(cycle_idx)

            # Extract agent IDs to remove
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            # Remove clustered agents
            removed_count = len(agents_to_remove_ids)
            self.agents = [a for a in self.agents if a.agent_id not in agents_to_remove_ids]

            return removed_count

        return 0

    def extract_agent(self) -> FractalAgent:
        """
        Remove and return random agent for migration.

        Returns:
            Migrating agent or None if population empty
        """
        if len(self.agents) == 0:
            return None

        migrant_idx = np.random.randint(len(self.agents))
        migrant = self.agents.pop(migrant_idx)
        return migrant

    def receive_agent(self, agent: FractalAgent):
        """Accept migrating agent from another population."""
        if len(self.agents) < MAX_AGENTS_PER_POP:
            self.agents.append(agent)


def run_metapopulation_experiment(seed: int, cycles: int) -> dict:
    """
    Run meta-population experiment with hierarchical dynamics.

    Args:
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with hierarchical metrics
    """
    # Seed for reproducibility
    np.random.seed(seed)

    # Initialize shared components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Create populations
    populations = [Population(i, bridge, reality) for i in range(N_POPULATIONS)]

    # Calculate spawn/migration intervals
    spawn_interval = max(1, int(100.0 / F_INTRA))
    migrate_interval = max(1, int(100.0 / F_MIGRATE))

    # Track swarm-level metrics
    swarm_population_trajectory = []
    migration_events = []

    # Track population-level energy
    population_energy_history = defaultdict(list)
    population_size_history = defaultdict(list)

    # Run cycles
    for cycle_idx in range(cycles):
        # Intra-population spawning
        if (cycle_idx % spawn_interval) == 0:
            for pop in populations:
                pop.spawn_agent(cycle_idx)

        # Inter-population migration
        if (cycle_idx % migrate_interval) == 0 and cycle_idx > 0:
            # Select source and target populations (random)
            if len(populations) >= 2:
                source_idx = np.random.randint(N_POPULATIONS)
                target_idx = np.random.randint(N_POPULATIONS)

                # Ensure different populations
                while target_idx == source_idx:
                    target_idx = np.random.randint(N_POPULATIONS)

                # Execute migration
                migrant = populations[source_idx].extract_agent()
                if migrant is not None:
                    populations[target_idx].receive_agent(migrant)
                    migration_events.append({
                        'cycle': cycle_idx,
                        'source': source_idx,
                        'target': target_idx,
                        'agent_id': migrant.agent_id
                    })

        # Evolve all agents in all populations
        delta_time = 0.01
        for pop in populations:
            pop.evolve_agents(delta_time)

        # Detect compositions in all populations
        for pop in populations:
            pop.detect_compositions(cycle_idx)

        # Record hierarchical metrics
        total_swarm_population = sum(pop.get_population_size() for pop in populations)
        swarm_population_trajectory.append(total_swarm_population)

        for pop in populations:
            population_energy_history[pop.pop_id].append(pop.get_total_energy())
            population_size_history[pop.pop_id].append(pop.get_population_size())

    # Analyze per-population metrics
    population_results = []
    for pop in populations:
        # Calculate composition rate (same as C171/C175/C177)
        bins = np.arange(0, cycles + 1, WINDOW_SIZE)
        hist, _ = np.histogram(pop.composition_events, bins=bins)
        avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

        # Basin classification
        basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

        # Population statistics
        final_population = pop.get_population_size()
        pop_trajectory = population_size_history[pop.pop_id]
        mean_population = float(np.mean(pop_trajectory))
        std_population = float(np.std(pop_trajectory))
        cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0

        # Energy statistics
        energy_trajectory = population_energy_history[pop.pop_id]
        mean_energy = float(np.mean(energy_trajectory))
        std_energy = float(np.std(energy_trajectory))
        cv_energy = (std_energy / mean_energy * 100) if mean_energy > 0 else 0.0

        population_results.append({
            'population_id': pop.pop_id,
            'avg_composition_events': avg_composition_events,
            'basin': basin,
            'spawn_count': pop.spawn_count,
            'total_composition_events': len(pop.composition_events),
            'final_population': final_population,
            'mean_population': mean_population,
            'std_population': std_population,
            'cv_population': cv_population,
            'mean_energy': mean_energy,
            'std_energy': std_energy,
            'cv_energy': cv_energy,
        })

    # Analyze swarm-level metrics
    mean_swarm_population = float(np.mean(swarm_population_trajectory))
    std_swarm_population = float(np.std(swarm_population_trajectory))
    cv_swarm_population = (std_swarm_population / mean_swarm_population * 100) if mean_swarm_population > 0 else 0.0

    # Calculate between-population variance (hierarchical metric)
    population_means = [r['mean_population'] for r in population_results]
    between_pop_std = float(np.std(population_means))
    between_pop_cv = (between_pop_std / np.mean(population_means) * 100) if np.mean(population_means) > 0 else 0.0

    # Calculate basin classification for meta-population
    basin_a_count = sum(1 for r in population_results if r['basin'] == 'A')
    basin_a_percentage = (basin_a_count / N_POPULATIONS) * 100

    return {
        'seed': seed,
        'populations': population_results,
        'swarm_metrics': {
            'mean_population': mean_swarm_population,
            'std_population': std_swarm_population,
            'cv_population': cv_swarm_population,
            'final_population': swarm_population_trajectory[-1],
            'basin_a_percentage': basin_a_percentage,
        },
        'hierarchical_metrics': {
            'between_population_std': between_pop_std,
            'between_population_cv': between_pop_cv,
            'within_population_cv_mean': float(np.mean([r['cv_population'] for r in population_results])),
            'total_migrations': len(migration_events),
            'migrations_per_100_cycles': (len(migration_events) / cycles) * 100,
        },
        'implementation': 'MetaPopulation'
    }


def main():
    """Execute Cycle 186 meta-population hierarchical validation."""
    print("=" * 80)
    print("CYCLE 186: META-POPULATION HIERARCHICAL RESONANCE VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Test hierarchical energy dynamics (Extension 2 predictions)")
    print("Background: THEORETICAL_EXTENSIONS_HIERARCHICAL_ENERGY_DYNAMICS.md")
    print()
    print(f"Number of populations: {N_POPULATIONS}")
    print(f"Intra-population spawn frequency: {F_INTRA:.2f}% (validated homeostasis)")
    print(f"Inter-population migration frequency: {F_MIGRATE:.2f}%")
    print(f"Seeds: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    for idx, seed in enumerate(SEEDS):
        print(f"[{idx+1}/{len(SEEDS)}] Running seed {seed}...")

        result = run_metapopulation_experiment(seed, CYCLES)
        results.append(result)

        # Print summary
        basin_a_pct = result['swarm_metrics']['basin_a_percentage']
        mean_pop = result['swarm_metrics']['mean_population']
        cv_pop = result['swarm_metrics']['cv_population']
        migrations = result['hierarchical_metrics']['total_migrations']

        print(f"  Basin A: {basin_a_pct:.0f}% | "
              f"Mean Population: {mean_pop:.1f} | "
              f"CV: {cv_pop:.1f}% | "
              f"Migrations: {migrations}")
        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Aggregate analysis
    print("HIERARCHICAL ANALYSIS:")
    print("-" * 80)

    # Intra-population homeostasis validation
    all_basins = []
    for result in results:
        for pop_result in result['populations']:
            all_basins.append(pop_result['basin'])

    basin_a_count = sum(1 for b in all_basins if b == 'A')
    overall_basin_a_pct = (basin_a_count / len(all_basins)) * 100

    print(f"Intra-population homeostasis: {overall_basin_a_pct:.1f}% Basin A")
    print(f"  Expected: ~100% (f_intra = {F_INTRA:.2f}% validated in C171/C175)")

    if overall_basin_a_pct >= 90:
        print("  ✅ VALIDATED: Intra-population homeostasis maintained")
    else:
        print("  ⚠️  DEGRADED: Migration disrupts local homeostasis")

    print()

    # Inter-population regulation
    mean_swarm_cv = np.mean([r['swarm_metrics']['cv_population'] for r in results])
    mean_within_cv = np.mean([r['hierarchical_metrics']['within_population_cv_mean'] for r in results])
    mean_between_cv = np.mean([r['hierarchical_metrics']['between_population_cv'] for r in results])

    print(f"Population variability (CV):")
    print(f"  Swarm-level CV: {mean_swarm_cv:.2f}%")
    print(f"  Within-population CV (mean): {mean_within_cv:.2f}%")
    print(f"  Between-population CV: {mean_between_cv:.2f}%")

    if mean_swarm_cv < mean_within_cv:
        print("  ✅ META-STABILITY: Swarm more stable than individual populations")
    else:
        print("  ⚠️  NO META-STABILITY: Swarm variability ≥ population variability")

    print()

    # Migration effectiveness
    mean_migrations = np.mean([r['hierarchical_metrics']['total_migrations'] for r in results])
    mean_migrations_per_100 = np.mean([r['hierarchical_metrics']['migrations_per_100_cycles'] for r in results])

    print(f"Migration dynamics:")
    print(f"  Mean migrations: {mean_migrations:.1f} (over {CYCLES} cycles)")
    print(f"  Migrations per 100 cycles: {mean_migrations_per_100:.2f}")
    print(f"  Expected frequency: {F_MIGRATE:.2f}% → {F_MIGRATE} per 100 cycles")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '186',
            'scenario': 'Meta-Population Hierarchical Validation',
            'date': start_time.isoformat(),
            'n_populations': N_POPULATIONS,
            'f_intra': F_INTRA,
            'f_migrate': F_MIGRATE,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'purpose': 'Test hierarchical resonance dynamics (Extension 2)',
        },
        'experiments': results,
        'aggregate_analysis': {
            'intra_population_basin_a_pct': float(overall_basin_a_pct),
            'mean_swarm_cv': float(mean_swarm_cv),
            'mean_within_population_cv': float(mean_within_cv),
            'mean_between_population_cv': float(mean_between_cv),
            'mean_migrations': float(mean_migrations),
            'mean_migrations_per_100_cycles': float(mean_migrations_per_100),
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle186_metapopulation_hierarchical_validation.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 186 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
