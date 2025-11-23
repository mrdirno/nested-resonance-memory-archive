#!/usr/bin/env python3
"""
CYCLE 370: LOW HANDLING TIME - 40 CYCLES

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test low handling time sensitivity at 40 cycles.

Background:
  C369: 40 cycles, 1.5× handling - 45% survival
  C359: 40 cycles, baseline - 50% survival
  C370: 40 cycles, 0.5× handling - expect improved survival

Hypothesis:
  Lower handling time → more efficient predation → similar to higher attack

Design:
  - K declines from 600 to 200 over 40 cycles
  - Handling times: 0.5× baseline
  - 20 seeds
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C370"
CYCLE_NAME = "Low Handling Time 40 Cycles"
MODE = "LOW_HANDLING_40"

CYCLES = 30000
K_START = 600
K_END = 200
DECLINE_CYCLES = 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

# 0.5× handling times
BASE_PARAMS = [
    {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
    {"attack": 0.003, "h": 0.01, "e_con": 0.3, "e_gain": 0.5, "conv": 0.3},
    {"attack": 0.005, "h": 0.015, "e_con": 0.4, "e_gain": 0.6, "conv": 0.25},
    {"attack": 0.008, "h": 0.02, "e_con": 0.5, "e_gain": 0.8, "conv": 0.2},
    {"attack": 0.012, "h": 0.025, "e_con": 0.6, "e_gain": 1.0, "conv": 0.15},
    {"attack": 0.015, "h": 0.03, "e_con": 0.7, "e_gain": 1.2, "conv": 0.12},
    {"attack": 0.018, "h": 0.035, "e_con": 0.8, "e_gain": 1.4, "conv": 0.10}
]

SEEDS = list(range(5380, 5400))


def run_experiment(seed: int, cycles: int) -> dict:
    """Run low handling time experiment."""

    n_levels = 7

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c370_seed{seed}.db"
    reality = RealityInterface(db_path=db_path, n_populations=n_levels, mode=MODE)
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            agent_id = f"L{lvl}_{i}"
            e = 1.0 + lvl * 0.5
            reality.add_agent(FractalAgent(agent_id, lvl, e), lvl)

    histories = {i: [] for i in range(n_levels)}
    start_time = time.time()

    for cycle in range(cycles):
        if cycle < DECLINE_CYCLES:
            K = K_START - (K_START - K_END) * cycle / DECLINE_CYCLES
        else:
            K = K_END

        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]

        if sum(ns) >= 4000:
            break

        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

        for lvl in range(n_levels - 1, 0, -1):
            prey_lvl = lvl - 1
            pops[prey_lvl] = reality.get_population_agents(prey_lvl)
            ns[prey_lvl] = len(pops[prey_lvl])

            if ns[prey_lvl] > 0:
                ids = [a.agent_id for a in pops[prey_lvl]]
                consumed = []
                p = BASE_PARAMS[lvl]

                for pred in pops[lvl]:
                    avail = ns[prey_lvl] - len(consumed)
                    if avail > 0:
                        attack = p["attack"]
                        rate = (attack * avail) / (1 + attack * p["h"] * avail)

                        for _ in range(min(np.random.poisson(rate), avail)):
                            remain = [i for i in ids if i not in consumed]
                            if remain:
                                v = np.random.choice(remain)
                                consumed.append(v)
                                gains[lvl][pred.agent_id] += p["e_gain"]

                for v in consumed:
                    reality.remove_agent(v, prey_lvl)

        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, BASE_PARAMS[0]["f"] * (1 - len(pops[0]) / K))
            if np.random.random() < f:
                child_id = f"L0_{cycle}_{a.agent_id[-6:]}"
                reality.add_agent(FractalAgent(child_id, 0, 0.5), 0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < BASE_PARAMS[lvl]["conv"] * eg:
                    child_id = f"L{lvl}_{cycle}_{a.agent_id[-6:]}"
                    reality.add_agent(FractalAgent(child_id, lvl, 0.8), lvl)

        for a in reality.get_population_agents(0):
            a.energy -= BASE_PARAMS[0]["e_con"]
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + BASE_PARAMS[0]["e_rech"], 2.0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - BASE_PARAMS[lvl]["e_con"]
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                else:
                    a.energy = min(a.energy, 2.0 + lvl)

        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        if all(n == 0 for n in ns[:3]):
            break

    runtime = time.time() - start_time

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
        "runtime": runtime,
        "n_recordings": len(histories[0])
    }


def main():
    print("=" * 80)
    print(f"CYCLE 370: LOW HANDLING TIME - 40 CYCLES")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"K: {K_START} → {K_END} over {DECLINE_CYCLES} cycles")
    print(f"Handling times: 0.5× baseline")
    print("=" * 80)
    print()

    results = []
    total = len(SEEDS)

    for exp_num, seed in enumerate(SEEDS, 1):
        print(f"[{exp_num}/{total}] seed={seed}", end=" ")

        try:
            result = run_experiment(seed, CYCLES)
            results.append(result)
            status = "SURVIVE" if result["coexist"] else "COLLAPSE"
            l0_final = result["finals"]["L0"]
            recs = result["n_recordings"]
            print(f"→ {status}, L0={l0_final:.0f}, recordings={recs}")

        except Exception as e:
            print(f"✗ FAILED: {e}")

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    coexist_count = sum(1 for r in results if r["coexist"])
    print(f"\nCoexistence: {coexist_count}/{len(results)} ({coexist_count/len(results)*100:.0f}%)")

    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "k_start": K_START,
        "k_end": K_END,
        "decline_cycles": DECLINE_CYCLES,
        "handling_multiplier": 0.5,
        "n_seeds": len(SEEDS),
        "coexistence_rate": coexist_count / len(results) if results else 0,
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c370_low_handling_40cycles_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C370 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
