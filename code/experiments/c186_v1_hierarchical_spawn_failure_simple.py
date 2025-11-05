#!/usr/bin/env python3
"""
Cycle 186 V1: Hierarchical Viability Failure - Baseline Test (Simplified)

Purpose: Validate that 2× single-scale critical frequency is insufficient for
         hierarchical viability due to energy compartmentalization overhead

SIMPLIFIED VERSION: Removes TranscendentalBridge dependency for faster execution
                   and cleaner baseline testing. Composition detection not needed
                   for basic viability validation.

Background:
    - C171 single-scale: f_crit ≈ 2.0%, 100% Basin A at f=2.0-3.0%
    - Hierarchical prediction: α ≈ 2.0, so f_hier_crit ≈ 4.0-5.0%
    - Testing f_intra = 2.5% (between 2.0-5.0%, should fail if α > 1.25)

Hypothesis: f_intra = 2.5% will produce 0% Basin A (complete collapse)
            Confirms α > 1.25 (minimum hierarchical scaling coefficient)

Mechanism:
    Energy compartmentalization prevents bootstrap probability amplification
    Isolated populations fail to sustain viability even when single-scale
    systems would succeed at same frequency

Hierarchical Structure:
    Level 1 (Agent): Individual fractal agents
    Level 2 (Population): 10 independent populations

Energy Dynamics:
    - Agents spawn within populations at f_intra = 2.5%
    - Populations exchange agents via migration at f_migrate = 0.5%
    - Each population has isolated energy pool (compartmentalization)

Design:
    f_intra = 2.5% (1.25× single-scale critical frequency)
    f_migrate = 0.5% (minimal cross-population mixing)
    n_pop = 10 populations
    N_initial = 20 agents per population
    cycles = 3000
    seeds = 10

Expected Outcome:
    Basin A = 0% (complete viability failure)
    Mean population → 0 across all seeds

Validation:
    Compare to:
    - C171 (f=2.5%): 100% Basin A (single-scale succeeds)
    - C186 V2 (f_intra=5.0%): 50-60% Basin A (hierarchical threshold)

    Confirms: 2.5% < f_hier_crit, validating α > 1.25

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
F_INTRA_PCT = 2.5  # 2.5% intra-population spawn rate (expect failure)
F_MIGRATE = 0.005  # 0.5% inter-population migration rate
N_POP = 10  # Number of populations
N_INITIAL = 20  # Initial agents per population
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Spawn interval calculation (matching C176/C177 mechanism)
SPAWN_INTERVAL = max(1, int(100.0 / F_INTRA_PCT))  # 100 / 2.5 = 40 cycles

# Energy parameters (from C171 baseline)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5  # Energy recovery per cycle per agent
CHILD_ENERGY_FRACTION = 0.5  # Child energy as fraction of spawn threshold (prevents cascade)

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
        """Agents spawn within populations at SPAWN_INTERVAL (matching C176 mechanism)"""
        # KEY FIX: Only spawn on interval cycles (every SPAWN_INTERVAL cycles)
        should_spawn = (self.cycle_count % SPAWN_INTERVAL) == 0

        if not should_spawn:
            return  # Skip spawning this cycle

        for population in self.populations:
            if len(population.agents) == 0:
                continue

            # Single spawn attempt per population on spawn cycles (simplified from C176 logic)
            if len(population.agents) > 0:
                parent = self.random.choice(population.agents)

                if parent.energy >= E_SPAWN_THRESHOLD:
                    # Successful spawn
                    parent.energy -= E_SPAWN_COST

                    # KEY FIX: Child energy below threshold to prevent cascade
                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_SPAWN_THRESHOLD * CHILD_ENERGY_FRACTION  # 10.0 (< 20.0 threshold)
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
                  f"[{elapsed:.1f}s]", flush=True)

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
    print("CYCLE 186 V1: HIERARCHICAL SPAWN FAILURE - BASELINE TEST (SIMPLIFIED)")
    print("=" * 80)
    print()
    print(f"Parameters:")
    print(f"  f_intra = {F_INTRA_PCT:.1f}% (intra-population spawn rate)")
    print(f"  f_migrate = {F_MIGRATE*100:.1f}% (inter-population migration)")
    print(f"  n_pop = {N_POP} populations")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Expected: Basin A = 0% (complete failure, confirming α > 1.25)")
    print()
    print("-" * 80)

    results = []

    for i, seed in enumerate(SEEDS):
        print(f"[{i+1:2d}/{len(SEEDS)}] Running seed {seed}...", flush=True)
        result = run_single_experiment(seed)
        results.append(result)
        print(f"  → Basin {result['basin']}, mean_pop={result['mean_population']:.2f}, "
              f"energy={result['mean_energy']:.1f}", flush=True)
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
        print("  Confirms α > 1.25 (hierarchical scaling coefficient)")
        print("  Energy compartmentalization prevents viability at 2.5%")
    else:
        print("⚠ UNEXPECTED: Some experiments reached Basin A")
        print(f"  Expected 0%, observed {basin_a_pct:.1f}%")
        print("  May indicate α < 2.5/2.0 = 1.25 (lower overhead than predicted)")

    # Save results
    output = {
        'experiment': 'C186_V1_HIERARCHICAL_SPAWN_FAILURE_SIMPLE',
        'date': datetime.now().isoformat(),
        'metadata': {
            'f_intra': F_INTRA_PCT / 100,
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
    results_file = results_dir / "c186_v1_hierarchical_spawn_failure_simple.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved: {results_file.name}")
    print()

if __name__ == "__main__":
    main()
