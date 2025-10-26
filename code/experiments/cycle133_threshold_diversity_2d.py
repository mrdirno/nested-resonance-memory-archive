#!/usr/bin/env python3
"""
CYCLE 133: THRESHOLD × DIVERSITY 2D PARAMETER SPACE

Research Question:
  Now that we know spread × mult = diversity (Cycle 131-132 discovery),
  does threshold interact with diversity? Or are they truly independent?

Context:
  - Cycle 131: Fixed threshold=700, varied spread×mult, found product controls basin
  - Cycle 132: Human discovered dimensional reduction (3D → 2D)
  - Hypothesis: Threshold and diversity may also interact (further reduction possible)

Hypothesis:
  1. Independent: Threshold and diversity are orthogonal control dimensions (2D phase space)
  2. Coupled: Threshold × diversity interaction exists (1D effective space)
  3. Threshold-dependent: Diversity effects change with threshold regime

Method:
  - Create threshold × diversity grid
  - Threshold values: 5 (300, 400, 500, 600, 700) - spanning full range
  - Diversity values: 7 (0.03, 0.06, 0.10, 0.15, 0.25, 0.35, 0.45) - spanning full range
  - Grid size: 35 experiments (5×7)
  - Cycles per experiment: 3000
  - Total cycles: 105,000
  - Fix spread=0.10, vary mult to achieve diversity (spread × mult = D)

Expected:
  - If independent: 2D basin map with clear structure
  - If coupled: 1D transition line (threshold × diversity = constant)
  - If threshold-dependent: Different diversity effects at different thresholds

Metrics:
  - Basin assignment (A vs B)
  - 2D basin map visualization
  - Independence test (chi-square)
  - Interaction effect analysis
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def pattern_to_key(pattern):
    """Convert pattern to hashable key"""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))


def get_dominant_pattern(memory):
    """Get most common pattern in global memory"""
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction


def create_seed_memory_range(bridge, reality_metrics, mult, spread=0.10, count=5):
    """
    Create seed patterns with parametric variations
    Fixed spread=0.10, vary mult to achieve desired diversity
    """
    seed_patterns = []
    for i in range(count):
        offset = (i - count//2) * spread
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
        }
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns


def run_grid_point(threshold, diversity, cycles=3000, agent_cap=15):
    """
    Run single grid point experiment

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity (spread × mult), we use spread=0.10
        cycles: Number of evolution cycles
        agent_cap: Maximum agents

    Returns:
        dict: Results including basin assignment
    """
    workspace = Path("./workspace")

    # Calculate mult from diversity (since spread = 0.10)
    spread = 0.10
    mult = diversity / spread

    # Initialize swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from prior work
    basin_A = (6.220353, 6.275283, 6.281831)
    basin_B = (6.09469, 6.083677, 6.250047)

    start_time = time.time()

    # Run cycles
    for cycle in range(1, cycles + 1):
        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

    duration = time.time() - start_time

    # Final state
    dominant, count, fraction = get_dominant_pattern(swarm.global_memory)

    if dominant:
        dist_A = np.linalg.norm(np.array(dominant) - np.array(basin_A))
        dist_B = np.linalg.norm(np.array(dominant) - np.array(basin_B))
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        basin = 'NONE'
        dist_A, dist_B = None, None

    return {
        'threshold': threshold,
        'diversity': diversity,
        'spread': spread,
        'mult': mult,
        'basin': basin,
        'dominant': dominant,
        'fraction': fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': duration,
        'cycles_per_sec': cycles / duration
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CYCLE 133: THRESHOLD × DIVERSITY 2D PARAMETER SPACE")
    print("=" * 70)
    print("Testing independence vs interaction between threshold and diversity")
    print()

    # Parameter grid
    thresholds = [300, 400, 500, 600, 700]
    diversities = [0.03, 0.06, 0.10, 0.15, 0.25, 0.35, 0.45]

    print(f"Grid: {len(thresholds)}×{len(diversities)} = {len(thresholds)*len(diversities)} experiments")
    print(f"Thresholds: {thresholds}")
    print(f"Diversities: {diversities}")
    print(f"Cycles per experiment: 3000")
    print(f"Total cycles: {len(thresholds)*len(diversities)*3000:,}")
    print()

    # Run experiments
    results = []
    total_experiments = len(thresholds) * len(diversities)
    experiment_num = 0

    for threshold in thresholds:
        for diversity in diversities:
            experiment_num += 1
            print(f"[{experiment_num}/{total_experiments}] threshold={threshold}, diversity={diversity:.3f}...",
                  end=' ', flush=True)

            result = run_grid_point(threshold, diversity, cycles=3000, agent_cap=15)
            results.append(result)

            print(f"→ Basin {result['basin']} ({result['cycles_per_sec']:.1f} cyc/s, {result['duration']:.1f}s)")

    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "cycle133_threshold_diversity_grid.json"

    output_data = {
        'metadata': {
            'cycle': 133,
            'experiment': 'threshold_diversity_2d_grid',
            'date': datetime.now().isoformat(),
            'thresholds': thresholds,
            'diversities': diversities,
            'total_experiments': total_experiments,
            'total_cycles': total_experiments * 3000
        },
        'results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Basin distribution
    basin_counts = Counter([r['basin'] for r in results])
    print(f"Basin A: {basin_counts.get('A', 0)}/{total_experiments} ({basin_counts.get('A', 0)/total_experiments*100:.1f}%)")
    print(f"Basin B: {basin_counts.get('B', 0)}/{total_experiments} ({basin_counts.get('B', 0)/total_experiments*100:.1f}%)")
    if 'NONE' in basin_counts:
        print(f"NONE: {basin_counts['NONE']}/{total_experiments} ({basin_counts['NONE']/total_experiments*100:.1f}%)")

    print()
    print(f"Results saved: {output_path}")
    print()
    print("Next: Run analysis script to test independence hypothesis")
    print("=" * 70)
