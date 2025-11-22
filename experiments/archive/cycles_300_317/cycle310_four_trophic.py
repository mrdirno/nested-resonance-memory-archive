#!/usr/bin/env python3
"""
CYCLE 310: FOUR-TROPHIC CHAIN

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test four-level food chain (quaternary consumer).

Research Question:
  Can four trophic levels coexist stably?

Background:
  C304: Stable tri-trophic (100%)
  C310: Extend to four levels

Design:
  - 4 populations: prey, meso, top, apex
  - Compare three- vs four-trophic
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
CYCLE_ID = "C310"
CYCLE_NAME = "Four-Trophic Chain"
MODE = "FOUR_TROPHIC"

CYCLES = 30000
INITIAL_PREY = 300
INITIAL_MESO = 30
INITIAL_TOP = 10
INITIAL_APEX = 5

# Prey parameters
PREY_F_INTRA = 0.1
PREY_K = 600
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Mesopredator parameters
MESO_ATTACK_PREY = 0.003
MESO_H = 0.02
MESO_E_CONSUME = 0.3
MESO_E_PER_PREY = 0.5
MESO_CONVERSION = 0.3

# Top predator parameters
TOP_ATTACK_MESO = 0.005
TOP_H = 0.03
TOP_E_CONSUME = 0.4
TOP_E_PER_MESO = 0.6
TOP_CONVERSION = 0.25

# Apex predator parameters
APEX_ATTACK_TOP = 0.008
APEX_H = 0.04
APEX_E_CONSUME = 0.5
APEX_E_PER_TOP = 0.8
APEX_CONVERSION = 0.2

# Test conditions
CONDITIONS = [
    {"name": "three_trophic", "include_apex": False, "n_pops": 3},
    {"name": "four_trophic", "include_apex": True, "n_pops": 4}
]
SEEDS = [1700, 1701, 1702]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run four-trophic experiment."""

    label = condition["name"]
    include_apex = condition["include_apex"]
    n_pops = condition["n_pops"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c310_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=n_pops,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize prey
    for i in range(INITIAL_PREY):
        agent = FractalAgent(
            agent_id=f"prey_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    # Initialize mesopredators
    for i in range(INITIAL_MESO):
        agent = FractalAgent(
            agent_id=f"meso_{i}",
            population_id=1,
            energy=1.5
        )
        reality.add_agent(agent, population_id=1)

    # Initialize top predators
    for i in range(INITIAL_TOP):
        agent = FractalAgent(
            agent_id=f"top_{i}",
            population_id=2,
            energy=2.0
        )
        reality.add_agent(agent, population_id=2)

    # Initialize apex predators
    if include_apex:
        for i in range(INITIAL_APEX):
            agent = FractalAgent(
                agent_id=f"apex_{i}",
                population_id=3,
                energy=2.5
            )
            reality.add_agent(agent, population_id=3)

    MAX_POP = 4000
    prey_history = []
    meso_history = []
    top_history = []
    apex_history = []

    start_time = time.time()

    for cycle in range(cycles):
        prey_agents = reality.get_population_agents(0)
        meso_agents = reality.get_population_agents(1)
        top_agents = reality.get_population_agents(2)
        apex_agents = reality.get_population_agents(3) if include_apex else []

        n_prey = len(prey_agents)
        n_meso = len(meso_agents)
        n_top = len(top_agents)
        n_apex = len(apex_agents)

        if n_prey + n_meso + n_top + n_apex >= MAX_POP:
            break

        # APEX PREDATION ON TOP
        apex_energy_gain = {}
        top_ids = [a.agent_id for a in top_agents]
        top_consumed = []

        if include_apex:
            for apex in apex_agents:
                apex_energy_gain[apex.agent_id] = 0.0
                if n_top > 0:
                    available_top = n_top - len(top_consumed)
                    if APEX_H > 0 and available_top > 0:
                        effective_rate = (APEX_ATTACK_TOP * available_top) / \
                                       (1 + APEX_ATTACK_TOP * APEX_H * available_top)
                    else:
                        effective_rate = APEX_ATTACK_TOP * available_top

                    encounters = np.random.poisson(effective_rate)
                    for _ in range(min(encounters, available_top)):
                        remaining = [t for t in top_ids if t not in top_consumed]
                        if remaining:
                            victim = np.random.choice(remaining)
                            top_consumed.append(victim)
                            apex_energy_gain[apex.agent_id] += APEX_E_PER_TOP

            for top_id in top_consumed:
                reality.remove_agent(top_id, 2)

        # TOP PREDATION ON MESO
        top_agents = reality.get_population_agents(2)
        top_energy_gain = {t.agent_id: 0.0 for t in top_agents}
        meso_ids = [a.agent_id for a in meso_agents]
        meso_consumed = []

        for top in top_agents:
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

        # MESO PREDATION ON PREY
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

        # REPRODUCTION
        # Prey
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

        # Meso
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

        # Top
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

        # Apex
        if include_apex:
            apex_agents = reality.get_population_agents(3)
            new_apex = []

            for apex in apex_agents:
                energy_gained = apex_energy_gain.get(apex.agent_id, 0)
                if energy_gained > 0:
                    f_apex = APEX_CONVERSION * energy_gained
                    if np.random.random() < f_apex:
                        child = FractalAgent(
                            agent_id=f"apex_{cycle}_{apex.agent_id[-8:]}",
                            population_id=3,
                            energy=1.2
                        )
                        new_apex.append(child)

            for child in new_apex:
                reality.add_agent(child, population_id=3)

        # DEATH
        # Prey
        prey_agents = reality.get_population_agents(0)
        for agent in prey_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        # Meso
        meso_agents = reality.get_population_agents(1)
        for meso in meso_agents:
            energy_gained = meso_energy_gain.get(meso.agent_id, 0)
            meso.energy += energy_gained
            meso.energy -= MESO_E_CONSUME
            if meso.energy <= 0:
                reality.remove_agent(meso.agent_id, 1)
            else:
                meso.energy = min(meso.energy, 3.0)

        # Top
        top_agents = reality.get_population_agents(2)
        for top in top_agents:
            energy_gained = top_energy_gain.get(top.agent_id, 0)
            top.energy += energy_gained
            top.energy -= TOP_E_CONSUME
            if top.energy <= 0:
                reality.remove_agent(top.agent_id, 2)
            else:
                top.energy = min(top.energy, 4.0)

        # Apex
        if include_apex:
            apex_agents = reality.get_population_agents(3)
            for apex in apex_agents:
                energy_gained = apex_energy_gain.get(apex.agent_id, 0)
                apex.energy += energy_gained
                apex.energy -= APEX_E_CONSUME
                if apex.energy <= 0:
                    reality.remove_agent(apex.agent_id, 3)
                else:
                    apex.energy = min(apex.energy, 5.0)

        # Record
        if cycle % 100 == 0:
            current_prey = len(reality.get_population_agents(0))
            current_meso = len(reality.get_population_agents(1))
            current_top = len(reality.get_population_agents(2))
            current_apex = len(reality.get_population_agents(3)) if include_apex else 0

            prey_history.append(current_prey)
            meso_history.append(current_meso)
            top_history.append(current_top)
            apex_history.append(current_apex)

            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: prey={current_prey}, meso={current_meso}, "
                      f"top={current_top}, apex={current_apex}")

        if n_prey == 0 and n_meso == 0 and n_top == 0:
            break

    runtime = time.time() - start_time

    # Metrics
    if len(prey_history) > 10:
        prey_final = np.mean(prey_history[-10:])
        meso_final = np.mean(meso_history[-10:])
        top_final = np.mean(top_history[-10:])
        apex_final = np.mean(apex_history[-10:])
    else:
        prey_final = INITIAL_PREY
        meso_final = INITIAL_MESO
        top_final = INITIAL_TOP
        apex_final = INITIAL_APEX if include_apex else 0

    prey_survive = prey_final > 5
    meso_survive = meso_final > 5
    top_survive = top_final > 5
    apex_survive = apex_final > 3 if include_apex else True

    if include_apex:
        coexist = prey_survive and meso_survive and top_survive and apex_survive
    else:
        coexist = prey_survive and meso_survive and top_survive

    return {
        "condition": label,
        "include_apex": include_apex,
        "seed": seed,
        "prey_final": float(prey_final),
        "meso_final": float(meso_final),
        "top_final": float(top_final),
        "apex_final": float(apex_final),
        "prey_survive": bool(prey_survive),
        "meso_survive": bool(meso_survive),
        "top_survive": bool(top_survive),
        "apex_survive": bool(apex_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 310: FOUR-TROPHIC CHAIN")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Can four trophic levels coexist?")
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

                status = "COEXIST" if result["coexist"] else "PARTIAL"
                print(f"    → {status}, prey={result['prey_final']:.0f}, "
                      f"meso={result['meso_final']:.0f}, top={result['top_final']:.0f}, "
                      f"apex={result['apex_final']:.0f}")

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

    print("\nFour-Trophic Results:")
    print("-" * 90)
    print(f"{'Condition':>15} {'Prey':>8} {'Meso':>8} {'Top':>8} {'Apex':>8} {'Coexist':>10}")
    print("-" * 90)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            prey_f = np.mean([e["prey_final"] for e in exp_list])
            meso_f = np.mean([e["meso_final"] for e in exp_list])
            top_f = np.mean([e["top_final"] for e in exp_list])
            apex_f = np.mean([e["apex_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{name:>15} {prey_f:>8.0f} {meso_f:>8.0f} {top_f:>8.0f} {apex_f:>8.0f} {coexist:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "initial_prey": INITIAL_PREY,
            "initial_meso": INITIAL_MESO,
            "initial_top": INITIAL_TOP,
            "initial_apex": INITIAL_APEX,
            "conditions": CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c310_four_trophic_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C310 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
