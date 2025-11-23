#!/usr/bin/env python3
"""
C194: Energy Consumption Threshold (f_critical via Per-Cycle Consumption)

After FOUR campaigns with ZERO collapses (C190, C191, C192, C193), this experiment
adds per-cycle energy consumption to enable agent death and locate actual collapse boundary.

Research Question: At what energy consumption rate does collapse emerge?

Critical Insight (from C193):
  Current energy model (NO per-cycle consumption) is fundamentally non-collapsible
  because agents cannot die from energy depletion.

Experimental Design:
  - 4 E_CONSUME values: 0.1, 0.3, 0.5, 0.7 (test energy pressure gradient)
  - 3 N_initial values: 5, 10, 20 (test N-dependence under energy pressure)
  - 2 spawn mechanisms: Deterministic, Flat
  - 3 frequencies: 0.05%, 0.10%, 0.20%
  - 50 seeds per condition
  - Total: 3,600 experiments

Energy Balance Theory:
  Net Energy = RECHARGE_RATE - E_CONSUME

  E_CONSUME = 0.1: Net +0.4 → expect survival
  E_CONSUME = 0.3: Net +0.2 → likely survival
  E_CONSUME = 0.5: Net  0.0 → boundary condition
  E_CONSUME = 0.7: Net -0.2 → expect collapse

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08 (Cycle 1325+)
License: GPL-3.0
"""

import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# Experimental parameters (NEW: E_CONSUME as variable)
E_CONSUME_CONDITIONS = [0.1, 0.3, 0.5, 0.7]  # Energy consumption per cycle
N_INITIAL_CONDITIONS = [5, 10, 20]  # Population sizes
SPAWN_MECHANISMS = ['deterministic', 'flat']  # Focus on extremes
F_INTRA_PCT_CONDITIONS = [0.05, 0.10, 0.20]  # Frequencies
N_SEEDS = 50  # Balance precision and execution time

# Certainty values for spawn mechanisms
CERTAINTY_VALUES = {
    'deterministic': 1.0,  # Zero dropout (most robust)
    'flat': 0.0,  # Full probabilistic (least robust)
}

# System parameters (from C193)
N_POP = 1  # Single population
CYCLES = 5000  # Extended for slower dynamics

# Energy parameters (extend C193 with E_CONSUME)
E_INITIAL = 50.0  # Initial agent energy
E_SPAWN_THRESHOLD = 20.0  # Energy required to spawn
E_SPAWN_COST = 10.0  # Energy cost to parent (deducted on spawn)
RECHARGE_RATE = 0.5  # Energy recovered per cycle
CHILD_ENERGY_FRACTION = 0.5  # Offspring energy = E_INITIAL × this fraction

# Basin classification
BASIN_A_THRESHOLD = 2.5  # > 2.5 agents = viable (Basin A)

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Seeds for reproducibility (50 unique seeds)
BASE_SEEDS = [42, 123, 456, 789, 101,  # Match C191/C192/C193 baseline
              5661, 7296, 9074, 5127, 2734, 9846, 8394, 6229, 3831, 5009,
              1695, 779, 6959, 2443, 5321, 5061, 6430, 1194, 4565, 3395,
              6406, 8676, 9284, 2568, 7859, 2057, 2757, 9177, 199, 2744,
              3015, 4668, 1909, 7744, 1277, 1538, 3566, 3900, 8848, 5403,
              8802, 8443, 7523, 2622, 7051]

# ============================================================================
# AGENT CLASS (EXTENDED WITH DEATH MECHANICS)
# ============================================================================

class Agent:
    """Individual agent with energy dynamics and death mechanics (NEW in C194)"""

    def __init__(self, energy: float = E_INITIAL):
        self.energy = energy
        self.age = 0

    def increment_age(self):
        """Increment age"""
        self.age += 1

    def consume_energy(self, e_consume: float):
        """Consume energy per cycle (NEW in C194)"""
        self.energy -= e_consume

    def is_alive(self) -> bool:
        """Check if agent is alive (NEW in C194)"""
        return self.energy > 0

# ============================================================================
# POPULATION CLASS (EXTENDED WITH DEATH MECHANICS)
# ============================================================================

class Population:
    """Population of agents with spawn mechanics and death (NEW in C194)"""

    def __init__(self, n_initial: int, random_state):
        self.agents: List[Agent] = [Agent() for _ in range(n_initial)]
        self.random = random_state
        self.spawn_count = 0
        self.spawn_failures = 0
        self.death_count = 0  # NEW: track deaths

    def size(self) -> int:
        return len(self.agents)

    def mean_energy(self) -> float:
        if self.size() == 0:
            return 0.0
        return np.mean([a.energy for a in self.agents])

    def increment_ages(self):
        """Increment age for all agents"""
        for agent in self.agents:
            agent.increment_age()

    def consume_energy(self, e_consume: float):
        """All agents consume energy per cycle (NEW in C194)"""
        for agent in self.agents:
            agent.consume_energy(e_consume)

    def remove_dead(self):
        """Remove agents with energy ≤ 0 (NEW in C194)"""
        alive = [a for a in self.agents if a.is_alive()]
        deaths = len(self.agents) - len(alive)
        self.death_count += deaths
        self.agents = alive

    def recharge_energy(self, e_initial: float, recharge_rate: float):
        """All agents recover energy per cycle"""
        for agent in self.agents:
            agent.energy = min(e_initial, agent.energy + recharge_rate)

    def spawn_attempt(self, e_initial: float, e_spawn_threshold: float,
                     e_spawn_cost: float, child_energy_fraction: float) -> bool:
        """
        Attempt intra-population spawning

        Returns:
            True if spawn succeeded, False otherwise
        """
        if self.size() == 0:
            self.spawn_failures += 1
            return False

        # Random parent selection
        parent = self.random.choice(self.agents)

        # Check if parent has enough energy
        if parent.energy >= e_spawn_threshold:
            # Successful spawn: create offspring, deplete parent
            offspring_energy = e_initial * child_energy_fraction
            offspring = Agent(energy=offspring_energy)
            self.agents.append(offspring)
            parent.energy -= e_spawn_cost
            self.spawn_count += 1
            return True
        else:
            self.spawn_failures += 1
            return False

# ============================================================================
# SINGLE-POPULATION SYSTEM (EXTENDED WITH ENERGY CONSUMPTION)
# ============================================================================

class SinglePopulationSystem:
    """
    Single-population system with spawn mechanism variation and energy consumption

    NEW in C194: Per-cycle energy consumption with agent death
    """

    def __init__(self,
                 spawn_mechanism: str,
                 f_intra_pct: float,
                 n_initial: int,
                 e_consume: float,  # NEW
                 cycles: int = CYCLES,
                 seed: int = 42):
        """
        Initialize system

        Args:
            spawn_mechanism: 'deterministic' or 'flat'
            f_intra_pct: Intra-population spawn frequency (%)
            n_initial: Initial population size
            e_consume: Energy consumed per cycle (NEW in C194)
            cycles: Number of simulation cycles
            seed: Random seed for reproducibility
        """
        self.spawn_mechanism = spawn_mechanism
        self.f_intra_pct = f_intra_pct
        self.n_initial = n_initial
        self.e_consume = e_consume  # NEW
        self.cycles = cycles
        self.seed = seed

        # Random state
        self.random = np.random.RandomState(seed)

        # Spawn parameters
        self.certainty = CERTAINTY_VALUES[spawn_mechanism]

        if spawn_mechanism == 'deterministic':
            # Interval-based spawning
            self.spawn_interval = int(100 / f_intra_pct)
            self.spawn_probability = None
        else:
            # Probabilistic spawning (flat)
            self.spawn_interval = None
            self.spawn_probability = f_intra_pct / 100.0

        # Initialize population
        self.population = Population(n_initial, self.random)

        # Tracking
        self.cycle_count = 0
        self.population_history = []
        self.energy_history = []
        self.collapse_cycle = None  # Track when collapse occurred

    def _intra_spawning(self):
        """
        Execute intra-population spawning based on mechanism

        Mechanisms:
          - Deterministic (c=1.0): Every spawn_interval cycles
          - Flat (c=0.0): Probabilistic per-cycle
        """
        if self.population.size() == 0:
            return

        if self.spawn_mechanism == 'flat':
            # Probabilistic per-cycle
            if self.random.random() < self.spawn_probability:
                self.population.spawn_attempt(E_INITIAL, E_SPAWN_THRESHOLD,
                                             E_SPAWN_COST, CHILD_ENERGY_FRACTION)
        else:
            # Interval-based (deterministic)
            if (self.cycle_count % self.spawn_interval) == 0:
                if self.random.random() < self.certainty:
                    self.population.spawn_attempt(E_INITIAL, E_SPAWN_THRESHOLD,
                                                 E_SPAWN_COST, CHILD_ENERGY_FRACTION)

    def step(self):
        """Execute one simulation cycle (C194 energy model with consumption)"""
        # Track collapse
        if self.collapse_cycle is None and self.population.size() <= BASIN_A_THRESHOLD:
            self.collapse_cycle = self.cycle_count

        # Energy consumption (NEW - before energy recovery)
        self.population.consume_energy(self.e_consume)

        # Remove dead agents (NEW - after consumption)
        self.population.remove_dead()

        # Check for extinction (NEW)
        if self.population.size() == 0:
            # Population extinct - record and stop stepping
            self.population_history.append(0)
            self.energy_history.append(0.0)
            self.cycle_count += 1
            return

        # Energy recovery
        self.population.recharge_energy(E_INITIAL, RECHARGE_RATE)

        # Age increment
        self.population.increment_ages()

        # Intra-population spawning
        self._intra_spawning()

        # Record state
        self.population_history.append(self.population.size())
        self.energy_history.append(self.population.mean_energy())

        self.cycle_count += 1

    def run(self) -> Dict:
        """
        Run simulation for specified cycles

        Returns:
            Dict with results
        """
        for _ in range(self.cycles):
            # If population extinct, stop early
            if self.population.size() == 0:
                # Pad remaining cycles with zeros
                remaining = self.cycles - self.cycle_count
                self.population_history.extend([0] * remaining)
                self.energy_history.extend([0.0] * remaining)
                break

            self.step()

        # Final population
        final_population = self.population.size()

        # Basin classification
        basin = 'A' if final_population > BASIN_A_THRESHOLD else 'B'

        # Results
        results = {
            'spawn_mechanism': self.spawn_mechanism,
            'f_intra_pct': self.f_intra_pct,
            'n_initial': self.n_initial,
            'e_consume': self.e_consume,  # NEW
            'seed': self.seed,
            'basin': basin,
            'final_population': final_population,
            'mean_energy': self.population.mean_energy(),
            'intra_spawns': self.population.spawn_count,
            'spawn_failures': self.population.spawn_failures,
            'deaths': self.population.death_count,  # NEW
            'collapse_cycle': self.collapse_cycle if self.collapse_cycle is not None else -1,
            'certainty': self.certainty,
            'spawn_interval': self.spawn_interval,
            'spawn_probability': self.spawn_probability,
            'net_energy': RECHARGE_RATE - self.e_consume,  # NEW: track net energy
        }

        return results

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(mechanism: str, f_intra_pct: float, n_initial: int,
                  e_consume: float, seed: int) -> Dict:
    """Run single experiment"""
    system = SinglePopulationSystem(
        spawn_mechanism=mechanism,
        f_intra_pct=f_intra_pct,
        n_initial=n_initial,
        e_consume=e_consume,  # NEW
        seed=seed
    )
    return system.run()

def main():
    """Execute C194 experiments"""

    print("=" * 80)
    print("CYCLE 194: ENERGY CONSUMPTION THRESHOLD (f_critical via Per-Cycle Consumption)")
    print("=" * 80)
    print()

    print("Research Context:")
    print("  C190: 400 experiments, f ≥ 1.0%, E_CONSUME=0 → ZERO collapses")
    print("  C191: 900 experiments, f ≥ 0.3%, E_CONSUME=0 → ZERO collapses")
    print("  C192: 3,000 experiments, f ≥ 0.05%, E_CONSUME=0 → ZERO collapses")
    print("  C193: 1,200 experiments, N=5-20, E_CONSUME=0 → ZERO collapses")
    print("  Total: 6,000+ experiments, ZERO collapses (fundamentally non-collapsible)")
    print()
    print("Critical Insight: Current model (E_CONSUME=0) is fundamentally non-collapsible")
    print("                  because agents cannot die from energy depletion.")
    print()
    print("C194 Solution: Add per-cycle energy consumption → enable agent death")
    print()

    print("Energy Consumption Values:")
    for e_consume in E_CONSUME_CONDITIONS:
        net_energy = RECHARGE_RATE - e_consume
        print(f"  E_CONSUME = {e_consume} (net {net_energy:+.1f} energy/cycle)")
    print()

    print("Population Sizes:")
    for n in N_INITIAL_CONDITIONS:
        print(f"  N_initial = {n:2d} agents")
    print()

    print("Spawn Mechanisms:")
    for mech in SPAWN_MECHANISMS:
        certainty = CERTAINTY_VALUES[mech]
        print(f"  {mech:15s}: certainty={certainty:.2f}")
    print()

    print("Frequencies:")
    for f in F_INTRA_PCT_CONDITIONS:
        interval = int(100/f) if f > 0 else 'inf'
        print(f"  f_intra = {f}% (interval={interval} cycles if interval-based)")
    print()

    print("Fixed Parameters:")
    print(f"  n_pop = {N_POP} (single population)")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {N_SEEDS}")
    print()

    print("Energy Balance Theory:")
    print(f"  f_critical = (RECHARGE_RATE - E_CONSUME) / E_SPAWN_COST")
    print()
    for e_consume in E_CONSUME_CONDITIONS:
        if RECHARGE_RATE - e_consume >= 0:
            f_crit = 100 * (RECHARGE_RATE - e_consume) / E_SPAWN_COST
            print(f"  E_CONSUME={e_consume}: f_critical ≈ {f_crit:.3f}%")
        else:
            print(f"  E_CONSUME={e_consume}: f_critical < 0 (impossible → guaranteed collapse)")
    print()

    total_experiments = (len(E_CONSUME_CONDITIONS) * len(N_INITIAL_CONDITIONS) *
                        len(SPAWN_MECHANISMS) * len(F_INTRA_PCT_CONDITIONS) * N_SEEDS)
    print(f"Total Experiments: {len(E_CONSUME_CONDITIONS)} E_CONSUME × {len(N_INITIAL_CONDITIONS)} N × {len(SPAWN_MECHANISMS)} mech × {len(F_INTRA_PCT_CONDITIONS)} freq × {N_SEEDS} seeds = {total_experiments}")
    print()

    print("-" * 80)
    print()

    # Storage
    results = []
    condition_summaries = []

    experiment_num = 0
    start_time_total = time.time()

    # Execute experiments (NEW: loop over E_CONSUME)
    for e_consume in E_CONSUME_CONDITIONS:
        for n_initial in N_INITIAL_CONDITIONS:
            for mechanism in SPAWN_MECHANISMS:
                for f_intra_pct in F_INTRA_PCT_CONDITIONS:
                    # Run all seeds for this condition
                    condition_results = []

                    net_energy = RECHARGE_RATE - e_consume
                    print(f"CONDITION: E_CONSUME={e_consume} (net {net_energy:+.1f}), N={n_initial}, {mechanism.upper()}, f_intra={f_intra_pct}%")
                    print(f"  Certainty: {CERTAINTY_VALUES[mechanism]:.2f}")
                    print("-" * 40)

                    for i, seed in enumerate(BASE_SEEDS[:N_SEEDS]):
                        experiment_num += 1

                        start_time = time.time()

                        # Run experiment
                        result = run_experiment(mechanism, f_intra_pct, n_initial, e_consume, seed)

                        elapsed = time.time() - start_time

                        # Store
                        results.append(result)
                        condition_results.append(result)

                        # Progress (print every 10th to avoid clutter)
                        if (i + 1) % 10 == 0 or (i + 1) == N_SEEDS:
                            basin_label = result['basin']
                            collapse_str = f"collapse@{result['collapse_cycle']}" if result['collapse_cycle'] > 0 else "survived"
                            deaths_str = f"deaths={result['deaths']}" if result['deaths'] > 0 else "no deaths"

                            print(f"[{experiment_num:4d}/{total_experiments}] "
                                  f"E={e_consume}, N={n_initial:2d}, {mechanism[:4]:4s}, f={f_intra_pct:>5.2f}%, seed={seed:5d}... "
                                  f"Basin {basin_label}, pop={result['final_population']:3.0f}, "
                                  f"spawns={result['intra_spawns']:3d}, {deaths_str}, {collapse_str:15s}, "
                                  f"t={elapsed:.3f}s")

                    # Condition summary
                    basin_a_count = sum(1 for r in condition_results if r['basin'] == 'A')
                    basin_b_count = N_SEEDS - basin_a_count
                    basin_a_pct = 100.0 * basin_a_count / N_SEEDS
                    collapse_pct = 100.0 - basin_a_pct

                    # Mean population (Basin A only)
                    basin_a_pops = [r['final_population'] for r in condition_results if r['basin'] == 'A']
                    mean_pop_basin_a = np.mean(basin_a_pops) if basin_a_pops else 0.0
                    std_pop_basin_a = np.std(basin_a_pops, ddof=1) if len(basin_a_pops) > 1 else 0.0

                    # Mean population (all runs)
                    all_pops = [r['final_population'] for r in condition_results]
                    mean_pop_all = np.mean(all_pops)
                    std_pop_all = np.std(all_pops, ddof=1)

                    # Spawns and deaths
                    spawns_avg = np.mean([r['intra_spawns'] for r in condition_results])
                    deaths_avg = np.mean([r['deaths'] for r in condition_results])

                    print(f"Summary: Collapse {basin_b_count}/{N_SEEDS} ({collapse_pct:.1f}%), "
                          f"Survive {basin_a_count}/{N_SEEDS} ({basin_a_pct:.1f}%), "
                          f"mean(Basin A)={mean_pop_basin_a:.2f}±{std_pop_basin_a:.2f}, "
                          f"spawns_avg={spawns_avg:.1f}, deaths_avg={deaths_avg:.1f}")
                    print()

                    # Store condition summary
                    condition_summaries.append({
                        'e_consume': e_consume,  # NEW
                        'n_initial': n_initial,
                        'spawn_mechanism': mechanism,
                        'f_intra_pct': f_intra_pct,
                        'basin_a_count': basin_a_count,
                        'basin_b_count': basin_b_count,
                        'basin_a_pct': basin_a_pct,
                        'collapse_pct': collapse_pct,
                        'mean_population_basin_a': mean_pop_basin_a,
                        'std_population_basin_a': std_pop_basin_a,
                        'mean_population_all': mean_pop_all,
                        'std_population_all': std_pop_all,
                        'spawns_avg': spawns_avg,
                        'deaths_avg': deaths_avg,  # NEW
                        'certainty': CERTAINTY_VALUES[mechanism],
                        'net_energy': RECHARGE_RATE - e_consume,  # NEW
                    })

    total_elapsed = time.time() - start_time_total

    print("=" * 80)
    print(f"EXPERIMENTS COMPLETE: {total_experiments} experiments in {total_elapsed:.1f}s")
    print("=" * 80)
    print()

    # Save results
    output_file = OUTPUT_DIR / "c194_energy_consumption.json"

    output_data = {
        'experiment': 'C194_ENERGY_CONSUMPTION',
        'date': datetime.now().isoformat(),
        'metadata': {
            'e_consume_conditions': E_CONSUME_CONDITIONS,
            'n_initial_conditions': N_INITIAL_CONDITIONS,
            'spawn_mechanisms': SPAWN_MECHANISMS,
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'n_pop': N_POP,
            'cycles': CYCLES,
            'n_seeds': N_SEEDS,
            'certainty_values': CERTAINTY_VALUES,
            'basin_a_threshold': BASIN_A_THRESHOLD,
            'e_initial': E_INITIAL,
            'e_spawn_threshold': E_SPAWN_THRESHOLD,
            'e_spawn_cost': E_SPAWN_COST,
            'recharge_rate': RECHARGE_RATE,
            'child_energy_fraction': CHILD_ENERGY_FRACTION,
            'hypothesis': 'Collapse emerges when E_CONSUME > RECHARGE_RATE (net energy < 0)',
        },
        'condition_summaries': condition_summaries,
        'individual_results': results,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    print("Collapse Summary by E_CONSUME and Frequency:")
    print()

    for e_consume in E_CONSUME_CONDITIONS:
        net_energy = RECHARGE_RATE - e_consume
        print(f"E_CONSUME = {e_consume} (net {net_energy:+.1f} energy/cycle):")

        for f_intra_pct in F_INTRA_PCT_CONDITIONS:
            print(f"  f_intra = {f_intra_pct:>5.2f}%:")

            for n_initial in N_INITIAL_CONDITIONS:
                # Aggregate both mechanisms
                summaries_for_condition = [s for s in condition_summaries
                                          if s['e_consume'] == e_consume
                                          and s['f_intra_pct'] == f_intra_pct
                                          and s['n_initial'] == n_initial]

                total_collapse = sum(s['basin_b_count'] for s in summaries_for_condition)
                total_experiments_cond = sum(s['basin_a_count'] + s['basin_b_count'] for s in summaries_for_condition)
                collapse_pct = 100.0 * total_collapse / total_experiments_cond if total_experiments_cond > 0 else 0.0

                print(f"    N={n_initial:2d}: {collapse_pct:5.1f}% collapse ({total_collapse}/{total_experiments_cond})")

        print()

    print("=" * 80)
    print("ANALYSIS NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Logistic regression: P(collapse) ~ E_CONSUME + f + N + mechanism + interactions")
    print("2. Estimate f_critical(E_CONSUME, N) via sigmoid fits")
    print("3. Validate energy balance theory")
    print("4. Compare N-dependence at high vs low E_CONSUME")
    print("5. Generate 5 publication figures @ 300 DPI:")
    print("   - Collapse rate vs E_CONSUME (by frequency)")
    print("   - f_critical(E_CONSUME) scaling law with theory validation")
    print("   - N-dependence at high E_CONSUME")
    print("   - Death rates vs E_CONSUME")
    print("   - Energy balance validation")
    print()

if __name__ == "__main__":
    main()
