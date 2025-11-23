#!/usr/bin/env python3
"""
C186 V7 Migration Rate Sensitivity Figure Generator
Generates publication-quality figure and statistical analysis for V7 results

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1080)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats


# Color scheme (consistent with graphical abstract)
COLOR_HIERARCHICAL = '#27AE60'  # Green for hierarchical
COLOR_FAILURE = '#E74C3C'       # Red for failure/no migration
COLOR_TEXT = '#2C3E50'           # Dark gray text
COLOR_BG = '#F8F9F9'             # Light gray background


def load_v7_results(results_path: Path) -> dict:
    """Load V7 migration rate variation results"""
    if not results_path.exists():
        raise FileNotFoundError(f"V7 results not found: {results_path}")

    with open(results_path) as f:
        return json.load(f)


def extract_migration_sensitivity(results: dict) -> tuple:
    """
    Extract migration rate vs final population data

    Returns:
        migration_rates: array of f_migrate values (as percentages)
        mean_populations: array of mean final populations
        std_populations: array of standard deviations
        all_populations: list of lists (seeds for each rate)
        basin_classifications: list of Basin A/B for each rate
    """
    experiments = results['experiments']

    migration_rates = []
    mean_populations = []
    std_populations = []
    all_populations = []
    basin_classifications = []

    HOMEOSTASIS_THRESHOLD = 2.5

    for exp in experiments:
        f_migrate = exp['parameters']['migration_frequency']
        seeds_data = exp['seeds']

        # Extract final populations across all seeds
        final_pops = [seed['final_population'] for seed in seeds_data]

        mean_pop = np.mean(final_pops)
        basin = 'A' if mean_pop > HOMEOSTASIS_THRESHOLD else 'B'

        migration_rates.append(f_migrate * 100)  # Convert to percentage
        mean_populations.append(mean_pop)
        std_populations.append(np.std(final_pops, ddof=1))
        all_populations.append(final_pops)
        basin_classifications.append(basin)

    return (
        np.array(migration_rates),
        np.array(mean_populations),
        np.array(std_populations),
        all_populations,
        basin_classifications
    )


def identify_migration_thresholds(
    migration_rates: np.ndarray,
    mean_pops: np.ndarray,
    basin_classifications: list
) -> dict:
    """
    Identify key migration rate thresholds

    Returns:
        dict with:
        - is_necessary: bool, whether migration is necessary (f=0% fails)
        - optimal_rate: migration rate with highest mean population
        - optimal_population: mean population at optimal rate
        - robustness_window: (lower, upper) rates maintaining Basin A
        - failure_modes: dict describing low/high rate failure mechanisms
    """
    # Test necessity (f_migrate = 0%)
    zero_idx = np.where(migration_rates == 0)[0]
    is_necessary = basin_classifications[zero_idx[0]] == 'B' if len(zero_idx) > 0 else None

    # Optimal rate (highest mean population)
    optimal_idx = np.argmax(mean_pops)
    optimal_rate = migration_rates[optimal_idx]
    optimal_pop = mean_pops[optimal_idx]

    # Robustness window (all Basin A rates)
    basin_a_indices = [i for i, basin in enumerate(basin_classifications) if basin == 'A']
    if basin_a_indices:
        robust_lower = migration_rates[basin_a_indices].min()
        robust_upper = migration_rates[basin_a_indices].max()
        robustness_window = (robust_lower, robust_upper)
    else:
        robustness_window = None

    # Failure modes
    failure_modes = {}

    # Low rate failure (below robustness window)
    if robustness_window:
        low_rate_indices = np.where(migration_rates < robust_lower)[0]
        if len(low_rate_indices) > 0:
            low_rate_pops = mean_pops[low_rate_indices]
            failure_modes['low_rate'] = {
                'threshold': robust_lower,
                'mean_population': np.mean(low_rate_pops),
                'interpretation': 'insufficient rescue capability'
            }

        # High rate failure (above robustness window)
        high_rate_indices = np.where(migration_rates > robust_upper)[0]
        if len(high_rate_indices) > 0:
            high_rate_pops = mean_pops[high_rate_indices]
            failure_modes['high_rate'] = {
                'threshold': robust_upper,
                'mean_population': np.mean(high_rate_pops),
                'interpretation': 'excessive migration disrupts local dynamics'
            }

    return {
        'is_necessary': is_necessary,
        'optimal_rate': optimal_rate,
        'optimal_population': optimal_pop,
        'robustness_window': robustness_window,
        'failure_modes': failure_modes
    }


def generate_v7_figure(
    migration_rates: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    basin_classifications: list,
    thresholds: dict,
    output_path: Path
):
    """
    Generate publication-quality V7 migration sensitivity figure

    Figure structure:
    - Line plot with error bars (data points)
    - Basin A/B color coding
    - No migration (f=0%) highlighted if necessary
    - Optimal rate highlighted
    - Robustness window shaded
    - Basin threshold line (y=2.5)
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300, facecolor=COLOR_BG)

    # Line plot with error bars (all data)
    ax.plot(migration_rates, mean_pops, '-', color=COLOR_HIERARCHICAL,
           linewidth=3, alpha=0.7, label='Mean Population')

    # Data points color-coded by basin
    for i, (rate, pop, std, basin) in enumerate(zip(migration_rates, mean_pops, std_pops, basin_classifications)):
        color = COLOR_HIERARCHICAL if basin == 'A' else COLOR_FAILURE
        marker = 'o' if basin == 'A' else 'x'

        ax.errorbar([rate], [pop], yerr=[std],
                   fmt=marker, markersize=10, capsize=5, capthick=2,
                   color=color, markeredgecolor='black',
                   markeredgewidth=1.5, linewidth=2, alpha=0.8)

    # Highlight no migration (f=0%) if tested
    zero_idx = np.where(migration_rates == 0)[0]
    if len(zero_idx) > 0:
        zero_basin = basin_classifications[zero_idx[0]]
        zero_color = COLOR_FAILURE if zero_basin == 'B' else COLOR_HIERARCHICAL
        label_text = 'No Migration (FAILS)' if zero_basin == 'B' else 'No Migration (succeeds)'

        ax.scatter([0], [mean_pops[zero_idx[0]]],
                  s=250, c=zero_color, marker='D',
                  edgecolors='black', linewidths=2.5, zorder=5,
                  label=label_text)

    # Highlight optimal rate
    if thresholds['optimal_rate'] is not None:
        ax.scatter([thresholds['optimal_rate']], [thresholds['optimal_population']],
                  s=350, c='yellow', marker='*',
                  edgecolors='black', linewidths=2.5, zorder=5,
                  label=f'Optimal ({thresholds["optimal_rate"]:.2f}%)')

    # Robustness window shading
    if thresholds['robustness_window']:
        lower, upper = thresholds['robustness_window']
        ax.axvspan(lower, upper, alpha=0.15, color='green',
                  label=f'Robustness Window ({lower:.2f}-{upper:.2f}%)')

        # Threshold lines
        ax.axvline(x=lower, color='green', linestyle=':', linewidth=2, alpha=0.6)
        ax.axvline(x=upper, color='green', linestyle=':', linewidth=2, alpha=0.6)

    # Basin threshold line
    ax.axhline(y=2.5, color='gray', linestyle='--', linewidth=2,
              alpha=0.5, label='Basin Threshold')

    # Failure mode annotations
    if 'low_rate' in thresholds['failure_modes']:
        low_threshold = thresholds['failure_modes']['low_rate']['threshold']
        ax.axvline(x=low_threshold, color='red', linestyle=':', linewidth=2, alpha=0.5)

    if 'high_rate' in thresholds['failure_modes']:
        high_threshold = thresholds['failure_modes']['high_rate']['threshold']
        ax.axvline(x=high_threshold, color='orange', linestyle=':', linewidth=2, alpha=0.5)

    # Interpretation annotation
    necessity_text = (
        "Migration NECESSARY\nfor homeostasis"
        if thresholds['is_necessary']
        else "Migration OPTIONAL\n(enhances but not required)"
    )

    ax.text(0.97, 0.97, necessity_text,
           transform=ax.transAxes, fontsize=11, fontweight='bold',
           verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow' if thresholds['is_necessary'] else 'lightgreen',
                    edgecolor='black', linewidth=1.5, alpha=0.9))

    # Axis labels and title
    ax.set_xlabel('Migration Frequency (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Mean Final Population', fontsize=13, fontweight='bold')
    ax.set_title('C186 V7: Migration Rate Sensitivity',
                fontsize=14, fontweight='bold', pad=15)

    # Grid and legend
    ax.grid(True, alpha=0.3, linewidth=0.8)
    ax.legend(loc='best', fontsize=9, framealpha=0.95, edgecolor='black')

    # Axis limits
    ax.set_xlim(-0.1, migration_rates.max() * 1.1)
    ax.set_ylim(0, max(mean_pops.max() + std_pops.max(), 3.5) * 1.1)

    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=COLOR_BG)
    print(f"V7 figure saved: {output_path}")

    plt.close()


def save_v7_analysis(
    migration_rates: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    basin_classifications: list,
    thresholds: dict,
    output_path: Path
):
    """Save V7 statistical analysis to JSON"""
    analysis = {
        'migration_rates_percent': migration_rates.tolist(),
        'mean_populations': mean_pops.tolist(),
        'std_populations': std_pops.tolist(),
        'basin_classifications': basin_classifications,
        'thresholds': {
            'is_necessary': thresholds['is_necessary'],
            'optimal_rate': float(thresholds['optimal_rate']),
            'optimal_population': float(thresholds['optimal_population']),
            'robustness_window': [float(x) for x in thresholds['robustness_window']] if thresholds['robustness_window'] else None,
            'failure_modes': {
                k: {
                    'threshold': float(v['threshold']),
                    'mean_population': float(v['mean_population']),
                    'interpretation': v['interpretation']
                }
                for k, v in thresholds['failure_modes'].items()
            } if thresholds['failure_modes'] else {}
        }
    }

    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"V7 analysis saved: {output_path}")


def print_v7_summary(thresholds: dict, basin_classifications: list, migration_rates: np.ndarray):
    """Print human-readable summary of V7 analysis"""
    print("\n" + "="*70)
    print("C186 V7 MIGRATION RATE SENSITIVITY ANALYSIS")
    print("="*70)
    print()

    print("MIGRATION NECESSITY TEST:")
    if thresholds['is_necessary'] is not None:
        if thresholds['is_necessary']:
            print("  ❌ Migration IS NECESSARY for hierarchical homeostasis")
            print("     (f_migrate = 0% results in Basin B collapse)")
        else:
            print("  ✅ Migration IS OPTIONAL (enhances but not required)")
            print("     (f_migrate = 0% achieves Basin A homeostasis)")
    else:
        print("  ⚠️  No migration = 0% condition tested")
    print()

    print("OPTIMAL MIGRATION RATE:")
    print(f"  Rate: {thresholds['optimal_rate']:.2f}%")
    print(f"  Mean Population: {thresholds['optimal_population']:.2f}")
    print()

    print("ROBUSTNESS WINDOW:")
    if thresholds['robustness_window']:
        lower, upper = thresholds['robustness_window']
        print(f"  Range: {lower:.2f}% - {upper:.2f}%")
        print(f"  Width: {upper - lower:.2f} percentage points")

        # Count Basin A vs Basin B
        n_basin_a = sum(1 for b in basin_classifications if b == 'A')
        n_basin_b = sum(1 for b in basin_classifications if b == 'B')
        print(f"  Basin A conditions: {n_basin_a}/{len(basin_classifications)}")
        print(f"  Basin B conditions: {n_basin_b}/{len(basin_classifications)}")
    else:
        print("  ⚠️  No robustness window identified (all conditions fail)")
    print()

    print("FAILURE MODES:")
    if 'low_rate' in thresholds['failure_modes']:
        low = thresholds['failure_modes']['low_rate']
        print(f"  Low Rate (< {low['threshold']:.2f}%):")
        print(f"    Mean population: {low['mean_population']:.2f}")
        print(f"    Mechanism: {low['interpretation']}")

    if 'high_rate' in thresholds['failure_modes']:
        high = thresholds['failure_modes']['high_rate']
        print(f"  High Rate (> {high['threshold']:.2f}%):")
        print(f"    Mean population: {high['mean_population']:.2f}")
        print(f"    Mechanism: {high['interpretation']}")

    if not thresholds['failure_modes']:
        print("  ✅ No failure modes detected (all rates succeed)")
    print()

    print("INTERPRETATION:")
    if thresholds['is_necessary']:
        print("  The hierarchical rescue mechanism REQUIRES inter-population")
        print("  migration. Without migration, subpopulations fail independently")
        print("  and the system collapses to Basin B.")
        print()
        print(f"  Optimal migration rate ({thresholds['optimal_rate']:.2f}%) balances:")
        print("    • Sufficient rescue frequency (recolonization of failed subpops)")
        print("    • Minimal disruption to local population dynamics")
    else:
        print("  Hierarchical advantage exists WITHOUT migration, suggesting")
        print("  compartmentalization alone provides benefits. Migration")
        print(f"  enhances performance (optimal at {thresholds['optimal_rate']:.2f}%).")

    print("="*70)


def main():
    """Execute V7 migration rate sensitivity analysis"""
    print("="*70)
    print("C186 V7 Migration Rate Sensitivity Analysis")
    print("="*70)
    print()

    # Paths
    workspace_root = Path('/Volumes/dual/DUALITY-ZERO-V2')
    results_path = workspace_root / 'experiments' / 'results' / 'c186_v7_migration_rate_variation_results.json'
    figure_path = workspace_root / 'data' / 'figures' / 'c186_v7_migration_sensitivity.png'
    analysis_path = workspace_root / 'experiments' / 'results' / 'c186_v7_migration_sensitivity_analysis.json'

    # Load V7 results
    print("Loading V7 results...")
    try:
        results = load_v7_results(results_path)
        print(f"  ✅ Loaded {len(results['experiments'])} experiments")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        print("  V7 experiment has not completed yet")
        return

    # Extract migration sensitivity data
    print("\nExtracting migration sensitivity data...")
    migration_rates, mean_pops, std_pops, all_pops, basins = extract_migration_sensitivity(results)
    print(f"  ✅ Extracted {len(migration_rates)} migration rate conditions")

    # Identify thresholds
    print("\nIdentifying migration thresholds...")
    thresholds = identify_migration_thresholds(migration_rates, mean_pops, basins)
    if thresholds['is_necessary'] is not None:
        print(f"  {'❌' if thresholds['is_necessary'] else '✅'} Migration {'NECESSARY' if thresholds['is_necessary'] else 'OPTIONAL'}")
    print(f"  ✅ Optimal rate: {thresholds['optimal_rate']:.2f}%")
    if thresholds['robustness_window']:
        lower, upper = thresholds['robustness_window']
        print(f"  ✅ Robustness window: {lower:.2f}% - {upper:.2f}%")

    # Generate figure
    print("\nGenerating publication figure...")
    generate_v7_figure(migration_rates, mean_pops, std_pops, basins,
                      thresholds, figure_path)
    print(f"  ✅ Figure saved @ 300 DPI")

    # Save analysis
    print("\nSaving statistical analysis...")
    save_v7_analysis(migration_rates, mean_pops, std_pops, basins,
                    thresholds, analysis_path)
    print(f"  ✅ Analysis saved")

    # Print summary
    print_v7_summary(thresholds, basins, migration_rates)

    print("\n" + "="*70)
    print("V7 Analysis Complete")
    print("="*70)
    print(f"Figure: {figure_path}")
    print(f"Analysis: {analysis_path}")
    print("\nNext Steps:")
    print("  - Integrate findings into manuscript Results section 3.7")
    print("  - Update Discussion section 4.2 with migration mechanism details")
    print("  - Regenerate comprehensive visualization (Panel D)")
    print("="*70)


if __name__ == '__main__':
    main()
