#!/usr/bin/env python3
"""
CYCLE 333: SQUARED ATTACK COST TEST

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test squared cost function to create strong selection pressure.

Research Question:
  Does quadratic penalty drive evolution toward lower attack?

Background:
  C328-C331: Neutral evolution (no cost)
  C332: Linear cost - no evolution
  C333: Squared cost - should create selection

Design:
  - Cost = base_cost * trait^2
  - trait=1.0 → cost=1.0×
  - trait=1.3 → cost=1.69× (30% attack, 69% cost)
  - trait=0.7 → cost=0.49× (70% attack, 49% cost)
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

CYCLE_ID = "C333"
CYCLE_NAME = "Squared Attack Cost"
MODE = "SQUARED_COST"

CYCLES = 30000
K = 600
INITIAL = [300, 30, 10, 5, 3, 2, 2]
INITIAL_TRAIT = 1.0

BASE_PARAMS = [
    {"f": 0.1, "K": K, "e_con": 0.2, "e_rech": 0.4},
    {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 0.3},
    {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 0.25},
    {"attack": 0.008, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 0.2},
    {"attack": 0.012, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 0.15},
    {"attack": 0.015, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 0.12},
    {"attack": 0.018, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 0.10}
]

MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.2

SEEDS = list(range(4000, 4020))


def run_experiment(seed: int, cycles: int) -> dict:
    """Run squared cost experiment."""

    n_levels = 7

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c333_seed{seed}.db"
    reality = RealityInterface(db_path=db_path, n_populations=n_levels, mode=MODE)
    np.random.seed(seed)

    traits = {}
    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            agent_id = f"L{lvl}_{i}"
            e = 1.0 + lvl * 0.5
            reality.add_agent(FractalAgent(agent_id, lvl, e), lvl)
            if lvl > 0:
                traits[agent_id] = INITIAL_TRAIT + np.random.uniform(-0.05, 0.05)

    histories = {i: [] for i in range(n_levels)}
    trait_histories = {i: [] for i in range(1, n_levels)}
    start_time = time.time()

    for cycle in range(cycles):
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
                        trait_mult = traits.get(pred.agent_id, 1.0)
                        attack = p["attack"] * trait_mult
                        rate = (attack * avail) / (1 + attack * p["h"] * avail)

                        for _ in range(min(np.random.poisson(rate), avail)):
                            remain = [i for i in ids if i not in consumed]
                            if remain:
                                v = np.random.choice(remain)
                                consumed.append(v)
                                gains[lvl][pred.agent_id] += p["e_gain"]

                for v in consumed:
                    reality.remove_agent(v, prey_lvl)
                    if v in traits:
                        del traits[v]

        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, BASE_PARAMS[0]["f"] * (1 - len(pops[0]) / BASE_PARAMS[0]["K"]))
            if np.random.random() < f:
                child_id = f"L0_{cycle}_{a.agent_id[-6:]}"
                reality.add_agent(FractalAgent(child_id, 0, 0.5), 0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < BASE_PARAMS[lvl]["conv"] * eg:
                    child_id = f"L{lvl}_{cycle}_{a.agent_id[-6:]}"
                    reality.add_agent(FractalAgent(child_id, lvl, 0.8), lvl)

                    parent_trait = traits.get(a.agent_id, 1.0)
                    if np.random.random() < MUTATION_RATE:
                        mutation = np.random.uniform(-MUTATION_STRENGTH, MUTATION_STRENGTH)
                        traits[child_id] = max(0.5, min(1.5, parent_trait + mutation))
                    else:
                        traits[child_id] = parent_trait

        # Death with SQUARED attack cost
        for a in reality.get_population_agents(0):
            a.energy -= BASE_PARAMS[0]["e_con"]
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + BASE_PARAMS[0]["e_rech"], 2.0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                trait_mult = traits.get(a.agent_id, 1.0)
                # SQUARED COST: e_con * trait^2
                effective_cost = BASE_PARAMS[lvl]["e_con"] * (trait_mult ** 2)
                a.energy += gains[lvl].get(a.agent_id, 0) - effective_cost
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                    if a.agent_id in traits:
                        del traits[a.agent_id]
                else:
                    a.energy = min(a.energy, 2.0 + lvl)

        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

            for lvl in range(1, n_levels):
                lvl_agents = reality.get_population_agents(lvl)
                if lvl_agents:
                    mean_trait = np.mean([traits.get(a.agent_id, 1.0) for a in lvl_agents])
                    trait_histories[lvl].append(mean_trait)
                else:
                    trait_histories[lvl].append(0)

        if all(n == 0 for n in ns[:3]):
            break

    runtime = time.time() - start_time

    finals = {}
    final_traits = {}
    for i in range(n_levels):
        if len(histories[i]) > 10:
            finals[i] = np.mean(histories[i][-10:])
        else:
            finals[i] = INITIAL[i]

    for lvl in range(1, n_levels):
        if len(trait_histories[lvl]) > 10:
            final_traits[lvl] = np.mean(trait_histories[lvl][-10:])
        else:
            final_traits[lvl] = INITIAL_TRAIT

    coexist = all(finals[i] >= 0.5 for i in range(n_levels))

    return {
        "seed": seed,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "final_traits": {f"L{i}": float(final_traits[i]) for i in range(1, n_levels)},
        "coexist": bool(coexist),
        "runtime": runtime
    }


def main():
    print("=" * 80)
    print(f"CYCLE 333: SQUARED ATTACK COST")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Starting trait: {INITIAL_TRAIT}")
    print(f"Cost model: e_con * trait^2")
    print("=" * 80)
    print()

    results = []
    total = len(SEEDS)

    for exp_num, seed in enumerate(SEEDS, 1):
        print(f"[{exp_num}/{total}] seed={seed}", end=" ")

        try:
            result = run_experiment(seed, CYCLES)
            results.append(result)
            status = "COEXIST" if result["coexist"] else "PARTIAL"
            traits_str = ", ".join(f"L{i}={result['final_traits'][f'L{i}']:.2f}" for i in range(1, 7))
            print(f"→ {status}, Traits: {traits_str}")

        except Exception as e:
            print(f"✗ FAILED: {e}")

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    coexist_count = sum(1 for r in results if r["coexist"])
    print(f"\nCoexistence: {coexist_count}/{len(results)} ({coexist_count/len(results)*100:.0f}%)")

    print(f"\nTrait evolution (start={INITIAL_TRAIT}):")
    for lvl in range(1, 7):
        coexist_results = [r for r in results if r["coexist"]]
        if coexist_results:
            mean_trait = np.mean([r["final_traits"][f"L{lvl}"] for r in coexist_results])
            change = mean_trait - INITIAL_TRAIT
            direction = "↑" if change > 0.05 else "↓" if change < -0.05 else "→"
            print(f"  L{lvl}: {mean_trait:.3f} ({change:+.3f}) {direction}")
        else:
            print(f"  L{lvl}: No coexistence")

    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "initial_trait": INITIAL_TRAIT,
        "cost_model": "e_con * trait^2",
        "n_seeds": len(SEEDS),
        "coexistence_rate": coexist_count / len(results) if results else 0,
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c333_squared_cost_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C333 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
