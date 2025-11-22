#!/usr/bin/env python3
"""
CYCLE 288: SCALING EFFECTS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test how metapopulation dynamics scale with number of populations.

Research Question:
  Do synchronization and equilibrium patterns hold at different scales?

Design:
  - Variable population counts: 2, 5, 10, 20
  - Ring topology (minimal connected)
  - Migration rate: 0.05
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
CYCLE_ID = "C288"
CYCLE_NAME = "Scaling Effects"
MODE = "SCALING"

CYCLES = 15000  # Shorter due to larger systems
INITIAL_AGENTS_PER_POP = 20
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Density dependence
DENSITY_FACTOR = 0.1
K = 500

# Migration
MIGRATION_RATE = 0.05

# Test conditions
POPULATION_COUNTS = [2, 5, 10, 20]
SEEDS = [100, 101, 102]


def run_experiment(n_populations: int, seed: int, cycles: int) -> dict:
    """Run scaling experiment."""

    label = f"N{n_populations}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c288_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=n_populations,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize populations
    for pop_id in range(n_populations):
        for i in range(INITIAL_AGENTS_PER_POP):
            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{i}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)

    MAX_POP_PER = 5000
    pop_history = {p: [] for p in range(n_populations)}

    start_time = time.time()

    for cycle in range(cycles):
        # SPAWN
        for pop_id in range(n_populations):
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if np.random.random() < F_INTRA:
                    child = FractalAgent(
                        agent_id=f"spawn_{cycle}_{pop_id}_{agent.agent_id}",
                        population_id=pop_id,
                        energy=SPAWN_ENERGY
                    )
                    new_spawns.append(child)

            for child in new_spawns:
                reality.add_agent(child, population_id=pop_id)

        # MIGRATION (ring topology)
        for pop_id in range(n_populations):
            agents = list(reality.get_population_agents(pop_id))
            # Ring neighbors
            left = (pop_id - 1) % n_populations
            right = (pop_id + 1) % n_populations

            for agent in agents:
                if np.random.random() < MIGRATION_RATE:
                    target = np.random.choice([left, right])
                    reality.migrate_agent(agent.agent_id, pop_id, target)

        # DEATH
        for pop_id in range(n_populations):
            agents = reality.get_population_agents(pop_id)
            pop_size = len(agents)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    death_prob = DENSITY_FACTOR * (pop_size / K)
                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(n_populations):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 5000 == 0:
                total = sum(len(reality.get_population_agents(p)) for p in range(n_populations))
                print(f"      Cycle {cycle}: total={total}")

        # Check extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(n_populations))
        if total == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(n_populations)]
    total_pop = sum(final_pops)

    # Late-phase analysis
    if len(pop_history[0]) > 10:
        late_totals = []
        for i in range(-20, 0):
            if abs(i) <= len(pop_history[0]):
                total = sum(pop_history[p][i] for p in range(n_populations))
                late_totals.append(total)

        mean_total = np.mean(late_totals)
        std_total = np.std(late_totals)

        # Per-population mean
        per_pop_means = []
        for p in range(n_populations):
            late = pop_history[p][-20:]
            per_pop_means.append(np.mean(late))
        mean_per_pop = np.mean(per_pop_means)
        std_across_pops = np.std(per_pop_means)

        # Sync metric
        sync_metric = float(std_across_pops / max(mean_per_pop, 1))
    else:
        mean_total = total_pop
        std_total = 0
        mean_per_pop = total_pop / n_populations
        sync_metric = 0

    # Equilibrium per population (theoretical: K * f/df = 25)
    theoretical_per_pop = K * (F_INTRA / DENSITY_FACTOR)

    return {
        "n_populations": n_populations,
        "seed": seed,
        "final_total": total_pop,
        "mean_total": float(mean_total),
        "std_total": float(std_total),
        "mean_per_pop": float(mean_per_pop),
        "theoretical_per_pop": theoretical_per_pop,
        "sync_metric": sync_metric,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 288: SCALING EFFECTS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Do patterns hold at different scales?")
    print()
    print(f"Population counts: {POPULATION_COUNTS}")
    print(f"Total experiments: {len(POPULATION_COUNTS) * len(SEEDS)}")
    print()

    results = []
    total = len(POPULATION_COUNTS) * len(SEEDS)
    exp_num = 0

    for n_pops in POPULATION_COUNTS:
        print(f"\n{'='*60}")
        print(f"Populations: {n_pops}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] N={n_pops}, seed={seed}")

            try:
                result = run_experiment(n_pops, seed, CYCLES)
                results.append(result)

                print(f"    → total={result['mean_total']:.1f}, "
                      f"per_pop={result['mean_per_pop']:.1f}, "
                      f"sync={result['sync_metric']:.3f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_n = defaultdict(list)
    for r in results:
        by_n[r["n_populations"]].append(r)

    print("\nScaling Effects:")
    print("-" * 80)
    print(f"{'N Pops':>8} {'Mean Total':>12} {'Per Pop':>10} {'Theory':>10} {'Sync':>10}")
    print("-" * 80)

    for n_pops in POPULATION_COUNTS:
        exp_list = by_n[n_pops]
        mean_total = np.mean([e["mean_total"] for e in exp_list])
        per_pop = np.mean([e["mean_per_pop"] for e in exp_list])
        theory = exp_list[0]["theoretical_per_pop"]
        sync = np.mean([e["sync_metric"] for e in exp_list])

        print(f"{n_pops:>8} {mean_total:>12.1f} {per_pop:>10.1f} {theory:>10.1f} {sync:>10.3f}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "initial_agents_per_pop": INITIAL_AGENTS_PER_POP,
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "migration_rate": MIGRATION_RATE,
            "population_counts": POPULATION_COUNTS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c288_scaling_effects_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C288 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
