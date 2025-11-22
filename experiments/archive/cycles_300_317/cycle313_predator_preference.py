#!/usr/bin/env python3
"""
CYCLE 313: PREDATOR PREFERENCE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test asymmetric predation where predator prefers one prey.

Research Question:
  Does predator preference cause competitive exclusion?

Background:
  C312: Equal attack rate - equalized populations
  C313: Asymmetric attack rate - test for exclusion

Design:
  - Predator attack rate 2× higher on Prey A
  - Both prey have same K
  - 3 seeds
  - Total: 3 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C313"
CYCLE_NAME = "Predator Preference"
MODE = "PREDATOR_PREFERENCE"

CYCLES = 30000
INITIAL_PREY_A = 150
INITIAL_PREY_B = 150
INITIAL_PRED = 30

# Prey parameters (identical)
PREY_F_INTRA = 0.1
PREY_K = 300
PREY_E_CONSUME = 0.2
PREY_E_RECHARGE = 0.4

# Predator parameters
PRED_ATTACK_A = 0.006  # 2× preference for A
PRED_ATTACK_B = 0.003  # Normal for B
PRED_H = 0.02
PRED_E_CONSUME = 0.3
PRED_E_PER_PREY = 0.5
PRED_CONVERSION = 0.3

SEEDS = [2000, 2001, 2002]


def run_experiment(seed: int, cycles: int) -> dict:
    """Run predator preference experiment."""

    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c313_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=3,
        mode=MODE
    )

    np.random.seed(seed)

    # Initialize Prey A (preferred)
    for i in range(INITIAL_PREY_A):
        agent = FractalAgent(
            agent_id=f"preyA_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    # Initialize Prey B (less preferred)
    for i in range(INITIAL_PREY_B):
        agent = FractalAgent(
            agent_id=f"preyB_{i}",
            population_id=1,
            energy=1.0
        )
        reality.add_agent(agent, population_id=1)

    # Initialize predators
    for i in range(INITIAL_PRED):
        agent = FractalAgent(
            agent_id=f"pred_{i}",
            population_id=2,
            energy=1.5
        )
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

        # PREDATION ON PREY A (preferred)
        pred_energy_gain = {p.agent_id: 0.0 for p in pred_agents}
        prey_a_ids = [a.agent_id for a in prey_a_agents]
        prey_a_consumed = []

        for pred in pred_agents:
            if n_prey_a > 0:
                available_a = n_prey_a - len(prey_a_consumed)
                if PRED_H > 0 and available_a > 0:
                    effective_rate = (PRED_ATTACK_A * available_a) / \
                                   (1 + PRED_ATTACK_A * PRED_H * available_a)
                else:
                    effective_rate = PRED_ATTACK_A * available_a

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_a)):
                    remaining = [p for p in prey_a_ids if p not in prey_a_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_a_consumed.append(victim)
                        pred_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        for prey_id in prey_a_consumed:
            reality.remove_agent(prey_id, 0)

        # PREDATION ON PREY B (less preferred)
        prey_b_ids = [a.agent_id for a in prey_b_agents]
        prey_b_consumed = []

        for pred in pred_agents:
            if n_prey_b > 0:
                available_b = n_prey_b - len(prey_b_consumed)
                if PRED_H > 0 and available_b > 0:
                    effective_rate = (PRED_ATTACK_B * available_b) / \
                                   (1 + PRED_ATTACK_B * PRED_H * available_b)
                else:
                    effective_rate = PRED_ATTACK_B * available_b

                encounters = np.random.poisson(effective_rate)
                for _ in range(min(encounters, available_b)):
                    remaining = [p for p in prey_b_ids if p not in prey_b_consumed]
                    if remaining:
                        victim = np.random.choice(remaining)
                        prey_b_consumed.append(victim)
                        pred_energy_gain[pred.agent_id] += PRED_E_PER_PREY

        for prey_id in prey_b_consumed:
            reality.remove_agent(prey_id, 1)

        # PREY A REPRODUCTION
        prey_a_agents = reality.get_population_agents(0)
        n_prey_a = len(prey_a_agents)
        new_prey_a = []

        for agent in prey_a_agents:
            f_effective = PREY_F_INTRA * (1 - n_prey_a / PREY_K)
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

        # PREY B REPRODUCTION
        prey_b_agents = reality.get_population_agents(1)
        n_prey_b = len(prey_b_agents)
        new_prey_b = []

        for agent in prey_b_agents:
            f_effective = PREY_F_INTRA * (1 - n_prey_b / PREY_K)
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
        pred_agents = reality.get_population_agents(2)
        new_pred = []

        for pred in pred_agents:
            energy_gained = pred_energy_gain.get(pred.agent_id, 0)
            if energy_gained > 0:
                f_pred = PRED_CONVERSION * energy_gained
                if np.random.random() < f_pred:
                    child = FractalAgent(
                        agent_id=f"pred_{cycle}_{pred.agent_id[-8:]}",
                        population_id=2,
                        energy=0.8
                    )
                    new_pred.append(child)

        for child in new_pred:
            reality.add_agent(child, population_id=2)

        # DEATH
        prey_a_agents = reality.get_population_agents(0)
        for agent in prey_a_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        prey_b_agents = reality.get_population_agents(1)
        for agent in prey_b_agents:
            agent.energy -= PREY_E_CONSUME
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 1)
            else:
                agent.energy = min(agent.energy + PREY_E_RECHARGE, 2.0)

        pred_agents = reality.get_population_agents(2)
        for pred in pred_agents:
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
        prey_a_final = INITIAL_PREY_A
        prey_b_final = INITIAL_PREY_B
        pred_final = INITIAL_PRED

    prey_a_survive = prey_a_final > 5
    prey_b_survive = prey_b_final > 5
    pred_survive = pred_final > 5

    coexist_all = prey_a_survive and prey_b_survive and pred_survive
    exclusion = (prey_a_survive and not prey_b_survive) or (prey_b_survive and not prey_a_survive)

    return {
        "seed": seed,
        "prey_a_final": float(prey_a_final),
        "prey_b_final": float(prey_b_final),
        "pred_final": float(pred_final),
        "ratio_b_a": float(prey_b_final / prey_a_final) if prey_a_final > 0 else 0,
        "prey_a_survive": bool(prey_a_survive),
        "prey_b_survive": bool(prey_b_survive),
        "pred_survive": bool(pred_survive),
        "coexist_all": bool(coexist_all),
        "exclusion": bool(exclusion),
        "winner": "A" if prey_a_survive and not prey_b_survive else "B" if prey_b_survive and not prey_a_survive else "both" if coexist_all else "none",
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 313: PREDATOR PREFERENCE")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does predator preference cause exclusion?")
    print(f"Attack on A: {PRED_ATTACK_A} (preferred)")
    print(f"Attack on B: {PRED_ATTACK_B} (less preferred)")
    print()
    print(f"Total experiments: {len(SEEDS)}")
    print()

    results = []
    total = len(SEEDS)
    exp_num = 0

    for seed in SEEDS:
        exp_num += 1
        print(f"\n[{exp_num}/{total}] seed={seed}")

        try:
            result = run_experiment(seed, CYCLES)
            results.append(result)

            status = f"winner={result['winner']}, B/A={result['ratio_b_a']:.2f}"
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

    print("\nPredator Preference Results:")
    print("-" * 80)
    print(f"{'Seed':>10} {'Prey A':>10} {'Prey B':>10} {'B/A':>10} {'Pred':>10} {'Winner':>10}")
    print("-" * 80)

    for r in results:
        print(f"{r['seed']:>10} {r['prey_a_final']:>10.0f} {r['prey_b_final']:>10.0f} "
              f"{r['ratio_b_a']:>10.2f} {r['pred_final']:>10.0f} {r['winner']:>10}")

    # Summary stats
    avg_ratio = np.mean([r['ratio_b_a'] for r in results])
    print(f"\nAverage B/A ratio: {avg_ratio:.2f}")
    print("(Expected: >1 if preference causes exclusion of A)")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "pred_attack_a": PRED_ATTACK_A,
            "pred_attack_b": PRED_ATTACK_B,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c313_predator_preference_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C313 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
