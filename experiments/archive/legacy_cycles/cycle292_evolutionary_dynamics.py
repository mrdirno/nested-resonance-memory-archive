#!/usr/bin/env python3
"""
CYCLE 292: EVOLUTIONARY DYNAMICS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether natural selection produces evolutionary change in NRM.

Research Question:
  Does fitness-based selection lead to adaptation?

Design:
  - Agents have heritable fitness (f_intra varies by agent)
  - Offspring inherit parent fitness with mutation
  - Track mean fitness over time
  - 4 selection strengths: 0 (neutral), 0.5, 1.0, 2.0
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
CYCLE_ID = "C292"
CYCLE_NAME = "Evolutionary Dynamics"
MODE = "EVOLUTION"

CYCLES = 20000
N_POPULATIONS = 1
INITIAL_AGENTS = 100
BASE_F_INTRA = 0.005
MUTATION_RATE = 0.1
MUTATION_STD = 0.001

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Density dependence
DENSITY_FACTOR = 0.1
K = 500

# Selection strength: how much fitness affects reproduction
# f_effective = base + selection * (agent_fitness - base)
SELECTION_STRENGTHS = [0.0, 0.5, 1.0, 2.0]
SEEDS = [100, 101, 102]


def run_experiment(selection: float, seed: int, cycles: int) -> dict:
    """Run evolutionary dynamics experiment."""

    label = f"sel{selection}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c292_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Agent fitness tracking
    agent_fitness = {}

    # Initialize with variation
    for i in range(INITIAL_AGENTS):
        fitness = BASE_F_INTRA + np.random.normal(0, MUTATION_STD * 5)
        fitness = max(0.001, fitness)  # Minimum fitness

        agent = FractalAgent(
            agent_id=f"agent_0_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)
        agent_fitness[agent.agent_id] = fitness

    MAX_POPULATION = 5000
    fitness_history = []
    pop_history = []

    start_time = time.time()

    for cycle in range(cycles):
        agents = reality.get_population_agents(0)
        current_pop = len(agents)

        if current_pop >= MAX_POPULATION:
            break

        # SPAWN with selection
        new_spawns = []
        for agent in agents:
            if agent.agent_id not in agent_fitness:
                continue

            parent_fitness = agent_fitness[agent.agent_id]

            # Selection: higher fitness → higher reproduction
            if selection > 0:
                f_effective = BASE_F_INTRA + selection * (parent_fitness - BASE_F_INTRA)
            else:
                f_effective = BASE_F_INTRA  # Neutral: all same rate

            f_effective = max(0, f_effective)

            if np.random.random() < f_effective:
                # Offspring inherits fitness with mutation
                if np.random.random() < MUTATION_RATE:
                    child_fitness = parent_fitness + np.random.normal(0, MUTATION_STD)
                else:
                    child_fitness = parent_fitness

                child_fitness = max(0.001, child_fitness)

                child_id = f"spawn_{cycle}_{agent.agent_id}"
                child = FractalAgent(
                    agent_id=child_id,
                    population_id=0,
                    energy=SPAWN_ENERGY
                )
                new_spawns.append((child, child_fitness))

        for child, fitness in new_spawns:
            reality.add_agent(child, population_id=0)
            agent_fitness[child.agent_id] = fitness

        # DEATH
        agents = reality.get_population_agents(0)
        pop_size = len(agents)

        for agent in agents:
            agent.energy -= E_CONSUME

            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                if agent.agent_id in agent_fitness:
                    del agent_fitness[agent.agent_id]
            else:
                death_prob = DENSITY_FACTOR * (pop_size / K)
                if np.random.random() < death_prob:
                    reality.remove_agent(agent.agent_id, 0)
                    if agent.agent_id in agent_fitness:
                        del agent_fitness[agent.agent_id]
                    continue

                agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            current_agents = reality.get_population_agents(0)
            current_pop = len(current_agents)
            pop_history.append(current_pop)

            # Mean fitness
            if agent_fitness:
                living_fitness = [agent_fitness[a.agent_id] for a in current_agents if a.agent_id in agent_fitness]
                mean_fitness = np.mean(living_fitness) if living_fitness else BASE_F_INTRA
            else:
                mean_fitness = BASE_F_INTRA

            fitness_history.append(mean_fitness)

            if cycle % 5000 == 0:
                print(f"      Cycle {cycle}: pop={current_pop}, mean_f={mean_fitness:.5f}")

        # Check extinction
        if len(reality.get_population_agents(0)) == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pop = len(reality.get_population_agents(0))

    if len(fitness_history) > 10:
        initial_fitness = np.mean(fitness_history[:10])
        final_fitness = np.mean(fitness_history[-10:])
        fitness_change = final_fitness - initial_fitness
        relative_change = fitness_change / initial_fitness if initial_fitness > 0 else 0
    else:
        initial_fitness = BASE_F_INTRA
        final_fitness = BASE_F_INTRA
        fitness_change = 0
        relative_change = 0

    return {
        "selection": selection,
        "seed": seed,
        "final_pop": final_pop,
        "initial_fitness": float(initial_fitness),
        "final_fitness": float(final_fitness),
        "fitness_change": float(fitness_change),
        "relative_change": float(relative_change),
        "evolved": bool(fitness_change > 0),
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 292: EVOLUTIONARY DYNAMICS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does fitness-based selection lead to adaptation?")
    print()
    print(f"Selection strengths: {SELECTION_STRENGTHS}")
    print(f"Mutation rate: {MUTATION_RATE}, std: {MUTATION_STD}")
    print(f"Total experiments: {len(SELECTION_STRENGTHS) * len(SEEDS)}")
    print()

    results = []
    total = len(SELECTION_STRENGTHS) * len(SEEDS)
    exp_num = 0

    for selection in SELECTION_STRENGTHS:
        print(f"\n{'='*60}")
        print(f"Selection strength: {selection}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] sel={selection}, seed={seed}")

            try:
                result = run_experiment(selection, seed, CYCLES)
                results.append(result)

                print(f"    → fitness: {result['initial_fitness']:.5f} → {result['final_fitness']:.5f} "
                      f"({result['relative_change']:+.1%})")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_selection = defaultdict(list)
    for r in results:
        by_selection[r["selection"]].append(r)

    print("\nEvolutionary Change by Selection Strength:")
    print("-" * 70)
    print(f"{'Selection':>10} {'Init f':>12} {'Final f':>12} {'Change':>10} {'%':>10}")
    print("-" * 70)

    for selection in SELECTION_STRENGTHS:
        exp_list = by_selection[selection]
        init_f = np.mean([e["initial_fitness"] for e in exp_list])
        final_f = np.mean([e["final_fitness"] for e in exp_list])
        change = np.mean([e["fitness_change"] for e in exp_list])
        rel = np.mean([e["relative_change"] for e in exp_list])

        print(f"{selection:>10.1f} {init_f:>12.5f} {final_f:>12.5f} {change:>10.5f} {rel:>+10.1%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "initial_agents": INITIAL_AGENTS,
            "base_f_intra": BASE_F_INTRA,
            "mutation_rate": MUTATION_RATE,
            "mutation_std": MUTATION_STD,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "selection_strengths": SELECTION_STRENGTHS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c292_evolutionary_dynamics_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C292 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
