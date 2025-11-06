#!/usr/bin/env python3
"""
C186 V7: Migration Rate Variation Study
========================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1071)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test effect of inter-population migration rate on hierarchical system viability
and efficiency. Determine if migration is necessary for hierarchical advantage,
and identify optimal migration rate.

Background:
-----------
C186 V1-V5 Results (all with f_migrate = 0.5%):
- f=5.0%: 100% Basin A (mean_pop=170.0)
- f=2.5%: 100% Basin A (mean_pop=95.0)
- f=2.0%: 100% Basin A (mean_pop=79.9)
- f=1.5%: 100% Basin A (mean_pop=64.9)
- f=1.0%: 100% Basin A (mean_pop=49.8)

All tests used constant f_migrate = 0.5%. Migration identified as rescue mechanism
enabling hierarchical advantage through population rebalancing.

Research Questions:
-------------------
1. Is migration necessary for hierarchical advantage?
2. What is minimum viable migration rate?
3. What is optimal migration rate?
4. Does excessive migration degrade performance?

Hypothesis:
-----------
Migration provides rescue mechanism that enables hierarchical efficiency.

Expected outcomes:
- f_migrate = 0%: Possible collapse (no rescue)
- f_migrate = 0.1%: Possible threshold behavior
- f_migrate = 0.25%: Likely viable (reduced rescue)
- f_migrate = 0.5%: Known viable (baseline)
- f_migrate = 1.0%: Likely viable (enhanced rescue)
- f_migrate = 2.0%: Possible degradation (excessive mixing)

Alternative hypothesis: Migration not necessary, compartmentalization alone
provides advantage. If true, f_migrate = 0% should still show Basin A.

Experimental Design:
--------------------
Test 6 migration rates at fixed intra-population spawn frequency:

Fixed parameter:
- f_intra = 1.5% (spawn every 67 cycles) ← Known viable at f_migrate=0.5%

Variable parameter:
- f_migrate: 0%, 0.1%, 0.25%, 0.5%, 1.0%, 2.0%

Other parameters:
- 10 populations
- 20 agents per population (200 total initial)
- 3000 cycles
- 10 seeds per migration rate
- Total: 6 migration rates × 10 seeds = 60 experiments

Expected Outcomes:
------------------
If migration is necessary:
- f_migrate = 0%: Basin B (no rescue mechanism)
- f_migrate = 0.1%: Mixed outcomes (threshold)
- f_migrate ≥ 0.25%: Basin A (rescue operational)

If migration is not necessary:
- All migration rates show Basin A
- Population variance may differ

If optimal migration exists:
- Performance peaks at some f_migrate
- Degrades at extremes (0% or very high %)

Basin Classification:
- Basin A (homeostasis): mean_population > 2.5
- Basin B (collapse): mean_population ≤ 2.5

Success Criteria:
-----------------
1. Determine if f_migrate = 0% is viable
2. Identify minimum viable migration rate
3. Identify optimal migration rate (if exists)
4. Quantify relationship between f_migrate and system performance
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

MIGRATION_RATES_TO_TEST = [0.0, 0.001, 0.0025, 0.005, 0.01, 0.02]  # 0%, 0.1%, 0.25%, 0.5%, 1.0%, 2.0%
SEEDS_PER_RATE = 10
F_INTRA = 0.015  # 1.5% (known viable at f_migrate=0.5%)
SPAWN_INTERVAL = 67  # Spawn every 67 cycles
N_POPULATIONS = 10
AGENTS_PER_POPULATION = 20
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
    f_migrate: float
    populations: List[Population] = field(default_factory=list)
    cycle_count: int = 0
    total_spawns: int = 0
    spawn_failures: int = 0
    total_migrations: int = 0

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
        """Migration between populations at f_migrate rate."""
        if self.f_migrate == 0:
            return  # No migration

        total_agents = self.total_population()
        if total_agents == 0:
            return

        n_attempts = max(1, int(total_agents * self.f_migrate))

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
        pop_variance = sum((s - (self.total_population() / N_POPULATIONS))**2 for s in pop_sizes) / N_POPULATIONS

        return {
            "seed": self.seed,
            "f_migrate": self.f_migrate,
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

def run_experiment(f_migrate: float, seed: int) -> Dict[str, Any]:
    """Run single experiment."""
    system = HierarchicalSystem(seed=seed, f_migrate=f_migrate)

    for _ in range(N_CYCLES):
        system.step()

    return system.get_statistics()

def main():
    """Execute all experiments."""
    print("=" * 80)
    print("C186 V7: MIGRATION RATE VARIATION STUDY")
    print("=" * 80)
    print()
    print(f"Fixed f_intra: {F_INTRA * 100:.2f}% (spawn every {SPAWN_INTERVAL} cycles)")
    print(f"Testing {len(MIGRATION_RATES_TO_TEST)} migration rates × {SEEDS_PER_RATE} seeds")
    print(f"Total experiments: {len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE}")
    print(f"Estimated runtime: ~{len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE * 0.5:.0f} seconds (~{len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE * 0.5 / 60:.1f} minutes)")
    print()

    results = {
        "metadata": {
            "experiment": "C186 V7: Migration Rate Variation Study",
            "date": "2025-11-05",
            "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
            "repository": "https://github.com/mrdirno/nested-resonance-memory-archive",
            "f_intra": F_INTRA,
            "f_intra_pct": F_INTRA * 100,
            "spawn_interval": SPAWN_INTERVAL,
            "migration_rates_tested": [f * 100 for f in MIGRATION_RATES_TO_TEST],  # Convert to percentages
            "seeds_per_rate": SEEDS_PER_RATE,
            "n_populations": N_POPULATIONS,
            "agents_per_population": AGENTS_PER_POPULATION,
            "n_cycles": N_CYCLES,
            "basin_a_threshold": BASIN_A_THRESHOLD
        },
        "experiments": []
    }

    start_time = time.time()
    experiment_count = 0

    for f_migrate in MIGRATION_RATES_TO_TEST:
        f_pct = f_migrate * 100

        print(f"Testing f_migrate={f_pct:.2f}%")

        rate_results = []
        for seed in range(SEEDS_PER_RATE):
            exp_result = run_experiment(f_migrate, seed)
            rate_results.append(exp_result)
            experiment_count += 1

            if (experiment_count % 10) == 0:
                elapsed = time.time() - start_time
                rate = experiment_count / elapsed
                remaining = (len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE - experiment_count) / rate
                print(f"  Progress: {experiment_count}/{len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE} "
                      f"({experiment_count / (len(MIGRATION_RATES_TO_TEST) * SEEDS_PER_RATE) * 100:.0f}%) "
                      f"- {remaining / 60:.1f} min remaining")

        # Aggregate statistics for this migration rate
        basin_a_count = sum(1 for r in rate_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(rate_results)) * 100
        mean_pop_avg = sum(r['mean_population'] for r in rate_results) / len(rate_results)
        mean_pop_std = (sum((r['mean_population'] - mean_pop_avg) ** 2 for r in rate_results) / len(rate_results)) ** 0.5
        pop_var_avg = sum(r['population_variance'] for r in rate_results) / len(rate_results)

        print(f"  Basin A: {basin_a_count}/{len(rate_results)} ({basin_a_pct:.0f}%)")
        print(f"  Mean population: {mean_pop_avg:.2f} ± {mean_pop_std:.2f}")
        print(f"  Population variance: {pop_var_avg:.2f}")
        print()

        results["experiments"].append({
            "f_migrate": f_migrate,
            "f_migrate_pct": f_pct,
            "individual_runs": rate_results,
            "aggregate_statistics": {
                "basin_a_count": basin_a_count,
                "basin_a_pct": basin_a_pct,
                "basin_b_count": len(rate_results) - basin_a_count,
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
    output_file = RESULTS_DIR / "c186_v7_migration_rate_variation.json"
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
    print("Migration | Basin A  | Mean Pop | Std    | Pop Var | Outcome")
    print("-" * 70)
    for exp in results["experiments"]:
        f_pct = exp["f_migrate_pct"]
        stats = exp["aggregate_statistics"]
        basin_a_pct = stats["basin_a_pct"]
        mean_pop = stats["mean_population_avg"]
        std = stats["mean_population_std"]
        pop_var = stats["population_variance_avg"]
        outcome = "VIABLE" if basin_a_pct >= 50 else "COLLAPSE"
        print(f"{f_pct:7.2f}%  | {basin_a_pct:5.0f}%    | {mean_pop:7.2f} | {std:6.3f} | {pop_var:7.2f} | {outcome}")
    print()

    # Analysis
    print("MIGRATION NECESSITY ANALYSIS:")
    print()
    f_migrate_0_result = next((exp for exp in results["experiments"] if exp["f_migrate"] == 0.0), None)
    if f_migrate_0_result:
        stats = f_migrate_0_result["aggregate_statistics"]
        if stats["basin_a_pct"] >= 50:
            print("✓ f_migrate = 0% is VIABLE")
            print("  Migration is NOT necessary for hierarchical advantage!")
            print("  Compartmentalization alone provides resilience.")
        else:
            print("✗ f_migrate = 0% shows COLLAPSE")
            print("  Migration IS necessary for hierarchical advantage!")
            print("  Rescue mechanism is critical.")
    print()

    print("OPTIMAL MIGRATION RATE:")
    print()
    optimal_exp = max(results["experiments"], key=lambda e: e["aggregate_statistics"]["mean_population_avg"])
    print(f"Highest mean population at f_migrate = {optimal_exp['f_migrate_pct']:.2f}%")
    print(f"Mean population: {optimal_exp['aggregate_statistics']['mean_population_avg']:.2f}")
    print()

    # Variance analysis
    print("POPULATION VARIANCE (lower = more balanced):")
    print()
    for exp in results["experiments"]:
        f_pct = exp["f_migrate_pct"]
        pop_var = exp["aggregate_statistics"]["population_variance_avg"]
        print(f"f_migrate = {f_pct:5.2f}%: variance = {pop_var:.2f}")
    print()
    print("Higher migration rates should show lower variance (more mixing).")

if __name__ == "__main__":
    main()
