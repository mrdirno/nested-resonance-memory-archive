#!/usr/bin/env python3
"""
Cycle 63: Lower Threshold Scan - Finding the True Phase Boundary

Discovery from Cycle 62:
  All thresholds 900-1200 showed high-frequency behavior (~130-160 avg clusters).
  This means the phase transition occurs BELOW 900, not between 900-1200.

Hypothesis:
  Phase transition from standard (single-cluster) to high-frequency (multi-cluster)
  regime occurs somewhere between 500-900.

Test Approach:
  1. Test thresholds: 500, 600, 700, 800, 900
  2. Include known boundaries: 500 (standard from Cycle 59), 900 (high-freq from Cycle 62)
  3. Track cluster formation rate at each threshold
  4. Identify where dramatic increase occurs
  5. Characterize standard vs high-frequency regimes

Expected:
  Sharp or moderate increase in cluster formation between two adjacent thresholds,
  identifying the critical boundary.
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from workspace_utils import get_workspace_path, get_results_path


def run_threshold_scan(threshold: float, cycles: int = 300) -> dict:
    """
    Scan single threshold to measure cluster formation dynamics.

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
    workspace = get_workspace_path()
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
    median_clusters = np.median(cluster_counts) if cluster_counts else 0

    # Multi-cluster percentage
    multicluster_count = sum(1 for c in cluster_counts if c > 1)
    multicluster_pct = 100 * multicluster_count / len(cluster_counts) if cluster_counts else 0

    # Single-cluster percentage
    single_cluster_count = sum(1 for c in cluster_counts if c <= 1)
    single_cluster_pct = 100 * single_cluster_count / len(cluster_counts) if cluster_counts else 0

    print(f"  Average clusters: {avg_clusters:.1f}")
    print(f"  Median clusters: {median_clusters:.1f}")
    print(f"  Max clusters: {max_clusters}")
    print(f"  Std clusters: {std_clusters:.1f}")
    print(f"  Single-cluster checkpoints: {single_cluster_pct:.1f}%")
    print(f"  Multi-cluster checkpoints: {multicluster_pct:.1f}%")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(cluster_counts),
        'avg_clusters': avg_clusters,
        'median_clusters': median_clusters,
        'max_clusters': max_clusters,
        'std_clusters': std_clusters,
        'single_cluster_percentage': single_cluster_pct,
        'multicluster_percentage': multicluster_pct,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'duration': duration
    }


def analyze_phase_boundary(results: list) -> dict:
    """
    Analyze results to identify phase boundary.

    Args:
        results: List of threshold test results

    Returns:
        dict with phase boundary analysis
    """
    print(f"\n{'='*80}")
    print(f"PHASE BOUNDARY ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    avg_clusters = [r['avg_clusters'] for r in results]
    median_clusters = [r['median_clusters'] for r in results]
    single_cluster_pcts = [r['single_cluster_percentage'] for r in results]
    multi_cluster_pcts = [r['multicluster_percentage'] for r in results]

    print("Threshold → Cluster Metrics:")
    print(f"{'Threshold':>10} | {'Avg':>8} | {'Median':>8} | {'Single%':>9} | {'Multi%':>8}")
    print("-" * 60)
    for i, threshold in enumerate(thresholds):
        print(f"{threshold:>10.0f} | {avg_clusters[i]:>8.1f} | {median_clusters[i]:>8.1f} | "
              f"{single_cluster_pcts[i]:>9.1f} | {multi_cluster_pcts[i]:>8.1f}")
    print()

    # Find largest jump in average clusters
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
    if jumps:
        critical_jump = max(jumps, key=lambda j: j['jump'])
        critical_threshold_lower = critical_jump['from_threshold']
        critical_threshold_upper = critical_jump['to_threshold']

        print(f"Critical Threshold Range: {critical_threshold_lower:.0f}-{critical_threshold_upper:.0f}")
        print(f"  Jump magnitude: +{critical_jump['jump']:.1f} clusters")
        print(f"  Jump ratio: {critical_jump['jump_ratio']:.2f}x")
        print()

        # Characterize transition sharpness
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
        print()

        # Regime classification
        print("Regime Classification:")
        for i, (threshold, avg, single_pct) in enumerate(zip(thresholds, avg_clusters, single_cluster_pcts)):
            if threshold < critical_threshold_lower:
                if single_pct > 50:
                    regime = "Standard (Single-Cluster Dominance)"
                else:
                    regime = "Transitional (Mixed)"
            elif threshold <= critical_threshold_upper:
                regime = "Critical (Phase Transition)"
            else:
                regime = "High-Frequency (Multi-Cluster)"
            print(f"  threshold={threshold:4.0f}: {regime:35s} "
                  f"(avg {avg:5.1f} clusters, {single_pct:4.1f}% single)")
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
    else:
        return {}


def main():
    """Run lower threshold scan to find phase boundary."""
    print("="*80)
    print("CYCLE 63: LOWER THRESHOLD SCAN - FINDING TRUE PHASE BOUNDARY")
    print("="*80)
    print()
    print("Testing lower thresholds to identify where phase transition occurs")
    print("from standard (single-cluster) to high-frequency (multi-cluster) regime.")
    print()

    # Test thresholds spanning suspected phase boundary
    test_thresholds = [500, 600, 700, 800, 900]

    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_threshold_scan(threshold, cycles=300)
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
        # Analyze phase boundary
        boundary_analysis = analyze_phase_boundary(successful_results)

        if boundary_analysis:
            print("="*80)
            print("🎉 INSIGHT #28: TRUE PHASE BOUNDARY IDENTIFIED")
            print("="*80)
            print()
            print(f"Phase transition occurs between {boundary_analysis['critical_threshold_lower']:.0f}")
            print(f"and {boundary_analysis['critical_threshold_upper']:.0f} burst threshold.")
            print()
            print(f"Transition characteristics:")
            print(f"  - Type: {boundary_analysis['transition_type']}")
            print(f"  - Sharpness: {boundary_analysis['transition_sharpness']:.2%}")
            print(f"  - Jump magnitude: {boundary_analysis['critical_jump_magnitude']:.1f} clusters")
            print(f"  - Jump ratio: {boundary_analysis['critical_jump_ratio']:.2f}x")
            print()
            print("Complete regime map:")
            print(f"  1. Standard regime (< {boundary_analysis['critical_threshold_lower']:.0f}):")
            print("     - Single-cluster dominance (>50% of time)")
            print("     - Low cluster formation rate (~1-10 clusters)")
            print("     - Agent-cluster coupling tight")
            print()
            print(f"  2. High-frequency regime (> {boundary_analysis['critical_threshold_upper']:.0f}):")
            print("     - Multi-cluster coexistence (100% of time)")
            print("     - High cluster formation rate (~100-300 clusters)")
            print("     - Agent-cluster decoupling")
            print()
            print("="*80)

            insight_28 = True
        else:
            print("⚠️ Unable to identify clear phase boundary")
            boundary_analysis = {}
            insight_28 = False
    else:
        print("⚠️ Insufficient successful tests for phase boundary analysis")
        boundary_analysis = {}
        insight_28 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "phase_boundary"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle63_lower_threshold_scan.json"

    output_data = {
        'experiment': 'cycle63_lower_threshold_scan',
        'test_thresholds': test_thresholds,
        'results': results,
        'boundary_analysis': boundary_analysis,
        'insight_28_discovered': insight_28,
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
