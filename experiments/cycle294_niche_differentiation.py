#!/usr/bin/env python3
"""
CYCLE 294: NICHE DIFFERENTIATION

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether resource partitioning enables stable coevolution.

Research Question:
  Can niche differentiation prevent evolutionary exclusion?

Background:
  C293: Global K + coevolution → arms race → exclusion
  C294: Local K + coevolution → stable coexistence?

Design:
  - 2 populations, both evolving
  - Local vs global K
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
CYCLE_ID = "C294"
CYCLE_NAME = "Niche Differentiation"
MODE = "NICHE_COEVOLUTION"

CYCLES = 25000
N_POPULATIONS = 2
INITIAL_AGENTS_PER_POP = 50
BASE_F_INTRA = 0.005
MUTATION_RATE = 0.1
MUTATION_STD = 0.001
SELECTION = 1.0

# Energy
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Competition
DENSITY_FACTOR = 0.1
K = 500

# Test conditions
COMPETITION_MODES = [
    {"name": "global_K", "mode": "global"},
    {"name": "local_K", "mode": "local"}
]
SEEDS = [100, 101, 102]


def run_experiment(competition: dict, seed: int, cycles: int) -> dict:
    """Run niche differentiation experiment."""

    label = competition["name"]
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c294_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)
    mode = competition["mode"]

    # Agent fitness tracking
    agent_fitness = {0: {}, 1: {}}

    # Initialize
    for pop_id in range(N_POPULATIONS):
        for i in range(INITIAL_AGENTS_PER_POP):
            fitness = BASE_F_INTRA + np.random.normal(0, MUTATION_STD * 5)
            fitness = max(0.001, fitness)

            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{i}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)
            agent_fitness[pop_id][agent.agent_id] = fitness

    MAX_POP_PER = 3000
    fitness_history = {0: [], 1: []}
    pop_history = {0: [], 1: []}

    start_time = time.time()

    for cycle in range(cycles):
        pop_sizes = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
        total_pop = sum(pop_sizes)

        if any(p >= MAX_POP_PER for p in pop_sizes):
            break

        # SPAWN with evolution
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if agent.agent_id not in agent_fitness[pop_id]:
                    continue

                parent_fitness = agent_fitness[pop_id][agent.agent_id]
                f_effective = BASE_F_INTRA + SELECTION * (parent_fitness - BASE_F_INTRA)
                f_effective = max(0, f_effective)

                if np.random.random() < f_effective:
                    if np.random.random() < MUTATION_RATE:
                        child_fitness = parent_fitness + np.random.normal(0, MUTATION_STD)
                    else:
                        child_fitness = parent_fitness

                    child_fitness = max(0.001, child_fitness)
                    child_id = f"spawn_{cycle}_{pop_id}_{agent.agent_id}"
                    child = FractalAgent(
                        agent_id=child_id,
                        population_id=pop_id,
                        energy=SPAWN_ENERGY
                    )
                    new_spawns.append((child, child_fitness))

            for child, fitness in new_spawns:
                reality.add_agent(child, population_id=pop_id)
                agent_fitness[pop_id][child.agent_id] = fitness

        # DEATH
        pop_sizes = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
        total_pop = sum(pop_sizes)

        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                    if agent.agent_id in agent_fitness[pop_id]:
                        del agent_fitness[pop_id][agent.agent_id]
                else:
                    # Local vs global K
                    if mode == "global":
                        death_prob = DENSITY_FACTOR * (total_pop / K)
                    else:  # local
                        death_prob = DENSITY_FACTOR * (pop_sizes[pop_id] / K)

                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        if agent.agent_id in agent_fitness[pop_id]:
                            del agent_fitness[pop_id][agent.agent_id]
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(N_POPULATIONS):
                current_agents = reality.get_population_agents(pop_id)
                pop_history[pop_id].append(len(current_agents))

                if agent_fitness[pop_id]:
                    living = [agent_fitness[pop_id][a.agent_id] for a in current_agents if a.agent_id in agent_fitness[pop_id]]
                    mean_f = np.mean(living) if living else BASE_F_INTRA
                else:
                    mean_f = BASE_F_INTRA
                fitness_history[pop_id].append(mean_f)

            if cycle % 5000 == 0:
                pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
                fs = [fitness_history[p][-1] for p in range(N_POPULATIONS)]
                print(f"      Cycle {cycle}: pop={pops}, f={[f'{f:.4f}' for f in fs]}")

        if all(len(reality.get_population_agents(p)) == 0 for p in range(N_POPULATIONS)):
            break

    runtime = time.time() - start_time

    # Calculate metrics
    results = {}
    for pop_id in range(N_POPULATIONS):
        if len(fitness_history[pop_id]) > 10:
            init_f = np.mean(fitness_history[pop_id][:10])
            final_f = np.mean(fitness_history[pop_id][-10:])
            init_pop = np.mean(pop_history[pop_id][:10])
            final_pop = np.mean(pop_history[pop_id][-10:])
        else:
            init_f = final_f = BASE_F_INTRA
            init_pop = final_pop = 0

        results[f"pop{pop_id}_init_f"] = float(init_f)
        results[f"pop{pop_id}_final_f"] = float(final_f)
        results[f"pop{pop_id}_final_pop"] = float(final_pop)

    # Coexistence check
    coexist = results["pop0_final_pop"] > 5 and results["pop1_final_pop"] > 5

    return {
        "competition": competition["name"],
        "seed": seed,
        "coexist": bool(coexist),
        **results,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 294: NICHE DIFFERENTIATION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Can niche differentiation prevent evolutionary exclusion?")
    print()
    print(f"Conditions: {[c['name'] for c in COMPETITION_MODES]}")
    print(f"Total experiments: {len(COMPETITION_MODES) * len(SEEDS)}")
    print()

    results = []
    total = len(COMPETITION_MODES) * len(SEEDS)
    exp_num = 0

    for competition in COMPETITION_MODES:
        print(f"\n{'='*60}")
        print(f"Mode: {competition['name']}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {competition['name']}, seed={seed}")

            try:
                result = run_experiment(competition, seed, CYCLES)
                results.append(result)

                status = "COEXIST" if result["coexist"] else "EXCLUSION"
                print(f"    → {status}, "
                      f"f0={result['pop0_final_f']:.4f}, f1={result['pop1_final_f']:.4f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_mode = defaultdict(list)
    for r in results:
        by_mode[r["competition"]].append(r)

    print("\nNiche Differentiation vs Coevolution:")
    print("-" * 70)
    print(f"{'Mode':>12} {'P0 Final f':>12} {'P1 Final f':>12} {'Coexist':>10}")
    print("-" * 70)

    for mode in COMPETITION_MODES:
        name = mode["name"]
        exp_list = by_mode[name]
        f0 = np.mean([e["pop0_final_f"] for e in exp_list])
        f1 = np.mean([e["pop1_final_f"] for e in exp_list])
        coexist = sum(1 for e in exp_list if e["coexist"]) / len(exp_list)

        print(f"{name:>12} {f0:>12.4f} {f1:>12.4f} {coexist:>10.0%}")

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
            "mutation_rate": MUTATION_RATE,
            "mutation_std": MUTATION_STD,
            "selection": SELECTION,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "competition_modes": COMPETITION_MODES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c294_niche_differentiation_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C294 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
