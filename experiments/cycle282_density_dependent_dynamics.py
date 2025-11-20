#!/usr/bin/env python3
"""
CYCLE 282: DENSITY-DEPENDENT DYNAMICS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether NRM can exhibit self-limiting growth (natural carrying capacity)
  by adding density-dependent death rate.

Research Question:
  Can density-dependent mechanics produce emergent equilibrium?

Mechanism:
  Death probability increases with population:
  P(death) = base_death + density_factor * (N / K)

  Where K is the "carrying capacity" parameter.

Expected:
  - Without density dependence (C280): Exponential growth to external cap
  - With density dependence: Convergence to equilibrium near K

Design:
  - 3 density factors: 0 (control), 0.1, 0.5
  - 3 carrying capacities: 100, 500, 1000
  - 3 seeds per condition
  - Total: 27 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C282"
CYCLE_NAME = "Density-Dependent Dynamics"
MODE = "DENSITY_DEPENDENT"

CYCLES = 20000  # Longer to see equilibrium
N_POPULATIONS = 1
INITIAL_AGENTS = 10
F_INTRA = 0.005

# Energy parameters (viable growth regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Test conditions
DENSITY_FACTORS = [0.0, 0.1, 0.5]  # 0 = control (no density dependence)
CARRYING_CAPACITIES = [100, 500, 1000]
SEEDS = [100, 101, 102]


def run_experiment(density_factor: float, carrying_capacity: int,
                   seed: int, cycles: int) -> dict:
    """Run experiment with density-dependent death."""

    label = f"df{density_factor}_K{carrying_capacity}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c282_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize
    for i in range(INITIAL_AGENTS):
        agent = FractalAgent(
            agent_id=f"agent_0_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    MAX_POPULATION = 10000
    population_history = []

    start_time = time.time()

    for cycle in range(cycles):
        agents = reality.get_population_agents(0)
        current_pop = len(agents)

        if current_pop >= MAX_POPULATION:
            print(f"      [CAP] at cycle {cycle}")
            break

        # EXPONENTIAL SPAWN
        new_spawns = []
        for agent in agents:
            if np.random.random() < F_INTRA:
                child = FractalAgent(
                    agent_id=f"spawn_{cycle}_{agent.agent_id}",
                    population_id=0,
                    energy=SPAWN_ENERGY
                )
                new_spawns.append(child)

        for child in new_spawns:
            reality.add_agent(child, population_id=0)

        # DENSITY-DEPENDENT DEATH
        agents = reality.get_population_agents(0)
        current_pop = len(agents)

        for agent in agents:
            agent.energy -= E_CONSUME

            # Base death from energy depletion
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                # Density-dependent death
                if density_factor > 0 and carrying_capacity > 0:
                    death_prob = density_factor * (current_pop / carrying_capacity)
                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, 0)
                        continue

                # Recharge survivors
                agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        final_pop = len(reality.get_population_agents(0))
        if cycle % 100 == 0:
            population_history.append(final_pop)

            if cycle % 5000 == 0:
                print(f"      Cycle {cycle}: pop={final_pop}")

        if final_pop == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    final_pop = len(reality.get_population_agents(0))
    runtime = time.time() - start_time

    # Calculate equilibrium metrics
    if len(population_history) > 10:
        late_phase = population_history[-20:]  # Last 2000 cycles
        mean_late = np.mean(late_phase)
        std_late = np.std(late_phase)
        cv = std_late / mean_late if mean_late > 0 else 0
    else:
        mean_late = final_pop
        std_late = 0
        cv = 0

    return {
        "density_factor": density_factor,
        "carrying_capacity": carrying_capacity,
        "seed": seed,
        "final_population": final_pop,
        "mean_late": mean_late,
        "std_late": std_late,
        "cv": cv,  # Coefficient of variation - lower = more stable equilibrium
        "max_population": max(population_history) if population_history else 0,
        "population_history": population_history,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 282: DENSITY-DEPENDENT DYNAMICS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Can density-dependent mechanics produce emergent equilibrium?")
    print()
    print("Conditions:")
    print(f"  Density factors: {DENSITY_FACTORS}")
    print(f"  Carrying capacities: {CARRYING_CAPACITIES}")
    print(f"  Seeds: {len(SEEDS)}")
    print(f"  Total: {len(DENSITY_FACTORS) * len(CARRYING_CAPACITIES) * len(SEEDS)}")
    print()

    results = []
    total = len(DENSITY_FACTORS) * len(CARRYING_CAPACITIES) * len(SEEDS)
    exp_num = 0

    for df in DENSITY_FACTORS:
        for K in CARRYING_CAPACITIES:
            print(f"\n{'='*60}")
            print(f"Density Factor={df}, K={K}")
            print("=" * 60)

            for seed in SEEDS:
                exp_num += 1
                print(f"\n[{exp_num}/{total}] df={df}, K={K}, seed={seed}")

                try:
                    result = run_experiment(df, K, seed, CYCLES)
                    results.append(result)

                    print(f"    → final={result['final_population']}, "
                          f"mean_late={result['mean_late']:.1f}, "
                          f"CV={result['cv']:.3f}")

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
        key = (r["density_factor"], r["carrying_capacity"])
        by_condition[key].append(r)

    print("\nEquilibrium Analysis:")
    print("-" * 70)
    print(f"{'DF':>6} {'K':>8} {'Mean Late':>12} {'Std':>10} {'CV':>10} {'Status':>12}")
    print("-" * 70)

    for (df, K) in sorted(by_condition.keys()):
        exp_list = by_condition[(df, K)]
        mean_late = np.mean([e["mean_late"] for e in exp_list])
        std = np.mean([e["std_late"] for e in exp_list])
        cv = np.mean([e["cv"] for e in exp_list])

        # Determine status
        if df == 0:
            status = "CONTROL"
        elif cv < 0.1:
            status = "EQUILIBRIUM"
        elif cv < 0.3:
            status = "QUASI-STABLE"
        else:
            status = "UNSTABLE"

        print(f"{df:>6.1f} {K:>8} {mean_late:>12.1f} {std:>10.1f} {cv:>10.3f} {status:>12}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "initial_agents": INITIAL_AGENTS,
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factors": DENSITY_FACTORS,
            "carrying_capacities": CARRYING_CAPACITIES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c282_density_dependent_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C282 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
