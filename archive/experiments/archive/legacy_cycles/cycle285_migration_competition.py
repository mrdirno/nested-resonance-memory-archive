#!/usr/bin/env python3
"""
CYCLE 285: MIGRATION-COMPETITION INTERACTION

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether migration can rescue inferior competitors from exclusion
  when competing for shared resources.

Research Question:
  Can dispersal allow inferior competitors to persist?

Background:
  - C283: Migration synchronizes isolated populations
  - C284: Shared resources produce competitive exclusion

Design:
  - 2 populations with different fitness (ratio = 2.0)
  - Global K (shared resources - would produce exclusion)
  - Variable migration rates: 0, 0.01, 0.05, 0.10
  - 3 seeds per condition
  - Total: 12 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C285"
CYCLE_NAME = "Migration-Competition Interaction"
MODE = "MIGRATION_COMPETITION"

CYCLES = 30000
N_POPULATIONS = 2
INITIAL_AGENTS_PER_POP = 50
BASE_F_INTRA = 0.005
FITNESS_RATIO = 2.0  # Pop1 has 2x fitness

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Global competition
GLOBAL_K = 500
DENSITY_FACTOR = 0.1

# Test conditions
MIGRATION_RATES = [0.0, 0.01, 0.05, 0.10]
SEEDS = [100, 101, 102]


def run_experiment(migration_rate: float, seed: int, cycles: int) -> dict:
    """Run migration-competition experiment."""

    label = f"mig{migration_rate}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c285_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Fitness values
    f_intra = [BASE_F_INTRA, BASE_F_INTRA * FITNESS_RATIO]

    # Initialize populations
    for pop_id in range(N_POPULATIONS):
        for i in range(INITIAL_AGENTS_PER_POP):
            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{i}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)

    MAX_POP_PER = 5000
    pop_history = {p: [] for p in range(N_POPULATIONS)}

    # Track extinction time
    extinction_cycle = None

    start_time = time.time()

    for cycle in range(cycles):
        # SPAWN (per agent, different rates)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if np.random.random() < f_intra[pop_id]:
                    child = FractalAgent(
                        agent_id=f"spawn_{cycle}_{pop_id}_{agent.agent_id}",
                        population_id=pop_id,
                        energy=SPAWN_ENERGY
                    )
                    new_spawns.append(child)

            for child in new_spawns:
                reality.add_agent(child, population_id=pop_id)

        # MIGRATION
        if migration_rate > 0:
            for pop_id in range(N_POPULATIONS):
                agents = reality.get_population_agents(pop_id)
                for agent in list(agents):
                    if np.random.random() < migration_rate:
                        # Migrate to other population
                        target = 1 - pop_id
                        reality.migrate_agent(agent.agent_id, pop_id, target)

        # DEATH (energy + global competition)
        pop_sizes = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
        total_pop = sum(pop_sizes)

        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Global competition
                    death_prob = DENSITY_FACTOR * (total_pop / GLOBAL_K)

                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 10000 == 0:
                pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
                print(f"      Cycle {cycle}: pop0={pops[0]}, pop1={pops[1]}")

        # Check for pop0 extinction (inferior competitor)
        if extinction_cycle is None and len(reality.get_population_agents(0)) == 0:
            extinction_cycle = cycle

        # Check total extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
        if total == 0:
            print(f"      [ALL EXTINCT] at cycle {cycle}")
            break

        # Check cap
        if any(len(reality.get_population_agents(p)) >= MAX_POP_PER for p in range(N_POPULATIONS)):
            print(f"      [CAP] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]

    # Late-phase analysis
    outcomes = {}
    for pop_id in range(N_POPULATIONS):
        if len(pop_history[pop_id]) > 10:
            late = pop_history[pop_id][-20:]
            mean_late = np.mean(late)
            std_late = np.std(late)
        else:
            mean_late = final_pops[pop_id]
            std_late = 0

        outcomes[f"pop{pop_id}_mean"] = float(mean_late)
        outcomes[f"pop{pop_id}_std"] = float(std_late)
        outcomes[f"pop{pop_id}_extinct"] = bool(mean_late < 1)

    # Determine outcome
    if outcomes["pop0_extinct"] and outcomes["pop1_extinct"]:
        outcome_type = "MUTUAL_EXTINCTION"
    elif outcomes["pop0_extinct"]:
        outcome_type = "EXCLUSION"
    elif outcomes["pop1_extinct"]:
        outcome_type = "REVERSAL"
    else:
        outcome_type = "RESCUE"  # Migration rescued inferior competitor

    # Persistence ratio (fraction of time pop0 survived)
    if len(pop_history[0]) > 0:
        survived_periods = sum(1 for p in pop_history[0] if p > 0)
        persistence = survived_periods / len(pop_history[0])
    else:
        persistence = 0

    return {
        "migration_rate": migration_rate,
        "fitness_ratio": FITNESS_RATIO,
        "seed": seed,
        "final_pops": final_pops,
        "outcome_type": outcome_type,
        "extinction_cycle": extinction_cycle,
        "persistence": float(persistence),
        **outcomes,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 285: MIGRATION-COMPETITION INTERACTION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Can migration rescue inferior competitors from exclusion?")
    print()
    print(f"Fitness ratio: {FITNESS_RATIO}")
    print(f"Migration rates: {MIGRATION_RATES}")
    print(f"Global K: {GLOBAL_K}")
    print(f"Total experiments: {len(MIGRATION_RATES) * len(SEEDS)}")
    print()

    results = []
    total = len(MIGRATION_RATES) * len(SEEDS)
    exp_num = 0

    for mig_rate in MIGRATION_RATES:
        print(f"\n{'='*60}")
        print(f"Migration rate={mig_rate}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] mig={mig_rate}, seed={seed}")

            try:
                result = run_experiment(mig_rate, seed, CYCLES)
                results.append(result)

                print(f"    → {result['outcome_type']}, "
                      f"persistence={result['persistence']:.2f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_migration = defaultdict(list)
    for r in results:
        by_migration[r["migration_rate"]].append(r)

    print("\nMigration Rescue Effect:")
    print("-" * 80)
    print(f"{'Mig Rate':>10} {'Pop0 Mean':>10} {'Pop1 Mean':>10} {'Persist':>10} {'Outcome':>15}")
    print("-" * 80)

    for mig_rate in sorted(by_migration.keys()):
        exp_list = by_migration[mig_rate]
        pop0_mean = np.mean([e["pop0_mean"] for e in exp_list])
        pop1_mean = np.mean([e["pop1_mean"] for e in exp_list])
        persistence = np.mean([e["persistence"] for e in exp_list])

        # Most common outcome
        outcomes = [e["outcome_type"] for e in exp_list]
        outcome = max(set(outcomes), key=outcomes.count)

        print(f"{mig_rate:>10.2f} {pop0_mean:>10.1f} {pop1_mean:>10.1f} {persistence:>10.2f} {outcome:>15}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "n_populations": N_POPULATIONS,
            "initial_agents_per_pop": INITIAL_AGENTS_PER_POP,
            "base_f_intra": BASE_F_INTRA,
            "fitness_ratio": FITNESS_RATIO,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "global_K": GLOBAL_K,
            "density_factor": DENSITY_FACTOR,
            "migration_rates": MIGRATION_RATES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c285_migration_competition_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C285 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
