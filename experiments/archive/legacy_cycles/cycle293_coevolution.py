#!/usr/bin/env python3
"""
CYCLE 293: COEVOLUTION

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test whether competing populations evolving together produce arms races.

Research Question:
  Does coevolution lead to escalation, stable equilibrium, or cycles?

Design:
  - 2 populations competing for global K
  - Both populations evolve (heritable fitness)
  - 3 conditions: no evolution, one evolves, both evolve
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
CYCLE_ID = "C293"
CYCLE_NAME = "Coevolution"
MODE = "COEVOLUTION"

CYCLES = 25000
N_POPULATIONS = 2
INITIAL_AGENTS_PER_POP = 50
BASE_F_INTRA = 0.005
MUTATION_RATE = 0.1
MUTATION_STD = 0.001
SELECTION = 1.0

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Global competition
DENSITY_FACTOR = 0.1
K = 500

# Test conditions
EVOLUTION_CONFIGS = [
    {"name": "none", "pop0": False, "pop1": False},
    {"name": "pop1_only", "pop0": False, "pop1": True},
    {"name": "both", "pop0": True, "pop1": True}
]
SEEDS = [100, 101, 102]


def run_experiment(config: dict, seed: int, cycles: int) -> dict:
    """Run coevolution experiment."""

    label = config["name"]
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c293_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

    # Agent fitness tracking per population
    agent_fitness = {0: {}, 1: {}}

    # Initialize with variation
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
            evolves = config[f"pop{pop_id}"]
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if agent.agent_id not in agent_fitness[pop_id]:
                    continue

                parent_fitness = agent_fitness[pop_id][agent.agent_id]

                # Selection if evolving
                if evolves:
                    f_effective = BASE_F_INTRA + SELECTION * (parent_fitness - BASE_F_INTRA)
                else:
                    f_effective = BASE_F_INTRA

                f_effective = max(0, f_effective)

                if np.random.random() < f_effective:
                    # Offspring inherits with mutation
                    if evolves and np.random.random() < MUTATION_RATE:
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

        # DEATH (global competition)
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
                    death_prob = DENSITY_FACTOR * (total_pop / K)
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

        # Check extinction
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
        results[f"pop{pop_id}_init_pop"] = float(init_pop)
        results[f"pop{pop_id}_final_pop"] = float(final_pop)

    # Winner determination
    if results["pop0_final_pop"] > results["pop1_final_pop"] * 1.5:
        winner = "pop0"
    elif results["pop1_final_pop"] > results["pop0_final_pop"] * 1.5:
        winner = "pop1"
    else:
        winner = "tie"

    return {
        "config": config["name"],
        "seed": seed,
        "winner": winner,
        **results,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 293: COEVOLUTION")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does coevolution lead to escalation or equilibrium?")
    print()
    print(f"Conditions: {[c['name'] for c in EVOLUTION_CONFIGS]}")
    print(f"Total experiments: {len(EVOLUTION_CONFIGS) * len(SEEDS)}")
    print()

    results = []
    total = len(EVOLUTION_CONFIGS) * len(SEEDS)
    exp_num = 0

    for config in EVOLUTION_CONFIGS:
        print(f"\n{'='*60}")
        print(f"Config: {config['name']}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {config['name']}, seed={seed}")

            try:
                result = run_experiment(config, seed, CYCLES)
                results.append(result)

                print(f"    → winner={result['winner']}, "
                      f"pop0: {result['pop0_init_f']:.4f}→{result['pop0_final_f']:.4f}, "
                      f"pop1: {result['pop1_init_f']:.4f}→{result['pop1_final_f']:.4f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_config = defaultdict(list)
    for r in results:
        by_config[r["config"]].append(r)

    print("\nCoevolution Outcomes:")
    print("-" * 80)
    print(f"{'Config':>12} {'P0 Init f':>10} {'P0 Final f':>10} {'P1 Init f':>10} {'P1 Final f':>10} {'Winner':>8}")
    print("-" * 80)

    for config in EVOLUTION_CONFIGS:
        name = config["name"]
        exp_list = by_config[name]

        p0_init = np.mean([e["pop0_init_f"] for e in exp_list])
        p0_final = np.mean([e["pop0_final_f"] for e in exp_list])
        p1_init = np.mean([e["pop1_init_f"] for e in exp_list])
        p1_final = np.mean([e["pop1_final_f"] for e in exp_list])

        winners = [e["winner"] for e in exp_list]
        winner = max(set(winners), key=winners.count)

        print(f"{name:>12} {p0_init:>10.4f} {p0_final:>10.4f} {p1_init:>10.4f} {p1_final:>10.4f} {winner:>8}")

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
            "evolution_configs": EVOLUTION_CONFIGS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c293_coevolution_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C293 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
