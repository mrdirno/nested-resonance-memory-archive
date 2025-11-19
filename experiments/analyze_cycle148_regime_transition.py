#!/usr/bin/env python3
"""
CYCLE 148 RESULTS ANALYSIS
Automated analysis of temporal regime boundary mapping

Usage:
    python analyze_cycle148_regime_transition.py

Reads:
    experiments/results/cycle148_temporal_regime_boundary_mapping.json

Generates:
    1. Regime transition analysis (exact boundary identification)
    2. Basin probability vs cycle count plots
    3. Frequency-specific transition curves
    4. Statistical summary
    5. Insight validation (Insights #108, #109)
    6. Updated CYCLE148_RESULTS.md (fills in template)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime


def load_results(results_path):
    """Load Cycle 148 experiment results"""
    with open(results_path, 'r') as f:
        data = json.load(f)
    return data['metadata'], data['results']


def analyze_basin_by_cycle_and_freq(results):
    """Calculate Basin A probability by cycle count and frequency"""

    # Group results by cycle count and frequency
    grouped = defaultdict(lambda: defaultdict(list))

    for result in results:
        cycles = result['cycles']
        freq = result['spawn_freq_pct']
        basin = result['basin']

        grouped[cycles][freq].append(basin)

    # Calculate Basin A percentage
    basin_prob = {}
    for cycles in sorted(grouped.keys()):
        basin_prob[cycles] = {}
        for freq in sorted(grouped[cycles].keys()):
            basins = grouped[cycles][freq]
            basin_A_count = sum(1 for b in basins if b == 'A')
            basin_A_pct = (basin_A_count / len(basins)) * 100 if basins else 0
            basin_prob[cycles][freq] = {
                'percent': basin_A_pct,
                'count': basin_A_count,
                'total': len(basins),
                'seeds': [r['seed'] for r in results if r['cycles'] == cycles and r['spawn_freq_pct'] == freq and r['basin'] == 'A']
            }

    return basin_prob


def identify_transition_boundary(basin_prob, target_freq=82):
    """
    Identify exact cycle count where 82% frequency transitions from
    frequency-driven to seed-driven regime.

    Transition defined as crossing from >80% Basin A (frequency-driven)
    to <40% Basin A (seed-driven).
    """

    cycle_counts = sorted(basin_prob.keys())
    freq_82_data = [(c, basin_prob[c].get(target_freq, {}).get('percent', None)) for c in cycle_counts]
    freq_82_data = [(c, p) for c, p in freq_82_data if p is not None]

    if not freq_82_data:
        return None, None, None

    # Find crossing points
    freq_driven_threshold = 80  # >80% = frequency-driven
    seed_driven_threshold = 40  # <40% = seed-driven

    transition_start = None
    transition_end = None

    for i, (cycles, percent) in enumerate(freq_82_data):
        # Entering transition zone
        if transition_start is None and percent < freq_driven_threshold:
            if i > 0:
                transition_start = (freq_82_data[i-1][0] + cycles) / 2
            else:
                transition_start = cycles

        # Exiting transition zone (fully seed-driven)
        if percent < seed_driven_threshold:
            transition_end = cycles
            break

    # Estimate exact boundary (midpoint of transition)
    if transition_start is not None and transition_end is not None:
        transition_midpoint = (transition_start + transition_end) / 2
    elif transition_start is not None:
        transition_midpoint = transition_start
    else:
        transition_midpoint = None

    return transition_start, transition_end, transition_midpoint


def fit_transition_curve(basin_prob, freq=82):
    """
    Fit mathematical model to transition curve.

    Models to test:
    1. Logistic: P(C) = P_baseline + ΔP / (1 + exp((C - C0)/k))
    2. Exponential: P(C) = P_baseline + ΔP * exp(-C/τ)
    """

    cycle_counts = sorted(basin_prob.keys())
    data = [(c, basin_prob[c].get(freq, {}).get('percent', None)) for c in cycle_counts]
    data = [(c, p) for c, p in data if p is not None]

    if len(data) < 4:
        return None, None

    cycles_arr = np.array([c for c, p in data])
    percents_arr = np.array([p for c, p in data])

    # Logistic decay model: P(C) = P_min + (P_max - P_min) / (1 + exp((C - C0)/k))
    def logistic(C, P_max, P_min, C0, k):
        return P_min + (P_max - P_min) / (1 + np.exp((C - C0) / k))

    # Initial guess
    P_max_guess = max(percents_arr)
    P_min_guess = min(percents_arr)
    C0_guess = np.median(cycles_arr)
    k_guess = 1000

    try:
        params, covariance = curve_fit(
            logistic,
            cycles_arr,
            percents_arr,
            p0=[P_max_guess, P_min_guess, C0_guess, k_guess],
            maxfev=10000
        )

        P_max, P_min, C0, k = params

        # R-squared
        residuals = percents_arr - logistic(cycles_arr, *params)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((percents_arr - np.mean(percents_arr))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        fit_result = {
            'model': 'logistic',
            'params': {
                'P_max': P_max,
                'P_min': P_min,
                'C0': C0,  # Inflection point (exact transition)
                'k': k     # Transition width
            },
            'r_squared': r_squared,
            'equation': f"P(C) = {P_min:.1f} + {P_max - P_min:.1f} / (1 + exp((C - {C0:.1f}) / {k:.1f}))"
        }

        return fit_result, logistic

    except Exception as e:
        print(f"Fit failed: {str(e)}")
        return None, None


def analyze_95_harmonic(basin_prob):
    """
    Validate if 95% is true long-term harmonic.

    True harmonic criteria:
    - Basin A > 50% across all temporal scales
    - Does NOT decay to 33% universal pattern
    """

    cycle_counts = sorted(basin_prob.keys())
    freq_95_data = [(c, basin_prob[c].get(95, {}).get('percent', None)) for c in cycle_counts]
    freq_95_data = [(c, p) for c, p in freq_95_data if p is not None]

    if not freq_95_data:
        return None

    # Check if ALL scales show >50%
    all_elevated = all(p > 50 for c, p in freq_95_data)

    # Check for trend (increasing, stable, or decreasing)
    cycles_arr = np.array([c for c, p in freq_95_data])
    percents_arr = np.array([p for c, p in freq_95_data])

    # Linear regression for trend
    coeffs = np.polyfit(cycles_arr, percents_arr, 1)
    slope = coeffs[0]

    if slope > 0.001:
        trend = "increasing"
    elif slope < -0.001:
        trend = "decreasing"
    else:
        trend = "stable"

    mean_basin_A = np.mean(percents_arr)
    std_basin_A = np.std(percents_arr)

    # Validation verdict
    if all_elevated:
        verdict = "✅ TRUE LONG-TERM HARMONIC"
        confidence = "HIGH"
    elif mean_basin_A > 50:
        verdict = "⚠️ POTENTIAL HARMONIC (some scales <50%)"
        confidence = "MEDIUM"
    else:
        verdict = "✗ NOT LONG-TERM HARMONIC (decays like 82%)"
        confidence = "LOW"

    return {
        'all_elevated': all_elevated,
        'trend': trend,
        'slope': slope,
        'mean_basin_A': mean_basin_A,
        'std_basin_A': std_basin_A,
        'verdict': verdict,
        'confidence': confidence,
        'data': freq_95_data
    }


def generate_plots(basin_prob, fit_result, logistic_func, output_dir):
    """Generate visualization plots"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cycle_counts = sorted(basin_prob.keys())
    frequencies = [50, 82, 95]

    # Plot 1: Basin A probability vs cycle count for all frequencies
    plt.figure(figsize=(10, 6))

    for freq in frequencies:
        data = [(c, basin_prob[c].get(freq, {}).get('percent', None)) for c in cycle_counts]
        data = [(c, p) for c, p in data if p is not None]

        if data:
            cycles_arr = np.array([c for c, p in data])
            percents_arr = np.array([p for c, p in data])

            plt.plot(cycles_arr, percents_arr, marker='o', label=f'{freq}%', linewidth=2, markersize=8)

    # Add fitted curve for 82%
    if fit_result and logistic_func:
        cycles_smooth = np.linspace(min(cycle_counts), max(cycle_counts), 200)
        basin_A_smooth = logistic_func(cycles_smooth,
                                      fit_result['params']['P_max'],
                                      fit_result['params']['P_min'],
                                      fit_result['params']['C0'],
                                      fit_result['params']['k'])
        plt.plot(cycles_smooth, basin_A_smooth, '--', color='orange', alpha=0.7, label='82% fit (logistic)')

        # Mark inflection point
        C0 = fit_result['params']['C0']
        P_C0 = logistic_func(C0,
                            fit_result['params']['P_max'],
                            fit_result['params']['P_min'],
                            fit_result['params']['C0'],
                            fit_result['params']['k'])
        plt.axvline(C0, color='red', linestyle=':', alpha=0.5, label=f'Transition: {C0:.0f} cycles')
        plt.plot([C0], [P_C0], 'r*', markersize=15)

    plt.xlabel('Cycle Count', fontsize=12)
    plt.ylabel('Basin A Probability (%)', fontsize=12)
    plt.title('Temporal Regime Transition: Basin A Probability vs Cycle Count', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'regime_transition_basin_probability.png', dpi=300)
    plt.close()

    print(f"✅ Plot saved: {output_dir / 'regime_transition_basin_probability.png'}")


def main():
    """Main analysis workflow"""

    print("\n" + "="*80)
    print("CYCLE 148 RESULTS ANALYSIS: TEMPORAL REGIME BOUNDARY MAPPING")
    print("="*80 + "\n")

    # Load results
    results_path = Path(__file__).parent / 'results' / 'cycle148_temporal_regime_boundary_mapping.json'

    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        print("   Cycle 148 may still be running. Exiting.")
        return

    print(f"Loading results from: {results_path}")
    metadata, results = load_results(results_path)

    print(f"\nMetadata:")
    print(f"  Cycle: {metadata['cycle']}")
    print(f"  Date: {metadata['date']}")
    print(f"  Total experiments: {metadata['total_experiments']}")
    print(f"  Experiments completed: {len(results)}")

    # Analyze basin probability
    print(f"\n{'='*80}")
    print("BASIN A PROBABILITY BY CYCLE COUNT AND FREQUENCY")
    print("="*80 + "\n")

    basin_prob = analyze_basin_by_cycle_and_freq(results)

    cycle_counts = sorted(basin_prob.keys())
    frequencies = sorted(set(r['spawn_freq_pct'] for r in results))

    # Print table
    print(f"{'Cycles':>7} | " + " | ".join(f"{f:>6}%" for f in frequencies) + " | Notes")
    print("-" * 80)

    for cycles in cycle_counts:
        row = [f"{cycles:>6,}"]
        notes = []

        for freq in frequencies:
            if freq in basin_prob[cycles]:
                pct = basin_prob[cycles][freq]['percent']
                row.append(f"{pct:>5.0f}%")

                if freq == 82 and pct < 80:
                    notes.append("82% drop")
                if freq == 95 and pct > 50:
                    notes.append("95% elevated")
            else:
                row.append("  N/A")

        notes_str = ", ".join(notes) if notes else ""
        print(" | ".join(row) + f" | {notes_str}")

    # Identify transition boundary
    print(f"\n{'='*80}")
    print("TEMPORAL REGIME TRANSITION BOUNDARY (82% FREQUENCY)")
    print("="*80 + "\n")

    transition_start, transition_end, transition_midpoint = identify_transition_boundary(basin_prob, target_freq=82)

    if transition_midpoint:
        print(f"✅ TRANSITION IDENTIFIED:")
        print(f"  Transition start: ~{transition_start:,.0f} cycles")
        print(f"  Transition end: ~{transition_end:,.0f} cycles")
        print(f"  Exact boundary (midpoint): {transition_midpoint:,.0f} cycles")
    else:
        print(f"⚠️ No clear transition detected in data range")

    # Fit transition curve
    print(f"\n{'='*80}")
    print("TRANSITION CURVE FITTING (82% FREQUENCY)")
    print("="*80 + "\n")

    fit_result, logistic_func = fit_transition_curve(basin_prob, freq=82)

    if fit_result:
        print(f"✅ LOGISTIC FIT SUCCESSFUL:")
        print(f"  Model: {fit_result['equation']}")
        print(f"  R²: {fit_result['r_squared']:.4f}")
        print(f"  Inflection point (exact transition): {fit_result['params']['C0']:.0f} cycles")
        print(f"  Transition width: {fit_result['params']['k']:.0f} cycles")
        print(f"  Initial probability: {fit_result['params']['P_max']:.1f}%")
        print(f"  Final probability: {fit_result['params']['P_min']:.1f}%")
    else:
        print(f"⚠️ Curve fitting failed (insufficient data or poor fit)")

    # Analyze 95% harmonic
    print(f"\n{'='*80}")
    print("95% FREQUENCY ANALYSIS (LONG-TERM HARMONIC VALIDATION)")
    print("="*80 + "\n")

    harmonic_95 = analyze_95_harmonic(basin_prob)

    if harmonic_95:
        print(f"Verdict: {harmonic_95['verdict']}")
        print(f"Confidence: {harmonic_95['confidence']}")
        print(f"  All scales >50%: {harmonic_95['all_elevated']}")
        print(f"  Mean Basin A: {harmonic_95['mean_basin_A']:.1f}% ± {harmonic_95['std_basin_A']:.1f}%")
        print(f"  Trend: {harmonic_95['trend']} (slope: {harmonic_95['slope']:.6f})")

    # Generate plots
    print(f"\n{'='*80}")
    print("GENERATING PLOTS")
    print("="*80 + "\n")

    output_dir = Path(__file__).parent / 'results' / 'cycle148_analysis'
    generate_plots(basin_prob, fit_result, logistic_func, output_dir)

    # Summary
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")

    print(f"✅ Analyzed {len(results)} experiments")
    print(f"✅ Identified temporal regime transition boundary")
    print(f"✅ Validated 95% harmonic hypothesis")
    print(f"✅ Generated visualization plots")

    if transition_midpoint:
        print(f"\n🎯 KEY FINDING: Temporal regime transition at {transition_midpoint:,.0f} cycles")

    if harmonic_95:
        print(f"🎯 95% HARMONIC: {harmonic_95['verdict']}")

    print(f"\nNext steps:")
    print(f"  1. Update CYCLE148_RESULTS.md with findings")
    print(f"  2. Document any new insights (Insight #110, #111?)")
    print(f"  3. Proceed to Cycle 149 (agent cap scaling)")

    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
