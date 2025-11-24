#!/usr/bin/env python3
"""
CYCLE 284: COMPETITION DYNAMICS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Explore how populations compete for shared resources and whether
  competitive exclusion or coexistence emerges.

Research Question:
  Does competition produce extinction, coexistence, or dominance?

Design:
  - 2 populations with different fitness (f_intra values)
  - Shared carrying capacity (global density dependence)
  - 4 fitness ratios: 1.0, 1.5, 2.0, 3.0
  - 2 competition modes: local (within-pop), global (shared K)
  - 3 seeds per condition
  - Total: 24 experiments
"""

import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C284"
CYCLE_NAME = "Competition Dynamics"
MODE = "COMPETITION"

CYCLES = 30000
N_POPULATIONS = 2
INITIAL_AGENTS_PER_POP = 50
BASE_F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Test conditions
FITNESS_RATIOS = [1.0, 1.5, 2.0, 3.0]  # Pop1 f_intra = BASE * ratio
COMPETITION_MODES = [
    {"mode": "local", "label": "local_K"},     # Each pop has own K
    {"mode": "global", "label": "global_K"}    # Shared K across pops
]
GLOBAL_K = 500
DENSITY_FACTOR = 0.1
SEEDS = [100, 101, 102]


def run_experiment(fitness_ratio: float, competition_mode: dict,
                   seed: int, cycles: int) -> dict:
    """Run competition experiment."""

    label = f"ratio{fitness_ratio}_{competition_mode['label']}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c284_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Fitness values
    f_intra = [BASE_F_INTRA, BASE_F_INTRA * fitness_ratio]

    # Initialize populations
    for pop_id in range(N_POPULATIONS):
        for i in range(INITIAL_AGENTS_PER_POP):
            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{i}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)

    MAX_POP_PER = 5000
    pop_history = {p: [] for p in range(N_POPULATIONS)}

    start_time = time.time()

    for cycle in range(cycles):
        # SPAWN (per agent, different rates)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if np.random.random() < f_intra[pop_id]:
                    child = FractalAgent(
                        agent_id=f"spawn_{cycle}_{pop_id}_{agent.agent_id}",
                        population_id=pop_id,
                        energy=SPAWN_ENERGY
                    )
                    new_spawns.append(child)

            for child in new_spawns:
                reality.add_agent(child, population_id=pop_id)

        # DEATH (energy + competition-dependent)
        pop_sizes = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
        total_pop = sum(pop_sizes)

        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Competition-dependent death
                    if competition_mode["mode"] == "local":
                        # Local: each population has own K
                        death_prob = DENSITY_FACTOR * (pop_sizes[pop_id] / GLOBAL_K)
                    else:
                        # Global: shared K (true competition)
                        death_prob = DENSITY_FACTOR * (total_pop / GLOBAL_K)

                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 10000 == 0:
                pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
                print(f"      Cycle {cycle}: pop0={pops[0]}, pop1={pops[1]}")

        # Check extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
        if total == 0:
            print(f"      [ALL EXTINCT] at cycle {cycle}")
            break

        # Check cap
        if any(len(reality.get_population_agents(p)) >= MAX_POP_PER for p in range(N_POPULATIONS)):
            print(f"      [CAP] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]

    # Late-phase analysis
    outcomes = {}
    for pop_id in range(N_POPULATIONS):
        if len(pop_history[pop_id]) > 10:
            late = pop_history[pop_id][-20:]
            mean_late = np.mean(late)
            std_late = np.std(late)
        else:
            mean_late = final_pops[pop_id]
            std_late = 0

        outcomes[f"pop{pop_id}_mean"] = float(mean_late)
        outcomes[f"pop{pop_id}_std"] = float(std_late)
        outcomes[f"pop{pop_id}_extinct"] = bool(mean_late < 1)

    # Determine outcome
    if outcomes["pop0_extinct"] and outcomes["pop1_extinct"]:
        outcome_type = "MUTUAL_EXTINCTION"
    elif outcomes["pop0_extinct"]:
        outcome_type = "POP1_WINS"
    elif outcomes["pop1_extinct"]:
        outcome_type = "POP0_WINS"
    elif abs(outcomes["pop0_mean"] - outcomes["pop1_mean"]) < 5:
        outcome_type = "COEXISTENCE_EQUAL"
    else:
        outcome_type = "COEXISTENCE_UNEQUAL"

    # Dominance ratio
    if outcomes["pop0_mean"] + outcomes["pop1_mean"] > 0:
        dominance = outcomes["pop1_mean"] / (outcomes["pop0_mean"] + outcomes["pop1_mean"])
    else:
        dominance = 0.5

    return {
        "fitness_ratio": fitness_ratio,
        "competition_mode": competition_mode["label"],
        "f_intra_0": f_intra[0],
        "f_intra_1": f_intra[1],
        "seed": seed,
        "final_pops": final_pops,
        "outcome_type": outcome_type,
        "dominance": dominance,  # Fraction held by pop1
        **outcomes,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 284: COMPETITION DYNAMICS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does competition produce extinction, coexistence, or dominance?")
    print()
    print(f"Fitness ratios: {FITNESS_RATIOS}")
    print(f"Competition modes: {[c['label'] for c in COMPETITION_MODES]}")
    print(f"Total experiments: {len(FITNESS_RATIOS) * len(COMPETITION_MODES) * len(SEEDS)}")
    print()

    results = []
    total = len(FITNESS_RATIOS) * len(COMPETITION_MODES) * len(SEEDS)
    exp_num = 0

    for ratio in FITNESS_RATIOS:
        for comp_mode in COMPETITION_MODES:
            print(f"\n{'='*60}")
            print(f"Fitness ratio={ratio}, Mode={comp_mode['label']}")
            print("=" * 60)

            for seed in SEEDS:
                exp_num += 1
                print(f"\n[{exp_num}/{total}] ratio={ratio}, {comp_mode['label']}, seed={seed}")

                try:
                    result = run_experiment(ratio, comp_mode, seed, CYCLES)
                    results.append(result)

                    print(f"    → {result['outcome_type']}, "
                          f"dominance={result['dominance']:.2f}")

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
        key = (r["fitness_ratio"], r["competition_mode"])
        by_condition[key].append(r)

    print("\nCompetition Outcomes:")
    print("-" * 80)
    print(f"{'Ratio':>8} {'Mode':>12} {'Pop0 Mean':>10} {'Pop1 Mean':>10} {'Dominance':>10} {'Outcome':>20}")
    print("-" * 80)

    for (ratio, mode) in sorted(by_condition.keys()):
        exp_list = by_condition[(ratio, mode)]
        pop0_mean = np.mean([e["pop0_mean"] for e in exp_list])
        pop1_mean = np.mean([e["pop1_mean"] for e in exp_list])
        dominance = np.mean([e["dominance"] for e in exp_list])

        # Most common outcome
        outcomes = [e["outcome_type"] for e in exp_list]
        outcome = max(set(outcomes), key=outcomes.count)

        print(f"{ratio:>8.1f} {mode:>12} {pop0_mean:>10.1f} {pop1_mean:>10.1f} {dominance:>10.2f} {outcome:>20}")

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
            "initial_agents_per_pop": INITIAL_AGENTS_PER_POP,
            "base_f_intra": BASE_F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "fitness_ratios": FITNESS_RATIOS,
            "competition_modes": [c["label"] for c in COMPETITION_MODES],
            "global_K": GLOBAL_K,
            "density_factor": DENSITY_FACTOR,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c284_competition_dynamics_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C284 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
