#!/usr/bin/env python3
"""
CYCLE 165: UPPER FREQUENCY BOUNDARY MAPPING
Sample Size Effect Investigation

Research Question:
  Were Cycle 162 "anti-harmonic" frequencies (0% Basin A with n=3) true Basin B
  attractors or artifacts of small sample size?

Background:
  Cycle 162 (n=3): Frequencies 20%, 30%, 70%, 80% showed 0% Basin A
  Cycle 163 (n=10): All frequencies showed 100% Basin A
  Hypothesis: n=3 insufficient; anti-harmonic results were Type II error

Strategy:
  Test Cycle 162 anti-harmonic frequencies with n=10 seeds to resolve discrepancy.
  Include 1% control (known strong harmonic from Cycle 162).

Experimental Design:
  - Frequencies: [85, 90, 95, 99, 99.9] (4 anti-harmonic + 1 harmonic control)
  - Seeds: 10 seeds per frequency [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]
  - Total experiments: 5 frequencies × 10 seeds = 50

Analysis:
  - Basin A percentage at each frequency
  - Comparison with Cycle 162 (n=3) results
  - Sample size effect quantification
  - Harmonic structure validation

Expected Outcomes (if sample size hypothesis correct):
  - Anti-harmonic frequencies will show >0% Basin A with n=10
  - 1% control will remain 100% Basin A
  - Evidence for minimum sample size requirement

Publication Value:
  "Sample Size Dependence in Stochastic Basin Classification"

Date: 2025-10-25
Status: Sample Size Effect Investigation
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
from collections import defaultdict


# =============================================================================
# CONFIGURATION
# =============================================================================

FREQUENCIES = [85, 90, 95, 99, 99.9]  # 1% control + 4 anti-harmonic from Cycle 162
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # 10 seeds
CYCLES = 3000
AGENT_CAP = 15
THRESHOLD = 700  # Clustering threshold
DIVERSITY = 0.3  # Diversity parameter
BASIN_THRESHOLD = 2.5  # Calibrated from Cycle 161

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / 'cycle165_upper_frequency_boundary.json'


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
    Run single frequency-seed combination experiment.

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
# VARIANCE ANALYSIS
# =============================================================================

def variance_decomposition(experiments: List[Dict]) -> Dict:
    """
    Decompose variance into frequency, seed, and interaction components.

    Returns:
      - Total variance
      - Between-frequency variance
      - Between-seed variance
      - Interaction variance
      - Variance explained percentages
    """

    # Extract data
    compositions = np.array([exp['avg_composition_events'] for exp in experiments])
    frequencies = np.array([exp['frequency'] for exp in experiments])
    seeds = np.array([exp['seed'] for exp in experiments])

    # Overall mean
    grand_mean = np.mean(compositions)

    # Group by frequency
    freq_groups = defaultdict(list)
    for exp in experiments:
        freq_groups[exp['frequency']].append(exp['avg_composition_events'])

    # Group by seed
    seed_groups = defaultdict(list)
    for exp in experiments:
        seed_groups[exp['seed']].append(exp['avg_composition_events'])

    # Frequency effect
    freq_means = {freq: np.mean(vals) for freq, vals in freq_groups.items()}
    ss_freq = sum(len(vals) * (freq_means[freq] - grand_mean)**2
                  for freq, vals in freq_groups.items())

    # Seed effect
    seed_means = {seed: np.mean(vals) for seed, vals in seed_groups.items()}
    ss_seed = sum(len(vals) * (seed_means[seed] - grand_mean)**2
                  for seed, vals in seed_groups.items())

    # Total variance
    ss_total = np.sum((compositions - grand_mean)**2)

    # Within-cell variance (residual)
    ss_within = sum(np.sum((np.array(vals) - freq_means[freq])**2)
                    for freq, vals in freq_groups.items())

    # Interaction (residual after freq + seed)
    ss_interaction = ss_total - ss_freq - ss_seed - ss_within

    # Variance explained
    var_freq_pct = (ss_freq / ss_total * 100) if ss_total > 0 else 0
    var_seed_pct = (ss_seed / ss_total * 100) if ss_total > 0 else 0
    var_interaction_pct = (ss_interaction / ss_total * 100) if ss_total > 0 else 0

    return {
        'total_variance': float(ss_total),
        'frequency_variance': float(ss_freq),
        'seed_variance': float(ss_seed),
        'interaction_variance': float(ss_interaction),
        'within_variance': float(ss_within),
        'frequency_explained_pct': float(var_freq_pct),
        'seed_explained_pct': float(var_seed_pct),
        'interaction_explained_pct': float(var_interaction_pct),
    }


# =============================================================================
# MAIN EXPERIMENTAL PIPELINE
# =============================================================================

def main():
    """Run full Cycle 163C: Frequency-Seed Interaction Analysis."""

    total_experiments = len(FREQUENCIES) * len(SEEDS)

    print("=" * 80)
    print("CYCLE 165: UPPER FREQUENCY BOUNDARY MAPPING")
    print("=" * 80)
    print(f"Frequencies: {FREQUENCIES}")
    print(f"Seeds per frequency: {len(SEEDS)}")
    print(f"Total experiments: {total_experiments}")
    print(f"Basin A threshold: {BASIN_THRESHOLD}")
    print()

    start_time = time.time()

    experiments = []
    experiment_idx = 0

    for freq in FREQUENCIES:
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

    # Analysis
    print("=" * 80)
    print("FREQUENCY-SEED INTERACTION ANALYSIS")
    print("=" * 80)

    # 1. Frequency landscape
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

    print("FREQUENCY LANDSCAPE:")
    print("  Freq | N  | Basin A | Basin B | Basin A % | Mean Comp ± Std")
    print("  -----+----+---------+---------+-----------+-------------------")

    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        n_total = data['basin_a'] + data['basin_b']
        basin_a_pct = (data['basin_a'] / n_total * 100) if n_total > 0 else 0
        mean_comp = np.mean(data['compositions'])
        std_comp = np.std(data['compositions'])

        print(f"  {freq:4d}% | {n_total:2d} | {data['basin_a']:7d} | {data['basin_b']:7d} | "
              f"{basin_a_pct:8.1f}% | {mean_comp:6.3f} ± {std_comp:5.3f}")

    print()

    # 2. Seed variance by frequency
    print("SEED VARIANCE BY FREQUENCY:")
    print("  Freq | Seed Variance | Interpretation")
    print("  -----+---------------+-------------------")

    for freq in sorted(by_frequency.keys()):
        data = by_frequency[freq]
        seed_var = np.var(data['compositions'])

        if seed_var < 0.01:
            interpretation = "Low (seed-independent)"
        elif seed_var < 0.05:
            interpretation = "Moderate"
        else:
            interpretation = "High (seed-dependent)"

        print(f"  {freq:4d}% | {seed_var:13.4f} | {interpretation}")

    print()

    # 3. Variance decomposition
    print("VARIANCE DECOMPOSITION (Two-Way ANOVA-Style):")
    variance_analysis = variance_decomposition(experiments)

    print(f"  Total variance:        {variance_analysis['total_variance']:.4f}")
    print(f"  Frequency effect:      {variance_analysis['frequency_variance']:.4f} ({variance_analysis['frequency_explained_pct']:.1f}%)")
    print(f"  Seed effect:           {variance_analysis['seed_variance']:.4f} ({variance_analysis['seed_explained_pct']:.1f}%)")
    print(f"  Interaction effect:    {variance_analysis['interaction_variance']:.4f} ({variance_analysis['interaction_explained_pct']:.1f}%)")
    print(f"  Within-cell variance:  {variance_analysis['within_variance']:.4f}")
    print()

    # Interpretation
    if variance_analysis['interaction_explained_pct'] > 20:
        interpretation = "STRONG INTERACTION: Frequency modulates seed effect"
    elif variance_analysis['interaction_explained_pct'] > 10:
        interpretation = "MODERATE INTERACTION: Some frequency-seed coupling"
    else:
        interpretation = "WEAK INTERACTION: Frequency and seed mostly independent"

    print(f"Interpretation: {interpretation}")
    print()

    print(f"Total Duration: {total_duration/60:.1f} minutes")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '165',
            'scenario': 'Upper Frequency Boundary Mapping',
            'date': datetime.now().isoformat(),
            'frequencies': FREQUENCIES,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': total_experiments,
            'basin_threshold': BASIN_THRESHOLD,
            'duration_minutes': total_duration / 60,
        },
        'experiments': experiments,
        'analysis': {
            'variance_decomposition': variance_analysis,
            'interpretation': interpretation,
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)
    print("CYCLE 163C COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
