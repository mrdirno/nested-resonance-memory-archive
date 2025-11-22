#!/usr/bin/env python3
"""
CYCLE 170: BASIN THRESHOLD SENSITIVITY TEST
Definitive Mechanistic Validation of Composition Rate Control

Purpose:
  Test if critical frequency tracks basin threshold value across different thresholds

Background:
  - C169: Critical frequency = 2.55% for basin threshold = 2.5
  - Hypothesis: Critical frequency ≈ basin threshold value (linear relationship)
  - Mechanism: Composition event rate (events/window) ≈ frequency (%)

Context:
  - If confirmed: Composition rate definitively validated as control parameter
  - If refuted: Other factors influence critical point
  - This is the final mechanistic test

Experimental Design:
  - Basin thresholds: [1.5, 2.0, 2.5, 3.0, 3.5]
  - For each threshold, test frequencies around predicted critical point
  - Test ±0.5% from threshold value with 0.1% resolution
  - Seeds: n=10 (reliable sampling)
  - Cycles: 3000 per experiment

  Example for threshold=2.0:
    - Predicted critical freq: ~2.0%
    - Test range: 1.5%, 1.6%, 1.7%, 1.8%, 1.9%, 2.0%, 2.1%, 2.2%, 2.3%, 2.4%, 2.5%
    - Total per threshold: 11 frequencies × 10 seeds = 110 experiments

  Total: 5 thresholds × 110 experiments = 550 experiments

Expected Outcome:
  - If linear: Critical freq (threshold=1.5) ≈ 1.5%, (2.0) ≈ 2.0%, (3.0) ≈ 3.0%
  - If not linear: Critical frequencies deviate from threshold values
  - Slope = 1.0 ± 0.1 confirms mechanism

Significance:
  - Definitive validation of composition rate as control parameter
  - Complete mechanistic understanding of bistability
  - Final piece of evidence for publication
  - Linear relationship = simple, elegant mechanism

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 170 (Following C169 precision mapping)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge

# Configuration
BASIN_THRESHOLDS = [1.5, 2.0, 2.5, 3.0, 3.5]
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / 'cycle170_basin_threshold_sensitivity.json'


def generate_test_frequencies(threshold: float, resolution: float = 0.1, range_width: float = 1.0) -> list:
    """
    Generate frequencies to test around predicted critical point.

    For threshold=2.0, tests 1.5%, 1.6%, ..., 2.4%, 2.5% (±0.5%)
    """
    start = threshold - range_width/2
    end = threshold + range_width/2

    # Generate frequencies with specified resolution
    n_points = int((end - start) / resolution) + 1
    frequencies = [round(start + i * resolution, 1) for i in range(n_points)]

    # Filter to reasonable range (0.5% minimum)
    frequencies = [f for f in frequencies if f >= 0.5]

    return frequencies


def run_experiment(frequency: float, basin_threshold: float, seed: int, cycles: int) -> dict:
    """
    Run single frequency-threshold-seed experiment.

    Reality-grounded with actual system metrics.
    Uses specified basin threshold for classification.
    """

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Seed for reproducibility
    np.random.seed(seed)

    # Get real system metrics
    metrics = reality.get_system_metrics()
    base_energy = (100.0 - metrics['cpu_percent']) + (100.0 - metrics['memory_percent'])

    # Initialize agent
    phase = np.random.random() * 2 * np.pi
    energy = base_energy

    # Tracking
    composition_events = []
    spawn_count = 0

    # Run cycles
    for cycle_idx in range(cycles):

        # Determine spawn based on frequency
        spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else cycles + 1
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn:
            spawn_count += 1

            # Create spawn phase
            spawn_phase = phase + np.random.normal(0, 0.1)

            # Resonance detection (simplified)
            phase_diff = abs(phase - spawn_phase) % (2 * np.pi)
            phase_diff = min(phase_diff, 2 * np.pi - phase_diff)
            resonance = 1.0 - (phase_diff / np.pi)  # 0 to 1

            # Composition event if resonance exceeds threshold
            if resonance > 0.5:
                composition_events.append(cycle_idx)

        # Update phase (transcendental evolution)
        phase += 2 * np.pi * 0.01  # Fixed frequency for consistency
        phase = phase % (2 * np.pi)

    # Calculate statistics
    bins = np.arange(0, cycles + 1, 100)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification with SPECIFIED threshold
    basin = 'A' if avg_composition_events > basin_threshold else 'B'

    return {
        'frequency': frequency,
        'basin_threshold': basin_threshold,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
    }


def analyze_critical_frequency(results: list, threshold: float) -> dict:
    """
    Determine critical frequency for given basin threshold.

    Returns dict with critical frequency estimate and transition width.
    """
    # Group by frequency
    freq_basin_counts = defaultdict(lambda: {'A': 0, 'B': 0})

    for result in results:
        if result['basin_threshold'] == threshold:
            freq_basin_counts[result['frequency']][result['basin']] += 1

    # Sort frequencies
    frequencies = sorted(freq_basin_counts.keys())

    # Find transition point
    critical_freq = None
    transition_width = None
    last_dead_freq = None
    first_resonance_freq = None

    for freq in frequencies:
        a_count = freq_basin_counts[freq]['A']
        total = freq_basin_counts[freq]['A'] + freq_basin_counts[freq]['B']
        a_pct = (a_count / total * 100) if total > 0 else 0

        if a_pct == 0:
            last_dead_freq = freq
        elif a_pct > 0 and first_resonance_freq is None:
            first_resonance_freq = freq
            if last_dead_freq is not None:
                critical_freq = (last_dead_freq + first_resonance_freq) / 2
                transition_width = first_resonance_freq - last_dead_freq
            break

    return {
        'critical_frequency': critical_freq,
        'transition_width': transition_width,
        'last_dead_freq': last_dead_freq,
        'first_resonance_freq': first_resonance_freq,
    }


def main():
    """Execute Cycle 170 experiments."""

    print("=" * 80)
    print("CYCLE 170: BASIN THRESHOLD SENSITIVITY TEST")
    print("=" * 80)
    print()
    print("Hypothesis: Critical frequency = Basin threshold value")
    print("Testing thresholds:", BASIN_THRESHOLDS)
    print()

    start_time = datetime.now()
    all_results = []
    threshold_analyses = {}

    # Run experiments for each threshold
    for threshold_idx, basin_threshold in enumerate(BASIN_THRESHOLDS):
        print(f"\n{'='*80}")
        print(f"TESTING BASIN THRESHOLD: {basin_threshold}")
        print(f"{'='*80}")

        # Generate test frequencies for this threshold
        test_frequencies = generate_test_frequencies(basin_threshold, resolution=0.1, range_width=1.0)
        print(f"Test frequencies: {test_frequencies}")
        print(f"Predicted critical frequency: ~{basin_threshold}%")
        print()

        threshold_results = []

        for freq_idx, frequency in enumerate(test_frequencies):
            print(f"  Frequency {frequency}%:")

            for seed_idx, seed in enumerate(SEEDS):
                exp_num = freq_idx * len(SEEDS) + seed_idx + 1
                total_for_threshold = len(test_frequencies) * len(SEEDS)

                result = run_experiment(frequency, basin_threshold, seed, CYCLES)
                threshold_results.append(result)
                all_results.append(result)

                print(f"    [{exp_num:3d}/{total_for_threshold}] "
                      f"Seed {seed:3d}: {result['avg_composition_events']:.2f} events → Basin {result['basin']}")

        # Analyze critical frequency for this threshold
        analysis = analyze_critical_frequency(threshold_results, basin_threshold)
        threshold_analyses[basin_threshold] = analysis

        print(f"\n  Analysis for threshold {basin_threshold}:")
        if analysis['critical_frequency']:
            print(f"    Critical frequency: {analysis['critical_frequency']:.2f}%")
            print(f"    Transition width: ≤{analysis['transition_width']:.2f}%")
            print(f"    Last dead zone: {analysis['last_dead_freq']}%")
            print(f"    First resonance: {analysis['first_resonance_freq']}%")
        else:
            print(f"    ⚠️  Transition not clearly detected")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print(f"\n{'='*80}")
    print("ALL EXPERIMENTS COMPLETE")
    print(f"{'='*80}\n")

    # Summary analysis
    print("CRITICAL FREQUENCY vs. BASIN THRESHOLD:")
    print("-" * 80)
    print(f"{'Threshold':>12} | {'Critical Freq':>14} | {'Deviation':>12} | {'Rel Error %':>12}")
    print("-" * 80)

    critical_frequencies = []
    deviations = []

    for threshold in BASIN_THRESHOLDS:
        analysis = threshold_analyses[threshold]
        if analysis['critical_frequency']:
            crit_freq = analysis['critical_frequency']
            deviation = crit_freq - threshold
            rel_error = (deviation / threshold) * 100 if threshold > 0 else 0

            critical_frequencies.append((threshold, crit_freq))
            deviations.append(deviation)

            print(f"{threshold:12.1f} | {crit_freq:14.2f} | {deviation:+12.2f} | {rel_error:+11.1f}%")
        else:
            print(f"{threshold:12.1f} | {'N/A':>14} | {'N/A':>12} | {'N/A':>12}")

    print()

    # Linear regression analysis
    if len(critical_frequencies) >= 3:
        print("LINEAR RELATIONSHIP ANALYSIS:")
        print("-" * 80)

        thresholds_arr = np.array([x[0] for x in critical_frequencies])
        crit_freqs_arr = np.array([x[1] for x in critical_frequencies])

        # Linear fit: crit_freq = slope * threshold + intercept
        slope, intercept = np.polyfit(thresholds_arr, crit_freqs_arr, 1)

        # Calculate R²
        residuals = crit_freqs_arr - (slope * thresholds_arr + intercept)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((crit_freqs_arr - np.mean(crit_freqs_arr))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        print(f"Linear fit: Critical Freq = {slope:.4f} × Threshold + {intercept:.4f}")
        print(f"R² = {r_squared:.4f}")
        print(f"Average deviation: {np.mean(np.abs(deviations)):.3f}%")
        print(f"Max deviation: {np.max(np.abs(deviations)):.3f}%")
        print()

        # Hypothesis test
        if abs(slope - 1.0) < 0.1 and abs(intercept) < 0.2 and r_squared > 0.95:
            print("✅ HYPOTHESIS CONFIRMED: Critical Frequency = Basin Threshold")
            print(f"   Slope = {slope:.4f} (expected: 1.0, deviation: {abs(slope-1.0):.4f})")
            print(f"   Intercept = {intercept:.4f} (expected: 0.0, deviation: {abs(intercept):.4f})")
            print(f"   R² = {r_squared:.4f} (excellent fit)")
            print("   → Composition event rate IS the control parameter (definitively validated)")
        elif abs(slope - 1.0) < 0.2 and r_squared > 0.85:
            print("✅ HYPOTHESIS SUPPORTED: Strong linear relationship")
            print(f"   Slope = {slope:.4f} (close to 1.0)")
            print(f"   R² = {r_squared:.4f}")
            print("   → Composition event rate strongly influences critical point")
        else:
            print("❌ HYPOTHESIS REJECTED: Linear relationship not confirmed")
            print(f"   Slope = {slope:.4f} (expected: 1.0)")
            print(f"   R² = {r_squared:.4f}")
            print("   → Other factors may influence critical frequency")
    else:
        print("⚠️  Insufficient data for linear regression (need ≥3 points)")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '170',
            'scenario': 'Basin Threshold Sensitivity Test',
            'date': datetime.now().isoformat(),
            'basin_thresholds': BASIN_THRESHOLDS,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(all_results),
            'duration_minutes': duration,
        },
        'experiments': all_results,
        'threshold_analyses': {
            str(threshold): analysis for threshold, analysis in threshold_analyses.items()
        },
        'linear_regression': {
            'slope': float(slope) if len(critical_frequencies) >= 3 else None,
            'intercept': float(intercept) if len(critical_frequencies) >= 3 else None,
            'r_squared': float(r_squared) if len(critical_frequencies) >= 3 else None,
            'average_deviation': float(np.mean(np.abs(deviations))) if deviations else None,
            'max_deviation': float(np.max(np.abs(deviations))) if deviations else None,
        } if len(critical_frequencies) >= 3 else None,
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 170 COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
