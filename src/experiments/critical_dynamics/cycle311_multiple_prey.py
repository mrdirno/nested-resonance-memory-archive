#!/usr/bin/env python3
"""
CYCLE 311: MULTIPLE PREY SPECIES

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test horizontal diversity - two prey species.

Research Question:
  Does having multiple prey species stabilize or destabilize the predator?

Background:
  C304: Single prey species - 100% stable
  C311: Two prey species - test apparent competition

Design:
  - Two prey species with shared predator
  - Identical parameters between prey
  - Compare one vs two prey species
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
CYCLE_ID = "C311"
CYCLE_NAME = "Multiple Prey Species"
MODE = "MULTIPLE_PREY"

CYCLES = 30000
INITIAL_PREY_A = 150
INITIAL_PREY_B = 150
INITIAL_PRED = 30

# Prey A parameters
PREY_A_F_INTRA = 0.1
PREY_A_K = 300
PREY_A_E_CONSUME = 0.2
PREY_A_E_RECHARGE = 0.4

# Prey B parameters (identical)
PREY_B_F_INTRA = 0.1
PREY_B_K = 300
PREY_B_E_CONSUME = 0.2
PREY_B_E_RECHARGE = 0.4

# Predator parameters
PRED_ATTACK_RATE = 0.003
PRED_H = 0.02
PRED_E_CONSUME = 0.3
PRED_E_PER_PREY = 0.5
PRED_CONVERSION = 0.3

# Test conditions
CONDITIONS = [
    {"name": "one_prey", "two_prey": False, "n_pops": 2},
    {"name": "two_prey", "two_prey": True, "n_pops": 3}
]
SEEDS = [1800, 1801, 1802]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run multiple prey experiment."""

    label = condition["name"]
    two_prey = condition["two_prey"]
    n_pops = condition["n_pops"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c311_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=n_pops,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize Prey A
    initial_a = INITIAL_PREY_A if two_prey else INITIAL_PREY_A * 2
    for i in range(initial_a):
        agent = FractalAgent(
            agent_id=f"preyA_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    # Initialize Prey B (if two_prey)
    if two_prey:
        for i in range(INITIAL_PREY_B):
            agent = FractalAgent(
                agent_id=f"preyB_{i}",
                population_id=1,
                energy=1.0
            )
            reality.add_agent(agent, population_id=1)
        pred_pop = 2
    else:
        pred_pop = 1

    # Initialize predators
    for i in range(INITIAL_PRED):
        agent = FractalAgent(
            agent_id=f"pred_{i}",
            population_id=pred_pop,
            energy=1.5
        )
        reality.add_agent(agent, population_id=pred_pop)

    MAX_POP = 4000
    prey_a_history = []
    prey_b_history = []
    pred_history = []

    start_time = time.time()

    for cycle in range(cycles):
        prey_a_agents = reality.get_population_agents(0)
        prey_b_agents = reality.get_population_agents(1) if two_prey else []
        pred_agents = reality.get_population_agents(pred_pop)

        n_prey_a = len(prey_a_agents)
        n_prey_b = len(prey_b_agents)
        n_pred = len(pred_agents)
        n_total_prey = n_prey_a + n_prey_b

        if n_prey_a + n_prey_b + n_pred >= MAX_POP:
            break

        # PREDATION
        pred_energy_gain = {p.agent_id: 0.0 for p in pred_agents}

        # Combine prey pools
        all_prey_ids = [a.agent_id for a in prey_a_agents]
        if two_prey:
            all_prey_ids += [a.agent_id for a in prey_b_agents]

        prey_consumed = []

        for pred in pred_agents:
            if n_total_prey > 0:
                available_prey = n_total_prey - len(prey_consumed)
                if PRED_H > 0 and available_prey > 0:
                    effective_rate = (PRED_ATTACK_RATE * available_prey) / \
                                   (1 + PRED_ATTACK_RATE * PRED_H * available_prey)
                else:
                    effective_rate = PRED_ATTACK_RATE * available_prey

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_prey)):
                    remaining = [p for p in all_prey_ids if p not in prey_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed.append(victim)
                        pred_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        # Remove consumed prey
        for prey_id in prey_consumed:
            if prey_id.startswith("preyA"):
                reality.remove_agent(prey_id, 0)
            elif prey_id.startswith("preyB"):
                reality.remove_agent(prey_id, 1)

        # PREY A REPRODUCTION
        prey_a_agents = reality.get_population_agents(0)
        n_prey_a = len(prey_a_agents)
        k_a = PREY_A_K if two_prey else PREY_A_K * 2
        new_prey_a = []

        for agent in prey_a_agents:
            f_effective = PREY_A_F_INTRA * (1 - n_prey_a / k_a)
            f_effective = max(0, f_effective)
            if np.random.random() < f_effective:
                child = FractalAgent(
                    agent_id=f"preyA_{cycle}_{agent.agent_id[-8:]}",
                    population_id=0,
                    energy=0.5
                )
                new_prey_a.append(child)

        for child in new_prey_a:
            reality.add_agent(child, population_id=0)

        # PREY B REPRODUCTION (if two_prey)
        if two_prey:
            prey_b_agents = reality.get_population_agents(1)
            n_prey_b = len(prey_b_agents)
            new_prey_b = []

            for agent in prey_b_agents:
                f_effective = PREY_B_F_INTRA * (1 - n_prey_b / PREY_B_K)
                f_effective = max(0, f_effective)
                if np.random.random() < f_effective:
                    child = FractalAgent(
                        agent_id=f"preyB_{cycle}_{agent.agent_id[-8:]}",
                        population_id=1,
                        energy=0.5
                    )
                    new_prey_b.append(child)

            for child in new_prey_b:
                reality.add_agent(child, population_id=1)

        # PREDATOR REPRODUCTION
        pred_agents = reality.get_population_agents(pred_pop)
        new_pred = []

        for pred in pred_agents:
            energy_gained = pred_energy_gain.get(pred.agent_id, 0)
            if energy_gained > 0:
                f_pred = PRED_CONVERSION * energy_gained
                if np.random.random() < f_pred:
                    child = FractalAgent(
                        agent_id=f"pred_{cycle}_{pred.agent_id[-8:]}",
                        population_id=pred_pop,
                        energy=0.8
                    )
                    new_pred.append(child)

        for child in new_pred:
            reality.add_agent(child, population_id=pred_pop)

        # DEATH
        # Prey A
        prey_a_agents = reality.get_population_agents(0)
        for agent in prey_a_agents:
            agent.energy -= PREY_A_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_A_E_RECHARGE, 2.0)

        # Prey B
        if two_prey:
            prey_b_agents = reality.get_population_agents(1)
            for agent in prey_b_agents:
                agent.energy -= PREY_B_E_CONSUME
                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, 1)
                else:
                    agent.energy = min(agent.energy + PREY_B_E_RECHARGE, 2.0)

        # Predators
        pred_agents = reality.get_population_agents(pred_pop)
        for pred in pred_agents:
            energy_gained = pred_energy_gain.get(pred.agent_id, 0)
            pred.energy += energy_gained
            pred.energy -= PRED_E_CONSUME
            if pred.energy <= 0:
                reality.remove_agent(pred.agent_id, pred_pop)
            else:
                pred.energy = min(pred.energy, 3.0)

        # Record
        if cycle % 100 == 0:
            current_a = len(reality.get_population_agents(0))
            current_b = len(reality.get_population_agents(1)) if two_prey else 0
            current_pred = len(reality.get_population_agents(pred_pop))

            prey_a_history.append(current_a)
            prey_b_history.append(current_b)
            pred_history.append(current_pred)

            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: preyA={current_a}, preyB={current_b}, "
                      f"pred={current_pred}")

        if n_prey_a == 0 and n_prey_b == 0 and n_pred == 0:
            break

    runtime = time.time() - start_time

    # Metrics
    if len(prey_a_history) > 10:
        prey_a_final = np.mean(prey_a_history[-10:])
        prey_b_final = np.mean(prey_b_history[-10:])
        pred_final = np.mean(pred_history[-10:])
    else:
        prey_a_final = initial_a
        prey_b_final = INITIAL_PREY_B if two_prey else 0
        pred_final = INITIAL_PRED

    prey_a_survive = prey_a_final > 5
    prey_b_survive = prey_b_final > 5 if two_prey else True
    pred_survive = pred_final > 5

    if two_prey:
        coexist = prey_a_survive and prey_b_survive and pred_survive
    else:
        coexist = prey_a_survive and pred_survive

    return {
        "condition": label,
        "two_prey": two_prey,
        "seed": seed,
        "prey_a_final": float(prey_a_final),
        "prey_b_final": float(prey_b_final),
        "pred_final": float(pred_final),
        "total_prey": float(prey_a_final + prey_b_final),
        "prey_a_survive": bool(prey_a_survive),
        "prey_b_survive": bool(prey_b_survive),
        "pred_survive": bool(pred_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 311: MULTIPLE PREY SPECIES")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does multiple prey stabilize predator?")
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
                print(f"    → {status}, preyA={result['prey_a_final']:.0f}, "
                      f"preyB={result['prey_b_final']:.0f}, pred={result['pred_final']:.0f}")

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

    print("\nMultiple Prey Results:")
    print("-" * 80)
    print(f"{'Condition':>12} {'Prey A':>10} {'Prey B':>10} {'Total':>10} {'Pred':>10} {'Coexist':>10}")
    print("-" * 80)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            prey_a = np.mean([e["prey_a_final"] for e in exp_list])
            prey_b = np.mean([e["prey_b_final"] for e in exp_list])
            total_prey = np.mean([e["total_prey"] for e in exp_list])
            pred_f = np.mean([e["pred_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{name:>12} {prey_a:>10.0f} {prey_b:>10.0f} {total_prey:>10.0f} {pred_f:>10.0f} {coexist:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "initial_prey_a": INITIAL_PREY_A,
            "initial_prey_b": INITIAL_PREY_B,
            "initial_pred": INITIAL_PRED,
            "conditions": CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c311_multiple_prey_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C311 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
