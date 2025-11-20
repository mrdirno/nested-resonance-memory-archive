#!/usr/bin/env python3
"""
CYCLE 350: FULL REINTRODUCTION TEST

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test recovery with full initial population after collapse.

Background:
  C349: Small reintroduction (100) failed completely
  C350: Full reintroduction (300) at K=250

Design:
  - Start at K=200 (collapse)
  - Reintroduce FULL initial population at cycle 5000
  - K=250 (well above threshold)
  - 20 seeds
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C350"
CYCLE_NAME = "Full Reintroduction Test"
MODE = "FULL_REINTRO"

CYCLES = 30000
K_COLLAPSE = 200
K_RECOVERY = 250
REINTRO_CYCLE = 5000
INITIAL = [300, 30, 10, 5, 3, 2, 2]

BASE_PARAMS = [
    {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
    {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 0.3},
    {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 0.25},
    {"attack": 0.008, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 0.2},
    {"attack": 0.012, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 0.15},
    {"attack": 0.015, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 0.12},
    {"attack": 0.018, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 0.10}
]

SEEDS = list(range(4980, 5000))


def run_experiment(seed: int, cycles: int) -> dict:
    """Run full reintroduction experiment."""

    n_levels = 7

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c350_seed{seed}.db"
    reality = RealityInterface(db_path=db_path, n_populations=n_levels, mode=MODE)
    np.random.seed(seed)

    # Initial population
    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            agent_id = f"L{lvl}_{i}"
            e = 1.0 + lvl * 0.5
            reality.add_agent(FractalAgent(agent_id, lvl, e), lvl)

    histories = {i: [] for i in range(n_levels)}
    start_time = time.time()
    collapsed = False

    for cycle in range(cycles):
        # K changes at reintroduction
        if cycle < REINTRO_CYCLE:
            K = K_COLLAPSE
        else:
            K = K_RECOVERY

        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]

        # Check for collapse before reintroduction
        if cycle < REINTRO_CYCLE and sum(ns) == 0:
            collapsed = True

        # Reintroduce full population at REINTRO_CYCLE
        if cycle == REINTRO_CYCLE:
            # Clear any remaining agents
            for lvl in range(n_levels):
                for a in reality.get_population_agents(lvl):
                    reality.remove_agent(a.agent_id, lvl)

            # Full reintroduction
            for lvl in range(n_levels):
                for i in range(INITIAL[lvl]):
                    agent_id = f"R{lvl}_{i}"
                    e = 1.0 + lvl * 0.5
                    reality.add_agent(FractalAgent(agent_id, lvl, e), lvl)
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

    runtime = time.time() - start_time

    finals = {}
    for i in range(n_levels):
        if len(histories[i]) > 10:
            finals[i] = np.mean(histories[i][-10:])
        else:
            finals[i] = 0

    coexist = all(finals[i] >= 0.5 for i in range(n_levels))

    return {
        "seed": seed,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "collapsed": collapsed,
        "coexist": bool(coexist),
        "runtime": runtime,
        "n_recordings": len(histories[0])
    }


def main():
    print("=" * 80)
    print(f"CYCLE 350: FULL REINTRODUCTION TEST")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"K: {K_COLLAPSE} → {K_RECOVERY} at cycle {REINTRO_CYCLE}")
    print("=" * 80)
    print()

    results = []
    total = len(SEEDS)

    for exp_num, seed in enumerate(SEEDS, 1):
        print(f"[{exp_num}/{total}] seed={seed}", end=" ")

        try:
            result = run_experiment(seed, CYCLES)
            results.append(result)
            status = "RECOVER" if result["coexist"] else "FAIL"
            l0_final = result["finals"]["L0"]
            collapsed = "Y" if result["collapsed"] else "N"
            print(f"→ {status}, collapsed={collapsed}, L0={l0_final:.0f}")

        except Exception as e:
            print(f"✗ FAILED: {e}")

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    coexist_count = sum(1 for r in results if r["coexist"])
    collapsed_count = sum(1 for r in results if r["collapsed"])
    print(f"\nCollapsed first: {collapsed_count}/{len(results)}")
    print(f"Recovery success: {coexist_count}/{len(results)} ({coexist_count/len(results)*100:.0f}%)")

    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "k_collapse": K_COLLAPSE,
        "k_recovery": K_RECOVERY,
        "reintro_cycle": REINTRO_CYCLE,
        "n_seeds": len(SEEDS),
        "recovery_rate": coexist_count / len(results) if results else 0,
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c350_full_reintro_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C350 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
