#!/usr/bin/env python3
"""
Cycle 189: Hierarchical vs Flat Spawn - Mechanism Isolation

Purpose: Test if hierarchical spawn mechanics provide advantage over flat spawn

Research Question:
    Does interval-based spawning (hierarchical) provide advantage over
    continuous probabilistic spawning (flat) at same nominal frequency?

Background:
    - C187/C187-B: α independent of n_pop (structure doesn't matter)
    - Hypothesis: Advantage originates from spawn mechanics, not structure
    - C189: Direct test comparing hierarchical vs flat spawn in single populations

Mechanisms:
    Hierarchical: Deterministic spawn intervals (e.g., every 50 cycles for 2.0%)
    Flat: Probabilistic per-cycle spawn attempts (e.g., 2.0% per cycle)

Hypotheses:
    H1: Hierarchical > Flat (spawn mechanics advantage)
    H2: Hierarchical ≈ Flat (equivalent mechanisms)
    H3: Hierarchical < Flat (interval-based detrimental)

Experimental Design:
    Mechanisms: Hierarchical, Flat (2 conditions)
    Frequencies: 0.5%, 1.0%, 1.5%, 2.0% (4 frequencies)
    Seeds: 10 per condition
    Total: 80 experiments

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

# Experimental parameters
F_INTRA_PCT_CONDITIONS = [0.5, 1.0, 1.5, 2.0]
SPAWN_MECHANISMS = ['hierarchical', 'flat']
N_POP = 1  # Single population (isolate spawn mechanism)
N_INITIAL = 20
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Energy parameters (identical for both mechanisms)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5

@dataclass
class Agent:
    """Individual fractal agent"""
    id: int
    energy: float

@dataclass
class Population:
    """Population container"""
    id: int
    agents: List[Agent]

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class HierarchicalSystem:
    """Single-population system with configurable spawn mechanism"""

    def __init__(self, spawn_mechanism: str, f_intra_pct: float, seed: int):
        self.spawn_mechanism = spawn_mechanism
        self.f_intra_pct = f_intra_pct
        self.seed = seed
        self.random = random.Random(seed)

        # Hierarchical spawn: deterministic interval
        self.spawn_interval = max(1, int(100.0 / f_intra_pct))

        # Flat spawn: probabilistic per-cycle
        self.spawn_probability = f_intra_pct / 100.0

        self.population = Population(id=0, agents=[])
        self.next_agent_id = 0
        self.cycle_count = 0

        self.intra_spawns = 0
        self.spawn_failures = 0
        self.spawn_attempts = 0

        self._initialize_population()

    def _initialize_population(self):
        """Create initial population"""
        for _ in range(N_INITIAL):
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL
            )
            self.population.agents.append(agent)
            self.next_agent_id += 1

    def step(self):
        """Execute one cycle"""
        self.cycle_count += 1
        self._intra_spawning()
        self._energy_recovery()

    def _intra_spawning(self):
        """Spawn logic - hierarchical or flat depending on mechanism"""

        if len(self.population.agents) == 0:
            return

        if self.spawn_mechanism == 'hierarchical':
            # Deterministic interval-based spawning
            should_spawn = (self.cycle_count % self.spawn_interval) == 0

            if should_spawn:
                self._attempt_spawn()

        elif self.spawn_mechanism == 'flat':
            # Probabilistic per-cycle spawning
            if self.random.random() < self.spawn_probability:
                self._attempt_spawn()

    def _attempt_spawn(self):
        """Attempt to spawn new agent (same logic for both mechanisms)"""

        self.spawn_attempts += 1

        parent = self.random.choice(self.population.agents)

        if parent.energy >= E_SPAWN_THRESHOLD:
            # Successful spawn
            parent.energy -= E_SPAWN_COST

            child = Agent(
                id=self.next_agent_id,
                energy=E_SPAWN_THRESHOLD * CHILD_ENERGY_FRACTION
            )
            self.population.agents.append(child)
            self.next_agent_id += 1
            self.intra_spawns += 1
        else:
            self.spawn_failures += 1

    def _energy_recovery(self):
        """All agents recover energy per cycle"""
        for agent in self.population.agents:
            agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def get_metrics(self) -> Dict:
        """Get system-level metrics"""
        if len(self.population.agents) == 0:
            return {
                'total_population': 0,
                'mean_energy': 0.0
            }

        return {
            'total_population': len(self.population.agents),
            'mean_energy': sum(a.energy for a in self.population.agents) / len(self.population.agents)
        }

def run_single_experiment(spawn_mechanism: str, f_intra_pct: float, seed: int) -> Dict:
    """Run single experiment with given mechanism, frequency, and seed"""

    system = HierarchicalSystem(spawn_mechanism, f_intra_pct, seed)

    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()

    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time

    # Basin classification
    basin = 'A' if final_metrics['total_population'] > 2.5 else 'B'

    result = {
        'spawn_mechanism': spawn_mechanism,
        'f_intra_pct': f_intra_pct,
        'seed': seed,
        'basin': basin,
        'final_population': final_metrics['total_population'],
        'mean_energy': final_metrics['mean_energy'],
        'intra_spawns': system.intra_spawns,
        'spawn_failures': system.spawn_failures,
        'spawn_attempts': system.spawn_attempts,
        'runtime_seconds': elapsed,
        'spawn_interval': system.spawn_interval if spawn_mechanism == 'hierarchical' else None,
        'spawn_probability': system.spawn_probability if spawn_mechanism == 'flat' else None
    }

    return result

def main():
    """Execute C189 hierarchical vs flat spawn comparison"""

    print("=" * 80)
    print("CYCLE 189: HIERARCHICAL VS FLAT SPAWN - MECHANISM ISOLATION")
    print("=" * 80)
    print()
    print(f"Spawn Mechanisms:")
    print(f"  Hierarchical: Deterministic interval-based spawning")
    print(f"  Flat: Probabilistic per-cycle spawning")
    print()
    print(f"Frequency Conditions:")
    print(f"  f_intra = {F_INTRA_PCT_CONDITIONS}")
    print()
    print(f"Fixed Parameters:")
    print(f"  n_pop = {N_POP} (single population - isolate mechanism)")
    print(f"  N_initial = {N_INITIAL} agents")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Hypotheses:")
    print(f"  H1: Hierarchical > Flat (spawn mechanics advantage)")
    print(f"  H2: Hierarchical ≈ Flat (equivalent mechanisms)")
    print(f"  H3: Hierarchical < Flat (interval-based detrimental)")
    print()
    print(f"Total Experiments: {len(SPAWN_MECHANISMS)} mechanisms × {len(F_INTRA_PCT_CONDITIONS)} freq × {len(SEEDS)} seeds = {len(SPAWN_MECHANISMS) * len(F_INTRA_PCT_CONDITIONS) * len(SEEDS)}")
    print()
    print("-" * 80)
    print()

    all_results = []
    condition_summaries = []
    experiment_count = 0
    total_experiments = len(SPAWN_MECHANISMS) * len(F_INTRA_PCT_CONDITIONS) * len(SEEDS)

    for mech in SPAWN_MECHANISMS:
        for f_intra_pct in F_INTRA_PCT_CONDITIONS:
            print(f"CONDITION: {mech.upper()} spawn, f_intra={f_intra_pct:.1f}%")
            if mech == 'hierarchical':
                print(f"  Spawn interval: {max(1, int(100.0 / f_intra_pct))} cycles")
            else:
                print(f"  Spawn probability: {f_intra_pct/100.0:.4f} per cycle")
            print("-" * 80)

            condition_results = []

            for seed in SEEDS:
                experiment_count += 1
                print(f"[{experiment_count:2d}/{total_experiments}] "
                      f"{mech[0].upper()}, f={f_intra_pct:.1f}%, seed={seed:3d}...",
                      end=" ", flush=True)

                result = run_single_experiment(mech, f_intra_pct, seed)
                condition_results.append(result)
                all_results.append(result)

                print(f"Basin {result['basin']}, "
                      f"pop={result['final_population']:4.0f}, "
                      f"spawns={result['intra_spawns']}, "
                      f"t={result['runtime_seconds']:.3f}s", flush=True)

            # Condition summary
            basin_a_count = sum(1 for r in condition_results if r['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(condition_results)) * 100
            final_pops = [r['final_population'] for r in condition_results]
            mean_pop = sum(final_pops) / len(final_pops)
            std_pop = (sum((x-mean_pop)**2 for x in final_pops) / len(final_pops))**0.5
            spawns_avg = sum(r['intra_spawns'] for r in condition_results) / len(condition_results)

            summary = {
                'spawn_mechanism': mech,
                'f_intra_pct': f_intra_pct,
                'basin_a_count': basin_a_count,
                'basin_a_pct': basin_a_pct,
                'mean_population': mean_pop,
                'std_population': std_pop,
                'spawns_avg': spawns_avg
            }
            condition_summaries.append(summary)

            print(f"Summary: Basin A {basin_a_count}/{len(condition_results)} ({basin_a_pct:.1f}%), "
                  f"mean {mean_pop:.2f}±{std_pop:.2f}")
            print()

    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY - HIERARCHICAL VS FLAT SPAWN")
    print("=" * 80)
    print()

    # Group by frequency
    for f_intra_pct in F_INTRA_PCT_CONDITIONS:
        print(f"f_intra = {f_intra_pct:.1f}%:")
        print(f"{'Mechanism':<15} {'Basin A %':<10} {'Mean Pop':<15} {'Spawns':<10}")
        print("-" * 60)

        freq_summaries = [s for s in condition_summaries if s['f_intra_pct'] == f_intra_pct]

        hierarchical_sum = [s for s in freq_summaries if s['spawn_mechanism'] == 'hierarchical'][0]
        flat_sum = [s for s in freq_summaries if s['spawn_mechanism'] == 'flat'][0]

        print(f"{'Hierarchical':<15} "
              f"{hierarchical_sum['basin_a_pct']:>6.1f}%    "
              f"{hierarchical_sum['mean_population']:>6.2f} ± {hierarchical_sum['std_population']:<4.2f}  "
              f"{hierarchical_sum['spawns_avg']:>6.1f}")

        print(f"{'Flat':<15} "
              f"{flat_sum['basin_a_pct']:>6.1f}%    "
              f"{flat_sum['mean_population']:>6.2f} ± {flat_sum['std_population']:<4.2f}  "
              f"{flat_sum['spawns_avg']:>6.1f}")

        # Difference
        diff_pop = hierarchical_sum['mean_population'] - flat_sum['mean_population']
        diff_pct = (diff_pop / flat_sum['mean_population']) * 100 if flat_sum['mean_population'] > 0 else 0

        print(f"{'Difference':<15} "
              f"           "
              f"{diff_pop:>+7.2f}         "
              f"({diff_pct:>+5.1f}%)")
        print()

    # Hypothesis evaluation
    print("HYPOTHESIS EVALUATION:")
    print()

    for f_intra_pct in F_INTRA_PCT_CONDITIONS:
        freq_summaries = [s for s in condition_summaries if s['f_intra_pct'] == f_intra_pct]
        hierarchical_sum = [s for s in freq_summaries if s['spawn_mechanism'] == 'hierarchical'][0]
        flat_sum = [s for s in freq_summaries if s['spawn_mechanism'] == 'flat'][0]

        diff_pop = hierarchical_sum['mean_population'] - flat_sum['mean_population']

        print(f"f_intra = {f_intra_pct:.1f}%:")
        print(f"  Hierarchical: {hierarchical_sum['mean_population']:.2f} ± {hierarchical_sum['std_population']:.2f}")
        print(f"  Flat: {flat_sum['mean_population']:.2f} ± {flat_sum['std_population']:.2f}")
        print(f"  Difference: {diff_pop:+.2f} agents/pop")

        if abs(diff_pop) < 2.0:
            print(f"  → NEGLIGIBLE DIFFERENCE (supports H2: Equivalent)")
        elif diff_pop > 5.0:
            print(f"  → HIERARCHICAL ADVANTAGE (supports H1)")
        elif diff_pop < -5.0:
            print(f"  → FLAT ADVANTAGE (supports H3)")
        else:
            print(f"  → SMALL DIFFERENCE (ambiguous)")
        print()

    # Save results
    output = {
        'experiment': 'C189_HIERARCHICAL_VS_FLAT_SPAWN',
        'date': datetime.now().isoformat(),
        'metadata': {
            'spawn_mechanisms': SPAWN_MECHANISMS,
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': len(SEEDS),
            'hypothesis': 'Testing if hierarchical spawn mechanics provide advantage over flat spawn'
        },
        'condition_summaries': condition_summaries,
        'individual_results': all_results
    }

    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "c189_hierarchical_vs_flat_spawn.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {results_file}")
    print()
    print("=" * 80)
    print("C189 HIERARCHICAL VS FLAT SPAWN COMPLETE")
    print("=" * 80)
    print()
    print(f"Next Actions:")
    print(f"  1. Perform statistical tests (t-test, effect size)")
    print(f"  2. Generate comparison figures")
    print(f"  3. Interpret hypothesis support (H1, H2, or H3)")
    print(f"  4. Integrate into Paper 8 theoretical framework")
    print(f"  5. Document mechanism findings")
    print()

if __name__ == "__main__":
    main()
