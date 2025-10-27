#!/usr/bin/env python3
"""
CYCLE 163E: COMPOSITION DISTRIBUTION ANALYSIS
Triggered by Contingency E (Universal Harmonic - All Frequencies → Basin A)

Research Question:
  Why does the corrected implementation enable universal Basin A convergence?
  What threshold defines the bistable region?

Strategy:
  Test higher Basin A thresholds to find bistable region:
    1. Verify spawn calculation accuracy (99.7-100%)
    2. Analyze composition distribution (is avg_composition > 2.5 everywhere?)
    3. Test higher thresholds [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    4. Compare to Cycle 160-161 baseline

Experimental Design:
  - Representative frequencies: [5, 25, 50, 75, 95] (spread)
  - Seeds: [42, 123, 456] (3 replicates)
  - Thresholds: [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
  - Total experiments: 5 frequencies × 3 seeds × 6 thresholds = 90
  - NOTE: Same raw data, different threshold analysis

Expected Outcomes:
  - Identify new bistable threshold range
  - Characterize composition distribution shift
  - Understand why corrected spawning increases composition

Publication Value:
  "Threshold Calibration for Bistable Regions in Corrected NRM Implementation"

Date: 2025-10-25
Status: Contingency Script (Scenario E)
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import time
import numpy as np
import psutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict
from itertools import product


# =============================================================================
# CONFIGURATION
# =============================================================================

FREQUENCIES = [5, 25, 50, 75, 95]  # Representative spread
SEEDS = [42, 123, 456]  # 3 replicates
THRESHOLDS = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]  # Test range

CYCLES = 3000
AGENT_CAP = 15
CLUSTERING_THRESHOLD = 700
DIVERSITY = 0.3

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / 'cycle163e_composition_analysis.json'


# =============================================================================
# FRACTAL AGENT (NRM Implementation)
# =============================================================================

@dataclass
class FractalAgent:
    """
    Fractal agent with internal state space.
    Implements Nested Resonance Memory through transcendental phase dynamics.
    """
    agent_id: int
    phase: float  # Transcendental phase (0 to 2π)
    energy: float
    memory: List[float] = field(default_factory=list)

    def __post_init__(self):
        """Initialize memory with birth state."""
        self.memory.append(self.phase)

    def evolve(self, delta_time: float, pi: float, e: float, phi: float):
        """Evolve agent using transcendental substrate (π, e, φ)."""
        # Phase evolution: ω(t) = π·sin(e·t) + φ·cos(t)
        omega = pi * np.sin(e * delta_time) + phi * np.cos(delta_time)
        self.phase = (self.phase + omega * delta_time) % (2 * pi)

        # Energy dissipation
        self.energy *= 0.99

        # Memory retention (store recent phase)
        self.memory.append(self.phase)
        if len(self.memory) > 100:
            self.memory.pop(0)

    def resonance_score(self, other: 'FractalAgent') -> float:
        """Calculate resonance with another agent (phase alignment)."""
        phase_diff = abs(self.phase - other.phase)
        # Normalize to [0, π]
        if phase_diff > np.pi:
            phase_diff = 2 * np.pi - phase_diff
        # Resonance inversely proportional to phase difference
        return 1.0 - (phase_diff / np.pi)


# =============================================================================
# FRACTAL SWARM (Composition-Decomposition Dynamics)
# =============================================================================

class FractalSwarm:
    """
    Manages fractal agent population.
    Implements composition (clustering) and decomposition (burst) events.
    """

    def __init__(self, seed: int):
        self.agents: List[FractalAgent] = []
        self.next_id = 0
        self.rng = np.random.RandomState(seed)
        self.pi = np.pi
        self.e = np.e
        self.phi = (1 + np.sqrt(5)) / 2  # Golden ratio

    def spawn_agent(self, reality_metrics: Dict):
        """Spawn new fractal agent seeded by reality metrics."""
        # Phase initialized from CPU usage (0-100% → 0-2π)
        cpu_phase = (reality_metrics.get('cpu_percent', 50.0) / 100.0) * 2 * self.pi

        # Energy from memory availability
        mem_available = reality_metrics.get('memory_available_gb', 10.0)
        energy = mem_available / 16.0  # Normalize to ~1.0

        agent = FractalAgent(
            agent_id=self.next_id,
            phase=cpu_phase,
            energy=energy,
        )

        self.agents.append(agent)
        self.next_id += 1

    def evolve_cycle(self, delta_time: float):
        """Evolve all agents for one time step."""
        for agent in self.agents:
            agent.evolve(delta_time, self.pi, self.e, self.phi)

        # Remove low-energy agents (decomposition)
        self.agents = [a for a in self.agents if a.energy > 0.01]

    def get_agent_count(self) -> int:
        """Return current agent count."""
        return len(self.agents)

    def get_composition_clusters(self, threshold: float) -> List[List[FractalAgent]]:
        """
        Detect composition clusters (agents with high resonance).
        Returns list of clusters (each cluster is list of agents).
        """
        if len(self.agents) < 2:
            return []

        clusters = []
        visited = set()

        for i, agent_i in enumerate(self.agents):
            if i in visited:
                continue

            cluster = [agent_i]
            visited.add(i)

            for j, agent_j in enumerate(self.agents):
                if j <= i or j in visited:
                    continue

                # Check resonance
                resonance = agent_i.resonance_score(agent_j)
                if resonance > 0.7:  # High resonance threshold
                    cluster.append(agent_j)
                    visited.add(j)

            if len(cluster) >= 2:  # At least 2 agents to form cluster
                clusters.append(cluster)

        return clusters


# =============================================================================
# REALITY INTERFACE (Ground Truth)
# =============================================================================

class RealityInterface:
    """Interface to actual system metrics (psutil)."""

    def get_system_metrics(self) -> Dict:
        """Get real system metrics."""
        cpu = psutil.cpu_percent(interval=0.01)
        mem = psutil.virtual_memory()

        return {
            'cpu_percent': cpu,
            'memory_percent': mem.percent,
            'memory_available_gb': mem.available / (1024**3),
        }


# =============================================================================
# COMPOSITION DETECTION
# =============================================================================

def detect_composition_events(swarm: FractalSwarm) -> int:
    """
    Detect composition events (clustering).
    Returns count of agents in composition clusters.
    """
    clusters = swarm.get_composition_clusters(threshold=CLUSTERING_THRESHOLD)

    if not clusters:
        return 0

    # Count total agents in all clusters
    total_in_clusters = sum(len(cluster) for cluster in clusters)
    return total_in_clusters


# =============================================================================
# EXPERIMENT EXECUTION
# =============================================================================

def run_experiment(frequency: int, seed: int) -> Dict:
    """
    Run single experiment and collect composition trajectory.
    Basin determination done in post-processing with multiple thresholds.

    Returns:
      {
        'frequency': frequency %,
        'seed': seed value,
        'avg_composition_events': mean composition count,
        'spawn_count': total spawns,
        'spawn_accuracy_pct': actual vs expected spawns,
      }
    """

    # Initialize
    reality_interface = RealityInterface()
    swarm = FractalSwarm(seed=seed)

    # Corrected spawn interval calculation
    spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else CYCLES
    expected_spawns = CYCLES // spawn_interval

    # Tracking
    composition_events_history = []
    spawn_count = 0

    # Evolution loop
    for cycle in range(CYCLES):
        # Spawn agent at frequency interval
        if cycle % spawn_interval == 0 and cycle > 0:
            if swarm.get_agent_count() < AGENT_CAP:
                reality_metrics = reality_interface.get_system_metrics()
                swarm.spawn_agent(reality_metrics)
                spawn_count += 1

        # Evolve swarm
        swarm.evolve_cycle(delta_time=1.0)

        # Detect composition events
        comp_count = detect_composition_events(swarm)
        composition_events_history.append(comp_count)

    # Calculate metrics
    avg_composition = np.mean(composition_events_history)

    # Spawn accuracy
    spawn_accuracy_pct = (spawn_count / expected_spawns * 100.0) if expected_spawns > 0 else 0.0

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': float(avg_composition),
        'spawn_count': spawn_count,
        'expected_spawns': expected_spawns,
        'spawn_accuracy_pct': float(spawn_accuracy_pct),
    }


# =============================================================================
# MAIN EXPERIMENTAL PIPELINE
# =============================================================================

def main():
    """Run full Cycle 163E: Composition Distribution Analysis."""

    base_experiments = len(FREQUENCIES) * len(SEEDS)

    print("=" * 80)
    print("CYCLE 163E: COMPOSITION DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"Frequencies: {FREQUENCIES}")
    print(f"Seeds: {SEEDS}")
    print(f"Thresholds to test: {THRESHOLDS}")
    print(f"Base experiments (raw data): {base_experiments}")
    print(f"Total threshold analyses: {base_experiments * len(THRESHOLDS)}")
    print()

    start_time = time.time()

    raw_experiments = []
    experiment_idx = 0

    # Collect raw data
    for freq in FREQUENCIES:
        for seed in SEEDS:
            experiment_idx += 1
            exp_start = time.time()

            print(f"Experiment {experiment_idx}/{base_experiments}: Freq {freq}%, Seed {seed}")

            result = run_experiment(frequency=freq, seed=seed)
            raw_experiments.append(result)

            exp_duration = time.time() - exp_start

            print(f"  → Avg Composition: {result['avg_composition_events']:.3f}")
            print(f"  → Spawn Accuracy: {result['spawn_accuracy_pct']:.1f}%")
            print(f"  → Duration: {exp_duration:.1f}s")
            print()

    total_duration = time.time() - start_time

    # Post-processing: Apply multiple thresholds
    print("=" * 80)
    print("THRESHOLD CALIBRATION ANALYSIS")
    print("=" * 80)

    from collections import defaultdict

    threshold_results = {}

    for threshold in THRESHOLDS:
        basin_a_count = 0
        by_frequency = defaultdict(lambda: {'basin_a': 0, 'basin_b': 0, 'compositions': []})

        for exp in raw_experiments:
            freq = exp['frequency']
            comp = exp['avg_composition_events']
            basin = 'A' if comp > threshold else 'B'

            if basin == 'A':
                basin_a_count += 1
                by_frequency[freq]['basin_a'] += 1
            else:
                by_frequency[freq]['basin_b'] += 1

            by_frequency[freq]['compositions'].append(comp)

        basin_a_pct = (basin_a_count / base_experiments * 100)

        threshold_results[threshold] = {
            'basin_a_count': basin_a_count,
            'basin_a_pct': float(basin_a_pct),
            'by_frequency': dict(by_frequency),
        }

        print(f"Threshold {threshold}:")
        print(f"  Basin A: {basin_a_count}/{base_experiments} ({basin_a_pct:.1f}%)")
        print()

    # Identify bistable threshold
    bistable_threshold = None
    for threshold in THRESHOLDS:
        basin_a_pct = threshold_results[threshold]['basin_a_pct']
        if 30 <= basin_a_pct <= 70:  # Bistable range
            bistable_threshold = threshold
            break

    if bistable_threshold:
        print(f"BISTABLE THRESHOLD IDENTIFIED: {bistable_threshold}")
    else:
        print("NO BISTABLE THRESHOLD FOUND in tested range")
    print()

    # Composition distribution
    compositions = [exp['avg_composition_events'] for exp in raw_experiments]

    print("COMPOSITION STATISTICS:")
    print(f"  Mean: {np.mean(compositions):.3f} ± {np.std(compositions):.3f}")
    print(f"  Range: [{np.min(compositions):.3f}, {np.max(compositions):.3f}]")
    print(f"  Median: {np.median(compositions):.3f}")
    print()

    print(f"Total Duration: {total_duration/60:.1f} minutes")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '163E',
            'scenario': 'Composition Distribution Analysis',
            'date': datetime.now().isoformat(),
            'frequencies': FREQUENCIES,
            'seeds': SEEDS,
            'thresholds_tested': THRESHOLDS,
            'base_experiments': base_experiments,
            'duration_minutes': total_duration / 60,
        },
        'raw_experiments': raw_experiments,
        'threshold_analysis': {
            threshold: {
                'basin_a_count': results['basin_a_count'],
                'basin_a_pct': results['basin_a_pct'],
            }
            for threshold, results in threshold_results.items()
        },
        'bistable_threshold': bistable_threshold,
        'composition_stats': {
            'mean': float(np.mean(compositions)),
            'std': float(np.std(compositions)),
            'min': float(np.min(compositions)),
            'max': float(np.max(compositions)),
            'median': float(np.median(compositions)),
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)
    print("CYCLE 163E COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
