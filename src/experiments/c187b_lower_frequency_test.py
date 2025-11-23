#!/usr/bin/env python3
"""
Cycle 187-B: Lower Frequency Population Count Variation - Testing Ceiling Effect

Purpose: Test if hierarchical advantage scales with n_pop at frequencies near critical threshold

Research Question:
    Does α scale with n_pop when tested at lower frequencies (below C187 baseline)?

Background:
    - C187 showed α = 2.0 constant across all n_pop at f_intra = 2.0%
    - Hypothesis: 2.0% above ceiling, masking true scaling relationship
    - C187-B tests at 0.5%, 1.0%, 1.5% to find true critical thresholds

Hypotheses:
    H1: Ceiling Effect - α scaling emerges at lower frequencies
    H2: True Null - α constant regardless of frequency
    H3: Partial Scaling - Binary threshold at n_pop = 2

Experimental Design:
    f_intra = 0.5%, 1.0%, 1.5% (3 frequencies)
    n_pop = 1, 2, 5, 10, 20, 50 (6 conditions)
    seeds = 10 per condition
    Total: 180 experiments

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1319)
License: GPL-3.0
"""

import sys
import json
import time
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

# Experimental parameters (FREQUENCIES VARY, n_pop FIXED)
F_INTRA_PCT_CONDITIONS = [0.5, 1.0, 1.5]  # Lower than C187 baseline (2.0%)
F_MIGRATE = 0.005  # 0.5% inter-population migration rate
N_INITIAL = 20  # Initial agents per population
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Population counts to test (same as C187)
N_POP_CONDITIONS = [1, 2, 5, 10, 20, 50]

# Energy parameters (from C186/C187 baseline)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5

@dataclass
class Agent:
    """Individual fractal agent at Level 1"""
    id: int
    population_id: int
    energy: float

@dataclass
class Population:
    """Population container at Level 2"""
    id: int
    agents: List[Agent]

    def mean_population(self) -> float:
        return float(len(self.agents))

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class HierarchicalSystem:
    """Two-level hierarchical system (Agent → Population)"""

    def __init__(self, n_pop: int, f_intra_pct: float, seed: int):
        self.n_pop = n_pop
        self.f_intra_pct = f_intra_pct
        self.spawn_interval = max(1, int(100.0 / f_intra_pct))
        self.seed = seed
        self.random = random.Random(seed)

        self.populations: List[Population] = []
        self.next_agent_id = 0
        self.cycle_count = 0

        self.intra_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0

        self._initialize_populations()

    def _initialize_populations(self):
        """Create initial population structure"""
        for pop_id in range(self.n_pop):
            agents = []
            for _ in range(N_INITIAL):
                agent = Agent(
                    id=self.next_agent_id,
                    population_id=pop_id,
                    energy=E_INITIAL
                )
                agents.append(agent)
                self.next_agent_id += 1

            pop = Population(id=pop_id, agents=agents)
            self.populations.append(pop)

    def step(self):
        """Execute one cycle"""
        self.cycle_count += 1
        self._intra_spawning()
        self._inter_migration()
        self._energy_recovery()

    def _intra_spawning(self):
        """Agents spawn within populations at SPAWN_INTERVAL"""
        should_spawn = (self.cycle_count % self.spawn_interval) == 0

        if not should_spawn:
            return

        for population in self.populations:
            if len(population.agents) == 0:
                continue

            if len(population.agents) > 0:
                parent = self.random.choice(population.agents)

                if parent.energy >= E_SPAWN_THRESHOLD:
                    parent.energy -= E_SPAWN_COST

                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_SPAWN_THRESHOLD * CHILD_ENERGY_FRACTION
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    self.spawn_failures += 1

    def _inter_migration(self):
        """Migration between populations at F_MIGRATE rate (per cycle)"""
        if self.n_pop == 1:
            return

        if self.random.random() < F_MIGRATE:
            non_empty_pops = [p for p in self.populations if len(p.agents) > 0]
            if len(non_empty_pops) < 1:
                return

            source_pop = self.random.choice(non_empty_pops)

            dest_pops = [p for p in self.populations if p.id != source_pop.id]
            if not dest_pops:
                return

            if len(source_pop.agents) > 0:
                migrant = self.random.choice(source_pop.agents)
                dest_pop = self.random.choice(dest_pops)

                source_pop.agents.remove(migrant)
                migrant.population_id = dest_pop.id
                dest_pop.agents.append(migrant)
                self.migrations += 1

    def _energy_recovery(self):
        """All agents recover energy per cycle"""
        for population in self.populations:
            for agent in population.agents:
                agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def get_metrics(self) -> Dict:
        """Get system-level metrics"""
        all_agents = []
        for pop in self.populations:
            all_agents.extend(pop.agents)

        if len(all_agents) == 0:
            return {
                'total_population': 0,
                'mean_energy': 0.0,
                'active_populations': 0,
                'mean_population_per_pop': 0.0
            }

        active_pops = sum(1 for pop in self.populations if len(pop.agents) > 0)

        return {
            'total_population': len(all_agents),
            'mean_energy': sum(a.energy for a in all_agents) / len(all_agents),
            'active_populations': active_pops,
            'mean_population_per_pop': len(all_agents) / self.n_pop
        }

def run_single_experiment(f_intra_pct: float, n_pop: int, seed: int) -> Dict:
    """Run single experiment with given frequency, n_pop, and seed"""

    system = HierarchicalSystem(n_pop, f_intra_pct, seed)

    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()

    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time

    # Basin classification (per-population basis)
    mean_pop_per_pop = final_metrics['total_population'] / n_pop
    basin = 'A' if mean_pop_per_pop > 2.5 else 'B'

    result = {
        'f_intra_pct': f_intra_pct,
        'n_pop': n_pop,
        'seed': seed,
        'basin': basin,
        'total_population': final_metrics['total_population'],
        'mean_population_per_pop': mean_pop_per_pop,
        'mean_energy': final_metrics['mean_energy'],
        'active_populations': final_metrics['active_populations'],
        'intra_spawns': system.intra_spawns,
        'spawn_failures': system.spawn_failures,
        'migrations': system.migrations,
        'runtime_seconds': elapsed,
        'spawn_interval': system.spawn_interval
    }

    return result

def main():
    """Execute C187-B lower frequency population count variation experiment"""

    print("=" * 80)
    print("CYCLE 187-B: LOWER FREQUENCY POPULATION COUNT VARIATION")
    print("Testing Ceiling Effect Hypothesis")
    print("=" * 80)
    print()
    print(f"Frequency Conditions:")
    print(f"  f_intra = {F_INTRA_PCT_CONDITIONS} (lower than C187 baseline 2.0%)")
    print()
    print(f"Population Count Conditions:")
    print(f"  n_pop = {N_POP_CONDITIONS}")
    print()
    print(f"Fixed Parameters:")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (inter-population migration)")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Hypotheses:")
    print(f"  H1: Ceiling Effect - α scaling emerges at lower frequencies")
    print(f"  H2: True Null - α constant regardless of frequency")
    print(f"  H3: Partial Scaling - Binary threshold at n_pop = 2")
    print()
    print(f"Total Experiments: {len(F_INTRA_PCT_CONDITIONS)} freq × {len(N_POP_CONDITIONS)} n_pop × {len(SEEDS)} seeds = {len(F_INTRA_PCT_CONDITIONS) * len(N_POP_CONDITIONS) * len(SEEDS)}")
    print()
    print("-" * 80)
    print()

    all_results = []
    condition_summaries = []
    experiment_count = 0
    total_experiments = len(F_INTRA_PCT_CONDITIONS) * len(N_POP_CONDITIONS) * len(SEEDS)

    for freq_idx, f_intra_pct in enumerate(F_INTRA_PCT_CONDITIONS):
        for npop_idx, n_pop in enumerate(N_POP_CONDITIONS):
            print(f"CONDITION: f_intra={f_intra_pct:.1f}%, n_pop={n_pop}")
            print(f"  Spawn interval: {max(1, int(100.0 / f_intra_pct))} cycles")
            print(f"  Total initial agents: {n_pop * N_INITIAL}")
            print("-" * 80)

            condition_results = []

            for seed_idx, seed in enumerate(SEEDS):
                experiment_count += 1
                print(f"[{experiment_count:3d}/{total_experiments}] "
                      f"f={f_intra_pct:.1f}%, n={n_pop:2d}, seed={seed:3d}...",
                      end=" ", flush=True)

                result = run_single_experiment(f_intra_pct, n_pop, seed)
                condition_results.append(result)
                all_results.append(result)

                print(f"Basin {result['basin']}, "
                      f"total_pop={result['total_population']:4d}, "
                      f"mean/pop={result['mean_population_per_pop']:.1f}, "
                      f"t={result['runtime_seconds']:.2f}s", flush=True)

            # Condition summary
            basin_a_count = sum(1 for r in condition_results if r['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(condition_results)) * 100
            mean_pops = [r['mean_population_per_pop'] for r in condition_results]
            mean_pop_avg = sum(mean_pops) / len(mean_pops)
            mean_pop_std = (sum((x-mean_pop_avg)**2 for x in mean_pops) / len(mean_pops))**0.5
            total_pops = [r['total_population'] for r in condition_results]
            total_pop_avg = sum(total_pops) / len(total_pops)
            total_pop_std = (sum((x-total_pop_avg)**2 for x in total_pops) / len(total_pops))**0.5
            migrations_avg = sum(r['migrations'] for r in condition_results) / len(condition_results)

            summary = {
                'f_intra_pct': f_intra_pct,
                'n_pop': n_pop,
                'total_initial_agents': n_pop * N_INITIAL,
                'basin_a_count': basin_a_count,
                'basin_a_pct': basin_a_pct,
                'mean_population_per_pop_avg': mean_pop_avg,
                'mean_population_per_pop_std': mean_pop_std,
                'total_population_avg': total_pop_avg,
                'total_population_std': total_pop_std,
                'migrations_avg': migrations_avg,
                'spawn_interval': max(1, int(100.0 / f_intra_pct))
            }
            condition_summaries.append(summary)

            print(f"Summary: Basin A {basin_a_count}/{len(condition_results)} ({basin_a_pct:.1f}%), "
                  f"mean/pop {mean_pop_avg:.2f}±{mean_pop_std:.2f}")
            print()

    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY - LOWER FREQUENCY SCALING")
    print("=" * 80)
    print()

    # Group by frequency
    for f_intra_pct in F_INTRA_PCT_CONDITIONS:
        print(f"f_intra = {f_intra_pct:.1f}%:")
        print(f"{'n_pop':<7} {'Basin A %':<10} {'Mean/pop':<15} {'Migrations':<12}")
        print("-" * 60)

        freq_summaries = [s for s in condition_summaries if s['f_intra_pct'] == f_intra_pct]
        for summary in freq_summaries:
            print(f"{summary['n_pop']:<7} "
                  f"{summary['basin_a_pct']:>6.1f}%    "
                  f"{summary['mean_population_per_pop_avg']:>6.2f} ± {summary['mean_population_per_pop_std']:<4.2f}  "
                  f"{summary['migrations_avg']:>8.1f}")
        print()

    # Hypothesis evaluation
    print("HYPOTHESIS EVALUATION:")
    print()

    # Check for variation across n_pop for each frequency
    for f_intra_pct in F_INTRA_PCT_CONDITIONS:
        freq_summaries = [s for s in condition_summaries if s['f_intra_pct'] == f_intra_pct]
        basin_a_pcts = [s['basin_a_pct'] for s in freq_summaries]

        variation = max(basin_a_pcts) - min(basin_a_pcts)

        print(f"f_intra = {f_intra_pct:.1f}%:")
        print(f"  Basin A range: {min(basin_a_pcts):.1f}% - {max(basin_a_pcts):.1f}% (variation: {variation:.1f}%)")

        if variation > 20:
            print(f"  → SIGNIFICANT VARIATION (supports H1: Ceiling Effect)")
        elif variation < 5:
            print(f"  → NO VARIATION (supports H2: True Null)")
        else:
            print(f"  → MODERATE VARIATION (supports H3: Partial Scaling or ambiguous)")
        print()

    # Save results
    output = {
        'experiment': 'C187B_LOWER_FREQUENCY_POPULATION_COUNT_VARIATION',
        'date': datetime.now().isoformat(),
        'metadata': {
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'f_migrate': F_MIGRATE,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': len(SEEDS),
            'n_pop_conditions': N_POP_CONDITIONS,
            'hypothesis': 'Testing if hierarchical advantage scales with n_pop at lower frequencies'
        },
        'condition_summaries': condition_summaries,
        'individual_results': all_results
    }

    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "c187b_lower_frequency_test.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {results_file}")
    print()
    print("=" * 80)
    print("C187-B LOWER FREQUENCY TEST COMPLETE")
    print("=" * 80)
    print()
    print(f"Next Actions:")
    print(f"  1. Analyze critical thresholds by n_pop")
    print(f"  2. Calculate α for each (f_intra, n_pop) combination")
    print(f"  3. Compare to C187 baseline (2.0%)")
    print(f"  4. Generate comparative figures")
    print(f"  5. Determine hypothesis support (H1, H2, or H3)")
    print()

if __name__ == "__main__":
    main()
