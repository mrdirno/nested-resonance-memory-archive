#!/usr/bin/env python3
"""
CYCLE 163A: FINE-GRAINED HARMONIC FREQUENCY MAPPING
Triggered by Scenario A (Frequency-Dependent Harmonic Landscape)

Research Question:
  What is the precise frequency resolution of harmonic zones?

Strategy:
  Fine-grained frequency sweep around identified harmonic frequencies
  from Cycle 162 results. Tests ±5% around each harmonic in 1% steps.

Experimental Design:
  - Target frequencies: Harmonic frequencies ± 5% in 1% steps
  - Example: If 25% is harmonic, test [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
  - Seeds: [42, 123, 456] (3 replicates for consistency)
  - Total experiments: Depends on number of harmonic frequencies

Expected Outcomes:
  - Define harmonic bandwidth (e.g., 23-27% all harmonic)
  - Identify sharp vs gradual transitions
  - Quantify harmonic zone structure

Publication Value:
  "High-Resolution Mapping of Harmonic Frequency Zones in NRM Systems"

Date: 2025-10-25
Status: Contingency Script (Scenario A)
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import time
import argparse
import numpy as np
import psutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict


# =============================================================================
# CONFIGURATION
# =============================================================================

SEEDS = [42, 123, 456]  # 3 replicates
CYCLES = 3000
AGENT_CAP = 15
THRESHOLD = 700  # Clustering threshold
DIVERSITY = 0.3  # Diversity parameter
BASIN_THRESHOLD = 2.5  # Calibrated from Cycle 161

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / 'cycle163a_harmonic_fine_grained.json'


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
    clusters = swarm.get_composition_clusters(threshold=THRESHOLD)

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
    Run single fine-grained frequency experiment.

    Returns:
      {
        'frequency': frequency %,
        'seed': seed value,
        'avg_composition_events': mean composition count,
        'basin': 'A' or 'B',
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

    # Basin determination (calibrated threshold from Cycle 161)
    basin = 'A' if avg_composition > BASIN_THRESHOLD else 'B'

    # Spawn accuracy
    spawn_accuracy_pct = (spawn_count / expected_spawns * 100.0) if expected_spawns > 0 else 0.0

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': float(avg_composition),
        'basin': basin,
        'spawn_count': spawn_count,
        'expected_spawns': expected_spawns,
        'spawn_accuracy_pct': float(spawn_accuracy_pct),
    }


# =============================================================================
# FREQUENCY RANGE GENERATION
# =============================================================================

def generate_fine_grained_frequencies(harmonic_frequencies: List[int],
                                      bandwidth: int = 5,
                                      step: int = 1) -> List[int]:
    """
    Generate fine-grained frequency sweep around harmonic frequencies.

    Args:
      harmonic_frequencies: List of harmonic frequencies identified from Cycle 162
      bandwidth: Range around each harmonic (±bandwidth %)
      step: Step size for fine-grained sweep

    Returns:
      List of unique frequencies to test (sorted)
    """

    frequencies = set()

    for harmonic in harmonic_frequencies:
        # Generate range: [harmonic - bandwidth, harmonic + bandwidth]
        freq_range = range(
            max(1, harmonic - bandwidth),  # Don't go below 1%
            min(100, harmonic + bandwidth + 1),  # Don't go above 99%
            step
        )
        frequencies.update(freq_range)

    return sorted(frequencies)


# =============================================================================
# MAIN EXPERIMENTAL PIPELINE
# =============================================================================

def main():
    """Run full Cycle 163A: Fine-Grained Harmonic Mapping."""

    parser = argparse.ArgumentParser(
        description='Cycle 163A: Fine-grained harmonic frequency mapping'
    )
    parser.add_argument(
        '--harmonic-frequencies',
        type=int,
        nargs='+',
        required=True,
        help='List of harmonic frequencies from Cycle 162 (space-separated integers)'
    )
    parser.add_argument(
        '--bandwidth',
        type=int,
        default=5,
        help='Range around each harmonic (±bandwidth %%) (default: 5)'
    )
    parser.add_argument(
        '--step',
        type=int,
        default=1,
        help='Step size for fine-grained sweep (default: 1)'
    )

    args = parser.parse_args()

    harmonic_frequencies = args.harmonic_frequencies
    bandwidth = args.bandwidth
    step = args.step

    # Generate frequency test points
    frequencies = generate_fine_grained_frequencies(
        harmonic_frequencies,
        bandwidth=bandwidth,
        step=step
    )

    total_experiments = len(frequencies) * len(SEEDS)

    print("=" * 80)
    print("CYCLE 163A: FINE-GRAINED HARMONIC FREQUENCY MAPPING")
    print("=" * 80)
    print(f"Harmonic frequencies (from Cycle 162): {harmonic_frequencies}")
    print(f"Bandwidth: ±{bandwidth}%")
    print(f"Step size: {step}%")
    print(f"Frequencies to test: {len(frequencies)} → {frequencies}")
    print(f"Seeds per frequency: {len(SEEDS)}")
    print(f"Total experiments: {total_experiments}")
    print(f"Basin A threshold: {BASIN_THRESHOLD}")
    print()

    start_time = time.time()

    experiments = []
    experiment_idx = 0

    for freq in frequencies:
        for seed in SEEDS:
            experiment_idx += 1
            exp_start = time.time()

            print(f"Experiment {experiment_idx}/{total_experiments}: Freq {freq}%, Seed {seed}")

            result = run_experiment(frequency=freq, seed=seed)
            experiments.append(result)

            exp_duration = time.time() - exp_start

            print(f"  → Basin {result['basin']}")
            print(f"  → Avg Composition: {result['avg_composition_events']:.3f}")
            print(f"  → Spawn Accuracy: {result['spawn_accuracy_pct']:.1f}%")
            print(f"  → Duration: {exp_duration:.1f}s")
            print()

    total_duration = time.time() - start_time

    # Analysis: Group by frequency
    print("=" * 80)
    print("FINE-GRAINED HARMONIC MAPPING ANALYSIS")
    print("=" * 80)

    from collections import defaultdict
    by_frequency = defaultdict(lambda: {'basin_a': 0, 'basin_b': 0, 'compositions': []})

    for exp in experiments:
        freq = exp['frequency']
        basin = exp['basin']
        comp = exp['avg_composition_events']

        if basin == 'A':
            by_frequency[freq]['basin_a'] += 1
        else:
            by_frequency[freq]['basin_b'] += 1

        by_frequency[freq]['compositions'].append(comp)

    # Print frequency-basin table
    print("  Freq | N | Basin A | Basin B | Basin A % | Mean Comp | Classification")
    print("  -----+---+---------+---------+-----------+-----------+------------------")

    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        n_total = data['basin_a'] + data['basin_b']
        basin_a_pct = (data['basin_a'] / n_total * 100) if n_total > 0 else 0

        # Classification
        if basin_a_pct >= 67:
            classification = "Harmonic"
        elif basin_a_pct >= 33:
            classification = "Mixed"
        else:
            classification = "Anti-harmonic"

        mean_comp = np.mean(data['compositions'])

        print(f"  {freq:4d}% | {n_total} | {data['basin_a']:7d} | {data['basin_b']:7d} | "
              f"{basin_a_pct:8.1f}% | {mean_comp:9.3f} | {classification}")

    print()

    # Harmonic zones
    harmonic_zones = []
    current_zone = None

    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        n_total = data['basin_a'] + data['basin_b']
        basin_a_pct = (data['basin_a'] / n_total * 100) if n_total > 0 else 0

        if basin_a_pct >= 67:  # Harmonic
            if current_zone is None:
                current_zone = [freq, freq]  # [start, end]
            else:
                current_zone[1] = freq  # Extend zone
        else:
            if current_zone is not None:
                harmonic_zones.append(tuple(current_zone))
                current_zone = None

    # Finalize last zone
    if current_zone is not None:
        harmonic_zones.append(tuple(current_zone))

    print("HARMONIC ZONES IDENTIFIED:")
    for zone_start, zone_end in harmonic_zones:
        bandwidth = zone_end - zone_start + 1
        print(f"  {zone_start}% - {zone_end}% (bandwidth: {bandwidth}%)")
    print()

    print(f"Total Duration: {total_duration/60:.1f} minutes")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '163A',
            'scenario': 'Fine-Grained Harmonic Mapping',
            'date': datetime.now().isoformat(),
            'harmonic_frequencies_input': harmonic_frequencies,
            'bandwidth': bandwidth,
            'step': step,
            'frequencies_tested': frequencies,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': total_experiments,
            'basin_threshold': BASIN_THRESHOLD,
            'duration_minutes': total_duration / 60,
        },
        'experiments': experiments,
        'analysis': {
            'harmonic_zones': [{'start': z[0], 'end': z[1], 'bandwidth': z[1] - z[0] + 1}
                              for z in harmonic_zones],
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)
    print("CYCLE 163A COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
