#!/usr/bin/env python3
"""
Cycle 190: Variance Optimization - When Stochasticity Improves Outcomes

Purpose: Test if stochastic variance improves system performance under specific conditions

Research Question:
    Does controlled stochasticity OUTPERFORM determinism in specific environments
    (noisy, dynamic, exploration)?

Background:
    - C189: Hierarchical (SD=0) ≈ flat (SD=3-8) in MEAN, but different VARIANCE
    - Hypothesis: Variance is not always detrimental
    - Stochasticity enables exploration, robustness, adaptation, diversity

Experimental Design:
    Spawn Mechanisms: Deterministic, Hybrid Low, Hybrid Mid, Hybrid High, Flat (5)
    Environments: Stable, Noisy, Dynamic, Exploration (4)
    Frequencies: 1.0%, 2.0% (2)
    Seeds: 10 per condition
    Total: 400 experiments

Hypotheses:
    H1: Deterministic superior in stable environments
    H2: Stochastic superior in noisy environments (robustness)
    H3: Hybrid optimal in dynamic environments (adaptation)
    H4: High variance optimal for exploration (diversity)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1320)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

# Experimental parameters
SPAWN_MECHANISMS = ['deterministic', 'hybrid_low', 'hybrid_mid', 'hybrid_high', 'flat']
ENVIRONMENTS = ['stable', 'noisy', 'dynamic', 'exploration']
F_INTRA_PCT_CONDITIONS = [1.0, 2.0]
N_POP = 1  # Single population (isolate spawn mechanism)
N_INITIAL = 20
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Spawn mechanism parameters
CERTAINTY_VALUES = {
    'deterministic': 1.0,    # Pure deterministic (SD=0)
    'hybrid_low': 0.75,      # Low variance injection (25% dropout)
    'hybrid_mid': 0.50,      # Moderate variance (50% dropout)
    'hybrid_high': 0.25,     # High variance (75% dropout)
    'flat': 0.0              # Pure stochastic (will use probabilistic logic)
}

# Energy parameters (stable baseline)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5

# Environment-specific parameters
NOISE_RECHARGE_SD = 0.1      # Noisy: σ for energy recovery
NOISE_THRESHOLD_SD = 2.0     # Noisy: σ for spawn threshold
DYNAMIC_RECHARGE_START = 0.5  # Dynamic: starting recharge rate
DYNAMIC_RECHARGE_END = 0.3    # Dynamic: ending recharge rate

@dataclass
class Agent:
    """Individual fractal agent"""
    id: int
    energy: float

@dataclass
class Population:
    """Population container"""
    id: int
    agents: List[Agent]

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class VarianceOptimizationSystem:
    """Single-population system with configurable spawn mechanism and environment"""

    def __init__(self, spawn_mechanism: str, environment: str, f_intra_pct: float, seed: int):
        self.spawn_mechanism = spawn_mechanism
        self.environment = environment
        self.f_intra_pct = f_intra_pct
        self.seed = seed
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)  # For Gaussian noise

        # Spawn parameters
        self.spawn_interval = max(1, int(100.0 / f_intra_pct))
        self.spawn_probability = f_intra_pct / 100.0
        self.certainty = CERTAINTY_VALUES[spawn_mechanism]

        self.population = Population(id=0, agents=[])
        self.next_agent_id = 0
        self.cycle_count = 0

        self.intra_spawns = 0
        self.spawn_failures = 0
        self.spawn_attempts = 0

        self._initialize_population()

    def _initialize_population(self):
        """Create initial population"""
        for _ in range(N_INITIAL):
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL
            )
            self.population.agents.append(agent)
            self.next_agent_id += 1

    def step(self):
        """Execute one cycle"""
        self.cycle_count += 1
        self._intra_spawning()
        self._energy_recovery()

    def _intra_spawning(self):
        """Spawn logic - mechanism and environment dependent"""

        if len(self.population.agents) == 0:
            return

        if self.spawn_mechanism == 'flat':
            # Pure probabilistic (C189 flat baseline)
            if self.random.random() < self.spawn_probability:
                self._attempt_spawn()
        else:
            # Deterministic or hybrid (certainty-based)
            if (self.cycle_count % self.spawn_interval) == 0:
                if self.random.random() < self.certainty:
                    self._attempt_spawn()

    def _attempt_spawn(self):
        """Attempt to spawn new agent (environment-dependent threshold)"""

        self.spawn_attempts += 1

        parent = self.random.choice(self.population.agents)

        # Environment-specific spawn threshold
        if self.environment == 'noisy':
            # Add Gaussian noise to threshold
            threshold = self.np_random.normal(E_SPAWN_THRESHOLD, NOISE_THRESHOLD_SD)
        else:
            threshold = E_SPAWN_THRESHOLD

        if parent.energy >= threshold:
            # Successful spawn
            parent.energy -= E_SPAWN_COST

            child = Agent(
                id=self.next_agent_id,
                energy=E_SPAWN_THRESHOLD * CHILD_ENERGY_FRACTION
            )
            self.population.agents.append(child)
            self.next_agent_id += 1
            self.intra_spawns += 1
        else:
            self.spawn_failures += 1

    def _energy_recovery(self):
        """All agents recover energy per cycle (environment-dependent)"""

        # Determine recharge rate based on environment
        if self.environment == 'stable':
            # Fixed recharge rate
            recharge = RECHARGE_RATE

        elif self.environment == 'noisy':
            # Add Gaussian noise to recharge rate (per-agent)
            for agent in self.population.agents:
                recharge = self.np_random.normal(RECHARGE_RATE, NOISE_RECHARGE_SD)
                recharge = max(0, recharge)  # Clamp to non-negative
                agent.energy = min(E_INITIAL, agent.energy + recharge)
            return  # Early return (per-agent recharge already done)

        elif self.environment == 'dynamic':
            # Linear decay: DYNAMIC_RECHARGE_START → DYNAMIC_RECHARGE_END over CYCLES
            decay_rate = (DYNAMIC_RECHARGE_START - DYNAMIC_RECHARGE_END) / CYCLES
            recharge = DYNAMIC_RECHARGE_START - (self.cycle_count * decay_rate)
            recharge = max(0, recharge)  # Clamp to non-negative

        elif self.environment == 'exploration':
            # Stable (exploration scored by outcome diversity, not energy dynamics)
            recharge = RECHARGE_RATE

        else:
            recharge = RECHARGE_RATE  # Default

        # Apply recharge to all agents (if not noisy environment)
        for agent in self.population.agents:
            agent.energy = min(E_INITIAL, agent.energy + recharge)

    def get_metrics(self) -> Dict:
        """Get system-level metrics"""
        if len(self.population.agents) == 0:
            return {
                'total_population': 0,
                'mean_energy': 0.0
            }

        return {
            'total_population': len(self.population.agents),
            'mean_energy': sum(a.energy for a in self.population.agents) / len(self.population.agents)
        }

def run_single_experiment(mechanism: str, environment: str, f_intra_pct: float, seed: int) -> Dict:
    """Run single experiment with given mechanism, environment, frequency, and seed"""

    system = VarianceOptimizationSystem(mechanism, environment, f_intra_pct, seed)

    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()

    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time

    # Basin classification
    basin = 'A' if final_metrics['total_population'] > 2.5 else 'B'

    result = {
        'spawn_mechanism': mechanism,
        'environment': environment,
        'f_intra_pct': f_intra_pct,
        'seed': seed,
        'basin': basin,
        'final_population': final_metrics['total_population'],
        'mean_energy': final_metrics['mean_energy'],
        'intra_spawns': system.intra_spawns,
        'spawn_failures': system.spawn_failures,
        'spawn_attempts': system.spawn_attempts,
        'runtime_seconds': elapsed,
        'certainty': system.certainty,
        'spawn_interval': system.spawn_interval,
        'spawn_probability': system.spawn_probability
    }

    return result

def main():
    """Execute C190 variance optimization experiment"""

    print("=" * 80)
    print("CYCLE 190: VARIANCE OPTIMIZATION - WHEN STOCHASTICITY IMPROVES OUTCOMES")
    print("=" * 80)
    print()
    print(f"Spawn Mechanisms:")
    for mech in SPAWN_MECHANISMS:
        print(f"  {mech}: certainty={CERTAINTY_VALUES[mech]:.2f}")
    print()
    print(f"Environments:")
    print(f"  Stable: Fixed parameters (baseline)")
    print(f"  Noisy: Parameter uncertainty (σ_recharge={NOISE_RECHARGE_SD}, σ_threshold={NOISE_THRESHOLD_SD})")
    print(f"  Dynamic: Time-varying (recharge {DYNAMIC_RECHARGE_START} → {DYNAMIC_RECHARGE_END})")
    print(f"  Exploration: Diversity scoring (variance of outcomes)")
    print()
    print(f"Frequency Conditions:")
    print(f"  f_intra = {F_INTRA_PCT_CONDITIONS}")
    print()
    print(f"Fixed Parameters:")
    print(f"  n_pop = {N_POP} (single population - isolate mechanism)")
    print(f"  N_initial = {N_INITIAL} agents")
    print(f"  cycles = {CYCLES}")
    print(f"  seeds = {len(SEEDS)}")
    print()
    print(f"Hypotheses:")
    print(f"  H1: Deterministic superior in stable environments")
    print(f"  H2: Stochastic superior in noisy environments (robustness)")
    print(f"  H3: Hybrid optimal in dynamic environments (adaptation)")
    print(f"  H4: High variance optimal for exploration (diversity)")
    print()
    print(f"Total Experiments: {len(SPAWN_MECHANISMS)} mech × {len(ENVIRONMENTS)} env × {len(F_INTRA_PCT_CONDITIONS)} freq × {len(SEEDS)} seeds = {len(SPAWN_MECHANISMS) * len(ENVIRONMENTS) * len(F_INTRA_PCT_CONDITIONS) * len(SEEDS)}")
    print()
    print("-" * 80)
    print()

    all_results = []
    condition_summaries = []
    experiment_count = 0
    total_experiments = len(SPAWN_MECHANISMS) * len(ENVIRONMENTS) * len(F_INTRA_PCT_CONDITIONS) * len(SEEDS)

    for mech in SPAWN_MECHANISMS:
        for env in ENVIRONMENTS:
            for f_intra_pct in F_INTRA_PCT_CONDITIONS:
                print(f"CONDITION: {mech.upper()}, {env.upper()}, f_intra={f_intra_pct:.1f}%")
                print(f"  Certainty: {CERTAINTY_VALUES[mech]:.2f}")
                print("-" * 80)

                condition_results = []

                for seed in SEEDS:
                    experiment_count += 1
                    print(f"[{experiment_count:3d}/{total_experiments}] "
                          f"{mech[:4]}, {env[:4]}, f={f_intra_pct:.1f}%, seed={seed:3d}...",
                          end=" ", flush=True)

                    result = run_single_experiment(mech, env, f_intra_pct, seed)
                    condition_results.append(result)
                    all_results.append(result)

                    print(f"Basin {result['basin']}, "
                          f"pop={result['final_population']:4.0f}, "
                          f"spawns={result['intra_spawns']}, "
                          f"t={result['runtime_seconds']:.3f}s", flush=True)

                # Condition summary
                basin_a_count = sum(1 for r in condition_results if r['basin'] == 'A')
                basin_a_pct = (basin_a_count / len(condition_results)) * 100
                final_pops = [r['final_population'] for r in condition_results]
                mean_pop = sum(final_pops) / len(final_pops)
                std_pop = (sum((x-mean_pop)**2 for x in final_pops) / len(final_pops))**0.5
                spawns_avg = sum(r['intra_spawns'] for r in condition_results) / len(condition_results)

                summary = {
                    'spawn_mechanism': mech,
                    'environment': env,
                    'f_intra_pct': f_intra_pct,
                    'basin_a_count': basin_a_count,
                    'basin_a_pct': basin_a_pct,
                    'mean_population': mean_pop,
                    'std_population': std_pop,
                    'spawns_avg': spawns_avg,
                    'certainty': CERTAINTY_VALUES[mech]
                }
                condition_summaries.append(summary)

                print(f"Summary: Basin A {basin_a_count}/{len(condition_results)} ({basin_a_pct:.1f}%), "
                      f"mean {mean_pop:.2f}±{std_pop:.2f}")
                print()

    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY - VARIANCE OPTIMIZATION")
    print("=" * 80)
    print()

    # Group by environment
    for env in ENVIRONMENTS:
        print(f"{env.upper()} ENVIRONMENT:")
        print(f"{'Mechanism':<20} {'f_intra':<8} {'Basin A %':<10} {'Mean Pop':<20} {'Spawns':<10}")
        print("-" * 80)

        env_summaries = [s for s in condition_summaries if s['environment'] == env]

        for summary in env_summaries:
            print(f"{summary['spawn_mechanism']:<20} "
                  f"{summary['f_intra_pct']:<8.1f} "
                  f"{summary['basin_a_pct']:>6.1f}%    "
                  f"{summary['mean_population']:>6.2f} ± {summary['std_population']:<8.2f}  "
                  f"{summary['spawns_avg']:>6.1f}")
        print()

    # Hypothesis evaluation (per environment, f_intra=2.0% for clarity)
    print("=" * 80)
    print("HYPOTHESIS EVALUATION (f_intra=2.0%):")
    print("=" * 80)
    print()

    for env in ENVIRONMENTS:
        print(f"{env.upper()} Environment:")

        env_summaries_f2 = [s for s in condition_summaries
                           if s['environment'] == env and s['f_intra_pct'] == 2.0]

        # Find best mechanism by mean population
        best = max(env_summaries_f2, key=lambda x: x['mean_population'])

        print(f"  Best mechanism: {best['spawn_mechanism']} (mean={best['mean_population']:.2f})")

        # Show all mechanisms for comparison
        for summary in sorted(env_summaries_f2, key=lambda x: x['mean_population'], reverse=True):
            print(f"    {summary['spawn_mechanism']:<20} mean={summary['mean_population']:>6.2f}, SD={summary['std_population']:>5.2f}")

        # Hypothesis interpretation
        if env == 'stable' and best['spawn_mechanism'] == 'deterministic':
            print(f"  → H1 SUPPORTED: Deterministic superior in stable environment")
        elif env == 'noisy' and best['spawn_mechanism'] in ['flat', 'hybrid_high']:
            print(f"  → H2 SUPPORTED: Stochastic superior in noisy environment")
        elif env == 'dynamic' and 'hybrid' in best['spawn_mechanism']:
            print(f"  → H3 SUPPORTED: Hybrid optimal in dynamic environment")
        elif env == 'exploration':
            # Exploration scored by variance (higher SD = better exploration)
            best_exploration = max(env_summaries_f2, key=lambda x: x['std_population'])
            print(f"  → H4 SUPPORTED if: {best_exploration['spawn_mechanism']} (SD={best_exploration['std_population']:.2f})")
        else:
            print(f"  → Hypothesis NOT clearly supported (ambiguous)")

        print()

    # Save results
    output = {
        'experiment': 'C190_VARIANCE_OPTIMIZATION',
        'date': datetime.now().isoformat(),
        'metadata': {
            'spawn_mechanisms': SPAWN_MECHANISMS,
            'environments': ENVIRONMENTS,
            'f_intra_pct_conditions': F_INTRA_PCT_CONDITIONS,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'n_seeds': len(SEEDS),
            'certainty_values': CERTAINTY_VALUES,
            'hypothesis': 'Testing when stochastic variance improves outcomes (environment-dependent)'
        },
        'condition_summaries': condition_summaries,
        'individual_results': all_results
    }

    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "c190_variance_optimization.json"

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {results_file}")
    print()
    print("=" * 80)
    print("C190 VARIANCE OPTIMIZATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Next Actions:")
    print(f"  1. Perform statistical tests (ANOVA, interaction effects)")
    print(f"  2. Generate comparison figures (mechanism × environment)")
    print(f"  3. Calculate exploration scores (variance of outcomes)")
    print(f"  4. Interpret hypothesis support (H1, H2, H3, H4)")
    print(f"  5. Integrate into Paper 4 (variance as design parameter)")
    print()

if __name__ == "__main__":
    main()
