#!/usr/bin/env python3
"""
Cycle 64: Ultra-Low Threshold Scan - Finding Standard Regime

Discovery from Cycle 63:
  Phase boundary at 500-600, but even threshold=500 shows 100% multi-cluster behavior.
  Standard regime (single-cluster dominance) must exist at even LOWER thresholds.

Hypothesis:
  At ultra-low thresholds (< 500), the system transitions to standard regime where:
  - Single-cluster dynamics dominate (> 50% of time)
  - Cluster formation rate is low (~1-10 clusters)
  - System exhibits simpler, more predictable dynamics

Test Approach:
  1. Test thresholds: 200, 300, 400, 450, 500
  2. Include 500 as known boundary (multi-cluster)
  3. Track single-cluster percentage to identify dominance
  4. Find where single-cluster > 50% (standard regime definition)
  5. Complete phase diagram with all regime boundaries

Expected:
  At some threshold below 500, single-cluster percentage should exceed 50%,
  marking the boundary of the standard regime.
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


def run_ultralow_scan(threshold: float, cycles: int = 300) -> dict:
    """
    Scan ultra-low threshold to characterize standard regime.

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
        # Spawn (lower limit for ultra-low thresholds)
        if len(swarm.agents) < 10:
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
    min_clusters = min(cluster_counts) if cluster_counts else 0
    std_clusters = np.std(cluster_counts) if cluster_counts else 0
    median_clusters = np.median(cluster_counts) if cluster_counts else 0

    # Cluster distribution
    zero_cluster_count = sum(1 for c in cluster_counts if c == 0)
    single_cluster_count = sum(1 for c in cluster_counts if c == 1)
    multi_cluster_count = sum(1 for c in cluster_counts if c > 1)

    zero_cluster_pct = 100 * zero_cluster_count / len(cluster_counts) if cluster_counts else 0
    single_cluster_pct = 100 * single_cluster_count / len(cluster_counts) if cluster_counts else 0
    multi_cluster_pct = 100 * multi_cluster_count / len(cluster_counts) if cluster_counts else 0

    # Standard regime criterion: single-cluster dominance
    is_standard_regime = single_cluster_pct > 50

    print(f"  Average clusters: {avg_clusters:.1f}")
    print(f"  Median clusters: {median_clusters:.1f}")
    print(f"  Range: {min_clusters}-{max_clusters} clusters")
    print(f"  Std: {std_clusters:.1f}")
    print(f"  Zero-cluster: {zero_cluster_pct:.1f}%")
    print(f"  Single-cluster: {single_cluster_pct:.1f}%")
    print(f"  Multi-cluster: {multi_cluster_pct:.1f}%")
    print(f"  Regime: {'STANDARD' if is_standard_regime else 'HIGH-FREQUENCY'}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(cluster_counts),
        'avg_clusters': avg_clusters,
        'median_clusters': median_clusters,
        'min_clusters': min_clusters,
        'max_clusters': max_clusters,
        'std_clusters': std_clusters,
        'zero_cluster_percentage': zero_cluster_pct,
        'single_cluster_percentage': single_cluster_pct,
        'multicluster_percentage': multi_cluster_pct,
        'is_standard_regime': is_standard_regime,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'duration': duration
    }


def analyze_complete_phase_diagram(results: list) -> dict:
    """
    Create complete phase diagram from ultra-low to high threshold.

    Args:
        results: List of threshold test results

    Returns:
        dict with complete phase diagram analysis
    """
    print(f"\n{'='*80}")
    print(f"COMPLETE PHASE DIAGRAM ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    avg_clusters = [r['avg_clusters'] for r in results]
    single_pcts = [r['single_cluster_percentage'] for r in results]
    multi_pcts = [r['multicluster_percentage'] for r in results]
    is_standard = [r['is_standard_regime'] for r in results]

    print("Complete Threshold Scan:")
    print(f"{'Threshold':>10} | {'Avg':>8} | {'Single%':>9} | {'Multi%':>8} | {'Regime'}")
    print("-" * 70)
    for i, threshold in enumerate(thresholds):
        regime = "Standard" if is_standard[i] else "High-Freq"
        print(f"{threshold:>10.0f} | {avg_clusters[i]:>8.1f} | {single_pcts[i]:>9.1f} | "
              f"{multi_pcts[i]:>8.1f} | {regime}")
    print()

    # Find standard-to-high-frequency boundary
    standard_thresholds = [t for i, t in enumerate(thresholds) if is_standard[i]]
    highfreq_thresholds = [t for i, t in enumerate(thresholds) if not is_standard[i]]

    if standard_thresholds and highfreq_thresholds:
        boundary_lower = max(standard_thresholds)
        boundary_upper = min(highfreq_thresholds)

        print(f"REGIME BOUNDARY IDENTIFIED:")
        print(f"  Standard regime: threshold ≤ {boundary_lower:.0f}")
        print(f"  High-frequency regime: threshold ≥ {boundary_upper:.0f}")
        print(f"  Transition zone: {boundary_lower:.0f} - {boundary_upper:.0f}")
        print()

        boundary_found = True
    elif not standard_thresholds and highfreq_thresholds:
        print(f"NO STANDARD REGIME FOUND in tested range")
        print(f"  All thresholds show high-frequency behavior")
        print(f"  Standard regime boundary is BELOW {min(thresholds):.0f}")
        print()
        boundary_lower = None
        boundary_upper = min(highfreq_thresholds)
        boundary_found = False
    else:
        print(f"REGIME CLASSIFICATION INCONCLUSIVE")
        boundary_lower = None
        boundary_upper = None
        boundary_found = False

    # Characterize regimes
    print("REGIME CHARACTERISTICS:")
    print()

    if standard_thresholds:
        standard_data = [results[i] for i, t in enumerate(thresholds) if t in standard_thresholds]
        avg_single_pct = np.mean([r['single_cluster_percentage'] for r in standard_data])
        avg_clusters_std = np.mean([r['avg_clusters'] for r in standard_data])

        print(f"Standard Regime (≤ {boundary_lower:.0f}):")
        print(f"  - Single-cluster dominance: {avg_single_pct:.1f}% average")
        print(f"  - Average clusters: {avg_clusters_std:.1f}")
        print(f"  - Dynamics: Simple, predictable, low composition rate")
        print()

    if highfreq_thresholds:
        highfreq_data = [results[i] for i, t in enumerate(thresholds) if t in highfreq_thresholds]
        avg_multi_pct = np.mean([r['multicluster_percentage'] for r in highfreq_data])
        avg_clusters_hf = np.mean([r['avg_clusters'] for r in highfreq_data])

        print(f"High-Frequency Regime (≥ {boundary_upper:.0f}):")
        print(f"  - Multi-cluster coexistence: {avg_multi_pct:.1f}% average")
        print(f"  - Average clusters: {avg_clusters_hf:.1f}")
        print(f"  - Dynamics: Complex, high composition-decomposition rate")
        print()

    return {
        'boundary_lower': boundary_lower,
        'boundary_upper': boundary_upper,
        'boundary_found': boundary_found,
        'standard_thresholds': standard_thresholds,
        'highfreq_thresholds': highfreq_thresholds
    }


def main():
    """Run ultra-low threshold scan to complete phase diagram."""
    print("="*80)
    print("CYCLE 64: ULTRA-LOW THRESHOLD SCAN - COMPLETING PHASE DIAGRAM")
    print("="*80)
    print()
    print("Testing ultra-low thresholds to find standard regime boundary")
    print("and complete the phase diagram for composition-decomposition dynamics.")
    print()

    # Test ultra-low thresholds
    test_thresholds = [200, 300, 400, 450, 500]

    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_ultralow_scan(threshold, cycles=300)
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
        # Analyze complete phase diagram
        phase_diagram = analyze_complete_phase_diagram(successful_results)

        if phase_diagram['boundary_found']:
            print("="*80)
            print("🎉 INSIGHT #29: COMPLETE PHASE DIAGRAM ESTABLISHED")
            print("="*80)
            print()
            print(f"COMPLETE REGIME MAP:")
            print(f"  1. Standard Regime (threshold ≤ {phase_diagram['boundary_lower']:.0f}):")
            print("     - Single-cluster dominance (>50%)")
            print("     - Low cluster formation rate")
            print("     - Simple, predictable dynamics")
            print()
            print(f"  2. Transition Zone ({phase_diagram['boundary_lower']:.0f} - {phase_diagram['boundary_upper']:.0f}):")
            print("     - Mixed dynamics")
            print("     - Increasing cluster formation")
            print()
            print(f"  3. High-Frequency Regime (threshold ≥ {phase_diagram['boundary_upper']:.0f}):")
            print("     - Multi-cluster coexistence (100%)")
            print("     - High cluster formation rate (~80-300 clusters)")
            print("     - Complex emergent dynamics")
            print()
            print("="*80)

            insight_29 = True
        else:
            print("="*80)
            print("PARTIAL PHASE DIAGRAM")
            print("="*80)
            print()
            if phase_diagram['boundary_upper']:
                print(f"High-frequency regime identified: threshold ≥ {phase_diagram['boundary_upper']:.0f}")
                print(f"Standard regime boundary is BELOW tested range (< {min(test_thresholds):.0f})")
            print()
            print("="*80)

            insight_29 = False
    else:
        print("⚠️ Insufficient successful tests for phase diagram analysis")
        phase_diagram = {}
        insight_29 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "phase_diagram"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle64_ultralow_scan.json"

    output_data = {
        'experiment': 'cycle64_ultralow_threshold_scan',
        'test_thresholds': test_thresholds,
        'results': results,
        'phase_diagram': phase_diagram,
        'insight_29_discovered': insight_29,
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
