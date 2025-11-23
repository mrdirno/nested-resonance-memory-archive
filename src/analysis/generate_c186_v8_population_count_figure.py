#!/usr/bin/env python3
"""
C186 V8 Population Count Scaling Figure Generator
Generates publication-quality figure and statistical analysis for V8 results

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1080)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from scipy.optimize import curve_fit


# Color scheme (consistent with graphical abstract)
COLOR_HIERARCHICAL = '#27AE60'  # Green for hierarchical
COLOR_BASELINE = '#2E86C1'      # Blue for baseline (N=1)
COLOR_TEXT = '#2C3E50'           # Dark gray text
COLOR_BG = '#F8F9F9'             # Light gray background


def load_v8_results(results_path: Path) -> dict:
    """Load V8 population count variation results"""
    if not results_path.exists():
        raise FileNotFoundError(f"V8 results not found: {results_path}")

    with open(results_path) as f:
        return json.load(f)


def extract_population_scaling(results: dict) -> tuple:
    """
    Extract population count vs final population data

    Returns:
        population_counts: array of N values (subpopulation counts)
        mean_populations: array of mean final populations
        std_populations: array of standard deviations
        all_populations: list of lists (seeds for each N)
    """
    experiments = results['experiments']

    population_counts = []
    mean_populations = []
    std_populations = []
    all_populations = []

    for exp in experiments:
        n_subpops = exp['parameters']['n_subpopulations']
        seeds_data = exp['seeds']

        # Extract final populations across all seeds
        final_pops = [seed['final_population'] for seed in seeds_data]

        population_counts.append(n_subpops)
        mean_populations.append(np.mean(final_pops))
        std_populations.append(np.std(final_pops, ddof=1))
        all_populations.append(final_pops)

    return (
        np.array(population_counts),
        np.array(mean_populations),
        np.array(std_populations),
        all_populations
    )


def fit_scaling_models(n_values: np.ndarray, mean_pops: np.ndarray) -> dict:
    """
    Fit multiple scaling models to data

    Models tested:
    1. Linear: y = a*x + b
    2. Power law: y = a*x^b
    3. Logarithmic: y = a*log(x) + b
    4. Saturating: y = a*(1 - exp(-b*x))

    Returns:
        dict with model fits, parameters, R² values
    """
    models = {}

    # 1. Linear model
    linear_coeffs = np.polyfit(n_values, mean_pops, 1)
    linear_pred = np.polyval(linear_coeffs, n_values)
    linear_r2 = 1 - (np.sum((mean_pops - linear_pred)**2) /
                     np.sum((mean_pops - np.mean(mean_pops))**2))

    models['linear'] = {
        'name': 'Linear',
        'equation': f'y = {linear_coeffs[0]:.4f}x + {linear_coeffs[1]:.2f}',
        'params': linear_coeffs,
        'predictions': linear_pred,
        'r_squared': linear_r2
    }

    # 2. Power law model
    try:
        # Use log-log regression for initial guess
        log_n = np.log(n_values[n_values > 0])
        log_pop = np.log(mean_pops[n_values > 0])
        log_coeffs = np.polyfit(log_n, log_pop, 1)

        # Fit y = a * x^b
        def power_law(x, a, b):
            return a * x**b

        popt, _ = curve_fit(power_law, n_values, mean_pops,
                           p0=(np.exp(log_coeffs[1]), log_coeffs[0]))
        power_pred = power_law(n_values, *popt)
        power_r2 = 1 - (np.sum((mean_pops - power_pred)**2) /
                       np.sum((mean_pops - np.mean(mean_pops))**2))

        models['power'] = {
            'name': 'Power Law',
            'equation': f'y = {popt[0]:.2f}x^{popt[1]:.3f}',
            'params': popt,
            'predictions': power_pred,
            'r_squared': power_r2
        }
    except Exception as e:
        print(f"Power law fit failed: {e}")
        models['power'] = None

    # 3. Logarithmic model
    try:
        # y = a*log(x) + b
        log_n_safe = np.log(n_values[n_values > 0])
        log_coeffs = np.polyfit(log_n_safe, mean_pops[n_values > 0], 1)

        log_pred = log_coeffs[0] * np.log(n_values) + log_coeffs[1]
        log_r2 = 1 - (np.sum((mean_pops - log_pred)**2) /
                     np.sum((mean_pops - np.mean(mean_pops))**2))

        models['logarithmic'] = {
            'name': 'Logarithmic',
            'equation': f'y = {log_coeffs[0]:.2f}log(x) + {log_coeffs[1]:.2f}',
            'params': log_coeffs,
            'predictions': log_pred,
            'r_squared': log_r2
        }
    except Exception as e:
        print(f"Logarithmic fit failed: {e}")
        models['logarithmic'] = None

    # 4. Saturating exponential model
    try:
        # y = a*(1 - exp(-b*x))
        def saturating(x, a, b):
            return a * (1 - np.exp(-b * x))

        # Initial guess: a = max(mean_pops), b = 0.1
        popt, _ = curve_fit(saturating, n_values, mean_pops,
                           p0=(np.max(mean_pops), 0.1),
                           bounds=([0, 0], [np.inf, np.inf]))
        sat_pred = saturating(n_values, *popt)
        sat_r2 = 1 - (np.sum((mean_pops - sat_pred)**2) /
                     np.sum((mean_pops - np.mean(mean_pops))**2))

        models['saturating'] = {
            'name': 'Saturating',
            'equation': f'y = {popt[0]:.2f}(1 - e^(-{popt[1]:.3f}x))',
            'params': popt,
            'predictions': sat_pred,
            'r_squared': sat_r2
        }
    except Exception as e:
        print(f"Saturating fit failed: {e}")
        models['saturating'] = None

    return models


def select_best_model(models: dict) -> tuple:
    """
    Select best-fitting model based on R²

    Returns:
        (best_model_key, best_model_dict)
    """
    valid_models = {k: v for k, v in models.items() if v is not None}

    if not valid_models:
        return None, None

    best_key = max(valid_models, key=lambda k: valid_models[k]['r_squared'])
    return best_key, valid_models[best_key]


def identify_thresholds(n_values: np.ndarray, mean_pops: np.ndarray) -> dict:
    """
    Identify key thresholds in population count scaling

    Returns:
        dict with:
        - minimum_viable_n: Smallest N achieving homeostasis (pop > 2.5)
        - optimal_n: N with highest mean population
        - diminishing_threshold: N beyond which marginal benefit < threshold
    """
    # Homeostasis threshold (Basin A)
    HOMEOSTASIS_THRESHOLD = 2.5

    viable_indices = np.where(mean_pops > HOMEOSTASIS_THRESHOLD)[0]
    min_viable_n = n_values[viable_indices[0]] if len(viable_indices) > 0 else None

    # Optimal N (highest mean population)
    optimal_idx = np.argmax(mean_pops)
    optimal_n = n_values[optimal_idx]
    optimal_pop = mean_pops[optimal_idx]

    # Diminishing returns (marginal benefit < 10% of optimal)
    marginal_benefits = np.diff(mean_pops)
    threshold = 0.1 * optimal_pop
    diminishing_indices = np.where(marginal_benefits < threshold)[0]
    diminishing_threshold = n_values[diminishing_indices[0] + 1] if len(diminishing_indices) > 0 else None

    return {
        'minimum_viable_n': min_viable_n,
        'optimal_n': optimal_n,
        'optimal_population': optimal_pop,
        'diminishing_threshold': diminishing_threshold
    }


def generate_v8_figure(
    n_values: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    models: dict,
    best_model_key: str,
    thresholds: dict,
    output_path: Path
):
    """
    Generate publication-quality V8 population count scaling figure

    Figure structure:
    - Scatter plot with error bars (data points)
    - Best-fit model regression line
    - Baseline (N=1) highlighted
    - Optimal N highlighted
    - Basin threshold line (y=2.5)
    - Model equation and R² annotation
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300, facecolor=COLOR_BG)

    # Data points with error bars
    ax.errorbar(n_values, mean_pops, yerr=std_pops,
                fmt='o', markersize=10, capsize=5, capthick=2,
                color=COLOR_HIERARCHICAL, markeredgecolor='black',
                markeredgewidth=1.5, linewidth=2, alpha=0.7,
                label='Observed Data')

    # Highlight baseline (N=1)
    baseline_idx = np.where(n_values == 1)[0]
    if len(baseline_idx) > 0:
        ax.scatter([1], [mean_pops[baseline_idx[0]]],
                  s=200, c=COLOR_BASELINE, marker='s',
                  edgecolors='black', linewidths=2, zorder=5,
                  label='Baseline (N=1)')

    # Highlight optimal N
    if thresholds['optimal_n'] is not None:
        optimal_idx = np.where(n_values == thresholds['optimal_n'])[0]
        ax.scatter([thresholds['optimal_n']], [mean_pops[optimal_idx[0]]],
                  s=300, c='yellow', marker='*',
                  edgecolors='black', linewidths=2, zorder=5,
                  label=f'Optimal (N={thresholds["optimal_n"]})')

    # Best-fit model regression line
    if best_model_key and models[best_model_key]:
        best_model = models[best_model_key]

        # Smooth curve for visualization
        n_smooth = np.linspace(n_values.min(), n_values.max(), 200)

        if best_model_key == 'linear':
            y_smooth = np.polyval(best_model['params'], n_smooth)
        elif best_model_key == 'power':
            y_smooth = best_model['params'][0] * n_smooth**best_model['params'][1]
        elif best_model_key == 'logarithmic':
            y_smooth = best_model['params'][0] * np.log(n_smooth) + best_model['params'][1]
        elif best_model_key == 'saturating':
            y_smooth = best_model['params'][0] * (1 - np.exp(-best_model['params'][1] * n_smooth))

        ax.plot(n_smooth, y_smooth, '-', color='darkred', linewidth=3,
               alpha=0.8, label=f'{best_model["name"]} Fit')

    # Basin threshold line
    ax.axhline(y=2.5, color='gray', linestyle='--', linewidth=2,
              alpha=0.5, label='Basin Threshold')

    # Model annotation
    if best_model_key and models[best_model_key]:
        best_model = models[best_model_key]
        annotation_text = f'{best_model["equation"]}\nR² = {best_model["r_squared"]:.4f}'

        ax.text(0.05, 0.95, annotation_text,
               transform=ax.transAxes, fontsize=11, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='white',
                        edgecolor='black', linewidth=1.5, alpha=0.9))

    # Threshold annotations
    if thresholds['minimum_viable_n'] is not None:
        ax.axvline(x=thresholds['minimum_viable_n'], color='green',
                  linestyle=':', linewidth=2, alpha=0.5,
                  label=f'Min Viable (N≥{thresholds["minimum_viable_n"]})')

    if thresholds['diminishing_threshold'] is not None:
        ax.axvline(x=thresholds['diminishing_threshold'], color='orange',
                  linestyle=':', linewidth=2, alpha=0.5,
                  label=f'Diminishing Returns (N>{thresholds["diminishing_threshold"]})')

    # Axis labels and title
    ax.set_xlabel('Number of Subpopulations (N)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Mean Final Population', fontsize=13, fontweight='bold')
    ax.set_title('C186 V8: Population Count Scaling',
                fontsize=14, fontweight='bold', pad=15)

    # Grid and legend
    ax.grid(True, alpha=0.3, linewidth=0.8)
    ax.legend(loc='best', fontsize=9, framealpha=0.95, edgecolor='black')

    # Axis limits (ensure all data visible)
    ax.set_xlim(0, n_values.max() * 1.1)
    ax.set_ylim(0, max(mean_pops.max() + std_pops.max(), 3.5) * 1.1)

    # Save figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=COLOR_BG)
    print(f"V8 figure saved: {output_path}")

    plt.close()


def save_v8_analysis(
    n_values: np.ndarray,
    mean_pops: np.ndarray,
    std_pops: np.ndarray,
    models: dict,
    best_model_key: str,
    thresholds: dict,
    output_path: Path
):
    """Save V8 statistical analysis to JSON"""
    analysis = {
        'population_counts': n_values.tolist(),
        'mean_populations': mean_pops.tolist(),
        'std_populations': std_pops.tolist(),
        'models': {
            k: {
                'name': v['name'],
                'equation': v['equation'],
                'r_squared': float(v['r_squared']),
                'params': [float(p) for p in v['params']]
            }
            for k, v in models.items() if v is not None
        },
        'best_model': best_model_key,
        'thresholds': {
            k: (int(v) if isinstance(v, (int, np.integer)) else float(v))
            for k, v in thresholds.items() if v is not None
        }
    }

    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"V8 analysis saved: {output_path}")


def print_v8_summary(models: dict, best_model_key: str, thresholds: dict):
    """Print human-readable summary of V8 analysis"""
    print("\n" + "="*70)
    print("C186 V8 POPULATION COUNT SCALING ANALYSIS")
    print("="*70)
    print()

    print("MODEL FITS:")
    for key, model in models.items():
        if model is not None:
            marker = "**BEST**" if key == best_model_key else ""
            print(f"  {model['name']}: {marker}")
            print(f"    Equation: {model['equation']}")
            print(f"    R² = {model['r_squared']:.4f}")
    print()

    print("THRESHOLDS:")
    if thresholds['minimum_viable_n'] is not None:
        print(f"  Minimum Viable Hierarchy: N ≥ {thresholds['minimum_viable_n']}")
    if thresholds['optimal_n'] is not None:
        print(f"  Optimal Population Count: N = {thresholds['optimal_n']}")
        print(f"    (Mean population: {thresholds['optimal_population']:.2f})")
    if thresholds['diminishing_threshold'] is not None:
        print(f"  Diminishing Returns: N > {thresholds['diminishing_threshold']}")
    print()

    print("INTERPRETATION:")
    if best_model_key == 'linear':
        print("  Linear scaling suggests proportional benefit with each")
        print("  additional subpopulation (no saturation observed)")
    elif best_model_key == 'power':
        exponent = models[best_model_key]['params'][1]
        if exponent < 1:
            print(f"  Sublinear scaling (exponent = {exponent:.3f}) indicates")
            print("  diminishing marginal returns with additional subpopulations")
        elif exponent > 1:
            print(f"  Superlinear scaling (exponent = {exponent:.3f}) suggests")
            print("  accelerating benefits with organizational complexity")
        else:
            print("  Linear power law (exponent ≈ 1) confirms proportional scaling")
    elif best_model_key == 'logarithmic':
        print("  Logarithmic scaling shows rapid initial gains that saturate")
        print("  at higher population counts (diminishing returns)")
    elif best_model_key == 'saturating':
        print("  Saturating exponential indicates asymptotic approach to")
        print("  maximum stable population (system capacity limit)")

    print("="*70)


def main():
    """Execute V8 population count scaling analysis"""
    print("="*70)
    print("C186 V8 Population Count Scaling Analysis")
    print("="*70)
    print()

    # Paths
    workspace_root = Path('/Volumes/dual/DUALITY-ZERO-V2')
    results_path = workspace_root / 'experiments' / 'results' / 'c186_v8_population_count_variation_results.json'
    figure_path = workspace_root / 'data' / 'figures' / 'c186_v8_population_count_scaling.png'
    analysis_path = workspace_root / 'experiments' / 'results' / 'c186_v8_population_count_analysis.json'

    # Load V8 results
    print("Loading V8 results...")
    try:
        results = load_v8_results(results_path)
        print(f"  ✅ Loaded {len(results['experiments'])} experiments")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        print("  V8 experiment has not completed yet")
        return

    # Extract population scaling data
    print("\nExtracting population scaling data...")
    n_values, mean_pops, std_pops, all_pops = extract_population_scaling(results)
    print(f"  ✅ Extracted {len(n_values)} population count conditions")

    # Fit scaling models
    print("\nFitting scaling models...")
    models = fit_scaling_models(n_values, mean_pops)
    valid_models = [k for k, v in models.items() if v is not None]
    print(f"  ✅ Fit {len(valid_models)} models: {', '.join(valid_models)}")

    # Select best model
    best_model_key, best_model = select_best_model(models)
    if best_model:
        print(f"  ✅ Best model: {best_model['name']} (R² = {best_model['r_squared']:.4f})")

    # Identify thresholds
    print("\nIdentifying critical thresholds...")
    thresholds = identify_thresholds(n_values, mean_pops)
    print(f"  ✅ Minimum viable N: {thresholds['minimum_viable_n']}")
    print(f"  ✅ Optimal N: {thresholds['optimal_n']}")
    print(f"  ✅ Diminishing threshold: {thresholds['diminishing_threshold']}")

    # Generate figure
    print("\nGenerating publication figure...")
    generate_v8_figure(n_values, mean_pops, std_pops, models,
                      best_model_key, thresholds, figure_path)
    print(f"  ✅ Figure saved @ 300 DPI")

    # Save analysis
    print("\nSaving statistical analysis...")
    save_v8_analysis(n_values, mean_pops, std_pops, models,
                    best_model_key, thresholds, analysis_path)
    print(f"  ✅ Analysis saved")

    # Print summary
    print_v8_summary(models, best_model_key, thresholds)

    print("\n" + "="*70)
    print("V8 Analysis Complete")
    print("="*70)
    print(f"Figure: {figure_path}")
    print(f"Analysis: {analysis_path}")
    print("\nNext Steps:")
    print("  - Integrate findings into manuscript Results section 3.8")
    print("  - Update Discussion section 4.6 with scaling theory")
    print("  - Regenerate comprehensive visualization")
    print("="*70)


if __name__ == '__main__':
    main()
