#!/usr/bin/env python3
"""
CYCLE 287: ASYMMETRIC MIGRATION (SOURCE-SINK DYNAMICS)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test how asymmetric (directional) migration affects population dynamics.

Research Question:
  Does direction of migration flow matter for population outcomes?

Design:
  - 2 populations
  - Asymmetric migration: Pop0→Pop1 rate different from Pop1→Pop0
  - 4 asymmetry levels: 1:1, 2:1, 5:1, 10:1
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
CYCLE_ID = "C287"
CYCLE_NAME = "Asymmetric Migration"
MODE = "ASYMMETRIC_MIGRATION"

CYCLES = 20000
N_POPULATIONS = 2
INITIAL_AGENTS_PER_POP = 50
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Density dependence
DENSITY_FACTOR = 0.1
K = 500

# Base migration rate (symmetric would be 0.05 both ways)
BASE_MIGRATION = 0.05

# Asymmetry ratios (Pop0→Pop1 : Pop1→Pop0)
ASYMMETRY_RATIOS = [
    {"name": "1:1", "0to1": 0.05, "1to0": 0.05},
    {"name": "2:1", "0to1": 0.10, "1to0": 0.05},
    {"name": "5:1", "0to1": 0.25, "1to0": 0.05},
    {"name": "10:1", "0to1": 0.50, "1to0": 0.05}
]
SEEDS = [100, 101, 102]


def run_experiment(asymmetry: dict, seed: int, cycles: int) -> dict:
    """Run asymmetric migration experiment."""

    label = asymmetry["name"].replace(":", "to")
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c287_asym{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    mig_0to1 = asymmetry["0to1"]
    mig_1to0 = asymmetry["1to0"]

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
        # SPAWN
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

        # ASYMMETRIC MIGRATION
        # Pop0 → Pop1
        agents_0 = list(reality.get_population_agents(0))
        for agent in agents_0:
            if np.random.random() < mig_0to1:
                reality.migrate_agent(agent.agent_id, 0, 1)

        # Pop1 → Pop0
        agents_1 = list(reality.get_population_agents(1))
        for agent in agents_1:
            if np.random.random() < mig_1to0:
                reality.migrate_agent(agent.agent_id, 1, 0)

        # DEATH
        for pop_id in range(N_POPULATIONS):
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
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 5000 == 0:
                pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
                print(f"      Cycle {cycle}: pop0={pops[0]}, pop1={pops[1]}")

        # Check extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
        if total == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]

    # Late-phase analysis
    if len(pop_history[0]) > 10:
        late_0 = pop_history[0][-20:]
        late_1 = pop_history[1][-20:]

        mean_0 = np.mean(late_0)
        mean_1 = np.mean(late_1)
        std_0 = np.std(late_0)
        std_1 = np.std(late_1)

        # Population ratio (sink/source)
        if mean_0 > 0:
            pop_ratio = mean_1 / mean_0
        else:
            pop_ratio = float('inf')

        total_mean = mean_0 + mean_1
    else:
        mean_0, mean_1 = final_pops
        std_0, std_1 = 0, 0
        pop_ratio = mean_1 / mean_0 if mean_0 > 0 else float('inf')
        total_mean = sum(final_pops)

    # Net flow direction
    expected_flow = mig_0to1 - mig_1to0
    if expected_flow > 0:
        flow_direction = "0→1"
    elif expected_flow < 0:
        flow_direction = "1→0"
    else:
        flow_direction = "balanced"

    return {
        "asymmetry": asymmetry["name"],
        "mig_0to1": mig_0to1,
        "mig_1to0": mig_1to0,
        "seed": seed,
        "final_pops": final_pops,
        "mean_0": float(mean_0),
        "mean_1": float(mean_1),
        "std_0": float(std_0),
        "std_1": float(std_1),
        "pop_ratio": float(pop_ratio) if pop_ratio != float('inf') else 999,
        "total_mean": float(total_mean),
        "flow_direction": flow_direction,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 287: ASYMMETRIC MIGRATION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does direction of migration flow matter?")
    print()
    print(f"Asymmetry ratios: {[a['name'] for a in ASYMMETRY_RATIOS]}")
    print(f"Total experiments: {len(ASYMMETRY_RATIOS) * len(SEEDS)}")
    print()

    results = []
    total = len(ASYMMETRY_RATIOS) * len(SEEDS)
    exp_num = 0

    for asymmetry in ASYMMETRY_RATIOS:
        print(f"\n{'='*60}")
        print(f"Asymmetry: {asymmetry['name']} (0→1: {asymmetry['0to1']}, 1→0: {asymmetry['1to0']})")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {asymmetry['name']}, seed={seed}")

            try:
                result = run_experiment(asymmetry, seed, CYCLES)
                results.append(result)

                print(f"    → pop0={result['mean_0']:.1f}, pop1={result['mean_1']:.1f}, "
                      f"ratio={result['pop_ratio']:.2f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_asymmetry = defaultdict(list)
    for r in results:
        by_asymmetry[r["asymmetry"]].append(r)

    print("\nAsymmetric Migration Effects:")
    print("-" * 80)
    print(f"{'Ratio':>10} {'Pop0 (src)':>12} {'Pop1 (sink)':>12} {'Ratio':>10} {'Total':>10}")
    print("-" * 80)

    for asymmetry in ASYMMETRY_RATIOS:
        name = asymmetry["name"]
        exp_list = by_asymmetry[name]
        mean_0 = np.mean([e["mean_0"] for e in exp_list])
        mean_1 = np.mean([e["mean_1"] for e in exp_list])
        ratio = np.mean([e["pop_ratio"] for e in exp_list])
        total = np.mean([e["total_mean"] for e in exp_list])

        print(f"{name:>10} {mean_0:>12.1f} {mean_1:>12.1f} {ratio:>10.2f} {total:>10.1f}")

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
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "base_migration": BASE_MIGRATION,
            "asymmetry_ratios": ASYMMETRY_RATIOS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c287_asymmetric_migration_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C287 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
