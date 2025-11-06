#!/usr/bin/env python3
"""
C186 V6: Ultra-Low Frequency Test
==================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1071)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test hierarchical system viability at extremely low spawn frequencies to find
actual hierarchical critical frequency (f_hier_crit).

Background:
-----------
C186 V1-V5 Results:
- f=5.0%: 100% Basin A (mean_pop=170.0)
- f=2.5%: 100% Basin A (mean_pop=95.0)
- f=2.0%: 100% Basin A (mean_pop=79.9)
- f=1.5%: 100% Basin A (mean_pop=64.9)
- f=1.0%: 100% Basin A (mean_pop=49.8) ← Lowest tested so far

All frequencies show 100% viability. Need to go lower to find critical frequency.

Hypothesis:
-----------
Hierarchical critical frequency f_hier_crit exists somewhere between 0.1-1.0%.
Based on linear scaling (Population ≈ 30.04 × f + 19.80), critical frequency
occurs when mean population drops below Basin A threshold (pop < 2.5).

Predicted critical frequency:
2.5 = 30.04 × f + 19.80
f = (2.5 - 19.80) / 30.04 = -0.576%

WAIT - this predicts negative frequency! This means the linear model breaks down
at some point, OR the system never collapses (always viable at any f > 0).

Alternative hypothesis: System becomes Basin B when spawn interval exceeds
some critical value related to population decay time constant.

Experimental Design:
--------------------
Test 4 frequencies below 1.0%:
1. f=0.75% (spawn every 133 cycles)
2. f=0.50% (spawn every 200 cycles)
3. f=0.25% (spawn every 400 cycles)
4. f=0.10% (spawn every 1000 cycles)

Parameters:
- 10 populations
- 20 agents per population (200 total initial)
- f_migrate = 0.5% (constant)
- 3000 cycles
- 10 seeds per frequency
- Total: 4 frequencies × 10 seeds = 40 experiments

Expected Outcomes:
------------------
If linear model holds (unlikely):
- All frequencies should show Basin A (model never predicts collapse)

If spawn interval is critical factor:
- f=0.75%: Likely Basin A (133 cycles still reasonable)
- f=0.50%: Possible Basin A (200 cycles pushing limits)
- f=0.25%: Likely Basin B (400 cycles very long)
- f=0.10%: Very likely Basin B (1000 cycles extreme)

Basin Classification:
- Basin A (homeostasis): mean_population > 2.5
- Basin B (collapse): mean_population ≤ 2.5

Success Criteria:
-----------------
1. Identify first frequency with Basin B outcome
2. Measure transition from Basin A to Basin B
3. Calculate actual hierarchical scaling coefficient α
4. Compare with single-scale critical frequency (f_crit ≈ 2.0% from C171)
"""

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

# ============================================================================
# EXPERIMENT PARAMETERS
# ============================================================================

FREQUENCIES_TO_TEST = [0.0075, 0.0050, 0.0025, 0.0010]  # 0.75%, 0.50%, 0.25%, 0.10%
SEEDS_PER_FREQUENCY = 10
N_POPULATIONS = 10
AGENTS_PER_POPULATION = 20
F_MIGRATE = 0.005  # 0.5% inter-population migration
N_CYCLES = 3000

# Agent parameters
E_INITIAL = 50.0
E_THRESHOLD = 20.0
E_COST = 10.0
RECHARGE_RATE = 0.5

# Basin classification
BASIN_A_THRESHOLD = 2.5

# Output
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Agent:
    """Individual agent within a population."""
    agent_id: int
    population_id: int
    energy: float = E_INITIAL
    age: int = 0

@dataclass
class Population:
    """Population of agents."""
    population_id: int
    agents: List[Agent] = field(default_factory=list)

    def size(self) -> int:
        return len(self.agents)

@dataclass
class HierarchicalSystem:
    """Two-level hierarchical system: agents → populations."""
    seed: int
    f_intra: float
    spawn_interval: int
    populations: List[Population] = field(default_factory=list)
    cycle_count: int = 0
    total_spawns: int = 0
    spawn_failures: int = 0

    def __post_init__(self):
        """Initialize populations with agents."""
        random.seed(self.seed)

        agent_counter = 0
        for pop_id in range(N_POPULATIONS):
            pop = Population(population_id=pop_id)
            for _ in range(AGENTS_PER_POPULATION):
                agent = Agent(agent_id=agent_counter, population_id=pop_id)
                pop.agents.append(agent)
                agent_counter += 1
            self.populations.append(pop)

    def total_population(self) -> int:
        """Total number of agents across all populations."""
        return sum(pop.size() for pop in self.populations)

    def active_populations(self) -> int:
        """Number of non-empty populations."""
        return sum(1 for pop in self.populations if pop.size() > 0)

    def step(self):
        """Execute one simulation cycle."""
        self.cycle_count += 1

        # 1. Energy recovery (all agents)
        self._energy_recovery()

        # 2. Intra-population spawning (on spawn interval)
        self._intra_spawning()

        # 3. Inter-population migration
        self._inter_migration()

        # 4. Age all agents
        self._age_agents()

    def _energy_recovery(self):
        """All agents recover energy per cycle."""
        for pop in self.populations:
            for agent in pop.agents:
                agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def _intra_spawning(self):
        """Agents spawn within populations at spawn_interval."""
        should_spawn = (self.cycle_count % self.spawn_interval) == 0

        if not should_spawn:
            return

        for pop in self.populations:
            new_agents = []
            for agent in pop.agents:
                if agent.energy >= E_THRESHOLD:
                    # Spawn child
                    agent.energy -= E_COST
                    child = Agent(
                        agent_id=self.total_spawns,
                        population_id=pop.population_id,
                        energy=E_COST  # Child starts with cost energy (below threshold)
                    )
                    new_agents.append(child)
                    self.total_spawns += 1
                else:
                    self.spawn_failures += 1

            pop.agents.extend(new_agents)

    def _inter_migration(self):
        """Migration between populations at F_MIGRATE rate."""
        total_agents = self.total_population()
        if total_agents == 0:
            return

        n_attempts = max(1, int(total_agents * F_MIGRATE))

        for _ in range(n_attempts):
            # Select source population (weighted by size)
            source_pop = self._select_population_by_size()
            if source_pop is None or source_pop.size() == 0:
                continue

            # Select random agent from source
            agent = random.choice(source_pop.agents)

            # Select random destination (different from source)
            dest_pop = random.choice([p for p in self.populations if p.population_id != source_pop.population_id])

            # Migrate
            source_pop.agents.remove(agent)
            agent.population_id = dest_pop.population_id
            dest_pop.agents.append(agent)

    def _select_population_by_size(self) -> Population:
        """Select population weighted by size."""
        weights = [pop.size() for pop in self.populations]
        total_weight = sum(weights)

        if total_weight == 0:
            return None

        r = random.uniform(0, total_weight)
        cumsum = 0
        for pop, weight in zip(self.populations, weights):
            cumsum += weight
            if r <= cumsum:
                return pop

        return self.populations[-1]  # Fallback

    def _age_agents(self):
        """Increment age of all agents."""
        for pop in self.populations:
            for agent in pop.agents:
                agent.age += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Compute simulation statistics."""
        mean_pop = self.total_population() / N_CYCLES
        basin = "A" if mean_pop > BASIN_A_THRESHOLD else "B"

        return {
            "seed": self.seed,
            "f_intra": self.f_intra,
            "spawn_interval": self.spawn_interval,
            "final_population": self.total_population(),
            "active_populations": self.active_populations(),
            "total_spawns": self.total_spawns,
            "spawn_failures": self.spawn_failures,
            "mean_population": mean_pop,
            "basin": basin
        }

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(f_intra: float, seed: int) -> Dict[str, Any]:
    """Run single experiment."""
    spawn_interval = max(1, int(100.0 / (f_intra * 100)))

    system = HierarchicalSystem(seed=seed, f_intra=f_intra, spawn_interval=spawn_interval)

    for _ in range(N_CYCLES):
        system.step()

    return system.get_statistics()

def main():
    """Execute all experiments."""
    print("=" * 80)
    print("C186 V6: ULTRA-LOW FREQUENCY TEST")
    print("=" * 80)
    print()
    print(f"Testing {len(FREQUENCIES_TO_TEST)} frequencies × {SEEDS_PER_FREQUENCY} seeds")
    print(f"Total experiments: {len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY}")
    print(f"Estimated runtime: ~{len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY * 0.5:.0f} seconds (~{len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY * 0.5 / 60:.1f} minutes)")
    print()

    results = {
        "metadata": {
            "experiment": "C186 V6: Ultra-Low Frequency Test",
            "date": "2025-11-05",
            "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
            "repository": "https://github.com/mrdirno/nested-resonance-memory-archive",
            "frequencies_tested": [f * 100 for f in FREQUENCIES_TO_TEST],  # Convert to percentages
            "seeds_per_frequency": SEEDS_PER_FREQUENCY,
            "n_populations": N_POPULATIONS,
            "agents_per_population": AGENTS_PER_POPULATION,
            "f_migrate": F_MIGRATE,
            "n_cycles": N_CYCLES,
            "basin_a_threshold": BASIN_A_THRESHOLD
        },
        "experiments": []
    }

    start_time = time.time()
    experiment_count = 0

    for f_intra in FREQUENCIES_TO_TEST:
        f_pct = f_intra * 100
        spawn_interval = max(1, int(100.0 / f_pct))

        print(f"Testing f={f_pct:.2f}% (spawn every {spawn_interval} cycles)")

        frequency_results = []
        for seed in range(SEEDS_PER_FREQUENCY):
            exp_result = run_experiment(f_intra, seed)
            frequency_results.append(exp_result)
            experiment_count += 1

            if (experiment_count % 10) == 0:
                elapsed = time.time() - start_time
                rate = experiment_count / elapsed
                remaining = (len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY - experiment_count) / rate
                print(f"  Progress: {experiment_count}/{len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY} "
                      f"({experiment_count / (len(FREQUENCIES_TO_TEST) * SEEDS_PER_FREQUENCY) * 100:.0f}%) "
                      f"- {remaining / 60:.1f} min remaining")

        # Aggregate statistics for this frequency
        basin_a_count = sum(1 for r in frequency_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(frequency_results)) * 100
        mean_pop_avg = sum(r['mean_population'] for r in frequency_results) / len(frequency_results)
        mean_pop_std = (sum((r['mean_population'] - mean_pop_avg) ** 2 for r in frequency_results) / len(frequency_results)) ** 0.5

        print(f"  Basin A: {basin_a_count}/{len(frequency_results)} ({basin_a_pct:.0f}%)")
        print(f"  Mean population: {mean_pop_avg:.2f} ± {mean_pop_std:.2f}")
        print()

        results["experiments"].append({
            "f_intra": f_intra,
            "f_intra_pct": f_pct,
            "spawn_interval": spawn_interval,
            "individual_runs": frequency_results,
            "aggregate_statistics": {
                "basin_a_count": basin_a_count,
                "basin_a_pct": basin_a_pct,
                "basin_b_count": len(frequency_results) - basin_a_count,
                "basin_b_pct": 100 - basin_a_pct,
                "mean_population_avg": mean_pop_avg,
                "mean_population_std": mean_pop_std
            }
        })

    total_time = time.time() - start_time
    results["metadata"]["total_runtime_seconds"] = total_time
    results["metadata"]["total_runtime_minutes"] = total_time / 60

    # Save results
    output_file = RESULTS_DIR / "c186_v6_ultra_low_frequency_test.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"Total runtime: {total_time / 60:.1f} minutes")
    print(f"Results saved to: {output_file}")
    print()

    # Summary
    print("SUMMARY:")
    print()
    print("Frequency | Basin A  | Mean Pop | Std    | Outcome")
    print("-" * 60)
    for exp in results["experiments"]:
        f_pct = exp["f_intra_pct"]
        stats = exp["aggregate_statistics"]
        basin_a_pct = stats["basin_a_pct"]
        mean_pop = stats["mean_population_avg"]
        std = stats["mean_population_std"]
        outcome = "VIABLE" if basin_a_pct >= 50 else "COLLAPSE"
        print(f"{f_pct:6.2f}%  | {basin_a_pct:5.0f}%    | {mean_pop:7.2f} | {std:6.3f} | {outcome}")
    print()

    # Identify critical frequency
    print("CRITICAL FREQUENCY ANALYSIS:")
    print()
    for exp in results["experiments"]:
        stats = exp["aggregate_statistics"]
        if stats["basin_a_pct"] < 100:
            f_pct = exp["f_intra_pct"]
            print(f"First non-100% Basin A frequency: {f_pct:.2f}%")
            print(f"Basin A: {stats['basin_a_pct']:.0f}%")
            print(f"This is the transition region!")
            break
    else:
        print("All frequencies show 100% Basin A!")
        print("Hierarchical critical frequency f_hier_crit < 0.10%")
        print("Hierarchical scaling coefficient α < 0.05")
        print()
        print("This suggests hierarchical systems are DRAMATICALLY more efficient")
        print("than single-scale systems (10× or more!).")

if __name__ == "__main__":
    main()
