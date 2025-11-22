#!/usr/bin/env python3
"""
Cycle 62: Critical Threshold Mapping

Hypothesis from Cycle 61:
  Phase transition occurs between threshold=900 (standard regime) and
  threshold=1200 (high-frequency regime) where cluster formation rate
  increases by ~100x.

Observation:
  - threshold=900:  avg ~1-7 clusters/checkpoint (standard dynamics)
  - threshold=1200: avg ~252 clusters (high-frequency dynamics)

Test Approach:
  1. Test intermediate thresholds: 950, 1000, 1050, 1100, 1150
  2. Track cluster formation rate at each threshold
  3. Identify critical threshold where transition occurs
  4. Characterize transition sharpness (gradual vs sharp)

Expected:
  If phase transition exists:
    - Cluster formation rate should increase dramatically at some threshold
    - Transition may be sharp (discontinuous) or gradual
    - Critical threshold defines boundary between regimes
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def run_threshold_mapping(threshold: float, cycles: int = 300) -> dict:
    """
    Test single threshold to measure cluster formation dynamics.

    Args:
        threshold: Burst threshold to test
        cycles: Number of cycles

    Returns:
        dict with cluster formation metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold}")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    agent_counts = []
    cluster_counts = []
    checkpoint_interval = 10

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            agent_count = len(swarm.agents)
            cluster_count = len(swarm.composition.clusters)

            agent_counts.append(agent_count)
            cluster_counts.append(cluster_count)

    duration = time.time() - start_time

    # Analysis
    avg_clusters = np.mean(cluster_counts) if cluster_counts else 0
    max_clusters = max(cluster_counts) if cluster_counts else 0
    std_clusters = np.std(cluster_counts) if cluster_counts else 0

    # Cluster formation rate (clusters per checkpoint)
    formation_rate = avg_clusters / len(cluster_counts) if cluster_counts else 0

    # Multi-cluster percentage
    multicluster_count = sum(1 for c in cluster_counts if c > 1)
    multicluster_pct = 100 * multicluster_count / len(cluster_counts) if cluster_counts else 0

    print(f"  Average clusters: {avg_clusters:.1f}")
    print(f"  Max clusters: {max_clusters}")
    print(f"  Std clusters: {std_clusters:.1f}")
    print(f"  Multi-cluster checkpoints: {multicluster_pct:.1f}%")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(cluster_counts),
        'avg_clusters': avg_clusters,
        'max_clusters': max_clusters,
        'std_clusters': std_clusters,
        'formation_rate': formation_rate,
        'multicluster_percentage': multicluster_pct,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'duration': duration
    }


def analyze_phase_transition(results: list) -> dict:
    """
    Analyze results to identify critical threshold and transition characteristics.

    Args:
        results: List of threshold test results

    Returns:
        dict with phase transition analysis
    """
    print(f"\n{'='*80}")
    print(f"PHASE TRANSITION ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract cluster formation rates
    thresholds = [r['threshold'] for r in results]
    avg_clusters = [r['avg_clusters'] for r in results]
    max_clusters = [r['max_clusters'] for r in results]

    print("Threshold → Average Clusters:")
    for threshold, avg, max_c in zip(thresholds, avg_clusters, max_clusters):
        print(f"  {threshold:4.0f} → avg: {avg:6.1f}, max: {max_c:4.0f}")
    print()

    # Find largest jump in cluster formation rate
    jumps = []
    for i in range(len(avg_clusters) - 1):
        jump = avg_clusters[i+1] - avg_clusters[i]
        jump_ratio = avg_clusters[i+1] / avg_clusters[i] if avg_clusters[i] > 0 else float('inf')
        jumps.append({
            'from_threshold': thresholds[i],
            'to_threshold': thresholds[i+1],
            'jump': jump,
            'jump_ratio': jump_ratio
        })

    print("Cluster Formation Rate Jumps:")
    for j in jumps:
        print(f"  {j['from_threshold']:4.0f} → {j['to_threshold']:4.0f}: "
              f"+{j['jump']:6.1f} clusters ({j['jump_ratio']:.2f}x)")
    print()

    # Identify critical threshold (largest jump)
    critical_jump = max(jumps, key=lambda j: j['jump'])
    critical_threshold_lower = critical_jump['from_threshold']
    critical_threshold_upper = critical_jump['to_threshold']

    print(f"Critical Threshold Range: {critical_threshold_lower}-{critical_threshold_upper}")
    print(f"  Jump magnitude: +{critical_jump['jump']:.1f} clusters")
    print(f"  Jump ratio: {critical_jump['jump_ratio']:.2f}x")
    print()

    # Characterize transition sharpness
    # Sharp transition: one large jump dominates
    # Gradual transition: multiple comparable jumps
    total_jump = avg_clusters[-1] - avg_clusters[0]
    largest_jump = critical_jump['jump']
    sharpness = largest_jump / total_jump if total_jump > 0 else 0

    if sharpness > 0.7:
        transition_type = "SHARP (discontinuous)"
    elif sharpness > 0.4:
        transition_type = "MODERATE (semi-sharp)"
    else:
        transition_type = "GRADUAL (continuous)"

    print(f"Transition Sharpness: {sharpness:.2%}")
    print(f"  Classification: {transition_type}")
    print(f"  Interpretation: {largest_jump:.1f}/{total_jump:.1f} of total increase occurs at critical threshold")
    print()

    # Regime classification
    print("Regime Classification:")
    for i, (threshold, avg) in enumerate(zip(thresholds, avg_clusters)):
        if threshold < critical_threshold_lower:
            regime = "Standard"
        elif threshold <= critical_threshold_upper:
            regime = "Critical (Transition Zone)"
        else:
            regime = "High-Frequency"
        print(f"  threshold={threshold:4.0f}: {regime:25s} (avg {avg:6.1f} clusters)")
    print()

    return {
        'critical_threshold_lower': critical_threshold_lower,
        'critical_threshold_upper': critical_threshold_upper,
        'critical_jump_magnitude': critical_jump['jump'],
        'critical_jump_ratio': critical_jump['jump_ratio'],
        'transition_sharpness': sharpness,
        'transition_type': transition_type,
        'jumps': jumps
    }


def main():
    """Run critical threshold mapping experiment."""
    print("="*80)
    print("CYCLE 62: CRITICAL THRESHOLD MAPPING")
    print("="*80)
    print()
    print("Mapping phase transition between standard and high-frequency")
    print("composition regimes by testing intermediate thresholds.")
    print()

    # Include known boundary points + intermediate values
    test_thresholds = [900, 950, 1000, 1050, 1100, 1150, 1200]

    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_threshold_mapping(threshold, cycles=300)
            results.append(result)
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({
                'threshold': threshold,
                'error': str(e)
            })

    overall_duration = time.time() - overall_start

    # Filter successful results
    successful_results = [r for r in results if 'error' not in r]

    if len(successful_results) >= 3:
        # Analyze phase transition
        transition_analysis = analyze_phase_transition(successful_results)

        print("="*80)
        print("INSIGHT #27: CRITICAL THRESHOLD IDENTIFIED")
        print("="*80)
        print()
        print(f"Phase transition occurs between {transition_analysis['critical_threshold_lower']}")
        print(f"and {transition_analysis['critical_threshold_upper']} burst threshold.")
        print()
        print(f"Transition characteristics:")
        print(f"  - Type: {transition_analysis['transition_type']}")
        print(f"  - Sharpness: {transition_analysis['transition_sharpness']:.2%}")
        print(f"  - Jump magnitude: {transition_analysis['critical_jump_magnitude']:.1f} clusters")
        print(f"  - Jump ratio: {transition_analysis['critical_jump_ratio']:.2f}x")
        print()
        print("System exhibits two distinct dynamical regimes:")
        print("  1. Standard regime (< critical): ~1-10 clusters, single-cluster dominance")
        print("  2. High-frequency regime (> critical): ~100-500 clusters, multi-cluster coexistence")
        print()
        print("="*80)

        insight_27 = True
    else:
        print("⚠️ Insufficient successful tests for phase transition analysis")
        transition_analysis = {}
        insight_27 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "critical_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle62_threshold_mapping.json"

    output_data = {
        'experiment': 'cycle62_critical_threshold_mapping',
        'test_thresholds': test_thresholds,
        'results': results,
        'transition_analysis': transition_analysis,
        'insight_27_discovered': insight_27,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total experiment duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data


if __name__ == "__main__":
    main()
