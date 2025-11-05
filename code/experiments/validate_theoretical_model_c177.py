#!/usr/bin/env python3
"""
THEORETICAL MODEL VALIDATION - C177 BOUNDARY MAPPING
Compare theoretical predictions to empirical findings

Purpose:
  - Load C177 experimental results
  - Calculate spawns-per-agent for each frequency
  - Compare empirical spawn success to theoretical predictions
  - Generate validation figures and statistical analysis

Theoretical Model:
  Success(λ) = P(X < k_max) where X ~ Poisson(λ), k_max = 4
  Predicts spawn success from spawns-per-agent metric

Researcher: Claude (DUALITY-ZERO-V2)
Date: 2025-11-04 (Cycle 991)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import poisson
from scipy.stats import linregress

# File paths
RESULTS_FILE = Path(__file__).parent / "results" / "cycle177_extended_frequency_range_results.json"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Theoretical model parameters
K_MAX = 4  # Maximum sustainable compositions before energy depletion


def theoretical_success_rate(spawns_per_agent, k_max=K_MAX):
    """
    Predict spawn success rate from theoretical model.

    Parameters:
    -----------
    spawns_per_agent : float or array
        Average number of spawn attempts per agent (λ = S/N)
    k_max : int
        Maximum sustainable compositions before depletion (default: 4)

    Returns:
    --------
    success_rate : float or array
        Predicted spawn success rate (0.0 to 1.0)

    Theory:
    -------
    Success(λ) = P(X < k_max) where X ~ Poisson(λ)
               = Σⱼ₌₀^(k_max-1) [e^(-λ) · λʲ / j!]

    Derivation from energy parameters:
    - E₀ = 50.0 (initial energy)
    - α = 0.3 (energy transfer fraction)
    - E_spawn = 10.0 (spawn threshold)
    - Agent can sustain k_max = 4 compositions: 50→35→24.5→17.15→12.0→8.4(fail)
    """
    lambda_val = np.asarray(spawns_per_agent)
    return poisson.cdf(k_max - 1, lambda_val)


def load_results():
    """Load C177 experimental results."""
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)
    return data


def calculate_spawns_per_agent(experiments):
    """
    Calculate spawns-per-agent for each frequency.

    Methodology (from Paper 2, Section 2.4.6):
      S/N = Total spawn attempts / Average population size

    Returns:
    --------
    frequency_stats : dict
        {frequency: {'spawns_per_agent': float, 'spawn_success': float, ...}}
    """
    frequencies = sorted(set(exp['frequency'] for exp in experiments))
    stats = {}

    for freq in frequencies:
        freq_exps = [e for e in experiments if e['frequency'] == freq]

        # Calculate spawns/agent across all replicates
        spawns_per_agent_values = []
        spawn_success_values = []

        for exp in freq_exps:
            # Spawns/agent = spawn_attempts / average_population
            # From experimental data
            if 'spawn_attempts' in exp and 'average_population' in exp:
                if exp['average_population'] > 0:
                    spa = exp['spawn_attempts'] / exp['average_population']
                    spawns_per_agent_values.append(spa)

            # Spawn success rate
            if 'spawn_success_rate' in exp:
                spawn_success_values.append(exp['spawn_success_rate'])

        if spawns_per_agent_values:
            stats[freq] = {
                'spawns_per_agent_mean': np.mean(spawns_per_agent_values),
                'spawns_per_agent_std': np.std(spawns_per_agent_values),
                'spawn_success_mean': np.mean(spawn_success_values) if spawn_success_values else 0.0,
                'spawn_success_std': np.std(spawn_success_values) if spawn_success_values else 0.0,
                'n_replicates': len(freq_exps),
                'basin_a_percent': (sum(1 for e in freq_exps if e['basin'] == 'A') / len(freq_exps)) * 100
            }

    return stats


def validate_model(frequency_stats):
    """
    Compare theoretical predictions to empirical observations.

    Returns:
    --------
    validation_results : dict
        {frequency: {'predicted': float, 'observed': float, 'error': float, ...}}
    """
    results = {}

    for freq, stats in frequency_stats.items():
        lambda_val = stats['spawns_per_agent_mean']
        predicted = theoretical_success_rate(lambda_val)
        observed = stats['spawn_success_mean']
        error = predicted - observed

        # Classification
        if lambda_val < 2.0:
            zone = "HIGH"
        elif lambda_val < 4.0:
            zone = "TRANSITION"
        else:
            zone = "LOW"

        results[freq] = {
            'spawns_per_agent': lambda_val,
            'predicted_success': predicted,
            'observed_success': observed,
            'error_absolute': error,
            'error_relative': (error / observed * 100) if observed > 0 else np.nan,
            'threshold_zone': zone,
            'basin_a_percent': stats['basin_a_percent']
        }

    return results


def generate_validation_figures(frequency_stats, validation_results):
    """
    Generate publication-quality validation figures.

    Figures:
      1. Predicted vs Observed Spawn Success
      2. Error Analysis (residuals vs spawns/agent)
      3. Threshold Zone Classification
    """
    frequencies = sorted(frequency_stats.keys())

    # Extract data
    spawns_per_agent = [frequency_stats[f]['spawns_per_agent_mean'] for f in frequencies]
    observed_success = [frequency_stats[f]['spawn_success_mean'] for f in frequencies]
    predicted_success = [validation_results[f]['predicted_success'] for f in frequencies]
    errors = [validation_results[f]['error_absolute'] for f in frequencies]

    # Figure 1: Predicted vs Observed
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot observed data points
    ax.plot(spawns_per_agent, observed_success, 'o', markersize=10,
            color='darkblue', label='Empirical Data (C177)', zorder=3)

    # Plot theoretical prediction curve
    lambda_range = np.linspace(0, max(spawns_per_agent) * 1.1, 100)
    theory_curve = theoretical_success_rate(lambda_range)
    ax.plot(lambda_range, theory_curve, '-', linewidth=2,
            color='red', label='Theoretical Model', zorder=2)

    # Add threshold zones
    ax.axvspan(0, 2.0, alpha=0.1, color='green', label='High Success Zone')
    ax.axvspan(2.0, 4.0, alpha=0.1, color='orange', label='Transition Zone')
    ax.axvspan(4.0, max(spawns_per_agent) * 1.1, alpha=0.1, color='red',
               label='Low Success Zone')

    # Add reference lines
    ax.axhline(0.857, linestyle='--', color='gray', alpha=0.5,
               label='85.7% (2.0 threshold)')
    ax.axvline(2.0, linestyle='--', color='gray', alpha=0.5)

    ax.set_xlabel('Spawns Per Agent (λ = S/N)', fontsize=12)
    ax.set_ylabel('Spawn Success Rate', fontsize=12)
    ax.set_title('Theoretical Model Validation: Predicted vs Observed Spawn Success (C177)',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_model_validation_prediction_vs_observation.png', dpi=300)
    plt.close()

    # Figure 2: Error Analysis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color by threshold zone
    colors = []
    for spa in spawns_per_agent:
        if spa < 2.0:
            colors.append('green')
        elif spa < 4.0:
            colors.append('orange')
        else:
            colors.append('red')

    ax.scatter(spawns_per_agent, errors, c=colors, s=100, alpha=0.7, edgecolors='black')
    ax.axhline(0, linestyle='-', color='black', linewidth=1)
    ax.axvline(2.0, linestyle='--', color='gray', alpha=0.5)
    ax.axvline(4.0, linestyle='--', color='gray', alpha=0.5)

    ax.set_xlabel('Spawns Per Agent (λ = S/N)', fontsize=12)
    ax.set_ylabel('Prediction Error (Predicted - Observed)', fontsize=12)
    ax.set_title('Model Error Analysis (C177)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add error statistics
    rmse = np.sqrt(np.mean(np.array(errors)**2))
    mae = np.mean(np.abs(errors))
    ax.text(0.02, 0.98, f'RMSE: {rmse:.3f}\nMAE: {mae:.3f}',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_model_validation_error_analysis.png', dpi=300)
    plt.close()

    # Figure 3: Frequency vs Success with Basin Classification
    fig, ax = plt.subplots(figsize=(10, 6))

    # Separate by Basin
    basin_a_freqs = [f for f in frequencies if validation_results[f]['basin_a_percent'] == 100]
    basin_mixed_freqs = [f for f in frequencies if 0 < validation_results[f]['basin_a_percent'] < 100]
    basin_b_freqs = [f for f in frequencies if validation_results[f]['basin_a_percent'] == 0]

    # Plot by basin
    if basin_a_freqs:
        basin_a_success = [frequency_stats[f]['spawn_success_mean'] for f in basin_a_freqs]
        ax.plot(basin_a_freqs, basin_a_success, 'o', markersize=10,
                color='green', label='Basin A (100% homeostasis)', zorder=3)

    if basin_mixed_freqs:
        basin_mixed_success = [frequency_stats[f]['spawn_success_mean'] for f in basin_mixed_freqs]
        ax.plot(basin_mixed_freqs, basin_mixed_success, 's', markersize=10,
                color='orange', label='Mixed (partial homeostasis)', zorder=3)

    if basin_b_freqs:
        basin_b_success = [frequency_stats[f]['spawn_success_mean'] for f in basin_b_freqs]
        ax.plot(basin_b_freqs, basin_b_success, 'x', markersize=10,
                color='red', label='Basin B (collapse)', zorder=3)

    # Theoretical curve
    freq_range = np.linspace(min(frequencies), max(frequencies), 100)
    # Note: Can't directly map frequency to spawns/agent without population trajectory
    # So this is illustrative only
    ax.axhline(0.857, linestyle='--', color='gray', alpha=0.5,
               label='85.7% threshold')

    ax.set_xlabel('Spawn Frequency (%)', fontsize=12)
    ax.set_ylabel('Spawn Success Rate', fontsize=12)
    ax.set_title('Basin Classification vs Spawn Success (C177)',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'c177_model_validation_basin_classification.png', dpi=300)
    plt.close()

    print(f"✓ Generated 3 validation figures @ 300 DPI in {OUTPUT_DIR}")


def print_validation_report(frequency_stats, validation_results):
    """Print comprehensive validation report."""
    print("=" * 80)
    print("THEORETICAL MODEL VALIDATION REPORT - C177")
    print("=" * 80)
    print()

    print("THEORETICAL MODEL:")
    print("-" * 80)
    print(f"Formula: Success(λ) = P(X < {K_MAX}) where X ~ Poisson(λ)")
    print(f"Parameters: k_max = {K_MAX} compositions (derived from E₀=50, α=0.3, E_spawn=10)")
    print(f"Threshold: λ = 2.0 → 85.7% success (boundary of high/transition zones)")
    print()

    print("FREQUENCY-BY-FREQUENCY COMPARISON:")
    print("-" * 80)
    print(f"{'Freq':<8} {'S/N':<8} {'Pred':<8} {'Obs':<8} {'Error':<8} {'Zone':<12} {'Basin A':<10}")
    print("-" * 80)

    frequencies = sorted(validation_results.keys())
    for freq in frequencies:
        v = validation_results[freq]
        print(f"{freq:>6.1f}% {v['spawns_per_agent']:>7.2f} "
              f"{v['predicted_success']:>7.1%} {v['observed_success']:>7.1%} "
              f"{v['error_absolute']:>+7.3f} {v['threshold_zone']:<12} "
              f"{v['basin_a_percent']:>7.0f}%")

    print()

    # Statistical summary
    errors = [v['error_absolute'] for v in validation_results.values()]
    observed = [v['observed_success'] for v in validation_results.values() if v['observed_success'] > 0]
    relative_errors = [v['error_relative'] for v in validation_results.values()
                      if not np.isnan(v['error_relative'])]

    print("STATISTICAL SUMMARY:")
    print("-" * 80)
    print(f"Mean Absolute Error (MAE):        {np.mean(np.abs(errors)):.3f}")
    print(f"Root Mean Square Error (RMSE):    {np.sqrt(np.mean(np.array(errors)**2)):.3f}")
    print(f"Mean Relative Error:              {np.mean(relative_errors):.1f}%")
    print(f"Median Relative Error:            {np.median(relative_errors):.1f}%")
    print()

    # Correlation analysis
    predicted_vals = [v['predicted_success'] for v in validation_results.values()]
    observed_vals = [v['observed_success'] for v in validation_results.values()]

    if len(predicted_vals) > 2:
        r, p_value = np.corrcoef(predicted_vals, observed_vals)[0, 1], 0.0
        slope, intercept, r_value, p_value, std_err = linregress(predicted_vals, observed_vals)

        print("CORRELATION ANALYSIS:")
        print("-" * 80)
        print(f"Pearson correlation (r):          {r_value:.3f}")
        print(f"R-squared (r²):                   {r_value**2:.3f}")
        print(f"P-value:                          {p_value:.4f}")
        print(f"Linear fit: Observed = {slope:.3f} × Predicted + {intercept:.3f}")
        print()

    # Zone-specific analysis
    print("ZONE-SPECIFIC PERFORMANCE:")
    print("-" * 80)

    zones = ['HIGH', 'TRANSITION', 'LOW']
    for zone in zones:
        zone_results = [v for v in validation_results.values() if v['threshold_zone'] == zone]
        if zone_results:
            zone_errors = [v['error_absolute'] for v in zone_results]
            print(f"{zone} Zone (λ {zone_thresholds(zone)}):")
            print(f"  N = {len(zone_results)} frequencies")
            print(f"  MAE = {np.mean(np.abs(zone_errors)):.3f}")
            print(f"  RMSE = {np.sqrt(np.mean(np.array(zone_errors)**2)):.3f}")

    print()

    # Model assessment
    print("MODEL ASSESSMENT:")
    print("-" * 80)

    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(np.array(errors)**2))

    if rmse < 0.10:
        assessment = "EXCELLENT (RMSE < 0.10)"
    elif rmse < 0.20:
        assessment = "GOOD (RMSE < 0.20)"
    elif rmse < 0.30:
        assessment = "ACCEPTABLE (RMSE < 0.30)"
    else:
        assessment = "POOR (RMSE ≥ 0.30)"

    print(f"Overall Performance: {assessment}")
    print()

    # Identify discrepancies
    large_errors = [(f, v) for f, v in validation_results.items()
                   if abs(v['error_absolute']) > 0.15]

    if large_errors:
        print("SIGNIFICANT DISCREPANCIES (|error| > 0.15):")
        print("-" * 80)
        for freq, v in large_errors:
            print(f"  {freq:.1f}%: Predicted {v['predicted_success']:.1%}, "
                  f"Observed {v['observed_success']:.1%}, "
                  f"Error {v['error_absolute']:+.3f}")
            print(f"    Possible causes: {identify_discrepancy_causes(v)}")
    else:
        print("✓ No significant discrepancies (all |error| ≤ 0.15)")

    print()
    print("=" * 80)


def zone_thresholds(zone):
    """Return threshold description for zone."""
    if zone == "HIGH":
        return "< 2.0"
    elif zone == "TRANSITION":
        return "2.0-4.0"
    elif zone == "LOW":
        return "> 4.0"
    return "unknown"


def identify_discrepancy_causes(validation_result):
    """Suggest possible causes for large prediction errors."""
    causes = []

    spa = validation_result['spawns_per_agent']
    error = validation_result['error_absolute']

    if spa > 8.0 and error < 0:
        causes.append("High load → population turnover (fresh agents not in model)")

    if spa < 1.0 and error > 0:
        causes.append("Low load → statistical noise or stochastic effects")

    if validation_result['basin_a_percent'] < 100:
        causes.append("Mixed basin → population collapse affects success rate")

    if not causes:
        causes.append("Within expected stochastic variation")

    return ", ".join(causes)


def main():
    """Execute theoretical model validation."""
    print("=" * 80)
    print("THEORETICAL MODEL VALIDATION - C177 BOUNDARY MAPPING")
    print("=" * 80)
    print()

    # Load C177 results
    print("Loading C177 experimental results...")
    data = load_results()
    print(f"✓ Loaded {len(data['experiments'])} experiments")
    print()

    # Calculate spawns-per-agent statistics
    print("Calculating spawns-per-agent metrics...")
    frequency_stats = calculate_spawns_per_agent(data['experiments'])
    print(f"✓ Analyzed {len(frequency_stats)} frequencies")
    print()

    # Validate theoretical model
    print("Comparing theoretical predictions to empirical observations...")
    validation_results = validate_model(frequency_stats)
    print(f"✓ Validated model across {len(validation_results)} frequencies")
    print()

    # Generate validation figures
    print("Generating validation figures...")
    generate_validation_figures(frequency_stats, validation_results)
    print()

    # Print comprehensive report
    print_validation_report(frequency_stats, validation_results)

    print("Validation complete. Figures saved to:", OUTPUT_DIR)
    print("=" * 80)


if __name__ == '__main__':
    main()
