#!/usr/bin/env python3
"""
CYCLE 300: PREDATOR EFFICIENCY EVOLUTION

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether predator handling time evolves under selection.

Research Question:
  Does selection on handling time lead to optimization or destabilization?

Background:
  C298: Type II stabilizes via handling time
  C292-C294: Evolution and coevolution dynamics
  C300: Combine - evolving predator efficiency

Design:
  - Predators have heritable handling time
  - Higher efficiency (lower h) → more prey → more offspring
  - But lower h → less satiation → potential destabilization
  - Test selection on h
  - 3 seeds
  - Total: 6 experiments (evolving vs fixed)
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C300"
CYCLE_NAME = "Predator Efficiency Evolution"
MODE = "PREDATOR_EVOLUTION"

CYCLES = 40000
N_POPULATIONS = 2
INITIAL_PREY = 200
INITIAL_PREDATOR = 30

# Prey parameters
PREY_F_INTRA = 0.08
PREY_K = 500
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Predator parameters
BASE_ATTACK_RATE = 0.01
PRED_E_CONSUME = 0.3
PRED_E_PER_PREY = 0.5
PRED_CONVERSION = 0.3

# Evolution parameters
INITIAL_H = 0.02  # Starting handling time (stable in C298)
MUTATION_RATE = 0.2
MUTATION_STD = 0.002
SELECTION_STRENGTH = 1.0

# Test conditions
CONDITIONS = [
    {"name": "fixed_h", "evolving": False},
    {"name": "evolving_h", "evolving": True}
]
SEEDS = [700, 701, 702]


def run_experiment(condition: dict, seed: int, cycles: int) -> dict:
    """Run predator evolution experiment."""

    label = condition["name"]
    evolving = condition["evolving"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c300_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Track handling time per predator
    predator_h = {}

    # Initialize prey
    for i in range(INITIAL_PREY):
        agent = FractalAgent(
            agent_id=f"prey_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    # Initialize predators with handling time
    for i in range(INITIAL_PREDATOR):
        agent = FractalAgent(
            agent_id=f"pred_{i}",
            population_id=1,
            energy=1.5
        )
        reality.add_agent(agent, population_id=1)
        predator_h[agent.agent_id] = INITIAL_H

    MAX_POP = 3000
    prey_history = []
    pred_history = []
    h_history = []

    start_time = time.time()

    for cycle in range(cycles):
        prey_agents = reality.get_population_agents(0)
        pred_agents = reality.get_population_agents(1)
        n_prey = len(prey_agents)
        n_pred = len(pred_agents)

        if n_prey + n_pred >= MAX_POP:
            break

        # PREDATION with individual handling times
        predator_energy_gain = {a.agent_id: 0.0 for a in pred_agents}
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed = []

        for pred in pred_agents:
            if n_prey > 0 and len(prey_ids) > len(prey_consumed):
                available_prey = len(prey_ids) - len(prey_consumed)

                # Get this predator's handling time
                h = predator_h.get(pred.agent_id, INITIAL_H)

                # Type II with individual h
                if h > 0 and available_prey > 0:
                    effective_rate = (BASE_ATTACK_RATE * available_prey) / \
                                   (1 + BASE_ATTACK_RATE * h * available_prey)
                else:
                    effective_rate = BASE_ATTACK_RATE * available_prey

                encounters = np.random.poisson(effective_rate)

                for _ in range(min(encounters, available_prey)):
                    remaining = [p for p in prey_ids if p not in prey_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed.append(victim)
                        predator_energy_gain[pred.agent_id] += PRED_E_PER_PREY

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
                child_id = f"prey_{cycle}_{agent.agent_id[-10:]}"
                child = FractalAgent(
                    agent_id=child_id,
                    population_id=0,
                    energy=0.5
                )
                new_prey.append(child)

        for child in new_prey:
            reality.add_agent(child, population_id=0)

        # PREDATOR REPRODUCTION with evolution
        pred_agents = reality.get_population_agents(1)
        new_preds = []

        for pred in pred_agents:
            energy_gained = predator_energy_gain.get(pred.agent_id, 0)

            if energy_gained > 0:
                f_pred = PRED_CONVERSION * energy_gained
                if np.random.random() < f_pred:
                    child_id = f"pred_{cycle}_{pred.agent_id[-10:]}"
                    child = FractalAgent(
                        agent_id=child_id,
                        population_id=1,
                        energy=0.8
                    )

                    # Inherit handling time with possible mutation
                    parent_h = predator_h.get(pred.agent_id, INITIAL_H)

                    if evolving and np.random.random() < MUTATION_RATE:
                        child_h = parent_h + np.random.normal(0, MUTATION_STD)
                        child_h = max(0.001, child_h)  # Minimum handling time
                    else:
                        child_h = parent_h

                    new_preds.append((child, child_h))

        for child, h in new_preds:
            reality.add_agent(child, population_id=1)
            predator_h[child.agent_id] = h

        # DEATH
        prey_agents = reality.get_population_agents(0)
        for agent in prey_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        pred_agents = reality.get_population_agents(1)
        for pred in pred_agents:
            energy_gained = predator_energy_gain.get(pred.agent_id, 0)
            pred.energy += energy_gained
            pred.energy -= PRED_E_CONSUME

            if pred.energy <= 0:
                reality.remove_agent(pred.agent_id, 1)
                if pred.agent_id in predator_h:
                    del predator_h[pred.agent_id]
            else:
                pred.energy = min(pred.energy, 3.0)

        # Record
        if cycle % 100 == 0:
            prey_history.append(len(reality.get_population_agents(0)))
            pred_history.append(len(reality.get_population_agents(1)))

            # Mean handling time
            pred_agents = reality.get_population_agents(1)
            if pred_agents:
                current_h = [predator_h.get(a.agent_id, INITIAL_H) for a in pred_agents]
                mean_h = np.mean(current_h)
            else:
                mean_h = INITIAL_H
            h_history.append(mean_h)

            if cycle % 10000 == 0:
                print(f"      Cycle {cycle}: prey={prey_history[-1]}, pred={pred_history[-1]}, "
                      f"h={mean_h:.4f}")

        if len(reality.get_population_agents(0)) == 0 and len(reality.get_population_agents(1)) == 0:
            break

    runtime = time.time() - start_time

    # Calculate metrics
    if len(prey_history) > 20:
        prey_init = np.mean(prey_history[:10])
        prey_final = np.mean(prey_history[-10:])
        pred_init = np.mean(pred_history[:10])
        pred_final = np.mean(pred_history[-10:])
        h_init = np.mean(h_history[:10])
        h_final = np.mean(h_history[-10:])
        h_change = h_final - h_init
    else:
        prey_init = prey_final = INITIAL_PREY
        pred_init = pred_final = INITIAL_PREDATOR
        h_init = h_final = INITIAL_H
        h_change = 0

    prey_survive = prey_final > 5
    pred_survive = pred_final > 5
    coexist = prey_survive and pred_survive

    return {
        "condition": label,
        "evolving": evolving,
        "seed": seed,
        "prey_init": float(prey_init),
        "prey_final": float(prey_final),
        "pred_init": float(pred_init),
        "pred_final": float(pred_final),
        "h_init": float(h_init),
        "h_final": float(h_final),
        "h_change": float(h_change),
        "prey_survive": bool(prey_survive),
        "pred_survive": bool(pred_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 300: PREDATOR EFFICIENCY EVOLUTION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does selection on handling time lead to optimization or destabilization?")
    print()
    print(f"Initial h: {INITIAL_H}")
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

                if result["coexist"]:
                    status = "COEXIST"
                elif result["prey_survive"]:
                    status = "PREY ONLY"
                else:
                    status = "EXTINCTION"

                h_str = f"Δh={result['h_change']:+.4f}" if result["evolving"] else "fixed"
                print(f"    → {status}, prey={result['prey_final']:.0f}, "
                      f"pred={result['pred_final']:.0f}, {h_str}")

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

    print("\nPredator Evolution Results:")
    print("-" * 80)
    print(f"{'Condition':>15} {'h_init':>10} {'h_final':>10} {'Δh':>10} {'Coexist':>10}")
    print("-" * 80)

    for cond in CONDITIONS:
        name = cond["name"]
        exp_list = by_condition[name]
        if exp_list:
            h_i = np.mean([e["h_init"] for e in exp_list])
            h_f = np.mean([e["h_final"] for e in exp_list])
            h_c = np.mean([e["h_change"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{name:>15} {h_i:>10.4f} {h_f:>10.4f} {h_c:>+10.4f} {coexist:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "n_populations": N_POPULATIONS,
            "initial_prey": INITIAL_PREY,
            "initial_predator": INITIAL_PREDATOR,
            "base_attack_rate": BASE_ATTACK_RATE,
            "initial_h": INITIAL_H,
            "mutation_rate": MUTATION_RATE,
            "mutation_std": MUTATION_STD,
            "selection_strength": SELECTION_STRENGTH,
            "conditions": CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c300_predator_evolution_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C300 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
