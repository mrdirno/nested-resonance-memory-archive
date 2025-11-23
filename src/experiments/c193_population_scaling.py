#!/usr/bin/env python3
"""
C193: Population Size Scaling Law (f_critical vs N_initial)

After three campaigns with ZERO collapses (C190, C191, C192), this experiment tests
the hypothesis that the collapse boundary depends on initial population size (N_initial),
not frequency alone.

Research Question: How does f_critical scale with N_initial?

Experimental Design:
  - 4 N_initial values: 5, 10, 15, 20 (span 4× range)
  - 2 spawn mechanisms: Deterministic (most robust), Flat (least robust from C191/C192)
  - 3 frequencies: 0.05%, 0.10%, 0.20% (around predicted f_critical for small N)
  - 50 seeds per condition (balance precision and time)
  - Total: 1,200 experiments

Hypotheses:
  H1: f_critical scales inversely with N_initial (f_critical ∝ 1/N)
  H2: Critical population exists (N_critical ≈ 10-15 agents)
  H3: Deterministic more robust than Flat at low N

Predictions:
  - N=5: Will show collapse at f=0.05% or f=0.10%
  - N=10: Transitional (some collapse at f=0.05%)
  - N=15: Mostly viable (rare collapse)
  - N=20: Replicates C192 (zero collapse)

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

# Experimental parameters (NEW: N_initial as variable)
N_INITIAL_CONDITIONS = [5, 10, 15, 20]  # Test population size scaling
SPAWN_MECHANISMS = ['deterministic', 'flat']  # Focus on extremes
F_INTRA_PCT_CONDITIONS = [0.05, 0.10, 0.20]  # Range around predicted f_critical for small N
N_SEEDS = 50  # Balance precision and execution time

# Certainty values for spawn mechanisms
CERTAINTY_VALUES = {
    'deterministic': 1.0,  # Zero dropout (most robust)
    'flat': 0.0,  # Full probabilistic (least robust from C191/C192)
}

# System parameters (from C192)
N_POP = 1  # Single population
CYCLES = 5000  # Extended for slower dynamics

# Energy parameters (matching C189/C190/C191/C192)
E_INITIAL = 50.0  # Initial agent energy
E_SPAWN_THRESHOLD = 20.0  # Energy required to spawn
E_SPAWN_COST = 10.0  # Energy cost to parent (deducted on spawn)
RECHARGE_RATE = 0.5  # Energy recovered per cycle
CHILD_ENERGY_FRACTION = 0.5  # Offspring energy = E_INITIAL × this fraction

# NOTE: NO per-cycle consumption in C189/C190/C191/C192 model
# Agents only lose energy through spawning, not existence

# Basin classification
BASIN_A_THRESHOLD = 2.5  # > 2.5 agents = viable (Basin A)

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Seeds for reproducibility (50 unique seeds)
BASE_SEEDS = [42, 123, 456, 789, 101,  # Match C191/C192 baseline
              5661, 7296, 9074, 5127, 2734, 9846, 8394, 6229, 3831, 5009,
              1695, 779, 6959, 2443, 5321, 5061, 6430, 1194, 4565, 3395,
              6406, 8676, 9284, 2568, 7859, 2057, 2757, 9177, 199, 2744,
              3015, 4668, 1909, 7744, 1277, 1538, 3566, 3900, 8848, 5403,
              8802, 8443, 7523, 2622, 7051]

# ============================================================================
# AGENT CLASS
# ============================================================================

class Agent:
    """Individual agent with energy dynamics (C192 model)"""

    def __init__(self, energy: float = E_INITIAL):
        self.energy = energy
        self.age = 0

    def increment_age(self):
        """Increment age (agents don't die from age or energy in this model)"""
        self.age += 1

# ============================================================================
# POPULATION CLASS
# ============================================================================

class Population:
    """Population of agents with spawn mechanics"""

    def __init__(self, n_initial: int, random_state):
        self.agents: List[Agent] = [Agent() for _ in range(n_initial)]
        self.random = random_state
        self.spawn_count = 0
        self.spawn_failures = 0

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

    def recharge_energy(self):
        """All agents recover energy per cycle"""
        for agent in self.agents:
            agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def spawn_attempt(self) -> bool:
        """
        Attempt intra-population spawning (C192 model)

        Returns:
            True if spawn succeeded, False otherwise
        """
        if self.size() == 0:
            self.spawn_failures += 1
            return False

        # Random parent selection
        parent = self.random.choice(self.agents)

        # Check if parent has enough energy
        if parent.energy >= E_SPAWN_THRESHOLD:
            # Successful spawn: create offspring, deplete parent
            offspring_energy = E_INITIAL * CHILD_ENERGY_FRACTION
            offspring = Agent(energy=offspring_energy)
            self.agents.append(offspring)
            parent.energy -= E_SPAWN_COST  # Parent loses E_SPAWN_COST, not E_SPAWN_THRESHOLD
            self.spawn_count += 1
            return True
        else:
            self.spawn_failures += 1
            return False

# ============================================================================
# SINGLE-POPULATION SYSTEM
# ============================================================================

class SinglePopulationSystem:
    """
    Single-population system with spawn mechanism variation

    Supports:
      - Deterministic: interval-based (certainty=1.0)
      - Flat: probabilistic per-cycle (certainty=0.0)
    """

    def __init__(self,
                 spawn_mechanism: str,
                 f_intra_pct: float,
                 n_initial: int,
                 cycles: int = CYCLES,
                 seed: int = 42):
        """
        Initialize system

        Args:
            spawn_mechanism: 'deterministic' or 'flat'
            f_intra_pct: Intra-population spawn frequency (%)
            n_initial: Initial population size (VARIABLE in C193)
            cycles: Number of simulation cycles
            seed: Random seed for reproducibility
        """
        self.spawn_mechanism = spawn_mechanism
        self.f_intra_pct = f_intra_pct
        self.n_initial = n_initial
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

        # Initialize population with variable n_initial
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
                self.population.spawn_attempt()
        else:
            # Interval-based (deterministic)
            if (self.cycle_count % self.spawn_interval) == 0:
                if self.random.random() < self.certainty:
                    self.population.spawn_attempt()

    def step(self):
        """Execute one simulation cycle (C192 energy model)"""
        # Track collapse
        if self.collapse_cycle is None and self.population.size() <= BASIN_A_THRESHOLD:
            self.collapse_cycle = self.cycle_count

        # Energy recovery
        self.population.recharge_energy()

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
            self.step()

        # Final population
        final_population = self.population.size()

        # Basin classification
        basin = 'A' if final_population > BASIN_A_THRESHOLD else 'B'

        # Results
        results = {
            'spawn_mechanism': self.spawn_mechanism,
            'f_intra_pct': self.f_intra_pct,
            'n_initial': self.n_initial,  # NEW: track N_initial
            'seed': self.seed,
            'basin': basin,
            'final_population': final_population,
            'mean_energy': self.population.mean_energy(),
            'intra_spawns': self.population.spawn_count,
            'spawn_failures': self.population.spawn_failures,
            'collapse_cycle': self.collapse_cycle if self.collapse_cycle is not None else -1,
            'certainty': self.certainty,
            'spawn_interval': self.spawn_interval,
            'spawn_probability': self.spawn_probability,
        }

        return results

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_experiment(mechanism: str, f_intra_pct: float, n_initial: int, seed: int) -> Dict:
    """Run single experiment"""
    system = SinglePopulationSystem(
        spawn_mechanism=mechanism,
        f_intra_pct=f_intra_pct,
        n_initial=n_initial,  # NEW: variable N_initial
        seed=seed
    )
    return system.run()

def main():
    """Execute C193 experiments"""

    print("=" * 80)
    print("CYCLE 193: POPULATION SIZE SCALING LAW (f_critical vs N_initial)")
    print("=" * 80)
    print()

    print("Research Context:")
    print("  C190: 400 experiments, f ≥ 1.0% → ZERO collapses")
    print("  C191: 900 experiments, f ≥ 0.3% → ZERO collapses")
    print("  C192: 3,000 experiments, f ≥ 0.05% → ZERO collapses")
    print("  Total: 4,800+ experiments, 40× frequency range, ZERO collapses")
    print()
    print("Interpretation: Collapse boundary likely depends on N_initial (population size)")
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

    print("Hypotheses:")
    print("  H1: f_critical scales inversely with N_initial (f_critical ∝ 1/N)")
    print("  H2: Critical population exists (N_critical ≈ 10-15 agents)")
    print("  H3: Deterministic more robust than Flat at low N")
    print()

    print("Predictions:")
    print("  N=5:  Will show collapse at f=0.05% or f=0.10%")
    print("  N=10: Transitional (some collapse at f=0.05%)")
    print("  N=15: Mostly viable (rare collapse)")
    print("  N=20: Replicates C192 (zero collapse)")
    print()

    total_experiments = len(N_INITIAL_CONDITIONS) * len(SPAWN_MECHANISMS) * len(F_INTRA_PCT_CONDITIONS) * N_SEEDS
    print(f"Total Experiments: {len(N_INITIAL_CONDITIONS)} N × {len(SPAWN_MECHANISMS)} mech × {len(F_INTRA_PCT_CONDITIONS)} freq × {N_SEEDS} seeds = {total_experiments}")
    print()

    print("-" * 80)
    print()

    # Storage
    results = []
    condition_summaries = []

    experiment_num = 0
    start_time_total = time.time()

    # Execute experiments (NEW: loop over N_initial)
    for n_initial in N_INITIAL_CONDITIONS:
        for mechanism in SPAWN_MECHANISMS:
            for f_intra_pct in F_INTRA_PCT_CONDITIONS:
                # Run all seeds for this condition
                condition_results = []

                print(f"CONDITION: N={n_initial}, {mechanism.upper()}, f_intra={f_intra_pct}%")
                print(f"  Certainty: {CERTAINTY_VALUES[mechanism]:.2f}")
                print("-" * 40)

                for i, seed in enumerate(BASE_SEEDS[:N_SEEDS]):
                    experiment_num += 1

                    start_time = time.time()

                    # Run experiment
                    result = run_experiment(mechanism, f_intra_pct, n_initial, seed)

                    elapsed = time.time() - start_time

                    # Store
                    results.append(result)
                    condition_results.append(result)

                    # Progress (print every 10th to avoid clutter)
                    if (i + 1) % 10 == 0 or (i + 1) == N_SEEDS:
                        basin_label = result['basin']
                        collapse_str = f"collapse@{result['collapse_cycle']}" if result['collapse_cycle'] > 0 else "survived"

                        print(f"[{experiment_num:4d}/{total_experiments}] "
                              f"N={n_initial:2d}, {mechanism[:4]:4s}, f={f_intra_pct:>5.2f}%, seed={seed:5d}... "
                              f"Basin {basin_label}, pop={result['final_population']:3.0f}, "
                              f"spawns={result['intra_spawns']:3d}, {collapse_str:15s}, "
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

                # Mean population (all runs, including collapses)
                all_pops = [r['final_population'] for r in condition_results]
                mean_pop_all = np.mean(all_pops)
                std_pop_all = np.std(all_pops, ddof=1)

                # Spawns
                spawns_avg = np.mean([r['intra_spawns'] for r in condition_results])

                print(f"Summary: Collapse {basin_b_count}/{N_SEEDS} ({collapse_pct:.1f}%), "
                      f"Survive {basin_a_count}/{N_SEEDS} ({basin_a_pct:.1f}%), "
                      f"mean(Basin A)={mean_pop_basin_a:.2f}±{std_pop_basin_a:.2f}, "
                      f"spawns_avg={spawns_avg:.1f}")
                print()

                # Store condition summary
                condition_summaries.append({
                    'n_initial': n_initial,  # NEW
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
                    'certainty': CERTAINTY_VALUES[mechanism],
                })

    total_elapsed = time.time() - start_time_total

    print("=" * 80)
    print(f"EXPERIMENTS COMPLETE: {total_experiments} experiments in {total_elapsed:.1f}s")
    print("=" * 80)
    print()

    # Save results
    output_file = OUTPUT_DIR / "c193_population_scaling.json"

    output_data = {
        'experiment': 'C193_POPULATION_SCALING',
        'date': datetime.now().isoformat(),
        'metadata': {
            'n_initial_conditions': N_INITIAL_CONDITIONS,
            'spawn_mechanisms': SPAWN_MECHANISMS,
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'n_pop': N_POP,
            'cycles': CYCLES,
            'n_seeds': N_SEEDS,
            'certainty_values': CERTAINTY_VALUES,
            'basin_a_threshold': BASIN_A_THRESHOLD,
            'hypothesis': 'f_critical scales inversely with N_initial (f_critical ∝ 1/N)',
        },
        'condition_summaries': condition_summaries,
        'individual_results': results,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    print("Collapse Summary by N_initial and Frequency:")
    print()

    for n_initial in N_INITIAL_CONDITIONS:
        print(f"N_initial = {n_initial:2d}:")

        for f_intra_pct in F_INTRA_PCT_CONDITIONS:
            print(f"  f_intra = {f_intra_pct:>5.2f}%:")

            for mechanism in SPAWN_MECHANISMS:
                # Find condition summary
                summary = next(s for s in condition_summaries
                              if s['n_initial'] == n_initial
                              and s['spawn_mechanism'] == mechanism
                              and s['f_intra_pct'] == f_intra_pct)

                collapse_pct = summary['collapse_pct']
                basin_a_pct = summary['basin_a_pct']

                print(f"    {mechanism:15s}: {collapse_pct:5.1f}% collapse, {basin_a_pct:5.1f}% survive")

        print()

    print("=" * 80)
    print("ANALYSIS NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Logistic regression: P(collapse) ~ f + N + mechanism + f×N + f×mechanism")
    print("2. Estimate f_critical(N) scaling law via power law fit")
    print("3. Identify N_critical (50% collapse point)")
    print("4. Compare mechanisms (Deterministic vs Flat across N)")
    print("5. Generate 4 publication figures @ 300 DPI:")
    print("   - Collapse rate vs N_initial (by frequency)")
    print("   - f_critical(N) scaling law with power law fit")
    print("   - Mechanism comparison across N values")
    print("   - Mean population vs N and f (Basin A only)")
    print()

if __name__ == "__main__":
    main()
