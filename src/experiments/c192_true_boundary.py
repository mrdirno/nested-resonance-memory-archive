#!/usr/bin/env python3
"""
C192: True Collapse Boundary Location

Locates the actual frequency at which the Basin A/B boundary exists by testing
frequencies below 0.3% (where C191 showed 100% survival).

Primary Hypothesis: Collapse boundary exists near energy balance critical point (f_critical ~ 0.05%)

Experimental Design:
  - 3 spawn mechanisms: Deterministic, Hybrid Mid (c=0.50), Flat
  - 10 frequencies: 0.05%, 0.08%, 0.10%, 0.12%, 0.15%, 0.18%, 0.20%, 0.23%, 0.25%, 0.30%
  - 100 seeds per condition (high replication for collapse probability estimation)
  - Total: 3,000 experiments

Key Metrics:
  - Collapse probability (% Basin B, final pop ≤ 2.5)
  - f_critical per mechanism (50% collapse point)
  - Mean population (among survivors only)
  - Collapse timing (cycle of extinction)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08 (Cycle 1320+)
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

# Experimental parameters
SPAWN_MECHANISMS = ['deterministic', 'hybrid_mid', 'flat']
F_INTRA_PCT_CONDITIONS = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.23, 0.25, 0.30]  # Search for boundary
N_SEEDS = 100  # High replication for collapse probability curves

# Certainty values for hybrid mechanisms
CERTAINTY_VALUES = {
    'deterministic': 1.0,
    'hybrid_mid': 0.50,  # 50% dropout
    'flat': 0.0,  # Full probabilistic
}

# System parameters (from C189/C190/C191)
N_POP = 1  # Single population
N_INITIAL = 20  # Initial agents
CYCLES = 5000  # Extended for slower dynamics

# Energy parameters (matching C189/C190/C191)
E_INITIAL = 50.0  # Initial agent energy
E_SPAWN_THRESHOLD = 20.0  # Energy required to spawn
E_SPAWN_COST = 10.0  # Energy cost to parent (deducted on spawn)
RECHARGE_RATE = 0.5  # Energy recovered per cycle
CHILD_ENERGY_FRACTION = 0.5  # Offspring energy = E_INITIAL × this fraction

# NOTE: NO per-cycle consumption in C189/C190/C191 model
# Agents only lose energy through spawning, not existence

# Basin classification
BASIN_A_THRESHOLD = 2.5  # > 2.5 agents = viable (Basin A)

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Seeds for reproducibility (100 unique seeds)
BASE_SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606,
              1695, 779, 6959, 2443, 5321, 5061, 6430, 1194, 4565, 3395,
              6406, 8676, 9284, 2568, 7859, 2057, 2757, 9177, 199, 2744,
              3015, 4668, 1909, 7744, 1277, 1538, 3566, 3900, 8848, 5403,
              8802, 8443, 7523, 2622, 7051, 9565, 6245, 5496, 7109, 9680,
              785, 8236, 3162, 1595, 3953, 7565, 3083, 1031, 3853, 7999,
              9702, 6883, 5685, 171, 4307, 1005, 7639, 9477, 1026, 7879,
              6449, 7902, 6873, 7926, 8539, 888, 9278, 4897, 4869, 6341,
              8581, 8694, 7218, 5286, 2072, 74, 8016, 2578, 5473, 2037,
              2705, 9697, 5268, 5628, 6746, 401, 5902, 3571, 6194, 3109]

# ============================================================================
# AGENT CLASS
# ============================================================================

class Agent:
    """Individual agent with energy dynamics (C189/C190/C191 model)"""

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
        Attempt intra-population spawning (C189/C190/C191 model)

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
      - Hybrid: interval-based with dropout (certainty=0.50)
      - Flat: probabilistic per-cycle (certainty=0.0)
    """

    def __init__(self,
                 spawn_mechanism: str,
                 f_intra_pct: float,
                 n_initial: int = N_INITIAL,
                 cycles: int = CYCLES,
                 seed: int = 42):
        """
        Initialize system

        Args:
            spawn_mechanism: 'deterministic', 'hybrid_mid', or 'flat'
            f_intra_pct: Intra-population spawn frequency (%)
            n_initial: Initial population size
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

        if spawn_mechanism in ['deterministic', 'hybrid_mid']:
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
          - Hybrid Mid (c=0.50): Every spawn_interval with 50% dropout
          - Flat (c=0.0): Probabilistic per-cycle
        """
        if self.population.size() == 0:
            return

        if self.spawn_mechanism == 'flat':
            # Probabilistic per-cycle
            if self.random.random() < self.spawn_probability:
                self.population.spawn_attempt()
        else:
            # Interval-based (deterministic or hybrid)
            if (self.cycle_count % self.spawn_interval) == 0:
                # Hybrid: apply dropout via certainty parameter
                if self.random.random() < self.certainty:
                    self.population.spawn_attempt()

    def step(self):
        """Execute one simulation cycle (C189/C190/C191 energy model)"""
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

def run_experiment(mechanism: str, f_intra_pct: float, seed: int) -> Dict:
    """Run single experiment"""
    system = SinglePopulationSystem(
        spawn_mechanism=mechanism,
        f_intra_pct=f_intra_pct,
        seed=seed
    )
    return system.run()

def main():
    """Execute C192 experiments"""

    print("=" * 80)
    print("CYCLE 192: TRUE COLLAPSE BOUNDARY LOCATION")
    print("=" * 80)
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
    print(f"  n_pop = {N_POP} (single population - isolate mechanism)")
    print(f"  N_initial = {N_INITIAL} agents")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {N_SEEDS} (high replication for collapse probability curves)")
    print()

    print("Hypotheses:")
    print("  H1: Collapse boundary exists near f_critical ~ 0.05% (energy balance)")
    print("  H2: Deterministic has lowest f_critical (most robust)")
    print("  H3: Transition is gradual (sigmoid curve, not cliff)")
    print()

    print("Energy Balance Theory:")
    f_critical_theory = 100 * RECHARGE_RATE / E_SPAWN_COST
    print(f"  f_critical = RECHARGE_RATE / E_SPAWN_COST")
    print(f"             = {RECHARGE_RATE} / {E_SPAWN_COST}")
    print(f"             ≈ {f_critical_theory:.3f}%")
    print()

    total_experiments = len(SPAWN_MECHANISMS) * len(F_INTRA_PCT_CONDITIONS) * N_SEEDS
    print(f"Total Experiments: {len(SPAWN_MECHANISMS)} mech × {len(F_INTRA_PCT_CONDITIONS)} freq × {N_SEEDS} seeds = {total_experiments}")
    print()

    print("-" * 80)
    print()

    # Storage
    results = []
    condition_summaries = []

    experiment_num = 0
    start_time_total = time.time()

    # Execute experiments
    for mechanism in SPAWN_MECHANISMS:
        for f_intra_pct in F_INTRA_PCT_CONDITIONS:
            # Run all seeds for this condition
            condition_results = []

            print(f"CONDITION: {mechanism.upper()}, f_intra={f_intra_pct}%")
            print(f"  Certainty: {CERTAINTY_VALUES[mechanism]:.2f}")
            print("-" * 40)

            for i, seed in enumerate(BASE_SEEDS[:N_SEEDS]):
                experiment_num += 1

                start_time = time.time()

                # Run experiment
                result = run_experiment(mechanism, f_intra_pct, seed)

                elapsed = time.time() - start_time

                # Store
                results.append(result)
                condition_results.append(result)

                # Progress (print every 10th to avoid clutter)
                if (i + 1) % 10 == 0 or (i + 1) == N_SEEDS:
                    basin_label = result['basin']
                    collapse_str = f"collapse@{result['collapse_cycle']}" if result['collapse_cycle'] > 0 else "survived"

                    print(f"[{experiment_num:4d}/{total_experiments}] "
                          f"{mechanism[:4]:4s}, f={f_intra_pct:>5.2f}%, seed={seed:5d}... "
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
    output_file = OUTPUT_DIR / "c192_true_boundary.json"

    output_data = {
        'experiment': 'C192_TRUE_BOUNDARY',
        'date': datetime.now().isoformat(),
        'metadata': {
            'spawn_mechanisms': SPAWN_MECHANISMS,
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': N_SEEDS,
            'certainty_values': CERTAINTY_VALUES,
            'basin_a_threshold': BASIN_A_THRESHOLD,
            'f_critical_theory': 100 * RECHARGE_RATE / E_SPAWN_COST,
            'hypothesis': 'Collapse boundary exists near energy balance critical point (f_critical ~ 0.05%)',
        },
        'condition_summaries': condition_summaries,
        'individual_results': results,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    print("Collapse Summary by Frequency:")
    print()

    for f_intra_pct in F_INTRA_PCT_CONDITIONS:
        print(f"f_intra = {f_intra_pct:>5.2f}%:")

        for mechanism in SPAWN_MECHANISMS:
            # Find condition summary
            summary = next(s for s in condition_summaries
                          if s['spawn_mechanism'] == mechanism and s['f_intra_pct'] == f_intra_pct)

            collapse_pct = summary['collapse_pct']
            basin_a_pct = summary['basin_a_pct']

            print(f"  {mechanism:15s}: {collapse_pct:5.1f}% collapse, {basin_a_pct:5.1f}% survive")

        print()

    print("=" * 80)
    print("ANALYSIS NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Logistic regression: P(collapse) ~ f + mechanism + interaction")
    print("2. Estimate f_critical per mechanism (50% collapse point)")
    print("3. Chi-square test: Collapse % ~ Mechanism (at each frequency)")
    print("4. ANOVA: Mean population (Basin A only) ~ Mechanism + Frequency")
    print("5. Generate 5 publication figures @ 300 DPI:")
    print("   - Collapse rate vs frequency (sigmoid curves)")
    print("   - f_critical comparison (bar chart)")
    print("   - Mean population vs frequency (Basin A only)")
    print("   - Kaplan-Meier survival curves")
    print("   - Energy balance theory validation")
    print()

if __name__ == "__main__":
    main()
