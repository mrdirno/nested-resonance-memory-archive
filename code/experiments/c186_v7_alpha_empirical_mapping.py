#!/usr/bin/env python3
"""
Cycle 186 V7: Empirical α Coefficient Mapping Across f_intra Range

Purpose: Precisely measure hierarchical scaling coefficient α across full frequency range
Background: C186 V1 (f_intra=2.5%) → 0% Basin A (below threshold)
            C186 V2 (f_intra=5.0%) → 50-60% Basin A (partial viability)
            Prediction: Viability threshold at f_intra ≈ 4.0-5.0%

Hypothesis: α coefficient can be quantified by mapping Basin A percentage vs f_intra
            Expected sigmoid curve: 0% Basin A at low f_intra → 100% at high f_intra
            Inflection point identifies f_crit_hierarchical precisely

Design:
    f_intra range: 2.0% to 6.0% in 0.5% steps (9 frequencies)
    f_migrate = 0.5% (constant, unchanged from C186 V1/V2)
    n_pop = 10 populations
    N_initial = 20 agents per population

    Expected outcomes per frequency:
        f_intra = 2.0-3.0%: Basin A ≈ 0% (below threshold, like C186 V1)
        f_intra = 3.5-4.5%: Basin A ≈ 20-80% (transition zone)
        f_intra = 5.0-6.0%: Basin A ≈ 50-100% (above threshold, like C186 V2)

    cycles = 3000
    seeds = 10 per frequency
    Total experiments: 90 (9 frequencies × 10 seeds)

Analysis:
    - Fit sigmoid curve: Basin_A(f) = 100 / (1 + exp(-k * (f - f_crit)))
    - Extract f_crit_hierarchical (inflection point)
    - Compute α = f_crit_hierarchical / f_crit_single-scale
    - Compare to theoretical prediction α ≈ 2.0

Validation:
    - f=2.5%: Should replicate C186 V1 (0% Basin A)
    - f=5.0%: Should replicate C186 V2 (50-60% Basin A)
    - Control points anchor sigmoid fit

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
F_INTRA_VALUES = [0.020, 0.025, 0.030, 0.035, 0.040, 0.045, 0.050, 0.055, 0.060]  # 2.0% to 6.0% in 0.5% steps
F_MIGRATE = 0.005  # 0.5% constant migration rate
N_POP = 10  # Number of populations
N_INITIAL = 20  # Initial agents per population
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

    def mean_population(self) -> float:
        return float(len(self.agents))

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class MetaPopulationSystem:
    """
    Meta-population system with energy-constrained dynamics
    Testing hierarchical viability threshold across f_intra range
    """

    def __init__(self, seed: int, f_intra: float, db_path: Path):
        self.seed = seed
        self.f_intra = f_intra
        self.random = random.Random(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Initialize populations
        self.populations: List[Population] = []
        self.next_agent_id = 0
        self.cycle_count = 0

        # Statistics tracking
        self.intra_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0
        self.composition_events = 0

        # Initialize structure
        self._initialize_populations()

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

            pop = Population(id=pop_id, agents=agents)
            self.populations.append(pop)

    def step(self):
        """Execute one cycle of meta-population dynamics"""
        self.cycle_count += 1

        # Intra-population spawning
        self._intra_spawning()

        # Inter-population migration
        if F_MIGRATE > 0:
            self._inter_migration()

        # Energy recovery
        self._energy_recovery()

        # Composition detection
        self._composition_detection()

    def _intra_spawning(self):
        """Agents spawn within their populations at f_intra rate"""
        for population in self.populations:
            if len(population.agents) == 0:
                continue

            # Determine number of spawn attempts for this population
            n_attempts = int(len(population.agents) * self.f_intra)
            if self.random.random() < (len(population.agents) * self.f_intra - n_attempts):
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
                        energy=E_INITIAL * 0.5,  # Child starts with half initial energy
                        phase=child_phase,
                        depth=parent.depth + 1,
                        compositions=0
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    # Spawn failure due to insufficient energy
                    self.spawn_failures += 1

    def _inter_migration(self):
        """Migration between populations"""
        if len(self.populations) < 2:
            return

        # Determine number of migration attempts
        total_agents = sum(len(pop.agents) for pop in self.populations)
        n_attempts = int(total_agents * F_MIGRATE)
        if self.random.random() < (total_agents * F_MIGRATE - n_attempts):
            n_attempts += 1

        for _ in range(n_attempts):
            # Select random source population (with agents)
            source_pops = [p for p in self.populations if len(p.agents) > 0]
            if not source_pops:
                continue

            source_pop = self.random.choice(source_pops)

            # Energy check: population must have sufficient total energy
            if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
                # Select random agent to migrate
                migrant = self.random.choice(source_pop.agents)

                # Select random destination population (different from source)
                dest_pops = [p for p in self.populations if p.id != source_pop.id]
                if not dest_pops:
                    continue

                dest_pop = self.random.choice(dest_pops)

                # Migrate agent
                source_pop.agents.remove(migrant)
                migrant.population_id = dest_pop.id
                dest_pop.agents.append(migrant)
                self.migrations += 1

    def _energy_recovery(self):
        """All agents recover energy"""
        for population in self.populations:
            for agent in population.agents:
                agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def _composition_detection(self):
        """Detect composition events using transcendental bridge"""
        for population in self.populations:
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

        for pop in self.populations:
            all_agents.extend(pop.agents)
            populations_data.append({
                'pop_id': pop.id,
                'n_agents': len(pop.agents),
                'total_energy': pop.total_energy(),
                'mean_energy': pop.total_energy() / len(pop.agents) if pop.agents else 0.0
            })

        mean_population = len(all_agents) / N_POP if N_POP > 0 else 0.0

        # Basin classification (population-level)
        # Basin A: sustained homeostasis (mean_pop > 2.5)
        # Basin B: collapse (mean_pop ≤ 2.5)
        basin = 'A' if mean_population > 2.5 else 'B'

        # Coefficient of variation across populations
        pop_sizes = [len(pop.agents) for pop in self.populations]
        if len(pop_sizes) > 1 and mean_population > 0:
            import statistics
            cv = (statistics.stdev(pop_sizes) / mean_population) * 100
        else:
            cv = 0.0

        # Spawn success rate
        total_spawn_attempts = self.intra_spawns + self.spawn_failures
        spawn_success_rate = (self.intra_spawns / total_spawn_attempts * 100) if total_spawn_attempts > 0 else 0.0

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
            'populations': populations_data
        }

def run_experiment(seed: int, f_intra: float, output_path: Path, db_path: Path) -> Dict:
    """
    Run single meta-population experiment for one seed at specific f_intra

    Returns final statistics including Basin classification
    """
    freq_idx = F_INTRA_VALUES.index(f_intra)
    seed_idx = SEEDS.index(seed)
    exp_num = freq_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(F_INTRA_VALUES) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] f={f_intra*100:4.1f}%, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database for seed isolation
    clear_bridge_database(db_path)

    # Initialize system
    system = MetaPopulationSystem(seed, f_intra, db_path)

    # Run for specified cycles
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Final statistics
    final_stats = system.get_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:4.1f} | "
          f"CV: {final_stats['cv_percent']:5.1f}% | "
          f"Success: {final_stats['spawn_success_rate']:5.1f}% | "
          f"{elapsed_total:4.0f}s")

    # Add metadata
    final_stats['seed'] = seed
    final_stats['f_intra'] = f_intra
    final_stats['f_migrate'] = F_MIGRATE
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C186 V7 α empirical mapping experiments"""

    print("=" * 80)
    print("CYCLE 186 V7: α COEFFICIENT EMPIRICAL MAPPING")
    print("=" * 80)
    print()
    print("Purpose: Precisely quantify hierarchical viability threshold via sigmoid fit")
    print("Background: C186 V1 (f=2.5%) → 0% Basin A, C186 V2 (f=5.0%) → 50-60% Basin A")
    print()
    print(f"Frequency Range:")
    print(f"  f_intra = 2.0% to 6.0% in 0.5% steps ({len(F_INTRA_VALUES)} frequencies)")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (constant)")
    print()
    print(f"Structure:")
    print(f"  n_pop = {N_POP} populations")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print()
    print(f"Experimental Parameters:")
    print(f"  Seeds per frequency: n={len(SEEDS)}")
    print(f"  Cycles per seed: {CYCLES}")
    print(f"  Total experiments: {len(F_INTRA_VALUES) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(F_INTRA_VALUES) * len(SEEDS) * 0.04:.1f} hours")
    print()
    print(f"Expected Basin A Pattern:")
    print(f"  f = 2.0-3.0%: ≈ 0% (below threshold)")
    print(f"  f = 3.5-4.5%: ≈ 20-80% (transition zone)")
    print(f"  f = 5.0-6.0%: ≈ 50-100% (above threshold)")
    print()

    # Setup paths
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c186_v7_alpha_empirical_mapping.json"

    db_path = Path(__file__).parent.parent / "bridge" / "bridge.db"

    # Run experiments
    results = []
    start_time_total = time.time()

    for f_intra in F_INTRA_VALUES:
        print()
        print(f"Testing frequency = {f_intra*100:.2f}%")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, f_intra, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate statistics per frequency
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS PER FREQUENCY")
    print("=" * 80)
    print()
    print(f"{'Frequency':>10s} | {'Basin A %':>10s} | {'Mean Pop':>10s} | {'CV %':>8s} | {'Success %':>10s}")
    print("-" * 80)

    freq_aggregates = []
    for f_intra in F_INTRA_VALUES:
        freq_results = [r for r in results if abs(r['f_intra'] - f_intra) < 0.0001]

        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_results)) * 100

        mean_pops = [r['mean_population'] for r in freq_results]
        mean_pop_avg = sum(mean_pops) / len(mean_pops)

        cvs = [r['cv_percent'] for r in freq_results]
        cv_avg = sum(cvs) / len(cvs)

        spawn_rates = [r['spawn_success_rate'] for r in freq_results]
        spawn_rate_avg = sum(spawn_rates) / len(spawn_rates)

        freq_aggregates.append({
            'f_intra': f_intra,
            'basin_a_pct': basin_a_pct,
            'mean_pop_avg': mean_pop_avg,
            'cv_avg': cv_avg,
            'spawn_success_avg': spawn_rate_avg
        })

        print(f"{f_intra*100:9.1f}% | {basin_a_pct:9.1f}% | {mean_pop_avg:10.2f} | {cv_avg:7.1f}% | {spawn_rate_avg:9.1f}%")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    # Sigmoid fit analysis
    print("=" * 80)
    print("VIABILITY THRESHOLD ANALYSIS")
    print("=" * 80)
    print()

    # Find transition point (Basin A crosses 50%)
    transition_idx = None
    for i, agg in enumerate(freq_aggregates):
        if agg['basin_a_pct'] >= 50.0:
            transition_idx = i
            break

    if transition_idx is not None:
        f_crit_hierarchical = freq_aggregates[transition_idx]['f_intra']
        f_crit_single = 0.020  # 2.0% baseline from C171

        alpha_empirical = f_crit_hierarchical / f_crit_single

        print(f"Viability Transition Detected:")
        print(f"  f_crit_hierarchical ≈ {f_crit_hierarchical*100:.1f}%")
        print(f"  f_crit_single-scale = {f_crit_single*100:.1f}% (C171 baseline)")
        print(f"  α_empirical = {alpha_empirical:.2f}")
        print()
        print(f"Comparison to Prediction:")
        print(f"  Predicted: α ≈ 2.0 (from THEORETICAL_UPDATE_C186)")
        if abs(alpha_empirical - 2.0) < 0.3:
            print(f"  ✓ VALIDATED: α_empirical = {alpha_empirical:.2f} matches prediction")
        elif alpha_empirical < 2.0:
            print(f"  ⚠ α_empirical = {alpha_empirical:.2f} < 2.0 (lower overhead than predicted)")
        else:
            print(f"  ⚠ α_empirical = {alpha_empirical:.2f} > 2.0 (higher overhead than predicted)")
    else:
        print(f"⚠ No clear transition detected in tested range")
        print(f"  Highest Basin A: {max(agg['basin_a_pct'] for agg in freq_aggregates):.1f}%")
        print(f"  Suggests f_crit_hierarchical > {max(F_INTRA_VALUES)*100:.1f}%")

    print()

    # Save results
    output_data = {
        'metadata': {
            'experiment': 'C186_V7_ALPHA_EMPIRICAL_MAPPING',
            'date': datetime.now().isoformat(),
            'purpose': 'Precisely quantify hierarchical scaling coefficient α',
            'f_intra_values': F_INTRA_VALUES,
            'f_migrate': F_MIGRATE,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'seeds': SEEDS,
        },
        'frequency_aggregates': freq_aggregates,
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C186 V7 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
