#!/usr/bin/env python3
"""
CYCLE 309: STRONG OMNIVORY

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test stronger omnivory where top predator competes more with mesopredator.

Research Question:
  At what level does omnivory destabilize the system?

Background:
  C308: Weak omnivory (0.001) - no effect
  C309: Test gradient of omnivory strength

Design:
  - Top predator attack on prey: 0.001, 0.002, 0.003
  - Compare across omnivory strengths
  - 3 seeds per condition
  - Total: 9 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C309"
CYCLE_NAME = "Strong Omnivory"
MODE = "STRONG_OMNIVORY"

CYCLES = 30000
INITIAL_PREY = 300
INITIAL_MESO = 30
INITIAL_TOP = 10

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

# Top predator base parameters
TOP_ATTACK_MESO = 0.005
TOP_H = 0.03
TOP_E_CONSUME = 0.4
TOP_E_PER_MESO = 0.6
TOP_E_PER_PREY = 0.3
TOP_CONVERSION = 0.25

# Test conditions - varying omnivory strength
CONDITIONS = [
    {"name": "weak_0.001", "top_attack_prey": 0.001},
    {"name": "medium_0.002", "top_attack_prey": 0.002},
    {"name": "strong_0.003", "top_attack_prey": 0.003}
]
SEEDS = [1600, 1601, 1602]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run strong omnivory experiment."""

    label = condition["name"]
    top_attack_prey = condition["top_attack_prey"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c309_{label}_seed{seed}.db"

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

    start_time = time.time()

    for cycle in range(cycles):
        prey_agents = reality.get_population_agents(0)
        meso_agents = reality.get_population_agents(1)
        top_agents = reality.get_population_agents(2)

        n_prey = len(prey_agents)
        n_meso = len(meso_agents)
        n_top = len(top_agents)

        if n_prey + n_meso + n_top >= MAX_POP:
            break

        # TOP PREDATOR PREDATION ON MESOPREDATORS
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

        # TOP PREDATOR PREDATION ON PREY (omnivory)
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed_by_top = []

        for top in top_agents:
            if n_prey > 0:
                available_prey = n_prey - len(prey_consumed_by_top)
                if TOP_H > 0 and available_prey > 0:
                    effective_rate = (top_attack_prey * available_prey) / \
                                   (1 + top_attack_prey * TOP_H * available_prey)
                else:
                    effective_rate = top_attack_prey * available_prey

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_prey)):
                    remaining = [p for p in prey_ids if p not in prey_consumed_by_top]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed_by_top.append(victim)
                        top_energy_gain[top.agent_id] += TOP_E_PER_PREY

        for prey_id in prey_consumed_by_top:
            reality.remove_agent(prey_id, 0)

        # MESOPREDATOR PREDATION ON PREY
        meso_agents = reality.get_population_agents(1)
        prey_agents = reality.get_population_agents(0)
        n_prey = len(prey_agents)

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

        # REPRODUCTION (same as before)
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

            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: prey={current_prey}, "
                      f"meso={current_meso}, top={current_top}")

        if n_prey == 0 and n_meso == 0 and n_top == 0:
            break

    runtime = time.time() - start_time

    # Metrics
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
    top_survive = top_final > 5

    coexist = prey_survive and meso_survive and top_survive

    return {
        "condition": label,
        "top_attack_prey": top_attack_prey,
        "seed": seed,
        "prey_final": float(prey_final),
        "meso_final": float(meso_final),
        "top_final": float(top_final),
        "prey_survive": bool(prey_survive),
        "meso_survive": bool(meso_survive),
        "top_survive": bool(top_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 309: STRONG OMNIVORY")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: At what level does omnivory destabilize?")
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

    print("\nStrong Omnivory Results:")
    print("-" * 80)
    print(f"{'Condition':>15} {'Prey':>10} {'Meso':>10} {'Top':>10} {'Coexist':>10}")
    print("-" * 80)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            prey_f = np.mean([e["prey_final"] for e in exp_list])
            meso_f = np.mean([e["meso_final"] for e in exp_list])
            top_f = np.mean([e["top_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{name:>15} {prey_f:>10.1f} {meso_f:>10.1f} {top_f:>10.1f} {coexist:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "top_attack_meso": TOP_ATTACK_MESO,
            "conditions": CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c309_strong_omnivory_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C309 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
