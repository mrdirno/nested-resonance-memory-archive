#!/usr/bin/env python3
"""
CYCLE 295 V2: PREDATOR-PREY DYNAMICS (CORRECTED)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test predator-prey dynamics with proper starvation mechanics.

Research Question:
  Do predator-prey systems produce stable cycles or oscillatory collapse?

V2 Corrections:
  - Predators require prey for energy (no passive recharge)
  - Predators starve without prey consumption
  - Energy dynamics properly coupled to trophic interactions

Design:
  - 2 populations: prey (pop0) and predator (pop1)
  - Predator energy comes ONLY from prey consumption
  - Test different attack rates
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
CYCLE_ID = "C295_V2"
CYCLE_NAME = "Predator-Prey Dynamics (Corrected)"
MODE = "PREDATOR_PREY_V2"

CYCLES = 30000
N_POPULATIONS = 2  # 0=prey, 1=predator
INITIAL_PREY = 200
INITIAL_PREDATOR = 20

# Prey parameters
PREY_F_INTRA = 0.08  # Reproduction rate
PREY_K = 500  # Carrying capacity
PREY_E_CONSUME = 0.2  # Prey metabolism
PREY_E_RECHARGE = 0.4  # Prey recharge (from resources)

# Predator parameters
PRED_E_CONSUME = 0.3  # Predator metabolism (higher)
PRED_E_PER_PREY = 0.5  # Energy gain per prey (must offset metabolism)
PRED_CONVERSION = 0.3  # Reproduction efficiency
# NOTE: Predators get NO passive recharge - must eat to survive

# Test conditions - attack rate
ATTACK_RATES = [0.001, 0.002, 0.005, 0.01]
SEEDS = [200, 201, 202]


def run_experiment(attack_rate: float, seed: int, cycles: int) -> dict:
    """Run predator-prey experiment with proper starvation."""

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c295v2_attack{attack_rate}_seed{seed}.db"

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
            energy=1.5  # Start with some buffer
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

        # PREDATION
        predator_energy_gain = {a.agent_id: 0.0 for a in pred_agents}
        prey_ids = [a.agent_id for a in prey_agents]
        prey_consumed = []

        for pred in pred_agents:
            if n_prey > 0 and len(prey_ids) > len(prey_consumed):
                # Encounter probability based on prey density
                available_prey = len(prey_ids) - len(prey_consumed)
                encounters = np.random.poisson(attack_rate * available_prey)

                for _ in range(min(encounters, available_prey)):
                    # Select random prey not yet consumed
                    remaining = [p for p in prey_ids if p not in prey_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_consumed.append(victim)
                        predator_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        # Remove consumed prey
        for prey_id in prey_consumed:
            reality.remove_agent(prey_id, 0)

        # PREY REPRODUCTION (logistic growth)
        prey_agents = reality.get_population_agents(0)
        n_prey = len(prey_agents)
        new_prey = []

        for agent in prey_agents:
            # Density-dependent reproduction
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

        # PREDATOR REPRODUCTION (depends on prey consumption)
        pred_agents = reality.get_population_agents(1)
        new_preds = []

        for pred in pred_agents:
            energy_gained = predator_energy_gain.get(pred.agent_id, 0)

            # Reproduction only if enough energy
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

        # DEATH - Energy consumption
        # Prey: consume and recharge
        prey_agents = reality.get_population_agents(0)
        for agent in prey_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        # Predators: consume but recharge ONLY from prey
        pred_agents = reality.get_population_agents(1)
        for pred in pred_agents:
            # Add energy from prey consumption
            energy_gained = predator_energy_gain.get(pred.agent_id, 0)
            pred.energy += energy_gained

            # Metabolism cost
            pred.energy -= PRED_E_CONSUME

            # Die if out of energy
            if pred.energy <= 0:
                reality.remove_agent(pred.agent_id, 1)
            else:
                # Cap energy
                pred.energy = min(pred.energy, 3.0)

        # Record
        if cycle % 100 == 0:
            prey_history.append(len(reality.get_population_agents(0)))
            pred_history.append(len(reality.get_population_agents(1)))

            if cycle % 5000 == 0:
                print(f"      Cycle {cycle}: prey={prey_history[-1]}, pred={pred_history[-1]}")

        # Check for total extinction
        if len(reality.get_population_agents(0)) == 0 and len(reality.get_population_agents(1)) == 0:
            break

    runtime = time.time() - start_time

    # Calculate metrics
    if len(prey_history) > 20:
        prey_init = np.mean(prey_history[:10])
        prey_final = np.mean(prey_history[-10:])
        pred_init = np.mean(pred_history[:10])
        pred_final = np.mean(pred_history[-10:])

        # Oscillation detection
        prey_cv = np.std(prey_history) / np.mean(prey_history) if np.mean(prey_history) > 0 else 0
        pred_cv = np.std(pred_history) / np.mean(pred_history) if np.mean(pred_history) > 0 else 0

        # Peak detection
        prey_peaks = 0
        for i in range(1, len(prey_history) - 1):
            if prey_history[i] > prey_history[i-1] and prey_history[i] > prey_history[i+1]:
                if prey_history[i] > 20:  # Significant peaks only
                    prey_peaks += 1
    else:
        prey_init = prey_final = INITIAL_PREY
        pred_init = pred_final = INITIAL_PREDATOR
        prey_cv = pred_cv = 0
        prey_peaks = 0

    # Coexistence check
    prey_survive = prey_final > 5
    pred_survive = pred_final > 5
    coexist = prey_survive and pred_survive

    return {
        "attack_rate": attack_rate,
        "seed": seed,
        "prey_init": float(prey_init),
        "prey_final": float(prey_final),
        "pred_init": float(pred_init),
        "pred_final": float(pred_final),
        "prey_cv": float(prey_cv),
        "pred_cv": float(pred_cv),
        "prey_peaks": int(prey_peaks),
        "prey_survive": bool(prey_survive),
        "pred_survive": bool(pred_survive),
        "coexist": bool(coexist),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 295 V2: PREDATOR-PREY DYNAMICS (CORRECTED)")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Do predator-prey systems produce stable cycles or collapse?")
    print()
    print("V2 Correction: Predators require prey for energy (proper starvation)")
    print()
    print(f"Attack rates: {ATTACK_RATES}")
    print(f"Total experiments: {len(ATTACK_RATES) * len(SEEDS)}")
    print()

    results = []
    total = len(ATTACK_RATES) * len(SEEDS)
    exp_num = 0

    for attack_rate in ATTACK_RATES:
        print(f"\n{'='*60}")
        print(f"Attack Rate: {attack_rate}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] attack={attack_rate}, seed={seed}")

            try:
                result = run_experiment(attack_rate, seed, CYCLES)
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
                      f"pred={result['pred_final']:.0f}, peaks={result['prey_peaks']}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_attack = defaultdict(list)
    for r in results:
        by_attack[r["attack_rate"]].append(r)

    print("\nPredator-Prey Dynamics by Attack Rate:")
    print("-" * 80)
    print(f"{'Attack':>10} {'Prey Final':>12} {'Pred Final':>12} {'Peaks':>8} {'Coexist':>10}")
    print("-" * 80)

    for attack in ATTACK_RATES:
        exp_list = by_attack[attack]
        if exp_list:
            prey_f = np.mean([e["prey_final"] for e in exp_list])
            pred_f = np.mean([e["pred_final"] for e in exp_list])
            peaks = np.mean([e["prey_peaks"] for e in exp_list])
            coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

            print(f"{attack:>10} {prey_f:>12.1f} {pred_f:>12.1f} {peaks:>8.1f} {coexist:>10.0%}")

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
            "prey_e_consume": PREY_E_CONSUME,
            "prey_e_recharge": PREY_E_RECHARGE,
            "pred_e_consume": PRED_E_CONSUME,
            "pred_e_per_prey": PRED_E_PER_PREY,
            "pred_conversion": PRED_CONVERSION,
            "attack_rates": ATTACK_RATES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c295v2_predator_prey_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C295 V2 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
