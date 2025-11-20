#!/usr/bin/env python3
"""
CYCLE 307: TUNED CASCADE PARAMETERS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Find parameter regime that creates trophic cascade.

Research Question:
  What parameters create cascade-prone (but stable) tri-trophic system?

Background:
  C305: Optimal attack (0.003) - no cascade, inherently stable
  C306: High attack (0.008) - system collapses before cascade
  C307: Intermediate attack (0.005) with strong top-down control

Design:
  - Mesopredator attack = 0.005 (between optimal and collapse)
  - Strong top predator control to suppress meso
  - Compare control vs removal
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
CYCLE_ID = "C307"
CYCLE_NAME = "Tuned Cascade Parameters"
MODE = "CASCADE_TUNED"

CYCLES = 30000
REMOVAL_CYCLE = 15000
INITIAL_PREY = 300
INITIAL_MESO = 30
INITIAL_TOP = 15  # More top predators for strong control

# Prey parameters
PREY_F_INTRA = 0.1
PREY_K = 600
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Mesopredator parameters - INTERMEDIATE
MESO_ATTACK_PREY = 0.005  # Between optimal (0.003) and collapse (0.008)
MESO_H = 0.02
MESO_E_CONSUME = 0.25  # Slightly lower metabolism for survival
MESO_E_PER_PREY = 0.5
MESO_CONVERSION = 0.25

# Top predator parameters - STRONG CONTROL
TOP_ATTACK_MESO = 0.015  # Very strong predation on meso
TOP_H = 0.02
TOP_E_CONSUME = 0.35
TOP_E_PER_MESO = 0.7
TOP_CONVERSION = 0.3

# Test conditions
CONDITIONS = [
    {"name": "control", "remove_top": False},
    {"name": "removal", "remove_top": True}
]
SEEDS = [1400, 1401, 1402]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run tuned cascade experiment."""

    label = condition["name"]
    remove_top = condition["remove_top"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c307_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=3,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize populations
    for i in range(INITIAL_PREY):
        agent = FractalAgent(
            agent_id=f"prey_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    for i in range(INITIAL_MESO):
        agent = FractalAgent(
            agent_id=f"meso_{i}",
            population_id=1,
            energy=1.5
        )
        reality.add_agent(agent, population_id=1)

    for i in range(INITIAL_TOP):
        agent = FractalAgent(
            agent_id=f"top_{i}",
            population_id=2,
            energy=2.0
        )
        reality.add_agent(agent, population_id=2)

    MAX_POP = 4000
    prey_history = []
    meso_history = []
    top_history = []

    pre_removal_prey = []
    pre_removal_meso = []
    post_removal_prey = []
    post_removal_meso = []

    start_time = time.time()
    top_removed = False

    for cycle in range(cycles):
        if remove_top and cycle == REMOVAL_CYCLE and not top_removed:
            top_agents = reality.get_population_agents(2)
            for top in top_agents:
                reality.remove_agent(top.agent_id, 2)
            top_removed = True
            print(f"      *** TOP PREDATOR REMOVED at cycle {cycle} ***")

        prey_agents = reality.get_population_agents(0)
        meso_agents = reality.get_population_agents(1)
        top_agents = reality.get_population_agents(2)

        n_prey = len(prey_agents)
        n_meso = len(meso_agents)
        n_top = len(top_agents)

        if n_prey + n_meso + n_top >= MAX_POP:
            break

        # TOP PREDATOR PREDATION
        top_energy_gain = {}
        meso_ids = [a.agent_id for a in meso_agents]
        meso_consumed = []

        for top in top_agents:
            top_energy_gain[top.agent_id] = 0.0
            if n_meso > 0:
                available_meso = n_meso - len(meso_consumed)
                if TOP_H > 0 and available_meso > 0:
                    effective_rate = (TOP_ATTACK_MESO * available_meso) / \
                                   (1 + TOP_ATTACK_MESO * TOP_H * available_meso)
                else:
                    effective_rate = TOP_ATTACK_MESO * available_meso

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_meso)):
                    remaining = [m for m in meso_ids if m not in meso_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        meso_consumed.append(victim)
                        top_energy_gain[top.agent_id] += TOP_E_PER_MESO

        for meso_id in meso_consumed:
            reality.remove_agent(meso_id, 1)

        # MESOPREDATOR PREDATION
        meso_agents = reality.get_population_agents(1)
        meso_energy_gain = {a.agent_id: 0.0 for a in meso_agents}
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed = []

        for meso in meso_agents:
            if n_prey > 0:
                available_prey = n_prey - len(prey_consumed)
                if MESO_H > 0 and available_prey > 0:
                    effective_rate = (MESO_ATTACK_PREY * available_prey) / \
                                   (1 + MESO_ATTACK_PREY * MESO_H * available_prey)
                else:
                    effective_rate = MESO_ATTACK_PREY * available_prey

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_prey)):
                    remaining = [p for p in prey_ids if p not in prey_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed.append(victim)
                        meso_energy_gain[meso.agent_id] += MESO_E_PER_PREY

        for prey_id in prey_consumed:
            reality.remove_agent(prey_id, 0)

        # PREY REPRODUCTION
        prey_agents = reality.get_population_agents(0)
        n_prey = len(prey_agents)
        new_prey = []

        for agent in prey_agents:
            f_effective = PREY_F_INTRA * (1 - n_prey / PREY_K)
            f_effective = max(0, f_effective)
            if np.random.random() < f_effective:
                child = FractalAgent(
                    agent_id=f"prey_{cycle}_{agent.agent_id[-8:]}",
                    population_id=0,
                    energy=0.5
                )
                new_prey.append(child)

        for child in new_prey:
            reality.add_agent(child, population_id=0)

        # MESOPREDATOR REPRODUCTION
        meso_agents = reality.get_population_agents(1)
        new_meso = []

        for meso in meso_agents:
            energy_gained = meso_energy_gain.get(meso.agent_id, 0)
            if energy_gained > 0:
                f_meso = MESO_CONVERSION * energy_gained
                if np.random.random() < f_meso:
                    child = FractalAgent(
                        agent_id=f"meso_{cycle}_{meso.agent_id[-8:]}",
                        population_id=1,
                        energy=0.8
                    )
                    new_meso.append(child)

        for child in new_meso:
            reality.add_agent(child, population_id=1)

        # TOP PREDATOR REPRODUCTION
        top_agents = reality.get_population_agents(2)
        new_top = []

        for top in top_agents:
            energy_gained = top_energy_gain.get(top.agent_id, 0)
            if energy_gained > 0:
                f_top = TOP_CONVERSION * energy_gained
                if np.random.random() < f_top:
                    child = FractalAgent(
                        agent_id=f"top_{cycle}_{top.agent_id[-8:]}",
                        population_id=2,
                        energy=1.0
                    )
                    new_top.append(child)

        for child in new_top:
            reality.add_agent(child, population_id=2)

        # DEATH
        prey_agents = reality.get_population_agents(0)
        for agent in prey_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        meso_agents = reality.get_population_agents(1)
        for meso in meso_agents:
            energy_gained = meso_energy_gain.get(meso.agent_id, 0)
            meso.energy += energy_gained
            meso.energy -= MESO_E_CONSUME
            if meso.energy <= 0:
                reality.remove_agent(meso.agent_id, 1)
            else:
                meso.energy = min(meso.energy, 3.0)

        top_agents = reality.get_population_agents(2)
        for top in top_agents:
            energy_gained = top_energy_gain.get(top.agent_id, 0)
            top.energy += energy_gained
            top.energy -= TOP_E_CONSUME
            if top.energy <= 0:
                reality.remove_agent(top.agent_id, 2)
            else:
                top.energy = min(top.energy, 4.0)

        # Record
        if cycle % 100 == 0:
            current_prey = len(reality.get_population_agents(0))
            current_meso = len(reality.get_population_agents(1))
            current_top = len(reality.get_population_agents(2))

            prey_history.append(current_prey)
            meso_history.append(current_meso)
            top_history.append(current_top)

            if cycle < REMOVAL_CYCLE:
                pre_removal_prey.append(current_prey)
                pre_removal_meso.append(current_meso)
            else:
                post_removal_prey.append(current_prey)
                post_removal_meso.append(current_meso)

            if cycle % 5000 == 0:
                print(f"      Cycle {cycle}: prey={current_prey}, "
                      f"meso={current_meso}, top={current_top}")

        if n_prey == 0 and n_meso == 0:
            break

    runtime = time.time() - start_time

    # Metrics
    if len(pre_removal_prey) >= 50:
        pre_prey_eq = np.mean(pre_removal_prey[-50:])
        pre_meso_eq = np.mean(pre_removal_meso[-50:])
    else:
        pre_prey_eq = np.mean(pre_removal_prey) if pre_removal_prey else INITIAL_PREY
        pre_meso_eq = np.mean(pre_removal_meso) if pre_removal_meso else INITIAL_MESO

    if len(post_removal_prey) >= 50:
        post_prey_eq = np.mean(post_removal_prey[-50:])
        post_meso_eq = np.mean(post_removal_meso[-50:])
    else:
        post_prey_eq = np.mean(post_removal_prey) if post_removal_prey else 0
        post_meso_eq = np.mean(post_removal_meso) if post_removal_meso else 0

    # Cascade detection with different thresholds
    meso_increase = post_meso_eq / pre_meso_eq if pre_meso_eq > 0 else 0
    prey_decrease = post_prey_eq / pre_prey_eq if pre_prey_eq > 0 else 0

    meso_release = meso_increase > 1.5  # 50% increase
    prey_crash = prey_decrease < 0.5   # 50% decrease
    cascade = meso_release and prey_crash

    if len(prey_history) > 10:
        prey_final = np.mean(prey_history[-10:])
        meso_final = np.mean(meso_history[-10:])
        top_final = np.mean(top_history[-10:])
    else:
        prey_final = 0
        meso_final = 0
        top_final = 0

    prey_survive = prey_final > 5
    meso_survive = meso_final > 5

    if remove_top:
        coexist = prey_survive and meso_survive
    else:
        top_survive = top_final > 5
        coexist = prey_survive and meso_survive and top_survive

    return {
        "condition": label,
        "remove_top": remove_top,
        "seed": seed,
        "pre_prey_eq": float(pre_prey_eq),
        "pre_meso_eq": float(pre_meso_eq),
        "post_prey_eq": float(post_prey_eq),
        "post_meso_eq": float(post_meso_eq),
        "meso_increase": float(meso_increase),
        "prey_decrease": float(prey_decrease),
        "meso_release": bool(meso_release),
        "prey_crash": bool(prey_crash),
        "cascade": bool(cascade),
        "prey_final": float(prey_final),
        "meso_final": float(meso_final),
        "top_final": float(top_final),
        "prey_survive": bool(prey_survive),
        "meso_survive": bool(meso_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 307: TUNED CASCADE PARAMETERS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: What parameters create stable cascade-prone system?")
    print(f"Meso attack: {MESO_ATTACK_PREY}, Top attack: {TOP_ATTACK_MESO}")
    print()
    print(f"Conditions: {[c['name'] for c in CONDITIONS]}")
    print(f"Total experiments: {len(CONDITIONS) * len(SEEDS)}")
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

                if result["remove_top"]:
                    status = "CASCADE" if result["cascade"] else "NO CASCADE"
                    print(f"    → {status}")
                    print(f"      Pre: prey={result['pre_prey_eq']:.0f}, meso={result['pre_meso_eq']:.0f}")
                    print(f"      Post: prey={result['post_prey_eq']:.0f}, meso={result['post_meso_eq']:.0f}")
                    print(f"      Meso×{result['meso_increase']:.2f}, Prey×{result['prey_decrease']:.2f}")
                else:
                    status = "COEXIST" if result["coexist"] else "PARTIAL"
                    print(f"    → {status}, prey={result['prey_final']:.0f}, "
                          f"meso={result['meso_final']:.0f}, top={result['top_final']:.0f}")

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
        by_condition[r["condition"]].append(r)

    print("\nTuned Cascade Results:")
    print("-" * 80)
    print(f"{'Condition':>12} {'Pre-Prey':>10} {'Post-Prey':>10} {'Pre-Meso':>10} {'Post-Meso':>10} {'Cascade':>10}")
    print("-" * 80)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            pre_prey = np.mean([e["pre_prey_eq"] for e in exp_list])
            post_prey = np.mean([e["post_prey_eq"] for e in exp_list])
            pre_meso = np.mean([e["pre_meso_eq"] for e in exp_list])
            post_meso = np.mean([e["post_meso_eq"] for e in exp_list])
            cascade = sum(1 for e in exp_list if e.get("cascade", False)) / len(exp_list)

            print(f"{name:>12} {pre_prey:>10.1f} {post_prey:>10.1f} {pre_meso:>10.1f} {post_meso:>10.1f} {cascade:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "removal_cycle": REMOVAL_CYCLE,
            "meso_attack_prey": MESO_ATTACK_PREY,
            "top_attack_meso": TOP_ATTACK_MESO,
            "conditions": CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c307_cascade_tuned_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C307 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
