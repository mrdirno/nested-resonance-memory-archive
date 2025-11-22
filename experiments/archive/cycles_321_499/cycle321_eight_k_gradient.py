#!/usr/bin/env python3
"""
CYCLE 321: EIGHT-TROPHIC K GRADIENT

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Investigate why eight-trophic collapses at K=2400.

Research Question:
  Where does eight-trophic stability break down?

Background:
  C319: K=1200 → eight-trophic stable (100%)
  C320: K=2400 → eight-trophic collapse (0%)
  C321: Test intermediate K values

Design:
  - 8 populations
  - K = 1200, 1800, 2400
  - 3 seeds per K
  - Total: 9 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C321"
CYCLE_NAME = "Eight-Trophic K Gradient"
MODE = "EIGHT_K_GRADIENT"

CYCLES = 30000

# Parameters for each level (same as C319-C320)
BASE_PARAMS = [
    {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},  # L0 prey
    {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 0.3},  # L1
    {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 0.25},  # L2
    {"attack": 0.008, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 0.2},  # L3
    {"attack": 0.012, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 0.15},  # L4
    {"attack": 0.015, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 0.12},  # L5
    {"attack": 0.018, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 0.10},  # L6
    {"attack": 0.020, "h": 0.08, "e_con": 0.9, "e_gain": 1.6, "conv": 0.08}   # L7
]

CONDITIONS = [
    {"name": "K1200", "K": 1200, "initial": [600, 60, 20, 10, 6, 4, 2, 1]},
    {"name": "K1800", "K": 1800, "initial": [900, 90, 30, 15, 9, 6, 3, 2]},
    {"name": "K2400", "K": 2400, "initial": [1200, 120, 40, 20, 12, 8, 4, 2]}
]
SEEDS = [2800, 2801, 2802]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run eight-trophic K gradient experiment."""

    label = condition["name"]
    K = condition["K"]
    initial = condition["initial"]
    n_levels = 8

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c321_{label}_seed{seed}.db"
    reality = RealityInterface(db_path=db_path, n_populations=n_levels, mode=MODE)
    np.random.seed(seed)

    # Build params with K
    params = []
    for i, p in enumerate(BASE_PARAMS):
        if i == 0:
            params.append({**p, "K": K})
        else:
            params.append(p)

    # Initialize
    for lvl in range(n_levels):
        for i in range(initial[lvl]):
            e = 1.0 + lvl * 0.5
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, e), lvl)

    histories = {i: [] for i in range(n_levels)}
    start_time = time.time()

    for cycle in range(cycles):
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]

        if sum(ns) >= 10000:
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
                p = params[lvl]

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
        # Prey
        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, params[0]["f"] * (1 - len(pops[0]) / params[0]["K"]))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"L0_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        # Predators
        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < params[lvl]["conv"] * eg:
                    reality.add_agent(FractalAgent(f"L{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        # Death
        # Prey
        for a in reality.get_population_agents(0):
            a.energy -= params[0]["e_con"]
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + params[0]["e_rech"], 2.0)

        # Predators
        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - params[lvl]["e_con"]
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                else:
                    a.energy = min(a.energy, 2.0 + lvl)

        # Record
        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))
            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: " + ", ".join(f"L{i}={histories[i][-1]}" for i in range(n_levels)))

        if all(n == 0 for n in ns[:3]):
            break

    runtime = time.time() - start_time

    # Metrics
    finals = {}
    for i in range(n_levels):
        if len(histories[i]) > 10:
            finals[i] = np.mean(histories[i][-10:])
        else:
            finals[i] = initial[i]

    # Coexistence: all levels > 0
    coexist = all(finals[i] >= 0.5 for i in range(n_levels))

    return {
        "condition": label,
        "K": K,
        "seed": seed,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "coexist": bool(coexist),
        "runtime": runtime
    }


def main():
    print("=" * 80)
    print(f"CYCLE 321: EIGHT-TROPHIC K GRADIENT")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    results = []
    total = len(CONDITIONS) * len(SEEDS)
    exp_num = 0

    for condition in CONDITIONS:
        print(f"\n{'='*60}")
        print(f"Condition: {condition['name']} (K={condition['K']})")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {condition['name']}, seed={seed}")

            try:
                result = run_experiment(condition, seed, CYCLES)
                results.append(result)
                status = "COEXIST" if result["coexist"] else "PARTIAL"
                pop_str = ", ".join(f"{k}={v:.0f}" for k, v in result["finals"].items())
                print(f"    → {status}, {pop_str}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_cond = defaultdict(list)
    for r in results:
        by_cond[r["condition"]].append(r)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_cond[name]
        if exp_list:
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)
            print(f"\n{name}: {coexist:.0%} coexistence")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c321_eight_k_gradient_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C321 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
