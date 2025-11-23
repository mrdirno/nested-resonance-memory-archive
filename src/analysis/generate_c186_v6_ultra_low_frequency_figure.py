#!/usr/bin/env python3
"""
C186 V6 Ultra-Low Frequency Figure Generator
Generates publication-quality figure for V6 hierarchical critical frequency analysis

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1093)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats


# Color scheme (consistent with C186 figures)
COLOR_BASIN_A = '#27AE60'      # Green for viable (Basin A)
COLOR_BASIN_B = '#E74C3C'       # Red for collapsed (Basin B)
COLOR_TEXT = '#2C3E50'           # Dark gray text
COLOR_BG = '#F8F9F9'             # Light gray background
COLOR_GRID = '#BDC3C7'           # Light gray grid


def load_v6_results(results_path: Path) -> dict:
    """Load V6 ultra-low frequency results"""
    if not results_path.exists():
        raise FileNotFoundError(f"V6 results not found: {results_path}")

    with open(results_path) as f:
        return json.load(f)


def extract_frequency_data(results: dict) -> tuple:
    """
    Extract frequency vs population data

    Returns:
        frequencies: array of spawn frequencies (as percentages)
        mean_populations: array of mean final populations
        std_populations: array of standard deviations
        all_populations: list of lists (seeds for each frequency)
        basin_classifications: list of Basin A/B for each frequency
        basin_a_rates: fraction of seeds reaching Basin A for each frequency
    """
    experiments = results['experiments']

    frequencies = []
    mean_populations = []
    std_populations = []
    all_populations = []
    basin_classifications = []
    basin_a_rates = []

    HOMEOSTASIS_THRESHOLD = 2.5

    for exp in experiments:
        freq = exp['parameters']['spawn_frequency']
        seeds_data = exp['seeds']

        # Extract final populations across all seeds
        final_pops = [seed['final_population'] for seed in seeds_data]

        mean_pop = np.mean(final_pops)
        basin = 'A' if mean_pop > HOMEOSTASIS_THRESHOLD else 'B'

        # Calculate fraction of seeds reaching Basin A
        basin_a_count = sum(1 for pop in final_pops if pop > HOMEOSTASIS_THRESHOLD)
        basin_a_fraction = basin_a_count / len(final_pops)

        frequencies.append(freq * 100)  # Convert to percentage
        mean_populations.append(mean_pop)
        std_populations.append(np.std(final_pops, ddof=1))
        all_populations.append(final_pops)
        basin_classifications.append(basin)
        basin_a_rates.append(basin_a_fraction)

    return (
        np.array(frequencies),
        np.array(mean_populations),
        np.array(std_populations),
        all_populations,
        basin_classifications,
        np.array(basin_a_rates)
    )


def identify_critical_frequency(
    frequencies: np.ndarray,
    mean_pops: np.ndarray,
    basin_a_rates: np.ndarray,
    threshold: float = 2.5
) -> dict:
    """
    Identify hierarchical critical frequency

    Returns:
        dict with:
        - f_hier_crit: hierarchical critical frequency (highest Basin B)
        - basin_transition: (freq_low, freq_high) bracketing transition
        - is_viable_all: whether all frequencies show viability
        - lowest_viable_freq: lowest frequency maintaining Basin A
    """
    # Sort by frequency
    sorted_idx = np.argsort(frequencies)
    freqs_sorted = frequencies[sorted_idx]
    pops_sorted = mean_pops[sorted_idx]
    basin_a_sorted = basin_a_rates[sorted_idx]

    # Find lowest frequency with Basin A
    viable_mask = basin_a_sorted > 0.5  # >50% of seeds reach Basin A

    if np.all(viable_mask):
        # All frequencies viable - critical frequency is below tested range
        return {
            'f_hier_crit': f'< {freqs_sorted[0]:.2f}%',
            'basin_transition': (0, freqs_sorted[0]),
            'is_viable_all': True,
            'lowest_viable_freq': freqs_sorted[0]
        }
    elif not np.any(viable_mask):
        # All frequencies non-viable - critical frequency is above tested range
        return {
            'f_hier_crit': f'> {freqs_sorted[-1]:.2f}%',
            'basin_transition': (freqs_sorted[-1], float('inf')),
            'is_viable_all': False,
            'lowest_viable_freq': None
        }
    else:
        # Transition within tested range
        transition_idx = np.where(np.diff(viable_mask.astype(int)))[0]
        if len(transition_idx) > 0:
            idx = transition_idx[0]
            return {
                'f_hier_crit': f'{freqs_sorted[idx]:.2f}-{freqs_sorted[idx+1]:.2f}%',
                'basin_transition': (freqs_sorted[idx], freqs_sorted[idx+1]),
                'is_viable_all': False,
                'lowest_viable_freq': freqs_sorted[idx+1]
            }
        else:
            # Find lowest viable
            viable_freqs = freqs_sorted[viable_mask]
            return {
                'f_hier_crit': f'< {viable_freqs[0]:.2f}%',
                'basin_transition': (0, viable_freqs[0]),
                'is_viable_all': False,
                'lowest_viable_freq': viable_freqs[0]
            }


def generate_figure(
    frequencies: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    all_pops: list,
    basin_classifications: list,
    basin_a_rates: np.ndarray,
    output_path: Path
):
    """Generate publication-quality V6 figure"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor('white')

    # Sort by frequency for plotting
    sorted_idx = np.argsort(frequencies)
    freqs_sorted = frequencies[sorted_idx]
    pops_sorted = mean_pops[sorted_idx]
    stds_sorted = std_pops[sorted_idx]
    basin_a_sorted = basin_a_rates[sorted_idx]

    # ========================================================================
    # Panel A: Frequency vs Population
    # ========================================================================

    # Plot individual seeds as scatter
    for i, idx in enumerate(sorted_idx):
        freq = frequencies[idx]
        pops = all_pops[idx]
        basin = basin_classifications[idx]
        color = COLOR_BASIN_A if basin == 'A' else COLOR_BASIN_B

        # Jitter x-values slightly for visibility
        x_jitter = freq + np.random.normal(0, 0.01, len(pops))
        ax1.scatter(x_jitter, pops, alpha=0.4, s=50, color=color,
                   edgecolors='none', zorder=2)

    # Plot means with error bars
    colors = [COLOR_BASIN_A if b == 'A' else COLOR_BASIN_B
             for b in [basin_classifications[i] for i in sorted_idx]]
    ax1.errorbar(freqs_sorted, pops_sorted, yerr=stds_sorted,
                fmt='o', markersize=12, linewidth=2, capsize=5,
                color='black', markerfacecolor=colors,
                markeredgewidth=2, zorder=3, label='Mean ± SD')

    # Add threshold line
    ax1.axhline(y=2.5, color=COLOR_TEXT, linestyle='--', linewidth=2,
               alpha=0.5, label='Basin A threshold', zorder=1)

    # Formatting
    ax1.set_xlabel('Spawn Frequency (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Mean Final Population', fontsize=14, fontweight='bold')
    ax1.set_title('A. Ultra-Low Frequency Viability Test',
                 fontsize=16, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, color=COLOR_GRID)
    ax1.legend(fontsize=11, framealpha=0.9)
    ax1.set_xlim(0, max(frequencies) * 1.1)
    ax1.set_ylim(0, max(mean_pops) * 1.2)

    # Add spawn interval annotations
    for freq in freqs_sorted:
        interval = int(100 / freq) if freq > 0 else 0
        y_pos = ax1.get_ylim()[1] * 0.95
        ax1.text(freq, y_pos, f'{interval} cycles',
                ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3',
                         facecolor='white', alpha=0.7))

    # ========================================================================
    # Panel B: Basin A Viability Rate
    # ========================================================================

    # Bar plot of Basin A rates
    bar_colors = [COLOR_BASIN_A if rate >= 0.5 else COLOR_BASIN_B
                 for rate in basin_a_sorted]
    bars = ax2.bar(freqs_sorted, basin_a_sorted * 100,
                   width=0.15, color=bar_colors,
                   edgecolor='black', linewidth=2, alpha=0.8)

    # Add 50% threshold line
    ax2.axhline(y=50, color=COLOR_TEXT, linestyle='--', linewidth=2,
               alpha=0.5, label='50% viability threshold')

    # Add percentage labels on bars
    for i, (freq, rate) in enumerate(zip(freqs_sorted, basin_a_sorted)):
        ax2.text(freq, rate * 100 + 5, f'{int(rate * 100)}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Formatting
    ax2.set_xlabel('Spawn Frequency (%)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Basin A Viability Rate (%)', fontsize=14, fontweight='bold')
    ax2.set_title('B. Hierarchical Critical Frequency Analysis',
                 fontsize=16, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, axis='y', color=COLOR_GRID)
    ax2.legend(fontsize=11, framealpha=0.9)
    ax2.set_xlim(0, max(frequencies) * 1.1)
    ax2.set_ylim(0, 110)

    plt.tight_layout()

    # Save figure
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"\nFigure 6 saved: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()


def print_statistical_summary(
    frequencies: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    basin_classifications: list,
    basin_a_rates: np.ndarray
):
    """Print comprehensive statistical summary"""

    print("\n" + "="*80)
    print("C186 V6 ULTRA-LOW FREQUENCY TEST - STATISTICAL SUMMARY")
    print("="*80)

    print("\nFrequency Analysis:")
    print("-" * 80)
    print(f"{'Frequency':<12} {'Mean Pop':<12} {'SD':<10} {'Basin':<8} "
          f"{'Viability':<12} {'Spawn Interval':<15}")
    print("-" * 80)

    sorted_idx = np.argsort(frequencies)
    for idx in sorted_idx:
        freq = frequencies[idx]
        interval = int(100 / freq) if freq > 0 else 0
        print(f"{freq:>10.2f}%  {mean_pops[idx]:>10.2f}  {std_pops[idx]:>8.2f}  "
              f"{basin_classifications[idx]:<6}  {basin_a_rates[idx]*100:>9.0f}%  "
              f"{interval:>12} cycles")

    # Critical frequency analysis
    crit_info = identify_critical_frequency(frequencies, mean_pops, basin_a_rates)

    print("\n" + "="*80)
    print("HIERARCHICAL CRITICAL FREQUENCY DETERMINATION")
    print("="*80)
    print(f"Hierarchical critical frequency (f_hier_crit): {crit_info['f_hier_crit']}")
    print(f"All frequencies viable: {crit_info['is_viable_all']}")
    if crit_info['lowest_viable_freq'] is not None:
        print(f"Lowest viable frequency: {crit_info['lowest_viable_freq']:.2f}%")
        print(f"Spawn interval at lowest viable: {int(100/crit_info['lowest_viable_freq'])} cycles")

    # Linear regression (if applicable)
    if len(frequencies) >= 3:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            frequencies, mean_pops
        )
        print("\nLinear Model (Population vs Frequency):")
        print(f"Population = {slope:.2f} × Frequency + {intercept:.2f}")
        print(f"R² = {r_value**2:.6f}")
        print(f"p-value = {p_value:.4e}")

        # Predicted critical frequency (where pop = 2.5)
        if slope != 0:
            f_predicted = (2.5 - intercept) / slope
            print(f"\nPredicted f_crit (linear model): {f_predicted:.3f}%")
            if f_predicted < 0:
                print("WARNING: Negative predicted frequency suggests linear model breaks down")
                print("         System may be viable at all f > 0 (no critical frequency)")

    print("\n" + "="*80)


def main():
    """Main execution"""

    # Paths
    results_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v6_ultra_low_frequency_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/c186_v6_ultra_low_frequency.png")

    print("C186 V6 Ultra-Low Frequency Figure Generator")
    print("=" * 80)

    # Load results
    print(f"\nLoading results from: {results_path}")
    results = load_v6_results(results_path)

    # Extract data
    print("Extracting frequency data...")
    (frequencies, mean_pops, std_pops,
     all_pops, basin_classifications, basin_a_rates) = extract_frequency_data(results)

    # Print statistical summary
    print_statistical_summary(frequencies, mean_pops, std_pops,
                            basin_classifications, basin_a_rates)

    # Generate figure
    print("\nGenerating Figure 6 (300 DPI)...")
    generate_figure(frequencies, mean_pops, std_pops, all_pops,
                   basin_classifications, basin_a_rates, output_path)

    print("\n" + "="*80)
    print("V6 FIGURE GENERATION COMPLETE")
    print("="*80)
    print(f"Output: {output_path}")
    print(f"Ready for manuscript integration (Figure 6)")
    print("="*80)


if __name__ == '__main__':
    main()
