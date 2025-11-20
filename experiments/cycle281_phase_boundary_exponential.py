#!/usr/bin/env python3
"""
CYCLE 281: PHASE BOUNDARY IN EXPONENTIAL GROWTH MODE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Validate phase boundary (E_net = 0) with exponential (per-agent) spawning.
  C280 only tested spawn threshold. This completes coverage.

Research Question:
  Does the phase boundary (E_net = 0) hold in exponential growth mode?

Expected:
  - E_net < 0: COLLAPSE (all agents die)
  - E_net = 0: HOMEOSTASIS (stable, no growth)
  - E_net > 0: Already validated in C280

Design:
  - 5 E_net values: -0.2, -0.1, 0.0, +0.1, +0.2
  - 5 seeds per condition
  - 10,000 cycles
  - Total: 25 experiments
"""

import sys
import os
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

# Add experiments directory to path for local imports
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C281"
CYCLE_NAME = "Phase Boundary in Exponential Growth"
MODE = "EXPONENTIAL_PHASE_BOUNDARY"

CYCLES = 10000
N_POPULATIONS = 1
INITIAL_AGENTS = 100  # Standard starting population
F_INTRA = 0.005  # 0.5% per agent per cycle
SPAWN_ENERGY = 0.5  # Standard spawn energy

# Energy conditions to test phase boundary
ENERGY_CONDITIONS = {
    "E_net_-0.2": {"E_consume": 0.7, "E_recharge": 0.5, "net": -0.2, "expected": "COLLAPSE"},
    "E_net_-0.1": {"E_consume": 0.6, "E_recharge": 0.5, "net": -0.1, "expected": "COLLAPSE"},
    "E_net_0.0": {"E_consume": 0.5, "E_recharge": 0.5, "net": 0.0, "expected": "HOMEOSTASIS"},
    "E_net_+0.1": {"E_consume": 0.4, "E_recharge": 0.5, "net": 0.1, "expected": "VIABLE"},
    "E_net_+0.2": {"E_consume": 0.3, "E_recharge": 0.5, "net": 0.2, "expected": "VIABLE"},
}

SEEDS = list(range(100, 105))  # 5 seeds


def run_experiment(energy_label: str, energy_params: dict, f_intra: float,
                   seed: int, cycles: int) -> dict:
    """Run single experiment with exponential spawning."""
    db_name = f"c281_PHASE_EXP_{energy_label}_seed{seed}.db"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/{db_name}"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    reality.energy_config = {
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"]
    }

    np.random.seed(seed)

    # Initialize agents
    for i in range(INITIAL_AGENTS):
        agent = FractalAgent(
            agent_id=f"agent_0_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    MAX_POPULATION = 100000
    population_history = []

    start_time = time.time()

    for cycle in range(cycles):
        agents = reality.get_population_agents(0)

        if len(agents) >= MAX_POPULATION:
            print(f"      [CAP] Population hit {MAX_POPULATION} at cycle {cycle}")
            break

        # EXPONENTIAL SPAWN
        new_spawns = []
        for agent in agents:
            if np.random.random() < f_intra:
                child = FractalAgent(
                    agent_id=f"spawn_{cycle}_{agent.agent_id}",
                    population_id=0,
                    energy=SPAWN_ENERGY
                )
                new_spawns.append(child)

        for child in new_spawns:
            reality.add_agent(child, population_id=0)

        # Death phase
        agents = reality.get_population_agents(0)
        for agent in agents:
            agent.energy -= energy_params["E_consume"]

            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + energy_params["E_recharge"], 2.0)

        current_pop = len(reality.get_population_agents(0))

        if cycle % 100 == 0:
            population_history.append(current_pop)

            if cycle % 2000 == 0:
                print(f"      Cycle {cycle}: pop={current_pop}")

        if current_pop == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    final_pop = len(reality.get_population_agents(0))
    runtime = time.time() - start_time

    return {
        "energy_label": energy_label,
        "E_net": energy_params["net"],
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"],
        "expected": energy_params["expected"],
        "f_intra": f_intra,
        "seed": seed,
        "cycles_completed": len(population_history) * 100,
        "final_population": final_pop,
        "max_population": max(population_history) if population_history else 0,
        "population_history": population_history,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 281: PHASE BOUNDARY IN EXPONENTIAL GROWTH")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Experimental Design:")
    print(f"  Purpose: Validate phase boundary (E_net=0) in exponential mode")
    print(f"  Conditions: {len(ENERGY_CONDITIONS)}")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(ENERGY_CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  Initial population: {INITIAL_AGENTS}")
    print()

    results = []
    total_exps = len(ENERGY_CONDITIONS) * len(SEEDS)
    exp_num = 0

    for label, params in ENERGY_CONDITIONS.items():
        print("=" * 80)
        print(f"Condition: {label} (expected: {params['expected']})")
        print(f"  E_consume={params['E_consume']}, E_recharge={params['E_recharge']}, E_net={params['net']}")
        print("=" * 80)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total_exps}] Running: {label}, seed={seed}")

            try:
                result = run_experiment(label, params, F_INTRA, seed, CYCLES)
                results.append(result)

                final = result["final_population"]
                max_pop = result["max_population"]
                runtime = result["runtime_seconds"]

                print(f"    → final={final}, max={max_pop}, runtime={runtime:.1f}s")

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
        by_condition[r["energy_label"]].append(r)

    print("\nPopulation by Condition:")
    print("-" * 70)
    print(f"{'Condition':<20} {'E_net':>8} {'Mean Pop':>10} {'Status':>12} {'Expected':>12}")
    print("-" * 70)

    correct = 0
    total = 0

    for label in sorted(by_condition.keys()):
        exp_list = by_condition[label]
        final_pops = [e["final_population"] for e in exp_list]
        mean_final = np.mean(final_pops)
        e_net = exp_list[0]["E_net"]
        expected = exp_list[0]["expected"]

        # Determine actual status
        if mean_final == 0:
            actual = "COLLAPSE"
        elif mean_final <= INITIAL_AGENTS * 1.5:
            actual = "HOMEOSTASIS"
        else:
            actual = "GROWTH"

        match = "✓" if (
            (expected == "COLLAPSE" and actual == "COLLAPSE") or
            (expected == "HOMEOSTASIS" and actual in ["HOMEOSTASIS", "COLLAPSE"]) or
            (expected == "VIABLE" and actual in ["HOMEOSTASIS", "GROWTH"])
        ) else "✗"

        if match == "✓":
            correct += 1
        total += 1

        print(f"{label:<20} {e_net:>8.1f} {mean_final:>10.1f} {actual:>12} {expected:>12} {match}")

    print("-" * 70)
    print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")

    # Save results
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "mode": "EXPONENTIAL (per-agent spawning)",
            "cycles": CYCLES,
            "initial_agents": INITIAL_AGENTS,
            "f_intra": F_INTRA,
            "spawn_energy": SPAWN_ENERGY,
            "conditions": ENERGY_CONDITIONS,
            "seeds": SEEDS
        },
        "results": results,
        "summary": {
            "total_experiments": total_exps,
            "accuracy": f"{correct}/{total}"
        }
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c281_phase_boundary_exponential_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C281 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
