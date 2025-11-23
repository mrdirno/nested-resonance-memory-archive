#!/usr/bin/env python3
"""
C186 V8: Population Count Variation Study
==========================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1071)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test effect of number of populations (hierarchical redundancy) on system viability
and efficiency. Determine if hierarchical advantage scales with redundancy, and
identify minimum viable hierarchy.

Background:
-----------
C186 V1-V5 Results (all with n_pop = 10):
- f=5.0%: 100% Basin A (mean_pop=170.0)
- f=2.5%: 100% Basin A (mean_pop=95.0)
- f=2.0%: 100% Basin A (mean_pop=79.9)
- f=1.5%: 100% Basin A (mean_pop=64.9)
- f=1.0%: 100% Basin A (mean_pop=49.8)

All tests used n_pop = 10 populations. Hierarchical advantage attributed to:
1. Risk compartmentalization
2. Migration rescue
3. Redundancy across populations

Research Questions:
-------------------
1. What is minimum number of populations for hierarchical advantage?
2. Does advantage scale with n_pop?
3. Is there optimal n_pop?
4. Does excessive fragmentation degrade performance?

Hypothesis:
-----------
Hierarchical advantage scales with redundancy. More populations → more resilience.

Expected outcomes:
- n_pop = 1: No hierarchy (degenerate to single-scale)
- n_pop = 2: Minimal hierarchy (limited redundancy)
- n_pop = 5: Moderate hierarchy (partial redundancy)
- n_pop = 10: Known viable (baseline)
- n_pop = 20: Enhanced hierarchy (more redundancy)
- n_pop = 50: Extreme fragmentation (possible degradation)

Alternative hypothesis: Advantage saturates at some n_pop. Beyond threshold,
additional populations provide diminishing returns.

Experimental Design:
--------------------
Test 6 population counts at fixed parameters:

Fixed parameters:
- f_intra = 1.5% (spawn every 67 cycles) ← Known viable at n_pop=10
- f_migrate = 0.5% (migration rate)
- Total initial agents = 200 (constant)
- agents_per_population = 200 / n_pop (varies)

Variable parameter:
- n_pop: 1, 2, 5, 10, 20, 50

Other parameters:
- 3000 cycles
- 10 seeds per population count
- Total: 6 population counts × 10 seeds = 60 experiments

Expected Outcomes:
------------------
If redundancy is critical:
- n_pop = 1: Likely Basin B (no compartmentalization)
- n_pop = 2: Possible threshold behavior
- n_pop ≥ 5: Basin A (advantage operational)

If advantage saturates:
- n_pop ≥ 10: Similar performance (no improvement)

If fragmentation degrades:
- n_pop = 50: Lower performance (populations too small)

Basin Classification:
- Basin A (homeostasis): mean_population > 2.5
- Basin B (collapse): mean_population ≤ 2.5

Success Criteria:
-----------------
1. Determine minimum viable n_pop
2. Quantify relationship between n_pop and system performance
3. Identify optimal n_pop (if exists)
4. Test saturation hypothesis
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

POPULATION_COUNTS_TO_TEST = [1, 2, 5, 10, 20, 50]
SEEDS_PER_COUNT = 10
TOTAL_INITIAL_AGENTS = 200  # Constant across all experiments
F_INTRA = 0.015  # 1.5% (known viable at n_pop=10)
SPAWN_INTERVAL = 67  # Spawn every 67 cycles
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
    n_pop: int
    agents_per_pop: int
    populations: List[Population] = field(default_factory=list)
    cycle_count: int = 0
    total_spawns: int = 0
    spawn_failures: int = 0
    total_migrations: int = 0

    def __post_init__(self):
        """Initialize populations with agents."""
        random.seed(self.seed)

        agent_counter = 0
        for pop_id in range(self.n_pop):
            pop = Population(population_id=pop_id)
            for _ in range(self.agents_per_pop):
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

        # 3. Inter-population migration (if n_pop > 1)
        if self.n_pop > 1:
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
        should_spawn = (self.cycle_count % SPAWN_INTERVAL) == 0

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
            self.total_migrations += 1

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

        # Population size variance across populations
        pop_sizes = [pop.size() for pop in self.populations]
        mean_pop_size = self.total_population() / self.n_pop if self.n_pop > 0 else 0
        pop_variance = sum((s - mean_pop_size)**2 for s in pop_sizes) / self.n_pop if self.n_pop > 0 else 0

        return {
            "seed": self.seed,
            "n_pop": self.n_pop,
            "agents_per_pop_initial": self.agents_per_pop,
            "final_population": self.total_population(),
            "active_populations": self.active_populations(),
            "total_spawns": self.total_spawns,
            "spawn_failures": self.spawn_failures,
            "total_migrations": self.total_migrations,
            "mean_population": mean_pop,
            "population_variance": pop_variance,
            "basin": basin
        }

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(n_pop: int, seed: int) -> Dict[str, Any]:
    """Run single experiment."""
    agents_per_pop = TOTAL_INITIAL_AGENTS // n_pop
    system = HierarchicalSystem(seed=seed, n_pop=n_pop, agents_per_pop=agents_per_pop)

    for _ in range(N_CYCLES):
        system.step()

    return system.get_statistics()

def main():
    """Execute all experiments."""
    print("=" * 80)
    print("C186 V8: POPULATION COUNT VARIATION STUDY")
    print("=" * 80)
    print()
    print(f"Fixed f_intra: {F_INTRA * 100:.2f}% (spawn every {SPAWN_INTERVAL} cycles)")
    print(f"Fixed f_migrate: {F_MIGRATE * 100:.2f}%")
    print(f"Fixed total initial agents: {TOTAL_INITIAL_AGENTS}")
    print(f"Testing {len(POPULATION_COUNTS_TO_TEST)} population counts × {SEEDS_PER_COUNT} seeds")
    print(f"Total experiments: {len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT}")
    print(f"Estimated runtime: ~{len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT * 0.5:.0f} seconds (~{len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT * 0.5 / 60:.1f} minutes)")
    print()

    results = {
        "metadata": {
            "experiment": "C186 V8: Population Count Variation Study",
            "date": "2025-11-05",
            "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
            "repository": "https://github.com/mrdirno/nested-resonance-memory-archive",
            "f_intra": F_INTRA,
            "f_intra_pct": F_INTRA * 100,
            "spawn_interval": SPAWN_INTERVAL,
            "f_migrate": F_MIGRATE,
            "f_migrate_pct": F_MIGRATE * 100,
            "total_initial_agents": TOTAL_INITIAL_AGENTS,
            "population_counts_tested": POPULATION_COUNTS_TO_TEST,
            "seeds_per_count": SEEDS_PER_COUNT,
            "n_cycles": N_CYCLES,
            "basin_a_threshold": BASIN_A_THRESHOLD
        },
        "experiments": []
    }

    start_time = time.time()
    experiment_count = 0

    for n_pop in POPULATION_COUNTS_TO_TEST:
        agents_per_pop = TOTAL_INITIAL_AGENTS // n_pop

        print(f"Testing n_pop={n_pop} ({agents_per_pop} agents per population)")

        count_results = []
        for seed in range(SEEDS_PER_COUNT):
            exp_result = run_experiment(n_pop, seed)
            count_results.append(exp_result)
            experiment_count += 1

            if (experiment_count % 10) == 0:
                elapsed = time.time() - start_time
                rate = experiment_count / elapsed
                remaining = (len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT - experiment_count) / rate
                print(f"  Progress: {experiment_count}/{len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT} "
                      f"({experiment_count / (len(POPULATION_COUNTS_TO_TEST) * SEEDS_PER_COUNT) * 100:.0f}%) "
                      f"- {remaining / 60:.1f} min remaining")

        # Aggregate statistics for this population count
        basin_a_count = sum(1 for r in count_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(count_results)) * 100
        mean_pop_avg = sum(r['mean_population'] for r in count_results) / len(count_results)
        mean_pop_std = (sum((r['mean_population'] - mean_pop_avg) ** 2 for r in count_results) / len(count_results)) ** 0.5
        pop_var_avg = sum(r['population_variance'] for r in count_results) / len(count_results)

        print(f"  Basin A: {basin_a_count}/{len(count_results)} ({basin_a_pct:.0f}%)")
        print(f"  Mean population: {mean_pop_avg:.2f} ± {mean_pop_std:.2f}")
        print(f"  Population variance: {pop_var_avg:.2f}")
        print()

        results["experiments"].append({
            "n_pop": n_pop,
            "agents_per_pop": agents_per_pop,
            "individual_runs": count_results,
            "aggregate_statistics": {
                "basin_a_count": basin_a_count,
                "basin_a_pct": basin_a_pct,
                "basin_b_count": len(count_results) - basin_a_count,
                "basin_b_pct": 100 - basin_a_pct,
                "mean_population_avg": mean_pop_avg,
                "mean_population_std": mean_pop_std,
                "population_variance_avg": pop_var_avg
            }
        })

    total_time = time.time() - start_time
    results["metadata"]["total_runtime_seconds"] = total_time
    results["metadata"]["total_runtime_minutes"] = total_time / 60

    # Save results
    output_file = RESULTS_DIR / "c186_v8_population_count_variation.json"
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
    print("n_pop | agents/pop | Basin A  | Mean Pop | Std    | Pop Var | Outcome")
    print("-" * 75)
    for exp in results["experiments"]:
        n_pop = exp["n_pop"]
        agents_per_pop = exp["agents_per_pop"]
        stats = exp["aggregate_statistics"]
        basin_a_pct = stats["basin_a_pct"]
        mean_pop = stats["mean_population_avg"]
        std = stats["mean_population_std"]
        pop_var = stats["population_variance_avg"]
        outcome = "VIABLE" if basin_a_pct >= 50 else "COLLAPSE"
        print(f"{n_pop:5} | {agents_per_pop:10} | {basin_a_pct:5.0f}%    | {mean_pop:7.2f} | {std:6.3f} | {pop_var:7.2f} | {outcome}")
    print()

    # Analysis
    print("MINIMUM VIABLE HIERARCHY:")
    print()
    for exp in results["experiments"]:
        stats = exp["aggregate_statistics"]
        if stats["basin_a_pct"] >= 50:
            print(f"First viable n_pop: {exp['n_pop']}")
            print(f"Basin A: {stats['basin_a_pct']:.0f}%")
            print(f"This is the minimum viable hierarchy threshold.")
            break
    else:
        print("No viable population count found!")
        print("Hierarchical structure may not provide advantage at f_intra=1.5%")
    print()

    print("SCALING ANALYSIS:")
    print()
    for exp in results["experiments"]:
        n_pop = exp["n_pop"]
        mean_pop = exp["aggregate_statistics"]["mean_population_avg"]
        print(f"n_pop = {n_pop:2}: mean_population = {mean_pop:.2f}")
    print()
    print("If advantage scales: mean_population should increase with n_pop")
    print("If advantage saturates: mean_population should plateau")
    print()

    # Identify optimal
    print("OPTIMAL POPULATION COUNT:")
    print()
    optimal_exp = max(results["experiments"], key=lambda e: e["aggregate_statistics"]["mean_population_avg"])
    print(f"Highest mean population at n_pop = {optimal_exp['n_pop']}")
    print(f"Mean population: {optimal_exp['aggregate_statistics']['mean_population_avg']:.2f}")

if __name__ == "__main__":
    main()
