#!/usr/bin/env python3
"""
CYCLE 298: TYPE II FUNCTIONAL RESPONSE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether Type II functional response (predator satiation) stabilizes dynamics.

Research Question:
  Does handling time limitation prevent overexploitation and stabilize coexistence?

Background:
  C295-C297: Predator-prey dynamics highly sensitive to attack rate
  Type II: Consumption rate saturates at high prey density (Holling disk equation)

  Attack rate becomes: a * N / (1 + a * h * N)
  where:
    a = base attack rate
    h = handling time per prey
    N = prey density

Design:
  - Compare Type I (linear) vs Type II (saturating) functional response
  - Test at high attack rate (0.01) that previously caused collapse
  - 3 seeds per condition
  - Total: 12 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C298"
CYCLE_NAME = "Type II Functional Response"
MODE = "TYPE_II_RESPONSE"

CYCLES = 30000
N_POPULATIONS = 2
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

# Base attack rate (high - caused collapse in Type I)
BASE_ATTACK_RATE = 0.01

# Test conditions - functional response type
RESPONSE_TYPES = [
    {"name": "type_I", "handling_time": 0.0},
    {"name": "type_II_low", "handling_time": 0.005},
    {"name": "type_II_mid", "handling_time": 0.01},
    {"name": "type_II_high", "handling_time": 0.02}
]
SEEDS = [500, 501, 502]


def run_experiment(response: dict, seed: int, cycles: int) -> dict:
    """Run Type II functional response experiment."""

    label = response["name"]
    handling_time = response["handling_time"]

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c298_{label}_seed{seed}.db"

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

        # PREDATION with functional response
        predator_energy_gain = {a.agent_id: 0.0 for a in pred_agents}
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed = []

        for pred in pred_agents:
            if n_prey > 0 and len(prey_ids) > len(prey_consumed):
                available_prey = len(prey_ids) - len(prey_consumed)

                # Type II functional response
                # Effective attack rate = a * N / (1 + a * h * N)
                if handling_time > 0:
                    effective_rate = (BASE_ATTACK_RATE * available_prey) / \
                                   (1 + BASE_ATTACK_RATE * handling_time * available_prey)
                else:
                    # Type I: linear
                    effective_rate = BASE_ATTACK_RATE * available_prey

                # Number of encounters (Poisson)
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
        "response_type": label,
        "handling_time": handling_time,
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
    print(f"CYCLE 298: TYPE II FUNCTIONAL RESPONSE")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does predator satiation prevent overexploitation?")
    print()
    print(f"Base attack rate: {BASE_ATTACK_RATE} (high - caused collapse in Type I)")
    print(f"Response types: {[r['name'] for r in RESPONSE_TYPES]}")
    print(f"Total experiments: {len(RESPONSE_TYPES) * len(SEEDS)}")
    print()

    results = []
    total = len(RESPONSE_TYPES) * len(SEEDS)
    exp_num = 0

    for response in RESPONSE_TYPES:
        print(f"\n{'='*60}")
        print(f"Response Type: {response['name']} (h={response['handling_time']})")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {response['name']}, seed={seed}")

            try:
                result = run_experiment(response, seed, CYCLES)
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
    by_response = defaultdict(list)
    for r in results:
        by_response[r["response_type"]].append(r)

    print("\nType II Functional Response Effects:")
    print("-" * 80)
    print(f"{'Response':>15} {'Handling':>10} {'Prey Final':>12} {'Pred Final':>12} {'Coexist':>10}")
    print("-" * 80)

    for response in RESPONSE_TYPES:
        name = response["name"]
        h = response["handling_time"]
        exp_list = by_response[name]
        if exp_list:
            prey_f = np.mean([e["prey_final"] for e in exp_list])
            pred_f = np.mean([e["pred_final"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{name:>15} {h:>10.3f} {prey_f:>12.1f} {pred_f:>12.1f} {coexist:>10.0%}")

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
            "base_attack_rate": BASE_ATTACK_RATE,
            "response_types": RESPONSE_TYPES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c298_type_ii_response_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C298 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
