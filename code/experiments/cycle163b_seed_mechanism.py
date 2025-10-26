#!/usr/bin/env python3
"""
CYCLE 163B: SEED-DEPENDENT MECHANISM INVESTIGATION
Triggered by Scenario B (Seed-Dependent Stochasticity)

Research Question:
  What mechanisms drive seed-dependent basin selection?

Strategy:
  Extended seed sweep at representative frequency to characterize:
    1. Basin A distribution across seeds
    2. Composition trajectory patterns
    3. Early-cycle indicators (predict final basin from first 500 cycles)
    4. Clustering dynamics (composition event timing)

Experimental Design:
  - Frequency: 50% (representative mid-range)
  - Seeds: 30 different seeds [10, 20, 30, ..., 300]
  - Cycles: 3,000 per experiment
  - Total experiments: 30

Expected Outcomes:
  - Quantify Basin A probability distribution (binomial fit)
  - Identify early predictors of final basin
  - Characterize stochastic attractor selection mechanism

Publication Value:
  "Intrinsic Stochasticity in Nested Resonance Memory: Seed-Dependent Attractor Selection"

Date: 2025-10-25
Status: Contingency Script (Scenario B)
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


# =============================================================================
# CONFIGURATION
# =============================================================================

FREQUENCY = 50  # Representative mid-range frequency
SEEDS = [i * 10 for i in range(1, 31)]  # [10, 20, 30, ..., 300]
CYCLES = 3000
AGENT_CAP = 15
THRESHOLD = 700  # Clustering threshold
DIVERSITY = 0.3  # Diversity parameter
BASIN_THRESHOLD = 2.5  # Calibrated from Cycle 161

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / 'cycle163b_seed_mechanism.json'


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

def run_experiment(seed: int, frequency: int) -> Dict:
    """
    Run single seed-dependent experiment.

    Returns:
      {
        'seed': seed value,
        'frequency': spawn frequency %,
        'avg_composition_events': mean composition count,
        'basin': 'A' or 'B',
        'composition_trajectory': full trajectory (sampled),
        'early_composition': composition in first 500 cycles,
        'late_composition': composition in last 500 cycles,
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

    # Early vs late composition
    early_composition = np.mean(composition_events_history[:500])  # First 500 cycles
    late_composition = np.mean(composition_events_history[-500:])  # Last 500 cycles

    # Basin determination (calibrated threshold from Cycle 161)
    basin = 'A' if avg_composition > BASIN_THRESHOLD else 'B'

    # Spawn accuracy
    spawn_accuracy_pct = (spawn_count / expected_spawns * 100.0) if expected_spawns > 0 else 0.0

    # Trajectory (sample every 10 cycles for storage efficiency)
    composition_trajectory = [float(composition_events_history[i])
                             for i in range(0, CYCLES, 10)]

    return {
        'seed': seed,
        'frequency': frequency,
        'avg_composition_events': float(avg_composition),
        'basin': basin,
        'composition_trajectory': composition_trajectory,
        'early_composition': float(early_composition),
        'late_composition': float(late_composition),
        'spawn_count': spawn_count,
        'expected_spawns': expected_spawns,
        'spawn_accuracy_pct': float(spawn_accuracy_pct),
    }


# =============================================================================
# MAIN EXPERIMENTAL PIPELINE
# =============================================================================

def main():
    """Run full Cycle 163B: Seed Mechanism Investigation."""

    print("=" * 80)
    print("CYCLE 163B: SEED-DEPENDENT MECHANISM INVESTIGATION")
    print("=" * 80)
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds: {len(SEEDS)} seeds from {SEEDS[0]} to {SEEDS[-1]}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(SEEDS)}")
    print(f"Basin A threshold: {BASIN_THRESHOLD}")
    print()

    start_time = time.time()

    experiments = []

    for idx, seed in enumerate(SEEDS, 1):
        exp_start = time.time()

        print(f"Experiment {idx}/{len(SEEDS)}: Seed {seed}")

        result = run_experiment(seed=seed, frequency=FREQUENCY)
        experiments.append(result)

        exp_duration = time.time() - exp_start

        print(f"  → Basin {result['basin']}")
        print(f"  → Avg Composition: {result['avg_composition_events']:.3f}")
        print(f"  → Early Composition: {result['early_composition']:.3f}")
        print(f"  → Late Composition: {result['late_composition']:.3f}")
        print(f"  → Spawn Accuracy: {result['spawn_accuracy_pct']:.1f}%")
        print(f"  → Duration: {exp_duration:.1f}s")
        print()

    total_duration = time.time() - start_time

    # Analysis
    print("=" * 80)
    print("SEED MECHANISM ANALYSIS")
    print("=" * 80)

    basin_a_count = sum(1 for exp in experiments if exp['basin'] == 'A')
    basin_b_count = len(experiments) - basin_a_count
    basin_a_pct = (basin_a_count / len(experiments)) * 100

    compositions = [exp['avg_composition_events'] for exp in experiments]
    early_comps = [exp['early_composition'] for exp in experiments]
    late_comps = [exp['late_composition'] for exp in experiments]

    print(f"Basin A: {basin_a_count}/{len(experiments)} ({basin_a_pct:.1f}%)")
    print(f"Basin B: {basin_b_count}/{len(experiments)} ({100-basin_a_pct:.1f}%)")
    print()
    print(f"Composition Stats:")
    print(f"  Mean: {np.mean(compositions):.3f} ± {np.std(compositions):.3f}")
    print(f"  Range: [{np.min(compositions):.3f}, {np.max(compositions):.3f}]")
    print()
    print(f"Early Composition (first 500 cycles):")
    print(f"  Mean: {np.mean(early_comps):.3f} ± {np.std(early_comps):.3f}")
    print()
    print(f"Late Composition (last 500 cycles):")
    print(f"  Mean: {np.mean(late_comps):.3f} ± {np.std(late_comps):.3f}")
    print()

    # Correlation: Early composition predicts final basin?
    basin_a_early = [exp['early_composition'] for exp in experiments if exp['basin'] == 'A']
    basin_b_early = [exp['early_composition'] for exp in experiments if exp['basin'] == 'B']

    if basin_a_early and basin_b_early:
        print(f"Early Composition by Final Basin:")
        print(f"  Basin A: {np.mean(basin_a_early):.3f} ± {np.std(basin_a_early):.3f}")
        print(f"  Basin B: {np.mean(basin_b_early):.3f} ± {np.std(basin_b_early):.3f}")

        # Simple t-test approximation (effect size)
        mean_diff = np.mean(basin_a_early) - np.mean(basin_b_early)
        pooled_std = np.sqrt((np.var(basin_a_early) + np.var(basin_b_early)) / 2)
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0

        print(f"  Cohen's d (early predictor): {cohens_d:.3f}")
        print()

    print(f"Total Duration: {total_duration/60:.1f} minutes")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '163B',
            'scenario': 'Seed-Dependent Mechanism Investigation',
            'date': datetime.now().isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(experiments),
            'basin_threshold': BASIN_THRESHOLD,
            'duration_minutes': total_duration / 60,
        },
        'experiments': experiments,
        'analysis': {
            'basin_a_count': basin_a_count,
            'basin_a_pct': float(basin_a_pct),
            'composition_mean': float(np.mean(compositions)),
            'composition_std': float(np.std(compositions)),
            'composition_min': float(np.min(compositions)),
            'composition_max': float(np.max(compositions)),
            'early_composition_mean': float(np.mean(early_comps)),
            'late_composition_mean': float(np.mean(late_comps)),
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)
    print("CYCLE 163B COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
