#!/usr/bin/env python3
"""
CYCLE 177: BOUNDARY MAPPING ANALYSIS
Analyze extended frequency range results to identify homeostatic regime boundaries

Purpose:
  - Determine lower boundary (where homeostasis breaks → collapse)
  - Determine upper boundary (where homeostasis breaks → saturation/novel)
  - Quantify homeostatic range robustness
  - Test theoretical predictions

Expected Input:
  - cycle177_extended_frequency_range_results.json
  - 9 frequencies × 10 seeds = 90 experiments

Analysis Goals:
  1. Boundary Detection:
     - Last frequency with 100% Basin A (homeostasis maintained)
     - First frequency with <100% Basin A (homeostasis breaking)
  2. Population Statistics:
     - Mean population vs. frequency
     - CV (coefficient of variation) vs. frequency
  3. Regime Classification:
     - Basin A % at each frequency
     - Population stability indicators
  4. Theoretical Validation:
     - Compare with C171 control frequencies (2.0%, 3.0%)
     - Test population collapse hypothesis (low f)
     - Test saturation hypothesis (high f)

Researcher: Claude (DUALITY-ZERO-V2)
Date: 2025-11-04 (Cycle 990 - Prepared during C177 execution)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Analysis parameters
RESULTS_FILE = Path(__file__).parent / "results" / "cycle177_extended_frequency_range_results.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_results():
    """Load C177 experimental results."""
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)
    return data

def analyze_boundaries(data):
    """
    Detect homeostatic regime boundaries.

    Returns:
        dict with boundary analysis results
    """
    frequencies = sorted(set(exp['frequency'] for exp in data['experiments']))

    # Calculate Basin A percentage at each frequency
    basin_stats = {}
    for freq in frequencies:
        freq_exps = [e for e in data['experiments'] if e['frequency'] == freq]
        basin_a_count = sum(1 for e in freq_exps if e['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_exps)) * 100 if freq_exps else 0

        # Population statistics
        pops = [e['mean_population'] for e in freq_exps]
        cvs = [e['cv_population'] for e in freq_exps]

        basin_stats[freq] = {
            'basin_a_percent': basin_a_pct,
            'n_experiments': len(freq_exps),
            'mean_population': np.mean(pops),
            'std_population': np.std(pops),
            'mean_cv': np.mean(cvs),
            'all_basin_a': basin_a_count == len(freq_exps)
        }

    # Find boundaries
    lower_boundary = None
    upper_boundary = None
    homeostatic_range = []

    for freq in frequencies:
        if basin_stats[freq]['all_basin_a']:
            homeostatic_range.append(freq)
        else:
            if not homeostatic_range:
                # Below homeostatic range
                lower_boundary = freq
            elif freq > max(homeostatic_range):
                # Above homeostatic range
                if upper_boundary is None:
                    upper_boundary = freq

    # Calculate homeostatic span
    if homeostatic_range:
        f_min = min(homeostatic_range)
        f_max = max(homeostatic_range)
        span = f_max - f_min
        span_pct = (span / f_min) * 100 if f_min > 0 else 0
    else:
        f_min = f_max = span = span_pct = None

    return {
        'frequencies': frequencies,
        'basin_stats': basin_stats,
        'lower_boundary': lower_boundary,
        'upper_boundary': upper_boundary,
        'homeostatic_range': homeostatic_range,
        'f_min': f_min,
        'f_max': f_max,
        'span': span,
        'span_percent': span_pct
    }

def validate_controls(data, boundary_results):
    """
    Validate C171 control frequencies (2.0%, 3.0%) replicated homeostasis.

    Returns:
        dict with validation results
    """
    control_freqs = [2.0, 3.0]
    validation = {}

    for freq in control_freqs:
        freq_exps = [e for e in data['experiments'] if e['frequency'] == freq]
        if not freq_exps:
            validation[freq] = {'status': 'MISSING', 'message': f'No data at {freq}%'}
            continue

        basin_a_count = sum(1 for e in freq_exps if e['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_exps)) * 100

        # C171 expectation: 100% Basin A, ~17 agents, CV < 15%
        pops = [e['mean_population'] for e in freq_exps]
        mean_pop = np.mean(pops)
        cvs = [e['cv_population'] for e in freq_exps]
        mean_cv = np.mean(cvs)

        if basin_a_pct == 100 and 15 < mean_pop < 22 and mean_cv < 20:
            status = 'PASS'
            message = f'Homeostasis replicated: {mean_pop:.1f} agents, CV={mean_cv:.1f}%'
        else:
            status = 'FAIL'
            message = f'Mismatch: {basin_a_pct}% Basin A, {mean_pop:.1f} agents, CV={mean_cv:.1f}%'

        validation[freq] = {
            'status': status,
            'message': message,
            'basin_a_percent': basin_a_pct,
            'mean_population': mean_pop,
            'mean_cv': mean_cv,
            'n_experiments': len(freq_exps)
        }

    return validation

def generate_figures(boundary_results):
    """
    Generate publication-quality figures.

    Figures:
      1. Extended Bifurcation (Basin A % vs. Frequency)
      2. Population vs. Frequency
      3. CV vs. Frequency
      4. Phase Diagram (Frequency × Population, colored by Basin)
    """
    basin_stats = boundary_results['basin_stats']
    frequencies = boundary_results['frequencies']

    # Extract data
    basin_a_pcts = [basin_stats[f]['basin_a_percent'] for f in frequencies]
    mean_pops = [basin_stats[f]['mean_population'] for f in frequencies]
    std_pops = [basin_stats[f]['std_population'] for f in frequencies]
    mean_cvs = [basin_stats[f]['mean_cv'] for f in frequencies]

    # Figure 1: Extended Bifurcation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(frequencies, basin_a_pcts, 'o-', linewidth=2, markersize=8, color='steelblue')
    ax.axhline(100, linestyle='--', color='gray', alpha=0.5, label='100% Basin A')
    if boundary_results['homeostatic_range']:
        ax.axvspan(min(boundary_results['homeostatic_range']),
                   max(boundary_results['homeostatic_range']),
                   alpha=0.2, color='green', label='Homeostatic Range')
    ax.set_xlabel('Spawn Frequency (%)', fontsize=12)
    ax.set_ylabel('Basin A Percentage', fontsize=12)
    ax.set_title('Extended Bifurcation: Homeostatic Regime Boundaries (C177)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_extended_bifurcation.png', dpi=300)
    plt.close()

    # Figure 2: Population vs. Frequency
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(frequencies, mean_pops, yerr=std_pops, fmt='o-', linewidth=2,
                markersize=8, capsize=5, color='darkgreen', label='Mean ± SD')
    ax.axhline(17.4, linestyle='--', color='gray', alpha=0.5, label='C171 Reference (17.4)')
    ax.set_xlabel('Spawn Frequency (%)', fontsize=12)
    ax.set_ylabel('Mean Population', fontsize=12)
    ax.set_title('Population vs. Frequency (C177)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_population_vs_frequency.png', dpi=300)
    plt.close()

    # Figure 3: CV vs. Frequency
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(frequencies, mean_cvs, 'o-', linewidth=2, markersize=8, color='coral')
    ax.axhline(15, linestyle='--', color='gray', alpha=0.5, label='CV Threshold (15%)')
    ax.set_xlabel('Spawn Frequency (%)', fontsize=12)
    ax.set_ylabel('Coefficient of Variation (%)', fontsize=12)
    ax.set_title('Population Stability vs. Frequency (C177)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_cv_vs_frequency.png', dpi=300)
    plt.close()

    print(f"✓ Generated 3 figures @ 300 DPI in {OUTPUT_DIR}")
    print(f"  - c177_extended_bifurcation.png")
    print(f"  - c177_population_vs_frequency.png")
    print(f"  - c177_cv_vs_frequency.png")

def main():
    """Execute C177 boundary mapping analysis."""
    print("=" * 80)
    print("CYCLE 177: BOUNDARY MAPPING ANALYSIS")
    print("=" * 80)
    print()

    # Load results
    print("Loading results...")
    data = load_results()
    print(f"✓ Loaded {len(data['experiments'])} experiments")
    print()

    # Analyze boundaries
    print("Analyzing homeostatic regime boundaries...")
    boundary_results = analyze_boundaries(data)
    print()

    # Print boundary findings
    print("BOUNDARY FINDINGS:")
    print("-" * 80)
    if boundary_results['homeostatic_range']:
        print(f"Homeostatic Range: {boundary_results['f_min']:.2f}% - {boundary_results['f_max']:.2f}%")
        print(f"Span: {boundary_results['span']:.2f}% ({boundary_results['span_percent']:.1f}% variation)")
    else:
        print("No complete homeostatic range found (no frequencies with 100% Basin A)")

    if boundary_results['lower_boundary']:
        print(f"Lower Boundary: Below {boundary_results['lower_boundary']:.2f}%")
    else:
        print("Lower Boundary: Not detected (homeostasis persists to lowest tested frequency)")

    if boundary_results['upper_boundary']:
        print(f"Upper Boundary: Above {boundary_results['upper_boundary']:.2f}%")
    else:
        print("Upper Boundary: Not detected (homeostasis persists to highest tested frequency)")
    print()

    # Basin A statistics by frequency
    print("BASIN A STATISTICS BY FREQUENCY:")
    print("-" * 80)
    for freq in boundary_results['frequencies']:
        stats = boundary_results['basin_stats'][freq]
        print(f"{freq:5.1f}%: {stats['basin_a_percent']:5.0f}% Basin A | "
              f"Pop: {stats['mean_population']:5.1f} ± {stats['std_population']:4.1f} | "
              f"CV: {stats['mean_cv']:5.1f}%")
    print()

    # Validate controls
    print("CONTROL VALIDATION (C171 Replication):")
    print("-" * 80)
    validation = validate_controls(data, boundary_results)
    for freq, result in sorted(validation.items()):
        print(f"{freq}%: {result['status']} - {result['message']}")
    print()

    # Generate figures
    print("Generating figures...")
    generate_figures(boundary_results)
    print()

    # Summary statistics
    print("SUMMARY:")
    print("-" * 80)
    print(f"Total Experiments: {len(data['experiments'])}")
    print(f"Frequencies Tested: {len(boundary_results['frequencies'])}")
    print(f"Overall Basin A Rate: {sum(1 for e in data['experiments'] if e['basin'] == 'A') / len(data['experiments']) * 100:.1f}%")

    # Determine experiment outcome
    all_controls_pass = all(v['status'] == 'PASS' for v in validation.values())
    if all_controls_pass:
        print()
        print("✓ CONTROLS VALIDATED - Results reliable")
    else:
        print()
        print("✗ CONTROL FAILURE - Results may be unreliable, investigate discrepancies")

    print()
    print("=" * 80)
    print("Analysis complete. Figures saved to:", OUTPUT_DIR)
    print("=" * 80)

if __name__ == '__main__':
    main()
