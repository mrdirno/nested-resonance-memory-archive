#!/usr/bin/env python3
"""
CYCLE 300: TRANSCENDENTAL SUBSTRATE VS PRNG COMPARATIVE VALIDATION (PC002)

Purpose:
  Test if transcendental constants (π,e,φ) as computational substrate produce
  superior emergent properties compared to PRNG substrates in self-organizing systems.

Hypothesis (PC002):
  Transcendental-based patterns will exhibit:
  - M1: Longer pattern lifetime (persistence across cycles)
  - M2: Better memory retention (pattern recall)
  - M3: Lower cluster stability (CV of cluster size)
  - M4: Faster complexity bootstrap (time to high-order patterns)

Experimental Design:
  - Factor A: Substrate (TS = Transcendental vs PS = PRNG)
  - Factor B: Scale (Light ~17 agents vs Heavy ~1000 agents)
  - Replications: n=20 per condition (80 total experiments)
  - Duration: 10,000 cycles per experiment
  - Total runtime: ~62 CPU hours estimated

Validation Criteria:
  PC002 validates if:
  - ≥2/4 metrics show p < 0.05
  - Significant metrics have Cohen's d ≥ 0.5
  - All significant effects favor TS > PS
  - Results replicate across 2 independent runs

Date: 2025-11-01 (Cycle 886+)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import sys
import json
import math
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add parent modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import FractalSwarm, CompositionEngine

# Transcendental Constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2


# ============================================================================
# PRNG SUBSTRATE BRIDGE (PS)
# ============================================================================

@dataclass
class PRNGState:
    """Phase state using PRNG substrate instead of transcendental constants."""
    pi_phase: float  # Named for compatibility, but uses PRNG
    e_phase: float
    phi_phase: float
    magnitude: float
    timestamp: float
    reality_anchor: Dict[str, float]


class PRNGBridge:
    """
    PRNG-based substrate bridge for PC002 comparative validation.

    Parallel implementation to TranscendentalBridge but using PRNG
    (Mersenne Twister MT19937) instead of transcendental constants.

    Maintains same statistical distribution (uniform [0, 2π)) but
    different computational origin (algorithmic vs transcendental).
    """

    def __init__(self, seed: int = 42):
        """Initialize PRNG bridge with deterministic seed."""
        self.rng = np.random.RandomState(seed)

        # Phase oscillator state (same interface as TranscendentalBridge)
        self.pi_offset = 0.0
        self.e_offset = 0.0
        self.phi_offset = 0.0

        # Resonance threshold (same as transcendental)
        self.resonance_threshold = 0.5

    def reality_to_phase(self, reality_metrics: Dict[str, float]) -> PRNGState:
        """
        Transform reality metrics to PRNG phase space.

        Uses PRNG to generate phases instead of transcendental constants.
        Statistical distribution matches TranscendentalBridge but
        computational origin is algorithmic (PRNG) not transcendental.
        """
        # Extract key metrics
        cpu = reality_metrics.get('cpu_percent', 0.0)
        memory = reality_metrics.get('memory_percent', 0.0)
        disk = reality_metrics.get('disk_percent', 0.0)

        # Normalize to [0, 1]
        cpu_norm = cpu / 100.0
        memory_norm = memory / 100.0
        disk_norm = disk / 100.0

        # Generate phases using PRNG (uniform [0, 2π))
        # Seed with metrics to maintain determinism but use PRNG algorithm
        state_seed = int((cpu_norm + memory_norm + disk_norm) * 1000000)
        temp_rng = np.random.RandomState(state_seed)

        pi_phase = temp_rng.uniform(0, 2 * PI)
        e_phase = temp_rng.uniform(0, 2 * PI)
        phi_phase = temp_rng.uniform(0, 2 * PI)

        # Add oscillator offsets
        pi_phase = (pi_phase + self.pi_offset) % (2 * PI)
        e_phase = (e_phase + self.e_offset) % (2 * PI)
        phi_phase = (phi_phase + self.phi_offset) % (2 * PI)

        # Calculate magnitude
        magnitude = math.sqrt(pi_phase**2 + e_phase**2 + phi_phase**2)

        # Create state with reality anchor
        state = PRNGState(
            pi_phase=pi_phase,
            e_phase=e_phase,
            phi_phase=phi_phase,
            magnitude=magnitude,
            timestamp=time.time(),
            reality_anchor=reality_metrics.copy()
        )

        return state

    def phase_to_reality(self, state: PRNGState) -> Dict[str, float]:
        """Transform PRNG phase state back to reality metrics."""
        return state.reality_anchor.copy()

    def generate_oscillation(self, frequency: float, duration: float) -> List[PRNGState]:
        """
        Generate oscillating sequence using PRNG.

        Uses PRNG increments instead of transcendental ratios.
        """
        sequence = []

        for step in range(int(duration)):
            # Increment using PRNG (algorithmic) instead of transcendental ratios
            self.pi_offset += frequency * self.rng.uniform(0.9, 1.1)
            self.e_offset += frequency * self.rng.uniform(0.9, 1.1)
            self.phi_offset += frequency * self.rng.uniform(0.9, 1.1)

            # Keep phases in [0, 2π]
            self.pi_offset %= (2 * PI)
            self.e_offset %= (2 * PI)
            self.phi_offset %= (2 * PI)

            # Create state (with empty reality anchor for oscillations)
            state = PRNGState(
                pi_phase=self.pi_offset,
                e_phase=self.e_offset,
                phi_phase=self.phi_offset,
                magnitude=math.sqrt(self.pi_offset**2 + self.e_offset**2 + self.phi_offset**2),
                timestamp=time.time(),
                reality_anchor={}
            )

            sequence.append(state)

        return sequence

    def detect_resonance(self, state1: PRNGState, state2: PRNGState) -> Dict[str, Any]:
        """Detect resonance between two PRNG states."""
        # Phase vectors
        vec1 = np.array([state1.pi_phase, state1.e_phase, state1.phi_phase])
        vec2 = np.array([state2.pi_phase, state2.e_phase, state2.phi_phase])

        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)

        if magnitude1 == 0 or magnitude2 == 0:
            phase_alignment = 0.0
        else:
            phase_alignment = dot_product / (magnitude1 * magnitude2)

        # Magnitude ratio
        if magnitude2 == 0:
            magnitude_ratio = 0.0
        else:
            magnitude_ratio = magnitude1 / magnitude2

        # Overall similarity
        similarity = (phase_alignment + 1.0) / 2.0  # Map [-1, 1] to [0, 1]

        is_resonant = similarity > self.resonance_threshold

        return {
            'similarity': similarity,
            'phase_alignment': phase_alignment,
            'magnitude_ratio': magnitude_ratio,
            'is_resonant': is_resonant
        }


# ============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

# Experimental conditions
CONDITIONS = [
    {'substrate': 'TS', 'scale': 'Light', 'capacity': 20, 'agents_target': 17},
    {'substrate': 'PS', 'scale': 'Light', 'capacity': 20, 'agents_target': 17},
    {'substrate': 'TS', 'scale': 'Heavy', 'capacity': 1200, 'agents_target': 1000},
    {'substrate': 'PS', 'scale': 'Heavy', 'capacity': 1200, 'agents_target': 1000},
]

# Seeds for reproducibility (n=20 per condition)
SEEDS = list(range(42, 62))  # Seeds 42-61 (n=20)

# Experiment parameters
CYCLES = 10000
SPAWN_FREQUENCY = 2.5  # % per 100 cycles (from C171 validated baseline)
RESULTS_DIR = Path(__file__).parent.parent.parent / 'experiments' / 'results'
RESULTS_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_FILE = RESULTS_DIR / f'cycle300_pc002_comparative_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'


# ============================================================================
# METRICS TRACKING
# ============================================================================

@dataclass
class PatternMemory:
    """Track pattern for lifetime and memory retention analysis."""
    pattern_id: str
    birth_cycle: int
    last_seen_cycle: int
    feature_vector: np.ndarray  # Cluster signature for similarity
    cluster_size_history: List[int]


class MetricsCollector:
    """
    Collect PC002 validation metrics during experiment.

    Tracks:
    - M1: Pattern lifetime (max persistence)
    - M2: Memory retention (cosine similarity over time)
    - M3: Cluster stability (CV of cluster sizes)
    - M4: Complexity bootstrap (time to first high-order pattern)
    """

    def __init__(self):
        self.patterns: Dict[str, PatternMemory] = {}
        self.next_pattern_id = 0
        self.cluster_size_history: List[int] = []
        self.complexity_threshold = 5  # High-order = clusters with 5+ agents
        self.bootstrap_cycle: Optional[int] = None

    def register_cluster(self, cycle: int, cluster: List[Any], feature_vector: np.ndarray):
        """Register cluster event for metrics tracking."""
        cluster_size = len(cluster)
        self.cluster_size_history.append(cluster_size)

        # Check for complexity bootstrap
        if self.bootstrap_cycle is None and cluster_size >= self.complexity_threshold:
            self.bootstrap_cycle = cycle

        # Pattern tracking (simplified: use feature vector hash as ID)
        pattern_id = f"pattern_{self.next_pattern_id}"
        self.next_pattern_id += 1

        self.patterns[pattern_id] = PatternMemory(
            pattern_id=pattern_id,
            birth_cycle=cycle,
            last_seen_cycle=cycle,
            feature_vector=feature_vector,
            cluster_size_history=[cluster_size]
        )

    def compute_metrics(self, total_cycles: int) -> Dict[str, float]:
        """Compute all PC002 metrics from collected data."""

        # M1: Pattern Lifetime (average max lifetime)
        if self.patterns:
            lifetimes = [
                (p.last_seen_cycle - p.birth_cycle)
                for p in self.patterns.values()
            ]
            pattern_lifetime = float(np.mean(lifetimes)) if lifetimes else 0.0
        else:
            pattern_lifetime = 0.0

        # M2: Memory Retention (simplified: pattern count retention)
        # Ratio of patterns that survived >50% of experiment
        if self.patterns:
            long_lived = sum(
                1 for p in self.patterns.values()
                if (p.last_seen_cycle - p.birth_cycle) > total_cycles * 0.5
            )
            memory_retention = long_lived / len(self.patterns)
        else:
            memory_retention = 0.0

        # M3: Cluster Stability (CV of cluster sizes)
        if len(self.cluster_size_history) > 1:
            cluster_stability = float(np.std(self.cluster_size_history) / np.mean(self.cluster_size_history))
        else:
            cluster_stability = 0.0

        # M4: Complexity Bootstrap Time
        complexity_bootstrap = float(self.bootstrap_cycle) if self.bootstrap_cycle is not None else total_cycles

        return {
            'pattern_lifetime': pattern_lifetime,
            'memory_retention': memory_retention,
            'cluster_stability': cluster_stability,
            'complexity_bootstrap': complexity_bootstrap
        }


# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_substrate_experiment(
    substrate: str,
    scale: str,
    capacity: int,
    agents_target: int,
    seed: int,
    cycles: int
) -> Dict[str, Any]:
    """
    Run single experiment with specified substrate and configuration.

    Args:
        substrate: 'TS' (transcendental) or 'PS' (PRNG)
        scale: 'Light' or 'Heavy'
        capacity: Agent capacity limit
        agents_target: Target agent count
        seed: Random seed for reproducibility
        cycles: Number of cycles to run

    Returns:
        Dictionary with all PC002 metrics
    """

    print(f"\n[{substrate}-{scale} seed={seed}] Starting experiment...")
    start_time = time.time()

    # Initialize substrate bridge
    if substrate == 'TS':
        bridge = TranscendentalBridge()
    else:  # PS
        bridge = PRNGBridge(seed=seed)

    # Initialize reality interface
    reality = RealityInterface()

    # Seed numpy for reproducibility
    np.random.seed(seed)

    # Create initial agent
    metrics = reality.get_system_metrics()
    initial_agent = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7
    )

    # Active agents list
    agents = [initial_agent]
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Metrics collector
    metrics_collector = MetricsCollector()

    # Calculate spawn interval from frequency
    spawn_interval = max(1, int(100.0 / SPAWN_FREQUENCY))
    spawn_count = 0

    # Run experiment cycles
    for cycle_idx in range(cycles):

        # Spawn new agent based on frequency
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < capacity:
            spawn_count += 1

            # Get current reality metrics
            current_metrics = reality.get_system_metrics()

            # Spawn from random existing agent
            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_count}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)

            if child:
                agents.append(child)

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters (composition events)
        cluster_events = composition_engine.detect_clusters(agents)

        # Register clusters for metrics tracking
        for cluster in cluster_events:
            # Create feature vector (simplified: phase averages)
            if cluster:
                phase_vectors = [
                    np.array([agent.phase_state.pi_phase, agent.phase_state.e_phase, agent.phase_state.phi_phase])
                    for agent in cluster
                ]
                feature_vector = np.mean(phase_vectors, axis=0)
                metrics_collector.register_cluster(cycle_idx, cluster, feature_vector)

        # Progress reporting (every 1000 cycles)
        if (cycle_idx + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"  Cycle {cycle_idx + 1}/{cycles} | Agents: {len(agents)} | "
                  f"Clusters: {len(metrics_collector.patterns)} | "
                  f"Elapsed: {elapsed:.1f}s")

    # Compute final metrics
    final_metrics = metrics_collector.compute_metrics(cycles)

    elapsed_time = time.time() - start_time

    print(f"[{substrate}-{scale} seed={seed}] Complete in {elapsed_time:.1f}s")
    print(f"  Metrics: lifetime={final_metrics['pattern_lifetime']:.2f}, "
          f"retention={final_metrics['memory_retention']:.2f}, "
          f"stability={final_metrics['cluster_stability']:.2f}, "
          f"bootstrap={final_metrics['complexity_bootstrap']:.0f}")

    return {
        'substrate': substrate,
        'scale': scale,
        'capacity': capacity,
        'agents_target': agents_target,
        'seed': seed,
        'cycles': cycles,
        'final_agent_count': len(agents),
        'total_patterns': len(metrics_collector.patterns),
        'metrics': final_metrics,
        'elapsed_time': elapsed_time
    }


def main():
    """Execute Cycle 300 PC002 comparative validation experiments."""

    print("=" * 80)
    print("CYCLE 300: PC002 TRANSCENDENTAL SUBSTRATE COMPARATIVE VALIDATION")
    print("=" * 80)
    print()
    print("Hypothesis: Transcendental substrate (π,e,φ) produces superior emergent")
    print("            properties vs PRNG in self-organizing systems")
    print()
    print("Design: 2×2 factorial (Substrate × Scale)")
    print(f"  Conditions: {len(CONDITIONS)}")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print()
    print("Metrics:")
    print("  M1: Pattern Lifetime (cycles)")
    print("  M2: Memory Retention (ratio)")
    print("  M3: Cluster Stability (CV)")
    print("  M4: Complexity Bootstrap (cycles to threshold)")
    print()
    print("=" * 80)
    print()

    # Confirm execution
    print(f"Output file: {OUTPUT_FILE}")
    print()
    response = input("Proceed with 80 experiments? (~62 CPU hours estimated) [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    print("Starting experiments...")
    print()

    experiment_start = datetime.now()
    all_results = []

    # Track results by substrate for incremental PC002 validation
    transcendental_results = defaultdict(list)
    prng_results = defaultdict(list)

    # Run all experiments
    total_experiments = len(CONDITIONS) * len(SEEDS)
    experiment_idx = 0

    for condition in CONDITIONS:
        substrate = condition['substrate']
        scale = condition['scale']
        capacity = condition['capacity']
        agents_target = condition['agents_target']

        print(f"\n{'=' * 80}")
        print(f"Condition: {substrate}-{scale} (Capacity={capacity}, Target={agents_target})")
        print(f"{'=' * 80}")

        for seed in SEEDS:
            experiment_idx += 1
            print(f"\n[Experiment {experiment_idx}/{total_experiments}]")

            result = run_substrate_experiment(
                substrate=substrate,
                scale=scale,
                capacity=capacity,
                agents_target=agents_target,
                seed=seed,
                cycles=CYCLES
            )

            all_results.append(result)

            # Aggregate by substrate for PC002 validation
            for metric_name, metric_value in result['metrics'].items():
                if substrate == 'TS':
                    transcendental_results[metric_name].append(metric_value)
                else:
                    prng_results[metric_name].append(metric_value)

            # Save incremental results (safety checkpoint)
            if experiment_idx % 10 == 0:
                checkpoint_file = RESULTS_DIR / f'cycle300_checkpoint_{experiment_idx}.json'
                with open(checkpoint_file, 'w') as f:
                    json.dump(all_results, f, indent=2)
                print(f"\n  [Checkpoint saved: {checkpoint_file}]")

    # Compute final elapsed time
    experiment_end = datetime.now()
    total_elapsed = (experiment_end - experiment_start).total_seconds()

    print()
    print("=" * 80)
    print("ALL EXPERIMENTS COMPLETE")
    print("=" * 80)
    print(f"Total experiments: {len(all_results)}")
    print(f"Total time: {total_elapsed / 3600:.2f} hours")
    print()

    # Prepare PC002 validation data
    pc002_data = {
        "metadata": {
            "experiment_id": "PC002_CYCLE300_TS_VS_PRNG",
            "pc_id": "PC002",
            "domain": "nested_resonance_memory",
            "timestamp": experiment_start.isoformat(),
            "n_transcendental": len([r for r in all_results if r['substrate'] == 'TS']),
            "n_prng": len([r for r in all_results if r['substrate'] == 'PS']),
            "total_experiments": len(all_results),
            "total_elapsed_hours": total_elapsed / 3600,
            "conditions": CONDITIONS,
            "seeds": SEEDS,
            "cycles": CYCLES
        },
        "transcendental_results": dict(transcendental_results),
        "prng_results": dict(prng_results),
        "metrics": ["pattern_lifetime", "memory_retention", "cluster_stability", "complexity_bootstrap"],
        "raw_results": all_results
    }

    # Save final results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(pc002_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("Next steps:")
    print("  1. Run PC002 validation: python code/tsf/pc002_transcendental_substrate.py")
    print("  2. Load data from OUTPUT_FILE and call pc002.validate()")
    print("  3. Update TEG based on validation outcome")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
