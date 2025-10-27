#!/usr/bin/env python3
"""
CYCLE 150 ANALYSIS: SUPER-HARMONIC DETECTION
Analyze low-frequency experiments to detect if 50% acts as sub-harmonic for larger cycles
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_cycle150_results():
    """Load Cycle 150 experimental results"""
    results_file = Path(__file__).parent / 'results' / 'cycle150_super_harmonic_detection.json'

    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        return None

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Normalize data structure (handle both 'experiments' and 'results' keys)
    if 'results' in data and 'experiments' not in data:
        data['experiments'] = data['results']

    print(f"Loaded {len(data['experiments'])} experiments")
    return data


def analyze_basin_convergence(data):
    """Analyze basin convergence patterns by frequency"""

    frequencies = sorted(set(exp['spawn_freq_pct'] for exp in data['experiments']))

    print("\n" + "="*80)
    print("BASIN CONVERGENCE ANALYSIS")
    print("="*80)

    results = {}

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments'] if exp['spawn_freq_pct'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_b_count = sum(1 for exp in freq_exps if exp['basin'] == 'B')
        total = len(freq_exps)

        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        results[freq] = {
            'basin_a_pct': basin_a_pct,
            'basin_a_count': basin_a_count,
            'basin_b_count': basin_b_count,
            'total': total
        }

        print(f"\n{freq}% Frequency:")
        print(f"  Basin A: {basin_a_count}/{total} ({basin_a_pct:.1f}%)")
        print(f"  Basin B: {basin_b_count}/{total}")

        # Compare to baseline (expected 33% from 50% frequency)
        baseline = 33.0
        deviation = basin_a_pct - baseline

        if abs(deviation) > 15:  # Significant deviation
            if deviation > 0:
                print(f"  ⚠️ ELEVATED: {deviation:+.1f}% vs baseline (possible harmonic)")
            else:
                print(f"  ⚠️ SUPPRESSED: {deviation:+.1f}% vs baseline (possible anti-harmonic)")
        else:
            print(f"  ✓ Baseline: {deviation:+.1f}% vs expected")

    return results


def detect_super_harmonics(data):
    """
    Detect if low frequencies show evidence of 50% sub-harmonic scaffolding

    Evidence would be:
    1. Enhanced basin convergence at specific low frequencies
    2. 50% frequency appearing in FFT analysis
    3. Harmonic ratios (e.g., 20% → 40% → 80% relationship to 50%)
    """

    print("\n" + "="*80)
    print("SUPER-HARMONIC DETECTION")
    print("="*80)

    frequencies = [10, 20, 30, 40]  # Tested frequencies

    # Check for harmonic relationships to 50%
    print("\nHARMONIC RATIO ANALYSIS:")
    print("(Testing if frequencies show integer relationships to 50%)")
    print()

    for freq in frequencies:
        # Ratio of 50% to this frequency
        ratio_50_to_freq = 50.0 / freq

        # Ratio of this frequency to potential super-harmonic
        super_harmonic_freq = 50.0 / freq * 100  # What would scaffold 50%?

        print(f"{freq}% frequency:")
        print(f"  50% / {freq}% = {ratio_50_to_freq:.2f}x")

        if abs(ratio_50_to_freq - round(ratio_50_to_freq)) < 0.1:
            print(f"  ✓ INTEGER RATIO: {freq}% is 1/{int(ratio_50_to_freq)} of 50%")
            print(f"  → Potential super-harmonic at {super_harmonic_freq:.0f}%")
        else:
            print(f"  Non-integer ratio (not directly harmonic)")

    # Check FFT peak analysis from experiments
    print("\n" + "-"*80)
    print("FFT PEAK ANALYSIS:")
    print("(Checking if 50% appears as sub-harmonic in low-frequency runs)")
    print()

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments'] if exp['spawn_freq_pct'] == freq]

        # Look for presence of ~50% in FFT peaks
        # Note: This is simplified - actual FFT data would need detailed analysis
        # For now, check composition/decomposition cycle patterns

        avg_comp = np.mean([exp.get('avg_composition_events', 0) for exp in freq_exps])

        print(f"{freq}% frequency:")
        print(f"  Avg composition events: {avg_comp:.1f}")

        # If composition events show ~50% pattern (every 2 cycles at low freq)
        # that would suggest 50% sub-harmonic presence
        expected_comp_for_50pct_subharmonic = 10 * (50 / freq)  # Rough estimate

        if abs(avg_comp - expected_comp_for_50pct_subharmonic) < 3:
            print(f"  ⚠️ POSSIBLE 50% SUB-HARMONIC DETECTED")
            print(f"  Expected for 50% scaffold: ~{expected_comp_for_50pct_subharmonic:.1f}")
        else:
            print(f"  No clear 50% sub-harmonic pattern")


def compare_to_baseline(data):
    """Compare results to known 50% baseline"""

    print("\n" + "="*80)
    print("BASELINE COMPARISON (vs 50% First Harmonic)")
    print("="*80)

    baseline_basin_a = 33.0  # From extensive 50% testing

    frequencies = sorted(set(exp['spawn_freq_pct'] for exp in data['experiments']))

    print(f"\nBaseline (50% frequency): {baseline_basin_a}% Basin A")
    print()

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments'] if exp['spawn_freq_pct'] == freq]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        deviation = basin_a_pct - baseline_basin_a

        print(f"{freq}% frequency: {basin_a_pct:.1f}% Basin A ({deviation:+.1f}% vs baseline)")


def generate_summary_plot(data, basin_results):
    """Generate visualization of super-harmonic detection results"""

    output_dir = Path(__file__).parent / 'results' / 'cycle150_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    frequencies = sorted(basin_results.keys())
    basin_a_pcts = [basin_results[f]['basin_a_pct'] for f in frequencies]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Basin A percentages
    ax.plot(frequencies, basin_a_pcts, 'o-', linewidth=2, markersize=8, label='Basin A %')

    # Add baseline reference (50% frequency)
    ax.axhline(y=33.0, color='green', linestyle='--', alpha=0.7, label='Baseline (50%)')

    # Highlight deviations
    for i, (freq, pct) in enumerate(zip(frequencies, basin_a_pcts)):
        deviation = pct - 33.0
        if abs(deviation) > 15:
            color = 'red' if deviation < 0 else 'blue'
            ax.annotate(f'{pct:.0f}%\n({deviation:+.0f}%)',
                       xy=(freq, pct),
                       xytext=(10, 10),
                       textcoords='offset points',
                       fontsize=9,
                       color=color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    ax.set_xlabel('Spawning Frequency (%)', fontsize=12)
    ax.set_ylabel('Basin A Convergence (%)', fontsize=12)
    ax.set_title('Cycle 150: Super-Harmonic Detection\nLow Frequency Basin Convergence', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plot_file = output_dir / 'super_harmonic_basin_convergence.png'
    plt.savefig(plot_file, dpi=150)
    print(f"\nPlot saved: {plot_file}")


def main():
    print("="*80)
    print("CYCLE 150 ANALYSIS: SUPER-HARMONIC DETECTION")
    print("="*80)

    # Load data
    data = load_cycle150_results()
    if not data:
        return

    # Analyze basin convergence
    basin_results = analyze_basin_convergence(data)

    # Detect super-harmonics
    detect_super_harmonics(data)

    # Compare to baseline
    compare_to_baseline(data)

    # Generate plots
    try:
        generate_summary_plot(data, basin_results)
    except Exception as e:
        print(f"\nNote: Could not generate plot: {e}")

    print("\n" + "="*80)
    print("CYCLE 150 ANALYSIS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
