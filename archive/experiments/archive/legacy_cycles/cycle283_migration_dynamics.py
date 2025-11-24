#!/usr/bin/env python3
"""
CYCLE 283: MIGRATION DYNAMICS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Explore how migration between populations affects dynamics and equilibrium.

Research Question:
  Does migration produce emergent collective behavior beyond individual
  population dynamics?

Design:
  - 3 migration rates: 0 (isolated), 0.01, 0.1
  - Multiple populations (5)
  - With and without density dependence
  - 3 seeds per condition
  - Total: 18 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C283"
CYCLE_NAME = "Migration Dynamics"
MODE = "MIGRATION"

CYCLES = 20000
N_POPULATIONS = 5
INITIAL_AGENTS_PER_POP = 20
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Test conditions
MIGRATION_RATES = [0.0, 0.01, 0.1]  # Probability of migration per agent per cycle
DENSITY_CONFIGS = [
    {"df": 0.0, "K": 1000, "label": "no_density"},
    {"df": 0.1, "K": 500, "label": "with_density"}
]
SEEDS = [100, 101, 102]


def run_experiment(migration_rate: float, density_config: dict,
                   seed: int, cycles: int) -> dict:
    """Run migration experiment."""

    label = f"mig{migration_rate}_{density_config['label']}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c283_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)
    df = density_config["df"]
    K = density_config["K"]

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

    start_time = time.time()

    for cycle in range(cycles):
        # SPAWN (exponential, per agent)
        for pop_id in range(N_POPULATIONS):
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

        # MIGRATION
        if migration_rate > 0:
            for pop_id in range(N_POPULATIONS):
                agents = reality.get_population_agents(pop_id)
                for agent in agents:
                    if np.random.random() < migration_rate:
                        # Migrate to random other population
                        target = np.random.randint(0, N_POPULATIONS - 1)
                        if target >= pop_id:
                            target += 1
                        reality.migrate_agent(agent.agent_id, pop_id, target)

        # DEATH (energy + density-dependent)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            pop_size = len(agents)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Density-dependent death
                    if df > 0 and K > 0:
                        death_prob = df * (pop_size / K)
                        if np.random.random() < death_prob:
                            reality.remove_agent(agent.agent_id, pop_id)
                            continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 5000 == 0:
                total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
                print(f"      Cycle {cycle}: total={total}")

        # Check extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
        if total == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

        # Check cap
        if any(len(reality.get_population_agents(p)) >= MAX_POP_PER for p in range(N_POPULATIONS)):
            print(f"      [CAP] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
    total_pop = sum(final_pops)

    # Population synchronization (variance across populations)
    if len(pop_history[0]) > 10:
        late_totals = []
        for i in range(-20, 0):
            if abs(i) <= len(pop_history[0]):
                total = sum(pop_history[p][i] for p in range(N_POPULATIONS))
                late_totals.append(total)

        mean_total = np.mean(late_totals)
        std_total = np.std(late_totals)

        # Cross-population variance
        cross_pop_var = []
        for i in range(-10, 0):
            if abs(i) <= len(pop_history[0]):
                pops = [pop_history[p][i] for p in range(N_POPULATIONS)]
                cross_pop_var.append(np.std(pops))

        sync_metric = np.mean(cross_pop_var) / max(np.mean(mean_total / N_POPULATIONS), 1)
    else:
        mean_total = total_pop
        std_total = 0
        sync_metric = 0

    return {
        "migration_rate": migration_rate,
        "density_config": density_config["label"],
        "df": df,
        "K": K,
        "seed": seed,
        "final_total": total_pop,
        "final_pops": final_pops,
        "mean_total": mean_total,
        "std_total": std_total,
        "sync_metric": sync_metric,  # Lower = more synchronized
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 283: MIGRATION DYNAMICS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does migration produce emergent collective behavior?")
    print()
    print(f"Migration rates: {MIGRATION_RATES}")
    print(f"Density configs: {[d['label'] for d in DENSITY_CONFIGS]}")
    print(f"Populations: {N_POPULATIONS}")
    print(f"Total experiments: {len(MIGRATION_RATES) * len(DENSITY_CONFIGS) * len(SEEDS)}")
    print()

    results = []
    total = len(MIGRATION_RATES) * len(DENSITY_CONFIGS) * len(SEEDS)
    exp_num = 0

    for mig_rate in MIGRATION_RATES:
        for density_config in DENSITY_CONFIGS:
            print(f"\n{'='*60}")
            print(f"Migration={mig_rate}, Density={density_config['label']}")
            print("=" * 60)

            for seed in SEEDS:
                exp_num += 1
                print(f"\n[{exp_num}/{total}] mig={mig_rate}, {density_config['label']}, seed={seed}")

                try:
                    result = run_experiment(mig_rate, density_config, seed, CYCLES)
                    results.append(result)

                    print(f"    → total={result['final_total']}, "
                          f"mean={result['mean_total']:.1f}, "
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
    by_condition = defaultdict(list)
    for r in results:
        key = (r["migration_rate"], r["density_config"])
        by_condition[key].append(r)

    print("\nMigration Effects:")
    print("-" * 80)
    print(f"{'Mig Rate':>10} {'Density':>15} {'Mean Total':>12} {'Std':>10} {'Sync':>10}")
    print("-" * 80)

    for (mig, dens) in sorted(by_condition.keys()):
        exp_list = by_condition[(mig, dens)]
        mean_total = np.mean([e["mean_total"] for e in exp_list])
        std = np.mean([e["std_total"] for e in exp_list])
        sync = np.mean([e["sync_metric"] for e in exp_list])

        print(f"{mig:>10.2f} {dens:>15} {mean_total:>12.1f} {std:>10.1f} {sync:>10.3f}")

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
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "migration_rates": MIGRATION_RATES,
            "density_configs": DENSITY_CONFIGS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c283_migration_dynamics_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C283 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
