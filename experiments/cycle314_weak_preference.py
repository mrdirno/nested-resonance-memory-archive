#!/usr/bin/env python3
"""
CYCLE 314: WEAK PREFERENCE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test weaker predator preference to find sustainable threshold.

Research Question:
  At what preference ratio can predator-prey coexist?

Background:
  C313: 2× preference - predator extinction
  C314: Test 1.5× and 1.25× preference

Design:
  - Three conditions: no pref (1×), weak (1.25×), moderate (1.5×)
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
CYCLE_ID = "C314"
CYCLE_NAME = "Weak Preference"
MODE = "WEAK_PREFERENCE"

CYCLES = 30000
INITIAL_PREY_A = 150
INITIAL_PREY_B = 150
INITIAL_PRED = 30

# Prey parameters
PREY_F_INTRA = 0.1
PREY_K = 300
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Base attack rate
BASE_ATTACK = 0.003

# Predator parameters
PRED_H = 0.02
PRED_E_CONSUME = 0.3
PRED_E_PER_PREY = 0.5
PRED_CONVERSION = 0.3

# Test conditions
CONDITIONS = [
    {"name": "no_pref_1.0x", "ratio": 1.0},
    {"name": "weak_1.25x", "ratio": 1.25},
    {"name": "moderate_1.5x", "ratio": 1.5}
]
SEEDS = [2100, 2101, 2102]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run weak preference experiment."""

    label = condition["name"]
    ratio = condition["ratio"]

    attack_a = BASE_ATTACK * ratio
    attack_b = BASE_ATTACK

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c314_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=3,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize prey
    for i in range(INITIAL_PREY_A):
        agent = FractalAgent(agent_id=f"preyA_{i}", population_id=0, energy=1.0)
        reality.add_agent(agent, population_id=0)

    for i in range(INITIAL_PREY_B):
        agent = FractalAgent(agent_id=f"preyB_{i}", population_id=1, energy=1.0)
        reality.add_agent(agent, population_id=1)

    for i in range(INITIAL_PRED):
        agent = FractalAgent(agent_id=f"pred_{i}", population_id=2, energy=1.5)
        reality.add_agent(agent, population_id=2)

    MAX_POP = 4000
    prey_a_history = []
    prey_b_history = []
    pred_history = []

    start_time = time.time()

    for cycle in range(cycles):
        prey_a_agents = reality.get_population_agents(0)
        prey_b_agents = reality.get_population_agents(1)
        pred_agents = reality.get_population_agents(2)

        n_prey_a = len(prey_a_agents)
        n_prey_b = len(prey_b_agents)
        n_pred = len(pred_agents)

        if n_prey_a + n_prey_b + n_pred >= MAX_POP:
            break

        # PREDATION ON PREY A
        pred_energy_gain = {p.agent_id: 0.0 for p in pred_agents}
        prey_a_ids = [a.agent_id for a in prey_a_agents]
        prey_a_consumed = []

        for pred in pred_agents:
            if n_prey_a > 0:
                available_a = n_prey_a - len(prey_a_consumed)
                if PRED_H > 0 and available_a > 0:
                    effective_rate = (attack_a * available_a) / (1 + attack_a * PRED_H * available_a)
                else:
                    effective_rate = attack_a * available_a

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_a)):
                    remaining = [p for p in prey_a_ids if p not in prey_a_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_a_consumed.append(victim)
                        pred_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        for prey_id in prey_a_consumed:
            reality.remove_agent(prey_id, 0)

        # PREDATION ON PREY B
        prey_b_ids = [a.agent_id for a in prey_b_agents]
        prey_b_consumed = []

        for pred in pred_agents:
            if n_prey_b > 0:
                available_b = n_prey_b - len(prey_b_consumed)
                if PRED_H > 0 and available_b > 0:
                    effective_rate = (attack_b * available_b) / (1 + attack_b * PRED_H * available_b)
                else:
                    effective_rate = attack_b * available_b

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_b)):
                    remaining = [p for p in prey_b_ids if p not in prey_b_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_b_consumed.append(victim)
                        pred_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        for prey_id in prey_b_consumed:
            reality.remove_agent(prey_id, 1)

        # REPRODUCTION
        prey_a_agents = reality.get_population_agents(0)
        n_prey_a = len(prey_a_agents)
        new_prey_a = []
        for agent in prey_a_agents:
            f_effective = max(0, PREY_F_INTRA * (1 - n_prey_a / PREY_K))
            if np.random.random() < f_effective:
                child = FractalAgent(agent_id=f"preyA_{cycle}_{agent.agent_id[-8:]}", population_id=0, energy=0.5)
                new_prey_a.append(child)
        for child in new_prey_a:
            reality.add_agent(child, population_id=0)

        prey_b_agents = reality.get_population_agents(1)
        n_prey_b = len(prey_b_agents)
        new_prey_b = []
        for agent in prey_b_agents:
            f_effective = max(0, PREY_F_INTRA * (1 - n_prey_b / PREY_K))
            if np.random.random() < f_effective:
                child = FractalAgent(agent_id=f"preyB_{cycle}_{agent.agent_id[-8:]}", population_id=1, energy=0.5)
                new_prey_b.append(child)
        for child in new_prey_b:
            reality.add_agent(child, population_id=1)

        pred_agents = reality.get_population_agents(2)
        new_pred = []
        for pred in pred_agents:
            energy_gained = pred_energy_gain.get(pred.agent_id, 0)
            if energy_gained > 0:
                f_pred = PRED_CONVERSION * energy_gained
                if np.random.random() < f_pred:
                    child = FractalAgent(agent_id=f"pred_{cycle}_{pred.agent_id[-8:]}", population_id=2, energy=0.8)
                    new_pred.append(child)
        for child in new_pred:
            reality.add_agent(child, population_id=2)

        # DEATH
        for agent in reality.get_population_agents(0):
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        for agent in reality.get_population_agents(1):
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 1)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        for pred in reality.get_population_agents(2):
            energy_gained = pred_energy_gain.get(pred.agent_id, 0)
            pred.energy += energy_gained
            pred.energy -= PRED_E_CONSUME
            if pred.energy <= 0:
                reality.remove_agent(pred.agent_id, 2)
            else:
                pred.energy = min(pred.energy, 3.0)

        # Record
        if cycle % 100 == 0:
            current_a = len(reality.get_population_agents(0))
            current_b = len(reality.get_population_agents(1))
            current_pred = len(reality.get_population_agents(2))
            prey_a_history.append(current_a)
            prey_b_history.append(current_b)
            pred_history.append(current_pred)

            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: preyA={current_a}, preyB={current_b}, pred={current_pred}")

        if n_prey_a == 0 and n_prey_b == 0 and n_pred == 0:
            break

    runtime = time.time() - start_time

    # Metrics
    if len(prey_a_history) > 10:
        prey_a_final = np.mean(prey_a_history[-10:])
        prey_b_final = np.mean(prey_b_history[-10:])
        pred_final = np.mean(pred_history[-10:])
    else:
        prey_a_final = INITIAL_PREY_A
        prey_b_final = INITIAL_PREY_B
        pred_final = INITIAL_PRED

    coexist = prey_a_final > 5 and prey_b_final > 5 and pred_final > 5

    return {
        "condition": label,
        "ratio": ratio,
        "seed": seed,
        "prey_a_final": float(prey_a_final),
        "prey_b_final": float(prey_b_final),
        "pred_final": float(pred_final),
        "ratio_b_a": float(prey_b_final / prey_a_final) if prey_a_final > 0 else 0,
        "coexist": bool(coexist),
        "runtime_seconds": runtime
    }


def main():
    print("=" * 80)
    print(f"CYCLE 314: WEAK PREFERENCE")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: At what preference can predator survive?")
    print(f"Base attack: {BASE_ATTACK}")
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
                print(f"    → {status}, A={result['prey_a_final']:.0f}, B={result['prey_b_final']:.0f}, "
                      f"pred={result['pred_final']:.0f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_condition = defaultdict(list)
    for r in results:
        by_condition[r["condition"]].append(r)

    print("\nWeak Preference Results:")
    print("-" * 80)
    print(f"{'Condition':>15} {'Prey A':>10} {'Prey B':>10} {'Pred':>10} {'Coexist':>10}")
    print("-" * 80)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            a = np.mean([e["prey_a_final"] for e in exp_list])
            b = np.mean([e["prey_b_final"] for e in exp_list])
            pred = np.mean([e["pred_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)
            print(f"{name:>15} {a:>10.0f} {b:>10.0f} {pred:>10.0f} {coexist:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {"base_attack": BASE_ATTACK, "conditions": CONDITIONS, "seeds": SEEDS},
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c314_weak_preference_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C314 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
