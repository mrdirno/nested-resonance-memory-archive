#!/usr/bin/env python3
"""
Cycle 187: Population Count Variation - Hierarchical Advantage Scaling

Purpose: Quantify how hierarchical advantage (α) scales with number of populations

Research Question:
    How does hierarchical advantage (α) scale with number of populations (n_pop)?

Background:
    - Paper 8 (C186) established α = 607× for n_pop = 10
    - V8 edge case: n_pop = 1 eliminates hierarchical advantage
    - Question: What is the relationship between n_pop and α?

Competing Hypotheses:
    H1: Monotonic Increase - More populations → more redundancy → higher α
    H2: Diminishing Returns - α increases but saturates (logarithmic)
    H3: Optimal Population Count - α peaks at intermediate n_pop
    H4: Threshold Behavior - Phase transition at critical n_pop

Experimental Design:
    n_pop = 1, 2, 5, 10, 20, 50 (6 conditions × 10 seeds = 60 experiments)
    f_intra = 2.0% (fixed, V3 baseline)
    f_migrate = 0.5% (fixed, validated in C186)
    n_initial = 20 agents per population (fixed)
    cycles = 3000
    seeds = 10

Expected Results:
    - n_pop = 1: α ≈ 1 (no advantage, V8 replication)
    - n_pop = 10: α ≈ 600 (V1-V5 replication)
    - Trend reveals scaling law (linear, logarithmic, optimal, or threshold)

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

# Experimental parameters (FIXED across all conditions)
F_INTRA_PCT = 2.0  # 2.0% intra-population spawn rate (V3 baseline)
F_MIGRATE = 0.005  # 0.5% inter-population migration rate
N_INITIAL = 20  # Initial agents per population
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Population counts to test (independent variable)
N_POP_CONDITIONS = [1, 2, 5, 10, 20, 50]

# Spawn interval calculation (matching C186 mechanism)
SPAWN_INTERVAL = max(1, int(100.0 / F_INTRA_PCT))  # 100 / 2.0 = 50 cycles

# Energy parameters (from C186 baseline)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5  # Energy recovery per cycle per agent
CHILD_ENERGY_FRACTION = 0.5  # Child energy as fraction of spawn threshold

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

    def __init__(self, n_pop: int, seed: int):
        self.n_pop = n_pop
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
        # Only spawn on interval cycles
        should_spawn = (self.cycle_count % SPAWN_INTERVAL) == 0

        if not should_spawn:
            return

        for population in self.populations:
            if len(population.agents) == 0:
                continue

            # Single spawn attempt per population on spawn cycles
            if len(population.agents) > 0:
                parent = self.random.choice(population.agents)

                if parent.energy >= E_SPAWN_THRESHOLD:
                    # Successful spawn
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
        # EDGE CASE: Skip migration if n_pop = 1 (no valid targets)
        if self.n_pop == 1:
            return

        # Per-cycle migration probability (as specified in design)
        if self.random.random() < F_MIGRATE:
            # Select source population (random from all populations)
            non_empty_pops = [p for p in self.populations if len(p.agents) > 0]
            if len(non_empty_pops) < 1:
                return

            source_pop = self.random.choice(non_empty_pops)

            # Select destination (exclude source)
            dest_pops = [p for p in self.populations if p.id != source_pop.id]
            if not dest_pops:
                return

            # Check if source has agents to migrate
            if len(source_pop.agents) > 0:
                migrant = self.random.choice(source_pop.agents)
                dest_pop = self.random.choice(dest_pops)

                # Transfer agent
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

def run_single_experiment(n_pop: int, seed: int) -> Dict:
    """Run single experiment with given n_pop and seed"""

    # Create system
    system = HierarchicalSystem(n_pop, seed)

    # Run cycles
    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()

        # Progress updates (every 1000 cycles)
        if (cycle + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            metrics = system.get_metrics()
            print(f"  n_pop={n_pop:2d}, seed={seed:3d}, cycle {cycle+1:4d}: "
                  f"total_pop={metrics['total_population']:4d}, "
                  f"mean_per_pop={metrics['mean_population_per_pop']:.1f}, "
                  f"active={metrics['active_populations']}/{n_pop} "
                  f"[{elapsed:.1f}s]", flush=True)

    # Final metrics
    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time

    # Basin classification (per-population basis)
    mean_pop_per_pop = final_metrics['total_population'] / n_pop
    basin = 'A' if mean_pop_per_pop > 2.5 else 'B'

    result = {
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
        'runtime_seconds': elapsed
    }

    return result

def main():
    """Execute C187 population count variation experiment"""

    print("=" * 80)
    print("CYCLE 187: POPULATION COUNT VARIATION - HIERARCHICAL ADVANTAGE SCALING")
    print("=" * 80)
    print()
    print(f"Fixed Parameters:")
    print(f"  f_intra = {F_INTRA_PCT:.1f}% (intra-population spawn rate)")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (inter-population migration)")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Variable Parameter:")
    print(f"  n_pop = {N_POP_CONDITIONS} (6 conditions)")
    print()
    print(f"Expected Results:")
    print(f"  - n_pop = 1: α ≈ 1 (no advantage, V8 replication)")
    print(f"  - n_pop = 10: α ≈ 600 (V1-V5 replication)")
    print(f"  - Trend: monotonic, logarithmic, optimal, or threshold?")
    print()
    print(f"Total Experiments: {len(N_POP_CONDITIONS)} × {len(SEEDS)} = {len(N_POP_CONDITIONS) * len(SEEDS)}")
    print()
    print("-" * 80)
    print()

    all_results = []
    condition_summaries = []

    for condition_idx, n_pop in enumerate(N_POP_CONDITIONS):
        print(f"CONDITION {condition_idx+1}/{len(N_POP_CONDITIONS)}: n_pop = {n_pop}")
        print(f"  Total initial agents: {n_pop * N_INITIAL}")
        print("-" * 80)

        condition_results = []

        for seed_idx, seed in enumerate(SEEDS):
            print(f"[{seed_idx+1:2d}/{len(SEEDS)}] n_pop={n_pop:2d}, seed={seed:3d}...", flush=True)
            result = run_single_experiment(n_pop, seed)
            condition_results.append(result)
            all_results.append(result)
            print(f"  → Basin {result['basin']}, "
                  f"total_pop={result['total_population']:4d}, "
                  f"mean_per_pop={result['mean_population_per_pop']:.2f}, "
                  f"migrations={result['migrations']}", flush=True)
            print()

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
            'n_pop': n_pop,
            'total_initial_agents': n_pop * N_INITIAL,
            'basin_a_count': basin_a_count,
            'basin_a_pct': basin_a_pct,
            'mean_population_per_pop_avg': mean_pop_avg,
            'mean_population_per_pop_std': mean_pop_std,
            'total_population_avg': total_pop_avg,
            'total_population_std': total_pop_std,
            'migrations_avg': migrations_avg
        }
        condition_summaries.append(summary)

        print(f"Summary for n_pop={n_pop}:")
        print(f"  Basin A: {basin_a_count}/{len(condition_results)} ({basin_a_pct:.1f}%)")
        print(f"  Mean per population: {mean_pop_avg:.2f} ± {mean_pop_std:.2f}")
        print(f"  Total population: {total_pop_avg:.1f} ± {total_pop_std:.1f}")
        print(f"  Migrations per experiment: {migrations_avg:.1f}")
        print()
        print("=" * 80)
        print()

    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY - POPULATION COUNT SCALING")
    print("=" * 80)
    print()
    print(f"{'n_pop':<7} {'Initial':<8} {'Basin A %':<10} {'Mean/pop':<15} {'Total Pop':<15} {'Migrations':<12}")
    print("-" * 80)
    for summary in condition_summaries:
        print(f"{summary['n_pop']:<7} "
              f"{summary['total_initial_agents']:<8} "
              f"{summary['basin_a_pct']:>6.1f}%    "
              f"{summary['mean_population_per_pop_avg']:>6.2f} ± {summary['mean_population_per_pop_std']:<4.2f}  "
              f"{summary['total_population_avg']:>6.1f} ± {summary['total_population_std']:<4.1f}  "
              f"{summary['migrations_avg']:>8.1f}")
    print()

    # Qualitative analysis
    print("QUALITATIVE ANALYSIS:")
    print()

    # Check baseline replication
    n10_summary = [s for s in condition_summaries if s['n_pop'] == 10][0]
    n1_summary = [s for s in condition_summaries if s['n_pop'] == 1][0]

    print(f"Baseline Validation:")
    print(f"  - n_pop = 10: {n10_summary['mean_population_per_pop_avg']:.2f} ± {n10_summary['mean_population_per_pop_std']:.2f} agents/pop")
    print(f"    Expected: ~80 agents/pop (V3 baseline)")
    if 70 <= n10_summary['mean_population_per_pop_avg'] <= 90:
        print(f"    ✓ REPLICATION SUCCESSFUL")
    else:
        print(f"    ⚠ REPLICATION UNCERTAIN (deviation from V3 baseline)")
    print()

    print(f"  - n_pop = 1: Basin A {n1_summary['basin_a_pct']:.1f}%")
    print(f"    Expected: α ≈ 1 (no hierarchical advantage)")
    if n1_summary['basin_a_pct'] < 60:
        print(f"    ✓ EDGE CASE VALIDATED (minimal advantage)")
    else:
        print(f"    ⚠ UNEXPECTED (should show no hierarchical advantage)")
    print()

    # Trend analysis
    mean_pops_by_npop = [s['mean_population_per_pop_avg'] for s in condition_summaries]
    print(f"Trend Analysis:")
    increasing = all(mean_pops_by_npop[i] <= mean_pops_by_npop[i+1] for i in range(len(mean_pops_by_npop)-1))
    if increasing:
        print(f"  ✓ MONOTONIC INCREASE: Mean population increases with n_pop")
        print(f"    Supports H1 (risk distribution dominates) or H2 (diminishing returns)")
    else:
        print(f"  ⚠ NON-MONOTONIC: Population varies non-monotonically with n_pop")
        print(f"    May support H3 (optimal n_pop exists)")
    print()

    # Save results
    output = {
        'experiment': 'C187_POPULATION_COUNT_VARIATION',
        'date': datetime.now().isoformat(),
        'metadata': {
            'f_intra': F_INTRA_PCT / 100,
            'f_migrate': F_MIGRATE,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': len(SEEDS),
            'spawn_interval': SPAWN_INTERVAL,
            'n_pop_conditions': N_POP_CONDITIONS,
            'hypothesis': 'Testing how hierarchical advantage (α) scales with population count (n_pop)'
        },
        'condition_summaries': condition_summaries,
        'individual_results': all_results
    }

    # Save to development workspace results directory
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "c187_population_count_variation.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {results_file}")
    print()
    print("=" * 80)
    print("C187 POPULATION COUNT VARIATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Next Actions:")
    print(f"  1. Analyze results with statistical tests (ANOVA, trend analysis)")
    print(f"  2. Generate publication figures (α vs n_pop)")
    print(f"  3. Calculate hierarchical advantage (α) for each n_pop")
    print(f"  4. Compare to C188 (migration rate variation)")
    print(f"  5. Integrate into Paper 8 or prepare Paper 8B")
    print()

if __name__ == "__main__":
    main()
