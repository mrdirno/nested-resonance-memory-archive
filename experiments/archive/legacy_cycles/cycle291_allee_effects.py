#!/usr/bin/env python3
"""
CYCLE 291: ALLEE EFFECTS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether Allee effects (reduced fitness at low density) can cause extinction.

Research Question:
  Is there a critical population threshold below which recovery fails?

Mechanism:
  Birth rate reduced at low density: f_effective = f_intra × min(N/A, 1)
  Where A is the Allee threshold.

Design:
  - Single population with Allee effect
  - 4 Allee thresholds: 0, 5, 10, 20
  - Initial populations: 3, 5, 10, 20
  - 3 seeds per condition
  - Total: 48 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C291"
CYCLE_NAME = "Allee Effects"
MODE = "ALLEE"

CYCLES = 15000
N_POPULATIONS = 1
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Density dependence
DENSITY_FACTOR = 0.1
K = 500

# Test conditions
ALLEE_THRESHOLDS = [0, 5, 10, 20]  # 0 = no Allee effect
INITIAL_POPULATIONS = [3, 5, 10, 20]
SEEDS = [100, 101, 102]


def run_experiment(allee_threshold: int, initial_pop: int, seed: int, cycles: int) -> dict:
    """Run Allee effect experiment."""

    label = f"A{allee_threshold}_N{initial_pop}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c291_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize population
    for i in range(initial_pop):
        agent = FractalAgent(
            agent_id=f"agent_0_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    MAX_POPULATION = 5000
    pop_history = []
    extinction_cycle = None

    start_time = time.time()

    for cycle in range(cycles):
        agents = reality.get_population_agents(0)
        current_pop = len(agents)

        if current_pop >= MAX_POPULATION:
            break

        # SPAWN with Allee effect
        if allee_threshold > 0:
            # Reduced birth rate at low density
            allee_factor = min(current_pop / allee_threshold, 1.0)
            effective_f = F_INTRA * allee_factor
        else:
            effective_f = F_INTRA

        new_spawns = []
        for agent in agents:
            if np.random.random() < effective_f:
                child = FractalAgent(
                    agent_id=f"spawn_{cycle}_{agent.agent_id}",
                    population_id=0,
                    energy=SPAWN_ENERGY
                )
                new_spawns.append(child)

        for child in new_spawns:
            reality.add_agent(child, population_id=0)

        # DEATH
        agents = reality.get_population_agents(0)
        pop_size = len(agents)

        for agent in agents:
            agent.energy -= E_CONSUME

            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                death_prob = DENSITY_FACTOR * (pop_size / K)
                if np.random.random() < death_prob:
                    reality.remove_agent(agent.agent_id, 0)
                    continue

                agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        final_pop = len(reality.get_population_agents(0))
        if cycle % 100 == 0:
            pop_history.append(final_pop)

        if final_pop == 0:
            extinction_cycle = cycle
            break

    runtime = time.time() - start_time
    final_pop = len(reality.get_population_agents(0))

    # Calculate metrics
    if len(pop_history) > 10:
        late_mean = np.mean(pop_history[-20:])
    else:
        late_mean = final_pop

    return {
        "allee_threshold": allee_threshold,
        "initial_pop": initial_pop,
        "seed": seed,
        "final_pop": final_pop,
        "late_mean": float(late_mean),
        "extinct": final_pop == 0,
        "extinction_cycle": extinction_cycle,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 291: ALLEE EFFECTS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Is there a critical threshold below which recovery fails?")
    print()
    print(f"Allee thresholds: {ALLEE_THRESHOLDS}")
    print(f"Initial populations: {INITIAL_POPULATIONS}")
    print(f"Total experiments: {len(ALLEE_THRESHOLDS) * len(INITIAL_POPULATIONS) * len(SEEDS)}")
    print()

    results = []
    total = len(ALLEE_THRESHOLDS) * len(INITIAL_POPULATIONS) * len(SEEDS)
    exp_num = 0

    for allee in ALLEE_THRESHOLDS:
        print(f"\n{'='*60}")
        print(f"Allee threshold: {allee}")
        print("=" * 60)

        for init_pop in INITIAL_POPULATIONS:
            for seed in SEEDS:
                exp_num += 1

                try:
                    result = run_experiment(allee, init_pop, seed, CYCLES)
                    results.append(result)

                    status = "EXTINCT" if result["extinct"] else f"N={result['late_mean']:.0f}"
                    if exp_num % 6 == 0:  # Print every 6th
                        print(f"  [{exp_num}/{total}] A={allee}, N0={init_pop}: {status}")

                except Exception as e:
                    print(f"  [{exp_num}/{total}] FAILED: {e}")

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_condition = defaultdict(list)
    for r in results:
        key = (r["allee_threshold"], r["initial_pop"])
        by_condition[key].append(r)

    print("\nExtinction Rates by Condition:")
    print("-" * 60)
    print(f"{'Allee':>8} {'Init':>8} {'Extinct':>10} {'Mean Final':>12}")
    print("-" * 60)

    for allee in ALLEE_THRESHOLDS:
        for init_pop in INITIAL_POPULATIONS:
            exp_list = by_condition[(allee, init_pop)]
            extinct_rate = sum(1 for e in exp_list if e["extinct"]) / len(exp_list)
            mean_final = np.mean([e["late_mean"] for e in exp_list if not e["extinct"]]) if any(not e["extinct"] for e in exp_list) else 0

            print(f"{allee:>8} {init_pop:>8} {extinct_rate:>10.0%} {mean_final:>12.1f}")

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
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "allee_thresholds": ALLEE_THRESHOLDS,
            "initial_populations": INITIAL_POPULATIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c291_allee_effects_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C291 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
