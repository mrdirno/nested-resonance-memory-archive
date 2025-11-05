#!/usr/bin/env python3
"""
Cycle 186 V2: Hierarchical Viability Threshold - Critical Frequency Test (Simplified)

Purpose: Validate hierarchical critical frequency threshold at ~2× single-scale

SIMPLIFIED VERSION: Removes TranscendentalBridge dependency for faster execution
                   and cleaner baseline testing. Composition detection not needed
                   for basic viability validation.

Background:
    - C171 single-scale: f_crit ≈ 2.0%, 100% Basin A at f=2.0-3.0%
    - C186 V1: f_intra=2.5%, 0% Basin A (confirmed failure below threshold)
    - Prediction: α ≈ 2.0, so f_hier_crit ≈ 4.0-5.0%

Hypothesis: f_intra = 5.0% will produce 50-60% Basin A (threshold viability)
            Confirms α ≈ 2.5 (5.0% / 2.0% = 2.5)

Mechanism:
    At threshold frequency, energy input rate roughly balances compartmentalization
    overhead. Some seeds succeed (Basin A) while others fail (Basin B), producing
    bimodal distribution characteristic of critical transitions.

Hierarchical Structure:
    Level 1 (Agent): Individual fractal agents
    Level 2 (Population): 10 independent populations

Energy Dynamics:
    - Agents spawn within populations at f_intra = 5.0%
    - Populations exchange agents via migration at f_migrate = 0.5%
    - Each population has isolated energy pool (compartmentalization)

Design:
    f_intra = 5.0% (2.5× single-scale critical frequency)
    f_migrate = 0.5% (minimal cross-population mixing)
    n_pop = 10 populations
    N_initial = 20 agents per population
    cycles = 3000
    seeds = 10

Expected Outcome:
    Basin A = 50-60% (threshold viability, mixed outcomes)
    Mean population distribution bimodal (collapse vs homeostasis)

Validation:
    Compare to:
    - C171 (f=2.5%): 100% Basin A (single-scale well above threshold)
    - C186 V1 (f_intra=2.5%): 0% Basin A (hierarchical below threshold)

    Confirms: 2.5% < f_hier_crit < 5.0%, validating 1.25 < α < 2.5

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1060)
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
F_INTRA = 0.050  # 5.0% intra-population spawn rate (threshold test)
F_MIGRATE = 0.005  # 0.5% inter-population migration rate
N_POP = 10  # Number of populations
N_INITIAL = 20  # Initial agents per population
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Energy parameters (from C171 baseline)
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

    def __init__(self, seed: int):
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
        for pop_id in range(N_POP):
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
        """Agents spawn within populations at F_INTRA rate"""
        for population in self.populations:
            if len(population.agents) == 0:
                continue

            # Attempt spawns at F_INTRA frequency
            n_attempts = max(1, int(len(population.agents) * F_INTRA))

            for _ in range(n_attempts):
                if len(population.agents) == 0:
                    break

                parent = self.random.choice(population.agents)

                if parent.energy >= E_SPAWN_THRESHOLD:
                    # Successful spawn
                    parent.energy -= E_SPAWN_COST

                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_INITIAL * 0.5
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    self.spawn_failures += 1

    def _inter_migration(self):
        """Migration between populations at F_MIGRATE rate"""
        total_agents = sum(len(pop.agents) for pop in self.populations)
        if total_agents == 0:
            return

        n_attempts = max(1, int(total_agents * F_MIGRATE))

        for _ in range(n_attempts):
            # Select source population (weighted by size)
            non_empty_pops = [p for p in self.populations if len(p.agents) > 0]
            if len(non_empty_pops) < 2:
                break

            source_pop = self.random.choice(non_empty_pops)

            # Select destination (any other population)
            dest_pops = [p for p in self.populations if p.id != source_pop.id]
            if not dest_pops:
                break

            # Check if source has sufficient energy for migration
            if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
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
                'active_populations': 0
            }

        active_pops = sum(1 for pop in self.populations if len(pop.agents) > 0)

        return {
            'total_population': len(all_agents),
            'mean_energy': sum(a.energy for a in all_agents) / len(all_agents),
            'active_populations': active_pops
        }

def run_single_experiment(seed: int) -> Dict:
    """Run single experiment with given seed"""

    # Create system
    system = HierarchicalSystem(seed)

    # Run cycles
    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()

        # Progress updates
        if (cycle + 1) % 500 == 0:
            elapsed = time.time() - start_time
            metrics = system.get_metrics()
            print(f"  Seed {seed:3d}, Cycle {cycle+1:4d}: "
                  f"pop={metrics['total_population']:3d}, "
                  f"energy={metrics['mean_energy']:.1f}, "
                  f"active_pops={metrics['active_populations']}/{N_POP} "
                  f"[{elapsed:.1f}s]")

    # Final metrics
    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time

    # Basin classification
    mean_pop = final_metrics['total_population'] / N_POP
    basin = 'A' if mean_pop > 2.5 else 'B'

    result = {
        'seed': seed,
        'basin': basin,
        'mean_population': mean_pop,
        'total_population': final_metrics['total_population'],
        'mean_energy': final_metrics['mean_energy'],
        'active_populations': final_metrics['active_populations'],
        'intra_spawns': system.intra_spawns,
        'spawn_failures': system.spawn_failures,
        'migrations': system.migrations,
        'runtime_seconds': elapsed
    }

    return result

def main():
    """Execute C186 V1 baseline failure test"""

    print("=" * 80)
    print("CYCLE 186 V2: HIERARCHICAL VIABILITY THRESHOLD - BASELINE TEST (SIMPLIFIED)")
    print("=" * 80)
    print()
    print(f"Parameters:")
    print(f"  f_intra = {F_INTRA*100:.1f}% (intra-population spawn rate)")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (inter-population migration)")
    print(f"  n_pop = {N_POP} populations")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Expected: Basin A = 50-60% (threshold viability, confirming α ≈ 2.5)")
    print()
    print("-" * 80)

    results = []

    for i, seed in enumerate(SEEDS):
        print(f"[{i+1:2d}/{len(SEEDS)}] Running seed {seed}...")
        result = run_single_experiment(seed)
        results.append(result)
        print(f"  → Basin {result['basin']}, mean_pop={result['mean_population']:.2f}, "
              f"energy={result['mean_energy']:.1f}")
        print()

    # Aggregate statistics
    basin_a_count = sum(1 for r in results if r['basin'] == 'A')
    basin_a_pct = (basin_a_count / len(results)) * 100
    mean_pops = [r['mean_population'] for r in results]
    mean_pop_avg = sum(mean_pops) / len(mean_pops)

    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Basin A: {basin_a_count}/{len(results)} ({basin_a_pct:.1f}%)")
    print(f"Mean population: {mean_pop_avg:.2f} ± {(sum((x-mean_pop_avg)**2 for x in mean_pops)/len(mean_pops))**0.5:.2f}")
    print()

    if basin_a_pct == 0:
        print("✓ VALIDATED: f_intra=2.5% produces 0% Basin A")
        print("  Confirms α ≈ 2.5 (hierarchical scaling coefficient)")
        print("  Energy compartmentalization prevents viability at 2.5%")
    else:
        print("⚠ UNEXPECTED: Some experiments reached Basin A")
        print(f"  Expected 0%, observed {basin_a_pct:.1f}%")
        print("  May indicate α < 2.5/2.0 = 1.25 (lower overhead than predicted)")

    # Save results
    output = {
        'experiment': 'C186_V2_HIERARCHICAL_SPAWN_SUCCESS_SIMPLE',
        'date': datetime.now().isoformat(),
        'metadata': {
            'f_intra': F_INTRA,
            'f_migrate': F_MIGRATE,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': len(SEEDS),
            'simplified': True,
            'composition_detection': False
        },
        'aggregate_statistics': {
            'basin_a_count': basin_a_count,
            'basin_a_pct': basin_a_pct,
            'mean_population_avg': mean_pop_avg,
            'mean_population_std': (sum((x-mean_pop_avg)**2 for x in mean_pops)/len(mean_pops))**0.5
        },
        'individual_results': results
    }

    results_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "c186_v2_hierarchical_spawn_success_simple.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved: {results_file.name}")
    print()

if __name__ == "__main__":
    main()
