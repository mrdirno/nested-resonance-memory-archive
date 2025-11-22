#!/usr/bin/env python3
"""
CYCLE 286: NETWORK TOPOLOGY EFFECTS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test how different network topologies affect metapopulation dynamics.

Research Question:
  Does network structure affect synchronization and stability?

Design:
  - 5 populations
  - 3 topologies: complete (all-to-all), ring, star
  - Migration rate: 0.05
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
CYCLE_ID = "C286"
CYCLE_NAME = "Network Topology Effects"
MODE = "NETWORK_TOPOLOGY"

CYCLES = 20000
N_POPULATIONS = 5
INITIAL_AGENTS_PER_POP = 20
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Density dependence
DENSITY_FACTOR = 0.1
K = 500

# Migration
MIGRATION_RATE = 0.05

# Network topologies
def get_neighbors(topology, pop_id, n_pops):
    """Return list of neighbor population IDs based on topology."""
    if topology == "complete":
        # All-to-all: every pop connects to every other
        return [i for i in range(n_pops) if i != pop_id]

    elif topology == "ring":
        # Ring: each pop connects to 2 neighbors
        left = (pop_id - 1) % n_pops
        right = (pop_id + 1) % n_pops
        return [left, right]

    elif topology == "star":
        # Star: pop 0 is hub, others connect only to hub
        if pop_id == 0:
            return list(range(1, n_pops))
        else:
            return [0]

    else:
        return []

TOPOLOGIES = ["complete", "ring", "star"]
SEEDS = [100, 101, 102]


def run_experiment(topology: str, seed: int, cycles: int) -> dict:
    """Run network topology experiment."""

    label = topology
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c286_{label}_seed{seed}.db"

    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    np.random.seed(seed)

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
        # SPAWN
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            new_spawns = []

            for agent in agents:
                if np.random.random() < F_INTRA:
                    child = FractalAgent(
                        agent_id=f"spawn_{cycle}_{pop_id}_{agent.agent_id}",
                        population_id=pop_id,
                        energy=SPAWN_ENERGY
                    )
                    new_spawns.append(child)

            for child in new_spawns:
                reality.add_agent(child, population_id=pop_id)

        # MIGRATION (topology-dependent)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            neighbors = get_neighbors(topology, pop_id, N_POPULATIONS)

            if not neighbors:
                continue

            for agent in list(agents):
                if np.random.random() < MIGRATION_RATE:
                    # Migrate to random neighbor
                    target = np.random.choice(neighbors)
                    reality.migrate_agent(agent.agent_id, pop_id, target)

        # DEATH
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            pop_size = len(agents)

            for agent in agents:
                agent.energy -= E_CONSUME

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Density-dependent death
                    death_prob = DENSITY_FACTOR * (pop_size / K)
                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 5000 == 0:
                total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
                print(f"      Cycle {cycle}: total={total}")

        # Check extinction
        total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
        if total == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    runtime = time.time() - start_time

    # Calculate metrics
    final_pops = [len(reality.get_population_agents(p)) for p in range(N_POPULATIONS)]
    total_pop = sum(final_pops)

    # Synchronization metric (cross-population variance)
    if len(pop_history[0]) > 10:
        late_totals = []
        for i in range(-20, 0):
            if abs(i) <= len(pop_history[0]):
                total = sum(pop_history[p][i] for p in range(N_POPULATIONS))
                late_totals.append(total)

        mean_total = np.mean(late_totals)
        std_total = np.std(late_totals)

        # Cross-population variance
        cross_pop_var = []
        for i in range(-10, 0):
            if abs(i) <= len(pop_history[0]):
                pops = [pop_history[p][i] for p in range(N_POPULATIONS)]
                cross_pop_var.append(np.std(pops))

        sync_metric = float(np.mean(cross_pop_var) / max(np.mean(mean_total / N_POPULATIONS), 1))

        # Per-population stability
        pop_stabilities = []
        for p in range(N_POPULATIONS):
            late = pop_history[p][-20:]
            cv = np.std(late) / max(np.mean(late), 1)
            pop_stabilities.append(cv)
        mean_stability = float(np.mean(pop_stabilities))
    else:
        mean_total = total_pop
        std_total = 0
        sync_metric = 0
        mean_stability = 0

    return {
        "topology": topology,
        "seed": seed,
        "final_total": total_pop,
        "final_pops": final_pops,
        "mean_total": float(mean_total),
        "std_total": float(std_total),
        "sync_metric": sync_metric,  # Lower = more synchronized
        "mean_stability": mean_stability,  # Lower = more stable
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 286: NETWORK TOPOLOGY EFFECTS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Does network structure affect synchronization and stability?")
    print()
    print(f"Topologies: {TOPOLOGIES}")
    print(f"Populations: {N_POPULATIONS}")
    print(f"Migration rate: {MIGRATION_RATE}")
    print(f"Total experiments: {len(TOPOLOGIES) * len(SEEDS)}")
    print()

    results = []
    total = len(TOPOLOGIES) * len(SEEDS)
    exp_num = 0

    for topology in TOPOLOGIES:
        print(f"\n{'='*60}")
        print(f"Topology: {topology}")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] {topology}, seed={seed}")

            try:
                result = run_experiment(topology, seed, CYCLES)
                results.append(result)

                print(f"    → total={result['final_total']}, "
                      f"sync={result['sync_metric']:.3f}, "
                      f"stability={result['mean_stability']:.3f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_topology = defaultdict(list)
    for r in results:
        by_topology[r["topology"]].append(r)

    print("\nTopology Effects:")
    print("-" * 80)
    print(f"{'Topology':>12} {'Mean Total':>12} {'Std':>10} {'Sync':>10} {'Stability':>10}")
    print("-" * 80)

    for topology in TOPOLOGIES:
        exp_list = by_topology[topology]
        mean_total = np.mean([e["mean_total"] for e in exp_list])
        std = np.mean([e["std_total"] for e in exp_list])
        sync = np.mean([e["sync_metric"] for e in exp_list])
        stability = np.mean([e["mean_stability"] for e in exp_list])

        print(f"{topology:>12} {mean_total:>12.1f} {std:>10.1f} {sync:>10.3f} {stability:>10.3f}")

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
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "migration_rate": MIGRATION_RATE,
            "topologies": TOPOLOGIES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c286_network_topology_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C286 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
