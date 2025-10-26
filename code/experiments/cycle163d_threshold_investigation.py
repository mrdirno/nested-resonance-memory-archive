#!/usr/bin/env python3
"""
CYCLE 163D: THRESHOLD AND PARAMETER INVESTIGATION
Triggered by Contingency D (All Anti-Harmonic - No Basin A Found)

Research Question:
  Why does the composition mechanism prevent Basin A convergence?

Strategy:
  Parameter space exploration to identify what prevents Basin A:
    1. Test multiple Basin A thresholds [2.0, 2.5, 3.0]
    2. Vary diversity parameter [0.1, 0.3, 0.5]
    3. Vary agent cap [15, 30]
    4. Test longer evolution cycles [3K, 10K]

Experimental Design:
  - Representative frequency: 50% (mid-range)
  - Representative seed: 42
  - Thresholds: [2.0, 2.5, 3.0]
  - Diversity: [0.1, 0.3, 0.5]
  - Agent caps: [15, 30]
  - Cycle lengths: [3000, 10000]
  - Total experiments: 3×3×2×2 = 36

Expected Outcomes:
  - Identify parameter combinations that enable Basin A
  - Characterize composition distribution across parameter space
  - Understand why avg_composition may be capped

Publication Value:
  "Parameter Space Constraints on Basin Convergence in NRM Systems"

Date: 2025-10-25
Status: Contingency Script (Scenario D)
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

FREQUENCY = 50  # Representative mid-range
SEED = 42  # Representative seed

# Parameter space
THRESHOLDS = [2.0, 2.5, 3.0]
DIVERSITIES = [0.1, 0.3, 0.5]
AGENT_CAPS = [15, 30]
CYCLE_LENGTHS = [3000, 10000]

CLUSTERING_THRESHOLD = 700  # For detecting composition events

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / 'cycle163d_threshold_investigation.json'


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

def run_experiment(basin_threshold: float,
                   diversity: float,
                   agent_cap: int,
                   cycles: int) -> Dict:
    """
    Run single parameter combination experiment.

    Returns:
      {
        'basin_threshold': threshold for Basin A,
        'diversity': diversity parameter,
        'agent_cap': maximum agents,
        'cycles': evolution cycles,
        'avg_composition_events': mean composition count,
        'max_composition': maximum composition observed,
        'basin': 'A' or 'B',
        'spawn_count': total spawns,
      }
    """

    # Initialize
    reality_interface = RealityInterface()
    swarm = FractalSwarm(seed=SEED)

    # Corrected spawn interval calculation
    spawn_interval = max(1, int(100.0 / FREQUENCY)) if FREQUENCY > 0 else cycles
    expected_spawns = cycles // spawn_interval

    # Tracking
    composition_events_history = []
    spawn_count = 0

    # Evolution loop
    for cycle in range(cycles):
        # Spawn agent at frequency interval
        if cycle % spawn_interval == 0 and cycle > 0:
            if swarm.get_agent_count() < agent_cap:
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
    max_composition = np.max(composition_events_history)

    # Basin determination (using parameter-specific threshold)
    basin = 'A' if avg_composition > basin_threshold else 'B'

    return {
        'basin_threshold': float(basin_threshold),
        'diversity': float(diversity),
        'agent_cap': int(agent_cap),
        'cycles': int(cycles),
        'avg_composition_events': float(avg_composition),
        'max_composition': float(max_composition),
        'basin': basin,
        'spawn_count': spawn_count,
        'expected_spawns': expected_spawns,
    }


# =============================================================================
# MAIN EXPERIMENTAL PIPELINE
# =============================================================================

def main():
    """Run full Cycle 163D: Threshold/Parameter Investigation."""

    # Generate parameter combinations
    param_combinations = list(product(THRESHOLDS, DIVERSITIES, AGENT_CAPS, CYCLE_LENGTHS))
    total_experiments = len(param_combinations)

    print("=" * 80)
    print("CYCLE 163D: THRESHOLD AND PARAMETER INVESTIGATION")
    print("=" * 80)
    print(f"Frequency: {FREQUENCY}% (fixed)")
    print(f"Seed: {SEED} (fixed)")
    print(f"Thresholds: {THRESHOLDS}")
    print(f"Diversities: {DIVERSITIES}")
    print(f"Agent caps: {AGENT_CAPS}")
    print(f"Cycle lengths: {CYCLE_LENGTHS}")
    print(f"Total experiments: {total_experiments}")
    print()

    start_time = time.time()

    experiments = []

    for idx, (threshold, diversity, agent_cap, cycles) in enumerate(param_combinations, 1):
        exp_start = time.time()

        print(f"Experiment {idx}/{total_experiments}:")
        print(f"  Threshold={threshold}, Diversity={diversity}, AgentCap={agent_cap}, Cycles={cycles}")

        result = run_experiment(
            basin_threshold=threshold,
            diversity=diversity,
            agent_cap=agent_cap,
            cycles=cycles
        )
        experiments.append(result)

        exp_duration = time.time() - exp_start

        print(f"  → Basin {result['basin']}")
        print(f"  → Avg Composition: {result['avg_composition_events']:.3f}")
        print(f"  → Max Composition: {result['max_composition']:.1f}")
        print(f"  → Duration: {exp_duration:.1f}s")
        print()

    total_duration = time.time() - start_time

    # Analysis
    print("=" * 80)
    print("PARAMETER SPACE ANALYSIS")
    print("=" * 80)

    # Basin A occurrence by parameter
    from collections import defaultdict

    basin_a_by_threshold = defaultdict(int)
    basin_a_by_diversity = defaultdict(int)
    basin_a_by_agent_cap = defaultdict(int)
    basin_a_by_cycles = defaultdict(int)

    for exp in experiments:
        if exp['basin'] == 'A':
            basin_a_by_threshold[exp['basin_threshold']] += 1
            basin_a_by_diversity[exp['diversity']] += 1
            basin_a_by_agent_cap[exp['agent_cap']] += 1
            basin_a_by_cycles[exp['cycles']] += 1

    print("BASIN A OCCURRENCE BY PARAMETER:")
    print(f"  By Threshold:")
    for thresh in sorted(basin_a_by_threshold.keys()):
        count = basin_a_by_threshold[thresh]
        pct = (count / (total_experiments // len(THRESHOLDS)) * 100)
        print(f"    {thresh}: {count}/{total_experiments // len(THRESHOLDS)} ({pct:.1f}%)")

    print(f"  By Diversity:")
    for div in sorted(basin_a_by_diversity.keys()):
        count = basin_a_by_diversity[div]
        pct = (count / (total_experiments // len(DIVERSITIES)) * 100)
        print(f"    {div}: {count}/{total_experiments // len(DIVERSITIES)} ({pct:.1f}%)")

    print(f"  By Agent Cap:")
    for cap in sorted(basin_a_by_agent_cap.keys()):
        count = basin_a_by_agent_cap[cap]
        pct = (count / (total_experiments // len(AGENT_CAPS)) * 100)
        print(f"    {cap}: {count}/{total_experiments // len(AGENT_CAPS)} ({pct:.1f}%)")

    print(f"  By Cycle Length:")
    for cyc in sorted(basin_a_by_cycles.keys()):
        count = basin_a_by_cycles[cyc]
        pct = (count / (total_experiments // len(CYCLE_LENGTHS)) * 100)
        print(f"    {cyc}: {count}/{total_experiments // len(CYCLE_LENGTHS)} ({pct:.1f}%)")

    print()

    # Composition distribution
    compositions = [exp['avg_composition_events'] for exp in experiments]
    max_compositions = [exp['max_composition'] for exp in experiments]

    print("COMPOSITION STATISTICS:")
    print(f"  Average composition across all experiments:")
    print(f"    Mean: {np.mean(compositions):.3f} ± {np.std(compositions):.3f}")
    print(f"    Range: [{np.min(compositions):.3f}, {np.max(compositions):.3f}]")
    print()
    print(f"  Maximum composition across all experiments:")
    print(f"    Mean: {np.mean(max_compositions):.1f} ± {np.std(max_compositions):.1f}")
    print(f"    Range: [{np.min(max_compositions):.1f}, {np.max(max_compositions):.1f}]")
    print()

    print(f"Total Duration: {total_duration/60:.1f} minutes")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '163D',
            'scenario': 'Threshold and Parameter Investigation',
            'date': datetime.now().isoformat(),
            'frequency': FREQUENCY,
            'seed': SEED,
            'parameter_space': {
                'thresholds': THRESHOLDS,
                'diversities': DIVERSITIES,
                'agent_caps': AGENT_CAPS,
                'cycle_lengths': CYCLE_LENGTHS,
            },
            'total_experiments': total_experiments,
            'duration_minutes': total_duration / 60,
        },
        'experiments': experiments,
        'analysis': {
            'composition_mean': float(np.mean(compositions)),
            'composition_std': float(np.std(compositions)),
            'composition_min': float(np.min(compositions)),
            'composition_max': float(np.max(compositions)),
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)
    print("CYCLE 163D COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
