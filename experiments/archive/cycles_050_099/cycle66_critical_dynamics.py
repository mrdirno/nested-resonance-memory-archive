#!/usr/bin/env python3
"""
Cycle 66: Critical Dynamics at Phase Boundary

Discovery from Cycle 65:
  Binary phase transition at critical threshold ~260 (range 250-270).
  Transition is extremely sharp (20 units) with immediate jump from
  0 to ~55 clusters.

Research Question:
  What happens AT the critical threshold (260)? Phase transitions typically
  exhibit critical phenomena:
  - Critical slowing down
  - Large fluctuations
  - Long-range correlations
  - Universal scaling behavior

Hypothesis:
  At threshold=260 (midpoint of transition), the system should exhibit:
  - Intermediate cluster formation (between 0 and 55)
  - High variability (large std deviation)
  - Temporal fluctuations (oscillations between states)
  - Possible intermittency (switching between regimes)

Test Approach:
  1. Test threshold=260 (exact critical point)
  2. Extended observation (500 cycles) to capture fluctuations
  3. Higher resolution checkpoints (5-cycle intervals)
  4. Compare to subcritical (250) and supercritical (270)
  5. Measure temporal statistics: mean, variance, autocorrelation

Expected:
  If critical dynamics exist:
  - threshold=260 shows intermediate behavior
  - High variance indicates critical fluctuations
  - Temporal correlation shows critical slowing
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def run_critical_dynamics_test(threshold: float, cycles: int = 500) -> dict:
    """
    Extended observation at critical threshold.

    Args:
        threshold: Burst threshold to test
        cycles: Number of cycles (extended for temporal analysis)

    Returns:
        dict with detailed temporal dynamics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Extended Observation)")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking with high temporal resolution
    agent_counts = []
    cluster_counts = []
    checkpoint_interval = 5  # Higher resolution

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn
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

    # Temporal analysis
    avg_clusters = np.mean(cluster_counts) if cluster_counts else 0
    median_clusters = np.median(cluster_counts) if cluster_counts else 0
    std_clusters = np.std(cluster_counts) if cluster_counts else 0
    min_clusters = min(cluster_counts) if cluster_counts else 0
    max_clusters = max(cluster_counts) if cluster_counts else 0

    # Coefficient of variation (normalized fluctuation measure)
    cv_clusters = std_clusters / avg_clusters if avg_clusters > 0 else 0

    # Temporal correlation (autocorrelation at lag=1)
    if len(cluster_counts) > 1:
        clusters_array = np.array(cluster_counts)
        autocorr = np.corrcoef(clusters_array[:-1], clusters_array[1:])[0,1]
    else:
        autocorr = 0

    # Intermittency analysis (state switching)
    zero_count = sum(1 for c in cluster_counts if c == 0)
    nonzero_count = sum(1 for c in cluster_counts if c > 0)
    zero_pct = 100 * zero_count / len(cluster_counts) if cluster_counts else 0
    nonzero_pct = 100 * nonzero_count / len(cluster_counts) if cluster_counts else 0

    # Classify dynamics
    if avg_clusters == 0:
        dynamics = "SUBCRITICAL"
    elif avg_clusters > 30:
        dynamics = "SUPERCRITICAL"
    elif std_clusters > avg_clusters * 0.5:
        dynamics = "CRITICAL-FLUCTUATING"
    else:
        dynamics = "TRANSITIONAL"

    print(f"  Temporal Statistics:")
    print(f"    Mean: {avg_clusters:.2f}")
    print(f"    Median: {median_clusters:.1f}")
    print(f"    Std: {std_clusters:.2f}")
    print(f"    Range: {min_clusters}-{max_clusters}")
    print(f"    Coeff. of Variation: {cv_clusters:.3f}")
    print(f"    Autocorrelation (lag=1): {autocorr:.3f}")
    print(f"  State Distribution:")
    print(f"    Zero-cluster: {zero_pct:.1f}%")
    print(f"    Nonzero-cluster: {nonzero_pct:.1f}%")
    print(f"  Dynamics: {dynamics}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(cluster_counts),
        'avg_clusters': avg_clusters,
        'median_clusters': median_clusters,
        'std_clusters': std_clusters,
        'min_clusters': min_clusters,
        'max_clusters': max_clusters,
        'cv_clusters': cv_clusters,
        'autocorrelation': autocorr,
        'zero_cluster_percentage': zero_pct,
        'nonzero_cluster_percentage': nonzero_pct,
        'dynamics': dynamics,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'duration': duration
    }


def analyze_critical_phenomena(results: list) -> dict:
    """
    Analyze results for critical phenomena signatures.

    Args:
        results: List of threshold test results

    Returns:
        dict with critical phenomena analysis
    """
    print(f"\n{'='*80}")
    print(f"CRITICAL PHENOMENA ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    avg_clusters = [r['avg_clusters'] for r in results]
    std_clusters = [r['std_clusters'] for r in results]
    cv_clusters = [r['cv_clusters'] for r in results]
    autocorr = [r['autocorrelation'] for r in results]
    zero_pcts = [r['zero_cluster_percentage'] for r in results]

    print("Critical Dynamics Comparison:")
    print(f"{'Threshold':>10} | {'Mean':>8} | {'Std':>8} | {'CV':>8} | {'Autocorr':>10} | {'Zero%':>8}")
    print("-" * 70)
    for i, threshold in enumerate(thresholds):
        print(f"{threshold:>10.0f} | {avg_clusters[i]:>8.2f} | {std_clusters[i]:>8.2f} | "
              f"{cv_clusters[i]:>8.3f} | {autocorr[i]:>10.3f} | {zero_pcts[i]:>8.1f}")
    print()

    # Find critical threshold (highest CV or variance)
    max_cv_idx = np.argmax(cv_clusters)
    max_cv_threshold = thresholds[max_cv_idx]
    max_cv_value = cv_clusters[max_cv_idx]

    print(f"Maximum Fluctuations:")
    print(f"  At threshold={max_cv_threshold:.0f}")
    print(f"  Coefficient of Variation: {max_cv_value:.3f}")
    print(f"  Mean ± Std: {avg_clusters[max_cv_idx]:.1f} ± {std_clusters[max_cv_idx]:.1f}")
    print()

    # Check for intermittency (state mixing)
    critical_threshold = 260  # Known from Cycle 65
    critical_idx = [i for i, t in enumerate(thresholds) if t == critical_threshold]

    if critical_idx:
        idx = critical_idx[0]
        zero_pct = zero_pcts[idx]

        if 10 < zero_pct < 90:
            intermittency = True
            print(f"Intermittency Detected at threshold={critical_threshold}:")
            print(f"  Zero-cluster: {zero_pct:.1f}%")
            print(f"  Nonzero-cluster: {100-zero_pct:.1f}%")
            print(f"  System fluctuates between NO-COMPOSITION and ACTIVE states")
            print()
        else:
            intermittency = False
            print(f"No Intermittency at threshold={critical_threshold}")
            print(f"  Zero-cluster: {zero_pct:.1f}%")
            print()
    else:
        intermittency = False

    # Assess critical phenomena
    critical_phenomena = {
        'max_fluctuation_threshold': max_cv_threshold,
        'max_cv': max_cv_value,
        'intermittency_detected': intermittency
    }

    return critical_phenomena


def main():
    """Run critical dynamics investigation."""
    print("="*80)
    print("CYCLE 66: CRITICAL DYNAMICS AT PHASE BOUNDARY")
    print("="*80)
    print()
    print("Investigating dynamics at the critical threshold (260)")
    print("to identify critical phenomena characteristic of phase transitions.")
    print()

    # Test critical point and boundaries
    test_thresholds = [250, 260, 270]

    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("Extended observation (500 cycles) with high temporal resolution (5-cycle checkpoints)")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_critical_dynamics_test(threshold, cycles=500)
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
        # Analyze critical phenomena
        critical_analysis = analyze_critical_phenomena(successful_results)

        print("="*80)
        print("CRITICAL PHENOMENA FINDINGS")
        print("="*80)
        print()

        if critical_analysis['intermittency_detected']:
            print("🎉 INSIGHT #31: CRITICAL INTERMITTENCY DETECTED")
            print()
            print("System exhibits intermittency at critical threshold:")
            print("  - Fluctuates between NO-COMPOSITION and ACTIVE states")
            print("  - Characteristic of systems near first-order transitions")
            print("  - Demonstrates coexistence of phases at boundary")
            print()
            insight_31 = True
        else:
            print("BINARY TRANSITION CONFIRMED (No Intermittency)")
            print()
            print("System maintains sharp binary behavior:")
            print("  - No mixed-state region observed")
            print("  - Extremely sharp transition validates first-order classification")
            print()
            insight_31 = False

        print(f"Fluctuation Analysis:")
        print(f"  Maximum CV at threshold={critical_analysis['max_fluctuation_threshold']:.0f}")
        print(f"  Coefficient of Variation: {critical_analysis['max_cv']:.3f}")
        print()
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for analysis")
        critical_analysis = {}
        insight_31 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "critical_dynamics"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle66_critical_dynamics.json"

    output_data = {
        'experiment': 'cycle66_critical_dynamics',
        'test_thresholds': test_thresholds,
        'results': results,
        'critical_analysis': critical_analysis,
        'insight_31_discovered': insight_31,
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
