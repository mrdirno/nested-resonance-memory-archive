#!/usr/bin/env python3
"""
CYCLE 315: FIVE-TROPHIC CHAIN

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test five-level food chain (quinternary consumer).

Research Question:
  Can five trophic levels coexist stably?

Background:
  C310: Four-trophic 100% stable
  C315: Extend to five levels

Design:
  - 5 populations: prey, meso, top, apex, hyper
  - Compare four- vs five-trophic
  - 3 seeds per condition
  - Total: 6 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C315"
CYCLE_NAME = "Five-Trophic Chain"
MODE = "FIVE_TROPHIC"

CYCLES = 30000
INITIAL_PREY = 300
INITIAL_MESO = 30
INITIAL_TOP = 10
INITIAL_APEX = 5
INITIAL_HYPER = 3

# Parameters (from C310)
PREY_F_INTRA = 0.1
PREY_K = 600
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

MESO_ATTACK = 0.003
MESO_H = 0.02
MESO_E_CONSUME = 0.3
MESO_E_GAIN = 0.5
MESO_CONV = 0.3

TOP_ATTACK = 0.005
TOP_H = 0.03
TOP_E_CONSUME = 0.4
TOP_E_GAIN = 0.6
TOP_CONV = 0.25

APEX_ATTACK = 0.008
APEX_H = 0.04
APEX_E_CONSUME = 0.5
APEX_E_GAIN = 0.8
APEX_CONV = 0.2

# Hyper predator
HYPER_ATTACK = 0.012
HYPER_H = 0.05
HYPER_E_CONSUME = 0.6
HYPER_E_GAIN = 1.0
HYPER_CONV = 0.15

CONDITIONS = [
    {"name": "four_trophic", "include_hyper": False, "n_pops": 4},
    {"name": "five_trophic", "include_hyper": True, "n_pops": 5}
]
SEEDS = [2200, 2201, 2202]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run five-trophic experiment."""

    label = condition["name"]
    include_hyper = condition["include_hyper"]
    n_pops = condition["n_pops"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c315_{label}_seed{seed}.db"

    reality = RealityInterface(db_path=db_path, n_populations=n_pops, mode=MODE)
    np.random.seed(seed)

    # Initialize
    for i in range(INITIAL_PREY):
        reality.add_agent(FractalAgent(f"prey_{i}", 0, 1.0), 0)
    for i in range(INITIAL_MESO):
        reality.add_agent(FractalAgent(f"meso_{i}", 1, 1.5), 1)
    for i in range(INITIAL_TOP):
        reality.add_agent(FractalAgent(f"top_{i}", 2, 2.0), 2)
    for i in range(INITIAL_APEX):
        reality.add_agent(FractalAgent(f"apex_{i}", 3, 2.5), 3)
    if include_hyper:
        for i in range(INITIAL_HYPER):
            reality.add_agent(FractalAgent(f"hyper_{i}", 4, 3.0), 4)

    histories = {i: [] for i in range(n_pops)}
    start_time = time.time()

    for cycle in range(cycles):
        pops = [reality.get_population_agents(i) for i in range(n_pops)]
        ns = [len(p) for p in pops]

        if sum(ns) >= 4000:
            break

        # Energy gains
        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_pops)]

        # HYPER → APEX predation
        if include_hyper and ns[3] > 0:
            ids = [a.agent_id for a in pops[3]]
            consumed = []
            for hyper in pops[4]:
                avail = ns[3] - len(consumed)
                if avail > 0:
                    rate = (HYPER_ATTACK * avail) / (1 + HYPER_ATTACK * HYPER_H * avail)
                    for _ in range(min(np.random.poisson(rate), avail)):
                        remain = [i for i in ids if i not in consumed]
                        if remain:
                            v = np.random.choice(remain)
                            consumed.append(v)
                            gains[4][hyper.agent_id] += HYPER_E_GAIN
            for v in consumed:
                reality.remove_agent(v, 3)

        # APEX → TOP
        pops[2] = reality.get_population_agents(2)
        ns[2] = len(pops[2])
        if ns[2] > 0:
            ids = [a.agent_id for a in pops[2]]
            consumed = []
            for apex in pops[3]:
                avail = ns[2] - len(consumed)
                if avail > 0:
                    rate = (APEX_ATTACK * avail) / (1 + APEX_ATTACK * APEX_H * avail)
                    for _ in range(min(np.random.poisson(rate), avail)):
                        remain = [i for i in ids if i not in consumed]
                        if remain:
                            v = np.random.choice(remain)
                            consumed.append(v)
                            gains[3][apex.agent_id] += APEX_E_GAIN
            for v in consumed:
                reality.remove_agent(v, 2)

        # TOP → MESO
        pops[1] = reality.get_population_agents(1)
        ns[1] = len(pops[1])
        if ns[1] > 0:
            ids = [a.agent_id for a in pops[1]]
            consumed = []
            for top in reality.get_population_agents(2):
                avail = ns[1] - len(consumed)
                if avail > 0:
                    rate = (TOP_ATTACK * avail) / (1 + TOP_ATTACK * TOP_H * avail)
                    for _ in range(min(np.random.poisson(rate), avail)):
                        remain = [i for i in ids if i not in consumed]
                        if remain:
                            v = np.random.choice(remain)
                            consumed.append(v)
                            gains[2][top.agent_id] += TOP_E_GAIN
            for v in consumed:
                reality.remove_agent(v, 1)

        # MESO → PREY
        pops[0] = reality.get_population_agents(0)
        ns[0] = len(pops[0])
        if ns[0] > 0:
            ids = [a.agent_id for a in pops[0]]
            consumed = []
            for meso in reality.get_population_agents(1):
                avail = ns[0] - len(consumed)
                if avail > 0:
                    rate = (MESO_ATTACK * avail) / (1 + MESO_ATTACK * MESO_H * avail)
                    for _ in range(min(np.random.poisson(rate), avail)):
                        remain = [i for i in ids if i not in consumed]
                        if remain:
                            v = np.random.choice(remain)
                            consumed.append(v)
                            gains[1][meso.agent_id] += MESO_E_GAIN
            for v in consumed:
                reality.remove_agent(v, 0)

        # REPRODUCTION
        # Prey
        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, PREY_F_INTRA * (1 - len(pops[0]) / PREY_K))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"prey_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        # Predators
        for lvl, (conv, ecap) in enumerate([(MESO_CONV, 3), (TOP_CONV, 4), (APEX_CONV, 5)], 1):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < conv * eg:
                    reality.add_agent(FractalAgent(f"p{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        if include_hyper:
            for a in reality.get_population_agents(4):
                eg = gains[4].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < HYPER_CONV * eg:
                    reality.add_agent(FractalAgent(f"hyper_{cycle}_{a.agent_id[-6:]}", 4, 1.0), 4)

        # DEATH
        for a in reality.get_population_agents(0):
            a.energy -= PREY_E_CONSUME
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + PREY_E_RECHARGE, 2.0)

        for lvl, (econ, ecap) in enumerate([(MESO_E_CONSUME, 3), (TOP_E_CONSUME, 4), (APEX_E_CONSUME, 5)], 1):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - econ
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                else:
                    a.energy = min(a.energy, ecap)

        if include_hyper:
            for a in reality.get_population_agents(4):
                a.energy += gains[4].get(a.agent_id, 0) - HYPER_E_CONSUME
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, 4)
                else:
                    a.energy = min(a.energy, 6.0)

        # Record
        if cycle % 100 == 0:
            for i in range(n_pops):
                histories[i].append(len(reality.get_population_agents(i)))
            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: " + ", ".join(f"L{i}={histories[i][-1]}" for i in range(n_pops)))

        if all(n == 0 for n in ns[:3]):
            break

    runtime = time.time() - start_time

    # Metrics
    finals = {}
    for i in range(n_pops):
        if len(histories[i]) > 10:
            finals[i] = np.mean(histories[i][-10:])
        else:
            finals[i] = [INITIAL_PREY, INITIAL_MESO, INITIAL_TOP, INITIAL_APEX, INITIAL_HYPER][i]

    coexist = all(finals[i] > (3 if i >= 3 else 5) for i in range(n_pops))

    return {
        "condition": label,
        "seed": seed,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_pops)},
        "coexist": bool(coexist),
        "runtime": runtime
    }


def main():
    print("=" * 80)
    print(f"CYCLE 315: FIVE-TROPHIC CHAIN")
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
        print(f"Condition: {condition['name']}")
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

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c315_five_trophic_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C315 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
