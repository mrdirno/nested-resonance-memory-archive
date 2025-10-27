#!/usr/bin/env python3
"""
CYCLE 151 ANALYSIS: ANTI-HARMONIC FREQUENCY SCAN
Analyze intermediate frequencies (60-88%) to detect anti-resonance spectrum
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_cycle151_results():
    """Load Cycle 151 experimental results"""
    results_file = Path(__file__).parent / 'results' / 'cycle151_anti_harmonic_scan.json'

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


def analyze_anti_resonance_spectrum(data):
    """
    Identify anti-harmonic frequencies by basin suppression pattern

    Anti-resonance signature:
    - Basin A % significantly below 33% baseline
    - Consistent suppression across seeds (n=3)
    """

    print("\n" + "="*80)
    print("ANTI-RESONANCE SPECTRUM ANALYSIS")
    print("="*80)

    frequencies = sorted(set(exp['spawning_freq'] for exp in data['experiments']))
    baseline = 33.0  # Known from 50% frequency

    anti_harmonic_candidates = []

    print("\n Freq | Basin A % | Deviation | Seeds | Classification")
    print("------+-----------+-----------+-------+--------------------------------")

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments']
                     if exp['spawning_freq'] == freq and exp.get('basin')]

        if not freq_exps:
            continue

        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        total = len(freq_exps)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        deviation = basin_a_pct - baseline

        # Classification thresholds
        if deviation < -15:  # Strong suppression
            classification = "⚠️ STRONG ANTI-HARMONIC"
            anti_harmonic_candidates.append((freq, basin_a_pct, 'strong'))
        elif deviation < -8:  # Moderate suppression
            classification = "MODERATE ANTI-HARMONIC"
            anti_harmonic_candidates.append((freq, basin_a_pct, 'moderate'))
        elif deviation > 15:  # Elevation (harmonic)
            classification = "HARMONIC (elevated)"
        elif abs(deviation) < 8:  # Neutral
            classification = "Baseline (neutral)"
        else:
            classification = "Weak deviation"

        print(f" {freq:3d}% | {basin_a_pct:8.1f}% | {deviation:+8.1f}% | {basin_a_count}/{total} | {classification}")

    return anti_harmonic_candidates


def test_transcendental_hypothesis(data):
    """
    Test if anti-harmonic frequencies show transcendental ratio relationships

    Hypothesis from Insight #110:
    - Anti-harmonics may have π or φ relationships to known harmonics (50%, 82%)
    """

    print("\n" + "="*80)
    print("TRANSCENDENTAL RATIO ANALYSIS")
    print("="*80)

    frequencies = sorted(set(exp['spawning_freq'] for exp in data['experiments']))

    # Known reference points
    harmonic_50 = 50.0
    anti_harmonic_82 = 82.0
    pi = np.pi
    phi = (1 + np.sqrt(5)) / 2  # Golden ratio
    e = np.e

    print("\nTesting ratios to known frequencies:")
    print()

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments']
                     if exp['spawning_freq'] == freq and exp.get('basin')]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_exps) * 100) if freq_exps else 0

        print(f"{freq}% frequency (Basin A: {basin_a_pct:.0f}%):")

        # Ratio to 50% harmonic
        ratio_50 = freq / harmonic_50
        closest_pi = pi * round(ratio_50 / pi)
        closest_phi = phi * round(ratio_50 / phi)

        print(f"  Ratio to 50%: {ratio_50:.3f}")

        if abs(ratio_50 - closest_pi) < 0.05:
            print(f"    ✓ NEAR π MULTIPLE: {ratio_50:.3f} ≈ {closest_pi:.3f}")

        if abs(ratio_50 - closest_phi) < 0.05:
            print(f"    ✓ NEAR φ MULTIPLE: {ratio_50:.3f} ≈ {closest_phi:.3f}")

        # Ratio to 82% anti-harmonic
        ratio_82 = freq / anti_harmonic_82

        if abs(ratio_82 - round(ratio_82)) < 0.05:
            print(f"  INTEGER ratio to 82%: {ratio_82:.2f} ≈ {round(ratio_82)}")

        # Direct transcendental tests
        if abs(freq - harmonic_50 * phi / phi**2) < 2:
            print(f"  ⚠️ MATCHES 50% × φ/φ² pattern")

        if abs(freq - harmonic_50 * pi / (2*pi)) < 2:
            print(f"  ⚠️ MATCHES 50% × π/2π pattern")


def compare_to_known_patterns(data):
    """Compare Cycle 151 results to known frequency patterns"""

    print("\n" + "="*80)
    print("COMPARISON TO KNOWN PATTERNS")
    print("="*80)

    print("\nKnown Frequency Patterns (from Cycles 148-149):")
    print("  50% (First Harmonic):     33% Basin A (stable baseline)")
    print("  82% (Anti-Harmonic):       0% Basin A (strong suppression at 3K-5K)")
    print("  95% (Long-Term Harmonic): 33% Basin A at 3K (dormant)")
    print()

    frequencies = sorted(set(exp['spawning_freq'] for exp in data['experiments']))

    print("Cycle 151 Results (3K cycles):")
    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments']
                     if exp['spawning_freq'] == freq and exp.get('basin')]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_exps) * 100) if freq_exps else 0

        # Compare to known patterns
        if basin_a_pct < 15:
            comparison = "← Similar to 82% anti-harmonic"
        elif 25 <= basin_a_pct <= 40:
            comparison = "← Similar to 50%/95% baseline"
        elif basin_a_pct > 50:
            comparison = "← Elevated (potential harmonic)"
        else:
            comparison = ""

        print(f"  {freq}%: {basin_a_pct:5.1f}% Basin A  {comparison}")


def identify_anti_harmonic_family(anti_harmonic_candidates):
    """
    Determine if multiple anti-harmonics exist (family) or if 82% is unique
    """

    print("\n" + "="*80)
    print("ANTI-HARMONIC FAMILY IDENTIFICATION")
    print("="*80)

    if not anti_harmonic_candidates:
        print("\n✗ NO ANTI-HARMONICS DETECTED")
        print("  82% appears to be unique anti-harmonic frequency")
        print("  Tested frequencies (60-88%) show baseline or harmonic patterns")
        return

    print(f"\n✓ ANTI-HARMONIC FAMILY DETECTED: {len(anti_harmonic_candidates)} frequencies")
    print()

    for freq, basin_pct, strength in anti_harmonic_candidates:
        print(f"  {freq}%: {basin_pct:.1f}% Basin A ({strength} suppression)")

    # Analyze spatial distribution
    if len(anti_harmonic_candidates) >= 2:
        freqs = [f[0] for f in anti_harmonic_candidates]
        spacing = np.diff(sorted(freqs))
        avg_spacing = np.mean(spacing)

        print(f"\nSpatial Analysis:")
        print(f"  Range: {min(freqs)}% - {max(freqs)}%")
        print(f"  Average spacing: {avg_spacing:.1f}%")

        if avg_spacing < 10:
            print("  → CLUSTERED anti-harmonics (close together)")
        else:
            print("  → DISTRIBUTED anti-harmonics (spread across spectrum)")


def generate_spectrum_plot(data):
    """Visualize anti-harmonic frequency spectrum"""

    output_dir = Path(__file__).parent / 'results' / 'cycle151_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    frequencies = sorted(set(exp['spawning_freq'] for exp in data['experiments']))
    basin_a_pcts = []

    for freq in frequencies:
        freq_exps = [exp for exp in data['experiments']
                     if exp['spawning_freq'] == freq and exp.get('basin')]
        basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_exps) * 100) if freq_exps else 0
        basin_a_pcts.append(basin_a_pct)

    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot spectrum
    ax.plot(frequencies, basin_a_pcts, 'o-', linewidth=2, markersize=10,
            color='steelblue', label='Measured Basin A %')

    # Add baseline reference
    ax.axhline(y=33, color='green', linestyle='--', alpha=0.7, linewidth=2,
               label='Baseline (50% reference)')

    # Add known points
    ax.plot([82], [0], 'r*', markersize=20, label='Known 82% Anti-Harmonic')
    ax.plot([50], [33], 'g*', markersize=20, label='Known 50% Harmonic')
    ax.plot([95], [33], 'b*', markersize=15, label='Known 95% (dormant at 3K)')

    # Annotate significant deviations
    for freq, pct in zip(frequencies, basin_a_pcts):
        deviation = pct - 33
        if abs(deviation) > 15:
            color = 'red' if deviation < 0 else 'blue'
            ax.annotate(f'{pct:.0f}%',
                       xy=(freq, pct),
                       xytext=(0, 15 if deviation < 0 else -15),
                       textcoords='offset points',
                       fontsize=9,
                       color=color,
                       ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    ax.set_xlabel('Spawning Frequency (%)', fontsize=13)
    ax.set_ylabel('Basin A Convergence (%)', fontsize=13)
    ax.set_title('Cycle 151: Anti-Harmonic Frequency Spectrum\n(60-88% Scan at 3K Cycles)',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best')
    ax.set_ylim(-5, 75)

    plt.tight_layout()
    plot_file = output_dir / 'anti_harmonic_spectrum.png'
    plt.savefig(plot_file, dpi=150)
    print(f"\nPlot saved: {plot_file}")


def main():
    print("="*80)
    print("CYCLE 151 ANALYSIS: ANTI-HARMONIC FREQUENCY SCAN")
    print("="*80)

    # Load data
    data = load_cycle151_results()
    if not data:
        return

    # Analyze anti-resonance spectrum
    anti_harmonic_candidates = analyze_anti_resonance_spectrum(data)

    # Test transcendental hypothesis
    test_transcendental_hypothesis(data)

    # Compare to known patterns
    compare_to_known_patterns(data)

    # Identify anti-harmonic family
    identify_anti_harmonic_family(anti_harmonic_candidates)

    # Generate visualization
    try:
        generate_spectrum_plot(data)
    except Exception as e:
        print(f"\nNote: Could not generate plot: {e}")

    print("\n" + "="*80)
    print("CYCLE 151 ANALYSIS COMPLETE")
    print("="*80)

    # Summary
    if anti_harmonic_candidates:
        print(f"\n✓ DISCOVERED: {len(anti_harmonic_candidates)} anti-harmonic frequency(ies)")
        print("\nNext Steps:")
        print("  1. Document as Insight #112 (if publishable)")
        print("  2. Design Cycle 152: Extended temporal scale validation")
        print("  3. Test anti-harmonic→baseline transition like 82%")
    else:
        print("\n✗ 82% appears to be UNIQUE anti-harmonic")
        print("\nNext Steps:")
        print("  1. Focus on mechanistic understanding of 82% specifically")
        print("  2. Design phase coherence measurement experiments")
        print("  3. Investigate why 82% is special")


if __name__ == '__main__':
    main()
