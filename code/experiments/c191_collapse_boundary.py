#!/usr/bin/env python3
"""
C191: Collapse Boundary Variation - Variance at the Edge

Tests whether stochastic variance affects collapse probability when operating near the
Basin A/Basin B boundary (f_intra < 1.0%).

Primary Hypothesis: Variance INCREASES collapse risk near boundary (fragility)

Experimental Design:
  - 3 spawn mechanisms: Deterministic, Hybrid Mid (c=0.50), Flat
  - 6 frequencies: 0.3%, 0.5%, 0.7%, 1.0%, 1.5%, 2.0%
  - 50 seeds per condition (high replication for collapse probability)
  - Total: 900 experiments

Key Metrics:
  - Collapse probability (% Basin B, final pop ≤ 2.5)
  - Mean population (among survivors only)
  - Collapse timing (cycle of extinction)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2 Sonnet 4.5)
Date: 2025-11-08 (Cycle 1319)
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
F_INTRA_PCT_CONDITIONS = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]  # Span collapse boundary
N_SEEDS = 50  # High replication for collapse probability estimation

# Certainty values for hybrid mechanisms
CERTAINTY_VALUES = {
    'deterministic': 1.0,
    'hybrid_mid': 0.50,  # 50% dropout
    'flat': 0.0,  # Full probabilistic
}

# System parameters (from C189/C190)
N_POP = 1  # Single population
N_INITIAL = 20  # Initial agents
CYCLES = 3000  # Sufficient for equilibrium

# Energy parameters (matching C189/C190)
E_INITIAL = 50.0  # Initial agent energy
E_SPAWN_THRESHOLD = 20.0  # Energy required to spawn
E_SPAWN_COST = 10.0  # Energy cost to parent (deducted on spawn)
RECHARGE_RATE = 0.5  # Energy recovered per cycle
CHILD_ENERGY_FRACTION = 0.5  # Offspring energy = E_INITIAL × this fraction

# NOTE: NO per-cycle consumption in C189/C190 model
# Agents only lose energy through spawning, not existence

# Basin classification
BASIN_A_THRESHOLD = 2.5  # > 2.5 agents = viable (Basin A)

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Seeds for reproducibility
BASE_SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606,
              707, 808, 909, 1010, 1111, 1212, 1313, 1414, 1515, 1616,
              1717, 1818, 1919, 2020, 2121, 2222, 2323, 2424, 2525, 2626,
              2727, 2828, 2929, 3030, 3131, 3232, 3333, 3434, 3535, 3636,
              3737, 3838, 3939, 4040, 4141, 4242, 4343, 4444, 4545, 4646]

# ============================================================================
# AGENT CLASS
# ============================================================================

class Agent:
    """Individual agent with energy dynamics (C189/C190 model)"""

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
        Attempt intra-population spawning (C189/C190 model)

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
        """Execute one simulation cycle (C189/C190 energy model)"""
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
    """Execute C191 experiments"""

    print("=" * 80)
    print("CYCLE 191: COLLAPSE BOUNDARY VARIATION - VARIANCE AT THE EDGE")
    print("=" * 80)
    print()

    print("Spawn Mechanisms:")
    for mech in SPAWN_MECHANISMS:
        certainty = CERTAINTY_VALUES[mech]
        print(f"  {mech:15s}: certainty={certainty:.2f}")
    print()

    print("Frequencies:")
    for f in F_INTRA_PCT_CONDITIONS:
        print(f"  f_intra = {f}% (interval={int(100/f)} cycles if interval-based)")
    print()

    print("Fixed Parameters:")
    print(f"  n_pop = {N_POP} (single population - isolate mechanism)")
    print(f"  N_initial = {N_INITIAL} agents")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {N_SEEDS} (high replication for collapse probability)")
    print()

    print("Hypotheses:")
    print("  H1: Variance INCREASES collapse risk (Flat > Hybrid > Deterministic)")
    print("  H2: Variance effect is frequency-dependent (only at low f)")
    print("  H3: C190 mean population finding replicates (among survivors)")
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

                # Progress
                basin_label = result['basin']
                collapse_str = f"collapse@{result['collapse_cycle']}" if result['collapse_cycle'] > 0 else "survived"

                print(f"[{experiment_num:3d}/{total_experiments}] "
                      f"{mechanism[:4]:4s}, f={f_intra_pct}%, seed={seed:5d}... "
                      f"Basin {basin_label}, pop={result['final_population']:3.0f}, "
                      f"spawns={result['intra_spawns']:2d}, {collapse_str}, "
                      f"t={elapsed:.3f}s")

            # Condition summary
            basin_a_count = sum(1 for r in condition_results if r['basin'] == 'A')
            basin_a_pct = 100.0 * basin_a_count / N_SEEDS

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

            print(f"Summary: Basin A {basin_a_count}/{N_SEEDS} ({basin_a_pct:.1f}%), "
                  f"mean(Basin A)={mean_pop_basin_a:.2f}±{std_pop_basin_a:.2f}, "
                  f"mean(all)={mean_pop_all:.2f}±{std_pop_all:.2f}, "
                  f"spawns_avg={spawns_avg:.1f}")
            print()

            # Store condition summary
            condition_summaries.append({
                'spawn_mechanism': mechanism,
                'f_intra_pct': f_intra_pct,
                'basin_a_count': basin_a_count,
                'basin_a_pct': basin_a_pct,
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
    output_file = OUTPUT_DIR / "c191_collapse_boundary.json"

    output_data = {
        'experiment': 'C191_COLLAPSE_BOUNDARY',
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
            'hypothesis': 'Variance INCREASES collapse risk near boundary (fragility)',
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
        print(f"f_intra = {f_intra_pct}%:")

        for mechanism in SPAWN_MECHANISMS:
            # Find condition summary
            summary = next(s for s in condition_summaries
                          if s['spawn_mechanism'] == mechanism and s['f_intra_pct'] == f_intra_pct)

            basin_a_pct = summary['basin_a_pct']
            collapse_pct = 100.0 - basin_a_pct

            print(f"  {mechanism:15s}: {collapse_pct:5.1f}% collapse (Basin A: {basin_a_pct:.1f}%)")

        print()

    print("=" * 80)
    print("ANALYSIS NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Chi-square test: Collapse % ~ Mechanism (for each frequency)")
    print("2. Logistic regression: Collapse ~ Mechanism + Frequency + Interaction")
    print("3. ANOVA: Mean population (Basin A only) ~ Mechanism")
    print("4. Kaplan-Meier survival curves (collapse timing)")
    print("5. Generate 5 publication figures @ 300 DPI")
    print()

if __name__ == "__main__":
    main()
