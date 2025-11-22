#!/usr/bin/env python3
"""
CYCLE 296: SPATIAL REFUGE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether spatial refuge (predator-free zones) stabilizes predator-prey dynamics.

Research Question:
  Can spatial refuge prevent predator-prey collapse?

Background:
  C295: Predator-prey coexistence only at intermediate attack rates
  C296: Can spatial structure (refuge) expand the coexistence parameter space?

Design:
  - Prey have access to refuge zone (proportion)
  - Predators can only attack prey outside refuge
  - Test refuge fractions with challenging attack rate
  - 3 seeds per condition
  - Total: 15 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C296"
CYCLE_NAME = "Spatial Refuge"
MODE = "SPATIAL_REFUGE"

CYCLES = 30000
N_POPULATIONS = 2  # 0=prey, 1=predator
INITIAL_PREY = 200
INITIAL_PREDATOR = 20

# Prey parameters
PREY_F_INTRA = 0.08
PREY_K = 500
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Predator parameters
PRED_E_CONSUME = 0.3
PRED_E_PER_PREY = 0.5
PRED_CONVERSION = 0.3

# Use high attack rate that caused collapse in C295
ATTACK_RATE = 0.01

# Test conditions - refuge fraction
REFUGE_FRACTIONS = [0.0, 0.1, 0.2, 0.3, 0.5]
SEEDS = [300, 301, 302]


def run_experiment(refuge_fraction: float, seed: int, cycles: int) -> dict:
    """Run spatial refuge experiment."""

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c296_refuge{refuge_fraction}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
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

    # Initialize predators
    for i in range(INITIAL_PREDATOR):
        agent = FractalAgent(
            agent_id=f"pred_{i}",
            population_id=1,
            energy=1.5
        )
        reality.add_agent(agent, population_id=1)

    MAX_POP = 3000
    prey_history = []
    pred_history = []

    start_time = time.time()

    for cycle in range(cycles):
        prey_agents = reality.get_population_agents(0)
        pred_agents = reality.get_population_agents(1)
        n_prey = len(prey_agents)
        n_pred = len(pred_agents)

        if n_prey + n_pred >= MAX_POP:
            break

        # PREDATION with refuge
        predator_energy_gain = {a.agent_id: 0.0 for a in pred_agents}
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed = []

        # Calculate prey outside refuge (available to predators)
        n_outside_refuge = int(n_prey * (1 - refuge_fraction))

        for pred in pred_agents:
            if n_outside_refuge > 0 and len(prey_ids) > len(prey_consumed):
                # Only encounter prey outside refuge
                available_prey = max(0, n_outside_refuge - len(prey_consumed))
                encounters = np.random.poisson(ATTACK_RATE * available_prey)

                for _ in range(min(encounters, available_prey)):
                    remaining = [p for p in prey_ids if p not in prey_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed.append(victim)
                        predator_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        # Remove consumed prey
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

        # PREDATOR REPRODUCTION
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
                    new_preds.append(child)

        for child in new_preds:
            reality.add_agent(child, population_id=1)

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
            else:
                pred.energy = min(pred.energy, 3.0)

        # Record
        if cycle % 100 == 0:
            prey_history.append(len(reality.get_population_agents(0)))
            pred_history.append(len(reality.get_population_agents(1)))

            if cycle % 5000 == 0:
                print(f"      Cycle {cycle}: prey={prey_history[-1]}, pred={pred_history[-1]}")

        if len(reality.get_population_agents(0)) == 0 and len(reality.get_population_agents(1)) == 0:
            break

    runtime = time.time() - start_time

    # Calculate metrics
    if len(prey_history) > 20:
        prey_init = np.mean(prey_history[:10])
        prey_final = np.mean(prey_history[-10:])
        pred_init = np.mean(pred_history[:10])
        pred_final = np.mean(pred_history[-10:])

        prey_cv = np.std(prey_history) / np.mean(prey_history) if np.mean(prey_history) > 0 else 0
        pred_cv = np.std(pred_history) / np.mean(pred_history) if np.mean(pred_history) > 0 else 0
    else:
        prey_init = prey_final = INITIAL_PREY
        pred_init = pred_final = INITIAL_PREDATOR
        prey_cv = pred_cv = 0

    prey_survive = prey_final > 5
    pred_survive = pred_final > 5
    coexist = prey_survive and pred_survive

    return {
        "refuge_fraction": refuge_fraction,
        "seed": seed,
        "prey_init": float(prey_init),
        "prey_final": float(prey_final),
        "pred_init": float(pred_init),
        "pred_final": float(pred_final),
        "prey_cv": float(prey_cv),
        "pred_cv": float(pred_cv),
        "prey_survive": bool(prey_survive),
        "pred_survive": bool(pred_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 296: SPATIAL REFUGE")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Can spatial refuge prevent predator-prey collapse?")
    print()
    print(f"Attack rate: {ATTACK_RATE} (collapsed in C295)")
    print(f"Refuge fractions: {REFUGE_FRACTIONS}")
    print(f"Total experiments: {len(REFUGE_FRACTIONS) * len(SEEDS)}")
    print()

    results = []
    total = len(REFUGE_FRACTIONS) * len(SEEDS)
    exp_num = 0

    for refuge in REFUGE_FRACTIONS:
        print(f"\n{'='*60}")
        print(f"Refuge Fraction: {refuge:.0%}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] refuge={refuge:.0%}, seed={seed}")

            try:
                result = run_experiment(refuge, seed, CYCLES)
                results.append(result)

                if result["coexist"]:
                    status = "COEXIST"
                elif result["prey_survive"]:
                    status = "PREY ONLY"
                elif result["pred_survive"]:
                    status = "PRED ONLY"
                else:
                    status = "EXTINCTION"

                print(f"    → {status}, prey={result['prey_final']:.0f}, "
                      f"pred={result['pred_final']:.0f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_refuge = defaultdict(list)
    for r in results:
        by_refuge[r["refuge_fraction"]].append(r)

    print("\nSpatial Refuge Effects:")
    print("-" * 80)
    print(f"{'Refuge':>10} {'Prey Final':>12} {'Pred Final':>12} {'Coexist':>10}")
    print("-" * 80)

    for refuge in REFUGE_FRACTIONS:
        exp_list = by_refuge[refuge]
        if exp_list:
            prey_f = np.mean([e["prey_final"] for e in exp_list])
            pred_f = np.mean([e["pred_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{refuge:>10.0%} {prey_f:>12.1f} {pred_f:>12.1f} {coexist:>10.0%}")

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
            "prey_f_intra": PREY_F_INTRA,
            "prey_k": PREY_K,
            "attack_rate": ATTACK_RATE,
            "refuge_fractions": REFUGE_FRACTIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c296_spatial_refuge_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C296 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
