#!/usr/bin/env python3
"""
CYCLE 290: CATASTROPHIC DISTURBANCE

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test how metapopulations respond to sudden catastrophic events.

Research Question:
  How do metapopulations recover from sudden population loss?

Design:
  - 5 populations with ring topology
  - Catastrophe at cycle 10000: kill fraction of all agents
  - 4 severity levels: 0%, 50%, 75%, 90%
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
CYCLE_ID = "C290"
CYCLE_NAME = "Catastrophic Disturbance"
MODE = "CATASTROPHE"

CYCLES = 20000
CATASTROPHE_CYCLE = 10000
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

# Test conditions
CATASTROPHE_SEVERITIES = [0.0, 0.50, 0.75, 0.90]  # Fraction killed
SEEDS = [100, 101, 102]


def run_experiment(severity: float, seed: int, cycles: int) -> dict:
    """Run catastrophic disturbance experiment."""

    label = f"sev{int(severity*100)}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c290_{label}_seed{seed}.db"

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

    # Pre/post catastrophe metrics
    pre_catastrophe_total = None
    post_catastrophe_total = None
    recovery_cycle = None

    start_time = time.time()

    for cycle in range(cycles):
        # CATASTROPHE
        if cycle == CATASTROPHE_CYCLE and severity > 0:
            pre_catastrophe_total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))

            # Kill fraction of agents across all populations
            for pop_id in range(N_POPULATIONS):
                agents = list(reality.get_population_agents(pop_id))
                for agent in agents:
                    if np.random.random() < severity:
                        reality.remove_agent(agent.agent_id, pop_id)

            post_catastrophe_total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
            print(f"      [CATASTROPHE] Cycle {cycle}: {pre_catastrophe_total} → {post_catastrophe_total}")

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

        # MIGRATION (ring topology)
        for pop_id in range(N_POPULATIONS):
            agents = list(reality.get_population_agents(pop_id))
            left = (pop_id - 1) % N_POPULATIONS
            right = (pop_id + 1) % N_POPULATIONS

            for agent in agents:
                if np.random.random() < MIGRATION_RATE:
                    target = np.random.choice([left, right])
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
                    death_prob = DENSITY_FACTOR * (pop_size / K)
                    if np.random.random() < death_prob:
                        reality.remove_agent(agent.agent_id, pop_id)
                        continue

                    agent.energy = min(agent.energy + E_RECHARGE, 2.0)

        # Record
        if cycle % 100 == 0:
            total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            # Check for recovery (return to 90% of pre-catastrophe)
            if recovery_cycle is None and pre_catastrophe_total is not None:
                if total >= 0.9 * pre_catastrophe_total:
                    recovery_cycle = cycle
                    print(f"      [RECOVERED] Cycle {cycle}: total={total}")

            if cycle % 5000 == 0:
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

    # Late-phase analysis
    if len(pop_history[0]) > 10:
        late_totals = []
        for i in range(-20, 0):
            if abs(i) <= len(pop_history[0]):
                total = sum(pop_history[p][i] for p in range(N_POPULATIONS))
                late_totals.append(total)

        mean_final = np.mean(late_totals)
    else:
        mean_final = total_pop

    # Recovery time
    if recovery_cycle is not None:
        recovery_time = recovery_cycle - CATASTROPHE_CYCLE
    else:
        recovery_time = None if severity > 0 else 0

    return {
        "severity": severity,
        "seed": seed,
        "pre_catastrophe": pre_catastrophe_total if pre_catastrophe_total else 0,
        "post_catastrophe": post_catastrophe_total if post_catastrophe_total else 0,
        "mean_final": float(mean_final),
        "recovery_time": recovery_time,
        "recovered": recovery_cycle is not None if severity > 0 else True,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 290: CATASTROPHIC DISTURBANCE")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: How do metapopulations recover from catastrophes?")
    print()
    print(f"Catastrophe severities: {[f'{int(s*100)}%' for s in CATASTROPHE_SEVERITIES]}")
    print(f"Catastrophe cycle: {CATASTROPHE_CYCLE}")
    print(f"Total experiments: {len(CATASTROPHE_SEVERITIES) * len(SEEDS)}")
    print()

    results = []
    total = len(CATASTROPHE_SEVERITIES) * len(SEEDS)
    exp_num = 0

    for severity in CATASTROPHE_SEVERITIES:
        print(f"\n{'='*60}")
        print(f"Severity: {int(severity*100)}%")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] sev={int(severity*100)}%, seed={seed}")

            try:
                result = run_experiment(severity, seed, CYCLES)
                results.append(result)

                recovery_str = f"{result['recovery_time']}" if result['recovery_time'] is not None else "N/A"
                print(f"    → final={result['mean_final']:.1f}, "
                      f"recovery={recovery_str}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_sev = defaultdict(list)
    for r in results:
        by_sev[r["severity"]].append(r)

    print("\nCatastrophic Disturbance Recovery:")
    print("-" * 80)
    print(f"{'Severity':>10} {'Pre':>10} {'Post':>10} {'Final':>10} {'Recovery':>12} {'Survived':>10}")
    print("-" * 80)

    for sev in CATASTROPHE_SEVERITIES:
        exp_list = by_sev[sev]
        pre = np.mean([e["pre_catastrophe"] for e in exp_list])
        post = np.mean([e["post_catastrophe"] for e in exp_list])
        final = np.mean([e["mean_final"] for e in exp_list])

        recovery_times = [e["recovery_time"] for e in exp_list if e["recovery_time"] is not None]
        recovery = np.mean(recovery_times) if recovery_times else None

        survived = sum(1 for e in exp_list if e["recovered"]) / len(exp_list)

        recovery_str = f"{recovery:.0f}" if recovery is not None else "N/A"
        print(f"{int(sev*100):>10}% {pre:>10.1f} {post:>10.1f} {final:>10.1f} {recovery_str:>12} {survived:>10.0%}")

    # Save
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "cycles": CYCLES,
            "catastrophe_cycle": CATASTROPHE_CYCLE,
            "n_populations": N_POPULATIONS,
            "initial_agents_per_pop": INITIAL_AGENTS_PER_POP,
            "f_intra": F_INTRA,
            "energy": {"E_consume": E_CONSUME, "E_recharge": E_RECHARGE, "spawn": SPAWN_ENERGY},
            "density_factor": DENSITY_FACTOR,
            "K": K,
            "migration_rate": MIGRATION_RATE,
            "catastrophe_severities": CATASTROPHE_SEVERITIES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c290_catastrophic_disturbance_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C290 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
