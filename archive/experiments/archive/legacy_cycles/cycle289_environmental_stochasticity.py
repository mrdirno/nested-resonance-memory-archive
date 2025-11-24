#!/usr/bin/env python3
"""
CYCLE 289: ENVIRONMENTAL STOCHASTICITY

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test how metapopulations respond to fluctuating environmental conditions.

Research Question:
  Are metapopulation dynamics robust to environmental stochasticity?

Design:
  - 5 populations with ring topology
  - Fluctuating K (carrying capacity) over time
  - 4 fluctuation amplitudes: 0%, 10%, 25%, 50%
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
CYCLE_ID = "C289"
CYCLE_NAME = "Environmental Stochasticity"
MODE = "STOCHASTIC_ENV"

CYCLES = 20000
N_POPULATIONS = 5
INITIAL_AGENTS_PER_POP = 20
F_INTRA = 0.005

# Energy (viable regime)
E_CONSUME = 0.3
E_RECHARGE = 0.5
SPAWN_ENERGY = 0.5

# Base density dependence
DENSITY_FACTOR = 0.1
BASE_K = 500
FLUCTUATION_PERIOD = 1000  # Cycles per fluctuation

# Migration
MIGRATION_RATE = 0.05

# Test conditions
FLUCTUATION_AMPLITUDES = [0.0, 0.10, 0.25, 0.50]  # Fraction of K
SEEDS = [100, 101, 102]


def run_experiment(amplitude: float, seed: int, cycles: int) -> dict:
    """Run environmental stochasticity experiment."""

    label = f"amp{int(amplitude*100)}"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c289_{label}_seed{seed}.db"

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
    K_history = []

    start_time = time.time()

    for cycle in range(cycles):
        # Calculate current K (sinusoidal fluctuation)
        if amplitude > 0:
            phase = 2 * np.pi * cycle / FLUCTUATION_PERIOD
            K = BASE_K * (1 + amplitude * np.sin(phase))
        else:
            K = BASE_K

        if cycle % 100 == 0:
            K_history.append(K)

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
            for pop_id in range(N_POPULATIONS):
                pop_size = len(reality.get_population_agents(pop_id))
                pop_history[pop_id].append(pop_size)

            if cycle % 5000 == 0:
                total = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
                print(f"      Cycle {cycle}: total={total}, K={K:.0f}")

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

        mean_total = np.mean(late_totals)
        std_total = np.std(late_totals)
        cv_total = std_total / mean_total if mean_total > 0 else 0

        # Track population against K
        if amplitude > 0 and len(K_history) > 20:
            late_K = K_history[-20:]
            mean_K = np.mean(late_K)
            # Check if population tracks K
            correlation = np.corrcoef(late_totals[:len(late_K)], late_K)[0, 1]
        else:
            mean_K = BASE_K
            correlation = 0
    else:
        mean_total = total_pop
        std_total = 0
        cv_total = 0
        mean_K = BASE_K
        correlation = 0

    # Theoretical equilibrium at mean K
    theoretical = mean_K * (F_INTRA / DENSITY_FACTOR) * N_POPULATIONS

    return {
        "amplitude": amplitude,
        "seed": seed,
        "final_total": total_pop,
        "mean_total": float(mean_total),
        "std_total": float(std_total),
        "cv_total": float(cv_total),
        "mean_K": float(mean_K),
        "theoretical": float(theoretical),
        "correlation": float(correlation) if not np.isnan(correlation) else 0,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    print("=" * 80)
    print(f"CYCLE 289: ENVIRONMENTAL STOCHASTICITY")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Research Question: Are dynamics robust to environmental fluctuation?")
    print()
    print(f"Fluctuation amplitudes: {[f'{int(a*100)}%' for a in FLUCTUATION_AMPLITUDES]}")
    print(f"Total experiments: {len(FLUCTUATION_AMPLITUDES) * len(SEEDS)}")
    print()

    results = []
    total = len(FLUCTUATION_AMPLITUDES) * len(SEEDS)
    exp_num = 0

    for amplitude in FLUCTUATION_AMPLITUDES:
        print(f"\n{'='*60}")
        print(f"Amplitude: {int(amplitude*100)}%")
        print("=" * 60)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total}] amp={int(amplitude*100)}%, seed={seed}")

            try:
                result = run_experiment(amplitude, seed, CYCLES)
                results.append(result)

                print(f"    → total={result['mean_total']:.1f}, "
                      f"CV={result['cv_total']:.3f}, "
                      f"corr={result['correlation']:.2f}")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_amp = defaultdict(list)
    for r in results:
        by_amp[r["amplitude"]].append(r)

    print("\nEnvironmental Stochasticity Effects:")
    print("-" * 80)
    print(f"{'Amplitude':>10} {'Mean Total':>12} {'CV':>10} {'Theory':>10} {'Corr':>10}")
    print("-" * 80)

    for amp in FLUCTUATION_AMPLITUDES:
        exp_list = by_amp[amp]
        mean_total = np.mean([e["mean_total"] for e in exp_list])
        cv = np.mean([e["cv_total"] for e in exp_list])
        theory = np.mean([e["theoretical"] for e in exp_list])
        corr = np.mean([e["correlation"] for e in exp_list])

        print(f"{int(amp*100):>10}% {mean_total:>12.1f} {cv:>10.3f} {theory:>10.1f} {corr:>10.2f}")

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
            "base_K": BASE_K,
            "fluctuation_period": FLUCTUATION_PERIOD,
            "migration_rate": MIGRATION_RATE,
            "fluctuation_amplitudes": FLUCTUATION_AMPLITUDES,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c289_environmental_stochasticity_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C289 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
