#!/usr/bin/env python3
"""
Cycle 189: Self-Organized Criticality and Burst Dynamics

Purpose: Test whether NRM exhibits power-law dynamics characteristic of self-organized criticality (SOC)
Background: Classical SOC systems (sandpile, forest fires, earthquakes) exhibit:
            - Power-law distributions P(s) ~ s^(-α)
            - Separation of timescales (slow driving + fast relaxation)
            - Criticality without fine-tuning

Hypothesis: NRM exhibits energy-regulated criticality:
            - Slow driving: Energy recharge (α_recharge = 0.5/cycle)
            - Fast relaxation: Composition events (instantaneous energy depletion)
            - Prediction: Inter-event intervals (IEI) follow power-law P(IEI) ~ IEI^(-α)

Design:
    Five Spawn Frequencies:
    1. f = 1.5% (near collapse boundary)
    2. f = 2.0% (lower homeostasis range)
    3. f = 2.5% (validated homeostasis, Paper 2)
    4. f = 3.0% (upper homeostasis range)
    5. f = 5.0% (high frequency, saturation regime)

Expected Outcomes:
    H5.1 (Power-Law IEI Distribution):
        P(IEI) ~ IEI^(-α) with α ∈ [1.5, 2.5]
        Power-law better fit than exponential (Poisson baseline)

    H5.2 (High Burstiness):
        B > 0.3 (above Poisson baseline B = 0)
        B = (σ_IEI - μ_IEI) / (σ_IEI + μ_IEI)

    H5.3 (Criticality Without Tuning):
        Power-law dynamics emerge across all frequencies (no special tuning required)

Mechanism:
    Energy recharge-depletion cycles → composition avalanches → clustered events
    → heavy-tailed IEI distribution → power-law regime

Extended Duration:
    cycles = 5000 (longer than C171/C175/C177)
    Reason: Power-law fitting requires large sample sizes (1000+ composition events)

Parameters:
    seeds = 20 per frequency (100 total experiments)
    N_max = 15 (population cap)
    Energy/composition params same as Paper 2

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1295)
License: GPL-3.0
"""

import sys
import json
import time
import random
import sqlite3
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000  # Extended duration for power-law statistics
N_INITIAL_MIN = 10
N_INITIAL_MAX = 20
N_MAX = 15  # Population cap (from Paper 2)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606,
         111, 222, 333, 444, 555, 666, 777, 888, 999, 1010]  # 20 seeds

# Spawn frequency conditions
FREQUENCIES = {
    'f_1.5': 0.015,  # 1.5% (near collapse boundary)
    'f_2.0': 0.020,  # 2.0% (lower homeostasis)
    'f_2.5': 0.025,  # 2.5% (validated homeostasis, Paper 2)
    'f_3.0': 0.030,  # 3.0% (upper homeostasis)
    'f_5.0': 0.050,  # 5.0% (high frequency, saturation)
}

# Energy parameters
E_INITIAL = 50.0
E_MAX = 50.0
E_THRESHOLD = 20.0
E_COST = 10.0
RECHARGE_RATE = 0.5

# Composition parameters
THETA_COMP = 0.85
THETA_DECOMP = 10.0

# Population parameters
BASIN_A_THRESHOLD = 2.5

@dataclass
class Agent:
    """Individual fractal agent"""
    id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0

@dataclass
class CompositionEvent:
    """Record of a composition event for IEI analysis"""
    cycle: int
    parent_id: int
    child_id: int

class CriticalityPopulation:
    """Single population for SOC burst dynamics experiments"""

    def __init__(self, seed: int, f_spawn: float, frequency_label: str, db_path: Path):
        self.seed = seed
        self.f_spawn = f_spawn
        self.frequency_label = frequency_label
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0

        # Composition event tracking (for IEI analysis)
        self.composition_events: List[CompositionEvent] = []

        self._initialize_agents()

    def _initialize_agents(self):
        """Create initial population"""
        n_initial = self.random.randint(N_INITIAL_MIN, N_INITIAL_MAX)

        for _ in range(n_initial):
            phase = self.bridge.get_phase(np.pi)
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL,
                phase=phase,
                depth=0,
                compositions=0
            )
            self.agents[self.next_agent_id] = agent
            self.next_agent_id += 1

    def _select_parent_uniform_random(self) -> Optional[Agent]:
        """Select parent uniformly at random (Paper 2 baseline)"""
        if not self.agents:
            return None
        return self.random.choice(list(self.agents.values()))

    def _try_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        parent = self._select_parent_uniform_random()
        if parent is None:
            self.spawn_failures += 1
            return

        # Check energy threshold
        if parent.energy < E_THRESHOLD:
            self.spawn_failures += 1
            return

        # Check population cap
        if len(self.agents) >= N_MAX:
            self.spawn_failures += 1
            return

        # Spawn succeeds
        parent.energy -= E_COST
        parent.compositions += 1
        self.spawn_successes += 1

        # Create child agent
        phase = self.bridge.get_phase(np.e)
        child = Agent(
            id=self.next_agent_id,
            energy=E_INITIAL,
            phase=phase,
            depth=parent.depth + 1,
            compositions=0
        )
        self.agents[self.next_agent_id] = child

        # Record composition event for IEI analysis
        event = CompositionEvent(
            cycle=self.cycle_count,
            parent_id=parent.id,
            child_id=self.next_agent_id
        )
        self.composition_events.append(event)

        self.next_agent_id += 1

    def _recharge_energy(self):
        """Recharge all agents' energy"""
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + RECHARGE_RATE)

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Spawn attempts (Poisson with mean = f_spawn * N)
        n_agents = len(self.agents)
        n_spawn_attempts = self.np_random.poisson(self.f_spawn * n_agents)

        for _ in range(n_spawn_attempts):
            self._try_spawn()

        # Energy recharge
        self._recharge_energy()

    def _calculate_inter_event_intervals(self) -> List[int]:
        """Calculate inter-event intervals (IEI) for power-law analysis"""
        if len(self.composition_events) < 2:
            return []

        event_times = [e.cycle for e in self.composition_events]
        event_times_sorted = sorted(event_times)
        ieis = np.diff(event_times_sorted).tolist()

        return ieis

    def _calculate_burstiness(self, ieis: List[int]) -> float:
        """Calculate burstiness coefficient B = (σ - μ) / (σ + μ)"""
        if len(ieis) == 0:
            return 0.0

        mu = np.mean(ieis)
        sigma = np.std(ieis)

        if mu + sigma == 0:
            return 0.0

        B = (sigma - mu) / (sigma + mu)
        return B

    def get_final_statistics(self) -> Dict:
        """Calculate final experiment statistics"""
        mean_population = len(self.agents)
        basin = 'A' if mean_population > BASIN_A_THRESHOLD else 'B'

        spawn_success_rate = (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0

        # Inter-event intervals
        ieis = self._calculate_inter_event_intervals()

        # Burstiness
        burstiness = self._calculate_burstiness(ieis)

        # Basic IEI statistics
        iei_stats = {
            'mean': np.mean(ieis) if ieis else 0.0,
            'std': np.std(ieis) if ieis else 0.0,
            'min': int(np.min(ieis)) if ieis else 0,
            'max': int(np.max(ieis)) if ieis else 0,
            'n_events': len(self.composition_events),
            'n_intervals': len(ieis),
        }

        return {
            'cycle': self.cycle_count,
            'frequency_label': self.frequency_label,
            'f_spawn': self.f_spawn,
            'final_agents': len(self.agents),
            'mean_population': mean_population,
            'basin': basin,
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'n_composition_events': len(self.composition_events),
            'burstiness': burstiness,
            'iei_statistics': iei_stats,
            'inter_event_intervals': ieis,  # Full IEI data for power-law fitting
        }

def run_experiment(seed: int, frequency_label: str, f_spawn: float, output_path: Path, db_path: Path) -> Dict:
    """Run single criticality experiment"""
    freq_labels = list(FREQUENCIES.keys())
    freq_idx = freq_labels.index(frequency_label)
    seed_idx = SEEDS.index(seed)
    exp_num = freq_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(freq_labels) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] {frequency_label:6s} (f={f_spawn*100:4.1f}%), Seed {seed:4d}: ", end='', flush=True)

    clear_bridge_database(db_path / "bridge.db")
    system = CriticalityPopulation(seed, f_spawn, frequency_label, db_path)

    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    final_stats = system.get_final_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:5.1f} | "
          f"η: {final_stats['spawn_success_rate']:5.1f}% | "
          f"Events: {final_stats['n_composition_events']:4d} | "
          f"B: {final_stats['burstiness']:6.3f} | "
          f"{elapsed_total:4.0f}s")

    final_stats['seed'] = seed
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C189 self-organized criticality experiments"""

    print("=" * 80)
    print("CYCLE 189: SELF-ORGANIZED CRITICALITY AND BURST DYNAMICS")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM exhibits power-law dynamics characteristic of SOC systems")
    print("Background: Classical SOC (sandpile, earthquakes) exhibits:")
    print("            - Power-law distributions P(s) ~ s^(-α)")
    print("            - Separation of timescales (slow driving + fast relaxation)")
    print("            - Criticality without fine-tuning")
    print()
    print(f"NRM SOC Parallel:")
    print(f"  Slow driving: Energy recharge (α_recharge = {RECHARGE_RATE}/cycle)")
    print(f"  Fast relaxation: Composition events (instantaneous energy depletion)")
    print(f"  Prediction: Inter-event intervals (IEI) follow power-law P(IEI) ~ IEI^(-α)")
    print()
    print(f"Spawn Frequencies Tested:")
    for label, freq in FREQUENCIES.items():
        print(f"  {label}: f = {freq*100:4.1f}%")
    print()
    print(f"Experimental Parameters:")
    print(f"  Cycles = {CYCLES} (extended duration for power-law statistics)")
    print(f"  N_max = {N_MAX} (population cap)")
    print(f"  Seeds per frequency: n={len(SEEDS)}")
    print(f"  Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(FREQUENCIES) * len(SEEDS) * 0.08:.1f} hours")
    print()
    print(f"Hypotheses:")
    print(f"  H5.1 (Power-Law IEI): P(IEI) ~ IEI^(-α) with α ∈ [1.5, 2.5]")
    print(f"  H5.2 (High Burstiness): B > 0.3 (above Poisson baseline)")
    print(f"  H5.3 (Criticality Without Tuning): Power-law across all frequencies")
    print()

    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c189_criticality.json"

    db_path = Path(__file__).parent.parent / "bridge"

    results = []
    start_time_total = time.time()

    for frequency_label, f_spawn in FREQUENCIES.items():
        print()
        print(f"Testing {frequency_label.upper()} (f = {f_spawn*100:.1f}%)")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, frequency_label, f_spawn, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Frequency':>10s} | {'f %':>6s} | {'Basin A %':>10s} | {'Mean η %':>10s} | {'Mean Events':>12s} | {'Mean B':>8s}")
    print("-" * 80)

    frequency_aggregates = []
    for frequency_label in FREQUENCIES.keys():
        freq_results = [r for r in results if r['frequency_label'] == frequency_label]

        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_results)) * 100

        spawn_rates = [r['spawn_success_rate'] for r in freq_results]
        mean_spawn_rate = np.mean(spawn_rates)

        n_events = [r['n_composition_events'] for r in freq_results]
        mean_events = np.mean(n_events)

        burstiness_values = [r['burstiness'] for r in freq_results]
        mean_burstiness = np.mean(burstiness_values)

        f_spawn = FREQUENCIES[frequency_label]

        frequency_aggregates.append({
            'frequency_label': frequency_label,
            'f_spawn': f_spawn,
            'basin_a_pct': basin_a_pct,
            'mean_spawn_rate': mean_spawn_rate,
            'spawn_rate_values': spawn_rates,
            'mean_events': mean_events,
            'mean_burstiness': mean_burstiness,
            'burstiness_values': burstiness_values,
        })

        print(f"{frequency_label:>10s} | {f_spawn*100:5.1f}% | {basin_a_pct:9.1f}% | {mean_spawn_rate:9.1f}% | {mean_events:12.1f} | {mean_burstiness:8.3f}")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    print("=" * 80)
    print("HYPOTHESIS TESTING (PRELIMINARY)")
    print("=" * 80)
    print()

    # H5.2: High burstiness
    print("H5.2 (High Burstiness: B > 0.3):")
    h52_supported = True
    for agg in frequency_aggregates:
        label = agg['frequency_label']
        B = agg['mean_burstiness']
        print(f"  {label}: B = {B:.3f}", end='')

        if B > 0.3:
            print(f" ✓ SUPPORTED (B > 0.3)")
        else:
            print(f" ⚠ NOT SUPPORTED (B ≤ 0.3)")
            h52_supported = False

    if h52_supported:
        h52_result = "SUPPORTED"
        print(f"  Overall: ✓ H5.2 SUPPORTED (all frequencies show B > 0.3)")
    else:
        h52_result = "NOT_SUPPORTED"
        print(f"  Overall: ⚠ H5.2 NOT SUPPORTED (some frequencies B ≤ 0.3)")
    print()

    print(f"Note: H5.1 (Power-Law IEI) and H5.3 (Criticality Without Tuning) require")
    print(f"      detailed power-law fitting via analysis pipeline (analyze_c189_criticality.py)")
    print(f"      using Clauset et al. (2009) MLE method with goodness-of-fit tests.")
    print()

    output_data = {
        'metadata': {
            'experiment': 'C189_CRITICALITY',
            'date': datetime.now().isoformat(),
            'purpose': 'Test self-organized criticality via power-law IEI distributions',
            'frequencies': {k: v for k, v in FREQUENCIES.items()},
            'cycles': CYCLES,
            'n_max': N_MAX,
            'seeds': SEEDS,
            'hypotheses': {
                'H5.1': 'Power-law IEI distribution P(IEI) ~ IEI^(-α) with α ∈ [1.5, 2.5]',
                'H5.2': 'High burstiness B > 0.3 (above Poisson baseline)',
                'H5.3': 'Criticality without tuning (power-law across all frequencies)',
            }
        },
        'frequency_aggregates': frequency_aggregates,
        'hypothesis_results': {
            'H5.2': h52_result,
        },
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C189 COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Run analysis pipeline: python code/analysis/analyze_c189_criticality.py")
    print("  2. Perform power-law fitting (Clauset et al. 2009 MLE method)")
    print("  3. Generate publication figures:")
    print("     - IEI distributions (log-log plots)")
    print("     - α vs. f (power-law exponent vs. frequency)")
    print("     - CCDF: P(IEI > x) vs. x")
    print("     - B vs. α (burstiness vs. power-law exponent)")
    print("  4. Model comparison tests (power-law vs. exponential/log-normal/Weibull)")
    print("  5. Update Paper 4 Section 3.5 with empirical results")

if __name__ == "__main__":
    main()
