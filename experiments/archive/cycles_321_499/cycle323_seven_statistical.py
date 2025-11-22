#!/usr/bin/env python3
"""
CYCLE 323: SEVEN-TROPHIC STATISTICAL CHARACTERIZATION

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Statistical characterization of bifurcation at seven trophic levels.

Research Question:
  What is the true stability rate at the bifurcation threshold?

Background:
  C317: Seven-trophic 67% (3 seeds)
  C323: Statistical power with 20 seeds

Design:
  - 7 populations
  - K=600
  - 20 seeds
  - Total: 20 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C323"
CYCLE_NAME = "Seven-Trophic Statistical"
MODE = "SEVEN_STAT"

CYCLES = 30000
K = 600
INITIAL = [300, 30, 10, 5, 3, 2, 1]

# Parameters for each level
PARAMS = [
    {"f": 0.1, "K": K, "e_con": 0.2, "e_rech": 0.4},  # L0 prey
    {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 0.3},  # L1
    {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 0.25},  # L2
    {"attack": 0.008, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 0.2},  # L3
    {"attack": 0.012, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 0.15},  # L4
    {"attack": 0.015, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 0.12},  # L5
    {"attack": 0.018, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 0.10}   # L6
]

SEEDS = list(range(3000, 3020))  # 20 seeds


def run_experiment(seed: int, cycles: int) -> dict:
    """Run seven-trophic statistical experiment."""

    n_levels = 7

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c323_seed{seed}.db"
    reality = RealityInterface(db_path=db_path, n_populations=n_levels, mode=MODE)
    np.random.seed(seed)

    # Initialize
    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            e = 1.0 + lvl * 0.5
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, e), lvl)

    histories = {i: [] for i in range(n_levels)}
    collapse_cycle = None
    start_time = time.time()

    for cycle in range(cycles):
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]

        if sum(ns) >= 4000:
            break

        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

        # Predation cascade (top-down)
        for lvl in range(n_levels - 1, 0, -1):
            prey_lvl = lvl - 1
            pops[prey_lvl] = reality.get_population_agents(prey_lvl)
            ns[prey_lvl] = len(pops[prey_lvl])

            if ns[prey_lvl] > 0:
                ids = [a.agent_id for a in pops[prey_lvl]]
                consumed = []
                p = PARAMS[lvl]

                for pred in pops[lvl]:
                    avail = ns[prey_lvl] - len(consumed)
                    if avail > 0:
                        rate = (p["attack"] * avail) / (1 + p["attack"] * p["h"] * avail)
                        for _ in range(min(np.random.poisson(rate), avail)):
                            remain = [i for i in ids if i not in consumed]
                            if remain:
                                v = np.random.choice(remain)
                                consumed.append(v)
                                gains[lvl][pred.agent_id] += p["e_gain"]

                for v in consumed:
                    reality.remove_agent(v, prey_lvl)

        # Reproduction
        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, PARAMS[0]["f"] * (1 - len(pops[0]) / PARAMS[0]["K"]))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"L0_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < PARAMS[lvl]["conv"] * eg:
                    reality.add_agent(FractalAgent(f"L{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        # Death
        for a in reality.get_population_agents(0):
            a.energy -= PARAMS[0]["e_con"]
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + PARAMS[0]["e_rech"], 2.0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - PARAMS[lvl]["e_con"]
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                else:
                    a.energy = min(a.energy, 2.0 + lvl)

        # Record
        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        # Track collapse
        if collapse_cycle is None and ns[n_levels-1] == 0:
            collapse_cycle = cycle

        if all(n == 0 for n in ns[:3]):
            break

    runtime = time.time() - start_time

    # Metrics
    finals = {}
    for i in range(n_levels):
        if len(histories[i]) > 10:
            finals[i] = np.mean(histories[i][-10:])
        else:
            finals[i] = INITIAL[i]

    coexist = all(finals[i] >= 0.5 for i in range(n_levels))

    return {
        "seed": seed,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "coexist": bool(coexist),
        "collapse_cycle": collapse_cycle,
        "runtime": runtime
    }


def main():
    print("=" * 80)
    print(f"CYCLE 323: SEVEN-TROPHIC STATISTICAL CHARACTERIZATION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    results = []
    total = len(SEEDS)

    for exp_num, seed in enumerate(SEEDS, 1):
        print(f"[{exp_num}/{total}] seed={seed}", end=" ")

        try:
            result = run_experiment(seed, CYCLES)
            results.append(result)
            status = "COEXIST" if result["coexist"] else f"COLLAPSE@{result['collapse_cycle']}"
            print(f"→ {status}")

        except Exception as e:
            print(f"✗ FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    coexist_count = sum(1 for r in results if r["coexist"])
    collapse_count = len(results) - coexist_count

    print(f"\nCoexistence: {coexist_count}/{len(results)} ({coexist_count/len(results)*100:.0f}%)")
    print(f"Collapse: {collapse_count}/{len(results)} ({collapse_count/len(results)*100:.0f}%)")

    if collapse_count > 0:
        collapse_cycles = [r["collapse_cycle"] for r in results if r["collapse_cycle"]]
        if collapse_cycles:
            print(f"\nCollapse timing:")
            print(f"  Mean: {np.mean(collapse_cycles):.0f}")
            print(f"  Std: {np.std(collapse_cycles):.0f}")
            print(f"  Min: {min(collapse_cycles)}")
            print(f"  Max: {max(collapse_cycles)}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "n_seeds": len(SEEDS),
        "coexistence_rate": coexist_count / len(results),
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c323_seven_statistical_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C323 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
