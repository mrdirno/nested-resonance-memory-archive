#!/usr/bin/env python3
"""
CYCLE 280: EXPONENTIAL GROWTH DYNAMICS

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-20

Purpose:
  Test population dynamics with PER-AGENT spawning (exponential growth)
  instead of PER-CYCLE spawning (linear growth).

Research Question:
  How do population dynamics change when birth rate is proportional to population?

Key Changes from C279:
  - Spawn check: for each agent, random() < f_intra (exponential)
  - Not: single random() < f_intra per cycle (linear)

Expected Behaviors:
  1. Initial exponential growth phase
  2. Possible equilibrium via energy depletion
  3. Test whether spawn threshold still determines viability

Experimental Design:
  - 3 spawn energies: 0.3, 0.5, 0.7
  - 3 relative E_consume: below, at, above spawn_energy
  - 5 seeds per condition
  - Shorter cycles (10,000) due to expected rapid growth
  - Total: 9 conditions × 5 seeds = 45 experiments
"""

import sys
import os
import json
import time
import numpy as np
from datetime import datetime

# Add experiments directory to path for local imports
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

from core.fractal_agent import FractalAgent, RealityInterface

# Configuration
CYCLE_ID = "C280"
CYCLE_NAME = "Exponential Growth Dynamics"
MODE = "EXPONENTIAL_GROWTH"

# Shorter cycles due to exponential growth
CYCLES = 10000
N_POPULATIONS = 1  # Single population for clarity
INITIAL_AGENTS = 10  # Smaller initial to see growth clearly
E_RECHARGE = 1.0

# Spawn probability per agent per cycle
F_INTRA = 0.005  # Same as C279

# Spawn energies to test
SPAWN_ENERGIES = [0.3, 0.5, 0.7]

# Build energy conditions
ENERGY_CONDITIONS = {}
for spawn_e in SPAWN_ENERGIES:
    for delta in [-0.1, 0.0, +0.1]:
        e_consume = spawn_e + delta
        label = f"spawn{spawn_e}_consume{e_consume:.1f}"
        expected = "GROWTH" if e_consume < spawn_e else ("THRESHOLD" if e_consume == spawn_e else "DEATH")
        ENERGY_CONDITIONS[label] = {
            "E_consume": e_consume,
            "E_recharge": E_RECHARGE,
            "net": E_RECHARGE - e_consume,
            "spawn_energy": spawn_e,
            "regime": expected
        }

SEEDS = list(range(100, 105))  # 5 seeds

def run_exponential_growth_experiment(energy_label: str, energy_params: dict,
                                      f_intra: float, seed: int, cycles: int) -> dict:
    """
    Run single experiment with per-agent (exponential) spawning.

    Key difference from C279: every agent has independent spawn chance each cycle.
    """
    # Create database path
    db_name = f"c280_EXP_GROWTH_{energy_label}_seed{seed}.db"
    db_path = f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/{db_name}"

    # Initialize reality (matching C279 pattern)
    reality = RealityInterface(
        db_path=db_path,
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    # Set energy parameters
    reality.energy_config = {
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"]
    }

    # Set random seed
    np.random.seed(seed)

    # Initialize agents
    for i in range(INITIAL_AGENTS):
        agent = FractalAgent(
            agent_id=f"agent_0_{i}",
            population_id=0,
            energy=1.0
        )
        reality.add_agent(agent, population_id=0)

    # Population cap to prevent memory overflow
    MAX_POPULATION = 100000

    # Track population over time
    population_history = []

    # Run simulation
    start_time = time.time()

    for cycle in range(cycles):
        agents = reality.get_population_agents(0)

        # Check population cap
        if len(agents) >= MAX_POPULATION:
            print(f"      [CAP] Population hit {MAX_POPULATION} at cycle {cycle}")
            break

        # EXPONENTIAL SPAWN: Check each agent independently
        new_spawns = []
        spawn_energy = energy_params.get("spawn_energy", 0.5)

        for agent in agents:
            if np.random.random() < f_intra:
                child = FractalAgent(
                    agent_id=f"spawn_{cycle}_{agent.agent_id}",
                    population_id=0,
                    energy=spawn_energy
                )
                new_spawns.append(child)

        # Add all spawns
        for child in new_spawns:
            reality.add_agent(child, population_id=0)

        # Death phase (energy-based)
        agents = reality.get_population_agents(0)  # Refresh after spawns
        for agent in agents:
            # Consume energy
            agent.energy -= energy_params["E_consume"]

            # Death if energy depleted
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
            else:
                # Recharge surviving agents
                agent.energy = min(agent.energy + energy_params["E_recharge"], 2.0)

        # Record metrics
        current_pop = len(reality.get_population_agents(0))

        if cycle % 100 == 0:
            population_history.append(current_pop)

            # Log progress
            if cycle % 1000 == 0:
                print(f"      Cycle {cycle}: pop={current_pop}")

        # Early termination if population goes extinct
        if current_pop == 0:
            print(f"      [EXTINCT] at cycle {cycle}")
            break

    # Get final population
    final_pop = len(reality.get_population_agents(0))
    runtime = time.time() - start_time

    return {
        "energy_label": energy_label,
        "E_net": energy_params["net"],
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"],
        "spawn_energy": energy_params["spawn_energy"],
        "regime": energy_params["regime"],
        "f_intra": f_intra,
        "seed": seed,
        "cycles_completed": len(population_history) * 100,
        "final_population": final_pop,
        "max_population": max(population_history) if population_history else 0,
        "population_history": population_history,
        "runtime_seconds": runtime,
        "db_path": db_path
    }


def main():
    """Run C280 Exponential Growth Dynamics experiments."""

    print("=" * 80)
    print(f"CYCLE 280: EXPONENTIAL GROWTH DYNAMICS")
    print(f"Author: Aldrin Payopay <aldrin.gdf@gmail.com>")
    print(f"Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    print("Experimental Design:")
    print(f"  Spawn mode: PER-AGENT (exponential growth)")
    print(f"  Conditions: {len(ENERGY_CONDITIONS)}")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(ENERGY_CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  Initial population: {INITIAL_AGENTS}")
    print(f"  f_intra: {F_INTRA:.3%}")
    print()

    results = []
    total_exps = len(ENERGY_CONDITIONS) * len(SEEDS)
    exp_num = 0

    for label, params in ENERGY_CONDITIONS.items():
        print("=" * 80)
        print(f"Condition: {label} (expected: {params['regime']})")
        print(f"  E_consume={params['E_consume']:.1f}, spawn_energy={params['spawn_energy']}")
        print("=" * 80)

        for seed in SEEDS:
            exp_num += 1
            print(f"\n[{exp_num}/{total_exps}] Running: {label}, seed={seed}")

            try:
                result = run_exponential_growth_experiment(
                    label, params, F_INTRA, seed, CYCLES
                )
                results.append(result)

                final = result["final_population"]
                max_pop = result["max_population"]
                runtime = result["runtime_seconds"]

                print(f"    → final={final}, max={max_pop}, runtime={runtime:.1f}s")

            except Exception as e:
                print(f"    ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()

    # Analyze results
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    by_condition = defaultdict(list)

    for r in results:
        by_condition[r["energy_label"]].append(r)

    print("\nPopulation by Condition:")
    print("-" * 60)
    print(f"{'Condition':<30} {'Mean':>10} {'Max':>10} {'Regime':>10}")
    print("-" * 60)

    for label in sorted(by_condition.keys()):
        exp_list = by_condition[label]
        final_pops = [e["final_population"] for e in exp_list]
        max_pops = [e["max_population"] for e in exp_list]
        mean_final = np.mean(final_pops)
        mean_max = np.mean(max_pops)
        regime = exp_list[0]["regime"]

        print(f"{label:<30} {mean_final:>10.1f} {mean_max:>10.1f} {regime:>10}")

    # Save results
    output = {
        "cycle_id": CYCLE_ID,
        "cycle_name": CYCLE_NAME,
        "date": datetime.now().isoformat(),
        "author": "Aldrin Payopay <aldrin.gdf@gmail.com>",
        "co_author": "Claude Sonnet 4.5 <noreply@anthropic.com>",
        "config": {
            "mode": "EXPONENTIAL (per-agent spawning)",
            "cycles": CYCLES,
            "initial_agents": INITIAL_AGENTS,
            "f_intra": F_INTRA,
            "n_populations": N_POPULATIONS,
            "conditions": ENERGY_CONDITIONS,
            "seeds": SEEDS
        },
        "results": results
    }

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c280_exponential_growth_results.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print("\n" + "=" * 80)
    print("C280 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
