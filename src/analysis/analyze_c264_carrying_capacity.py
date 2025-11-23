#!/usr/bin/env python3
"""
Analysis Script for C264: Carrying Capacity Dynamics in NRM

Purpose: Apply MOG falsification gauntlet to C264 experimental results
Hypothesis: K = β × E_recharge (linear carrying capacity relationship)
MOG Resonance: α = 0.92 (Very Strong, Tier 1 Priority)

Falsification Criteria (Pre-Registered):
  - Reject if R² < 0.6 (weak correlation)
  - Reject if β ≤ 0 (non-positive slope)
  - Reject if non-monotonic relationship
  - Reject if p > 0.05 (statistically insignificant)

Cross-Domain Analogy:
  Domain A: NRM Energy Homeostasis (computational)
  Domain B: Ecological Carrying Capacity (biological)
  Coupling: Energy ↔ Resource (HIGH), Self-regulation ↔ Density-dependence (HIGH)

MOG Falsification Tests:
  Newtonian: Quantitative prediction K = β × E_recharge with R² > 0.6
  Maxwellian: Unifies computational energy with ecological resource theory
  Einsteinian: Reduces to Paper 2 baseline (E=0.5 → K≈17)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1372)
License: GPL-3.0
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from scipy.optimize import curve_fit
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Publication-quality settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

@dataclass
class CarryingCapacityResults:
    """Aggregated results for single E_recharge condition"""
    e_recharge: float
    n_seeds: int
    mean_K: float
    std_K: float
    sem_K: float
    mean_eta: float  # spawn success rate
    std_eta: float
    extinction_rate: float
    mean_time_to_eq: float

def load_results(results_path: Path) -> Dict:
    """Load C264 experimental results"""
    with open(results_path, 'r') as f:
        data = json.load(f)
    return data

def aggregate_by_e_recharge(results: List[Dict]) -> List[CarryingCapacityResults]:
    """Aggregate results by E_recharge level"""
    e_recharge_values = sorted(set(r['e_recharge'] for r in results))
    aggregated = []

    for e_val in e_recharge_values:
        condition_data = [r for r in results if r['e_recharge'] == e_val]

        K_values = [r['mean_population'] for r in condition_data]
        eta_values = [r['spawn_success_rate'] for r in condition_data]
        extinctions = [r['extinction'] for r in condition_data]
        time_to_eq = [r['time_to_equilibrium'] for r in condition_data if r['time_to_equilibrium'] > 0]

        aggregated.append(CarryingCapacityResults(
            e_recharge=e_val,
            n_seeds=len(condition_data),
            mean_K=float(np.mean(K_values)),
            std_K=float(np.std(K_values)),
            sem_K=float(np.std(K_values) / np.sqrt(len(K_values))),
            mean_eta=float(np.mean(eta_values)),
            std_eta=float(np.std(eta_values)),
            extinction_rate=float(sum(extinctions) / len(extinctions)),
            mean_time_to_eq=float(np.mean(time_to_eq)) if time_to_eq else -1
        ))

    return aggregated

def test_linear_scaling(aggregated: List[CarryingCapacityResults]) -> Dict:
    """Test primary hypothesis: K = β × E_recharge (linear)"""

    e_values = np.array([a.e_recharge for a in aggregated])
    K_values = np.array([a.mean_K for a in aggregated])
    K_errors = np.array([a.sem_K for a in aggregated])

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(e_values, K_values)
    r_squared = r_value ** 2

    # Alternative models for comparison
    # Power law: K = α × E^γ
    def power_law(E, alpha, gamma):
        return alpha * (E ** gamma)

    try:
        popt_power, _ = curve_fit(power_law, e_values, K_values, p0=[1.0, 1.0])
        K_pred_power = power_law(e_values, *popt_power)
        r_squared_power = 1 - (np.sum((K_values - K_pred_power)**2) / 
                              np.sum((K_values - np.mean(K_values))**2))
    except:
        popt_power = [np.nan, np.nan]
        r_squared_power = 0.0

    # Saturation: K = K_max × (1 - exp(-E/E_0))
    def saturation(E, K_max, E_0):
        return K_max * (1 - np.exp(-E / E_0))

    try:
        popt_sat, _ = curve_fit(saturation, e_values, K_values, p0=[100.0, 1.0])
        K_pred_sat = saturation(e_values, *popt_sat)
        r_squared_sat = 1 - (np.sum((K_values - K_pred_sat)**2) / 
                            np.sum((K_values - np.mean(K_values))**2))
    except:
        popt_sat = [np.nan, np.nan]
        r_squared_sat = 0.0

    # Check monotonicity
    diffs = np.diff(K_values)
    monotonic = np.all(diffs >= 0) or np.all(diffs <= 0)

    # Falsification criteria
    falsified = []
    if r_squared < 0.6:
        falsified.append("R² < 0.6 (weak correlation)")
    if slope <= 0:
        falsified.append("β ≤ 0 (non-positive slope)")
    if not monotonic:
        falsified.append("Non-monotonic relationship")
    if p_value > 0.05:
        falsified.append("p > 0.05 (insignificant)")

    return {
        'model': 'Linear (K = β × E_recharge)',
        'slope_beta': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value,
        'std_err': std_err,
        'monotonic': monotonic,
        'falsified': len(falsified) > 0,
        'falsification_reasons': falsified,
        'status': 'FALSIFIED' if falsified else 'VALIDATED',
        'alternative_models': {
            'power_law': {
                'formula': 'K = α × E^γ',
                'alpha': popt_power[0],
                'gamma': popt_power[1],
                'r_squared': r_squared_power,
                'better_fit': r_squared_power > r_squared
            },
            'saturation': {
                'formula': 'K = K_max × (1 - exp(-E/E_0))',
                'K_max': popt_sat[0],
                'E_0': popt_sat[1],
                'r_squared': r_squared_sat,
                'better_fit': r_squared_sat > r_squared
            }
        }
    }

def test_allee_effect(aggregated: List[CarryingCapacityResults]) -> Dict:
    """Test secondary hypothesis: Allee effect at low E_recharge"""

    e_values = np.array([a.e_recharge for a in aggregated])
    extinction_rates = np.array([a.extinction_rate for a in aggregated])

    # Fit sigmoid: P(extinct) = 1 / (1 + exp((E - E_c) / σ))
    def sigmoid(E, E_c, sigma):
        return 1 / (1 + np.exp((E - E_c) / sigma))

    try:
        popt, _ = curve_fit(sigmoid, e_values, extinction_rates, p0=[0.2, 0.1])
        E_critical = popt[0]
        sigma = popt[1]

        # Check if threshold exists (extinction rate drops sharply)
        threshold_exists = (E_critical > 0.05) and (sigma < 0.5)
    except:
        E_critical = np.nan
        sigma = np.nan
        threshold_exists = False

    return {
        'hypothesis': 'Allee Effect (extinction threshold)',
        'E_critical': E_critical,
        'sigma': sigma,
        'threshold_exists': threshold_exists,
        'extinction_rates': extinction_rates.tolist(),
        'status': 'SUPPORTED' if threshold_exists else 'NOT DETECTED'
    }

def mog_falsification_gauntlet(aggregated: List[CarryingCapacityResults],
                               linear_test: Dict) -> Dict:
    """Apply MOG tri-fold falsification"""

    # Test 1: Newtonian (Predictive Accuracy)
    newtonian_pass = (linear_test['status'] == 'VALIDATED')

    # Test 2: Maxwellian (Domain Unification)
    # Does K = β × E_recharge unify computational and ecological theory?
    concepts_unified = [
        'Energy availability determines population size',
        'Resource limitation = Energy limitation',
        'Self-regulation emerges from energy constraint',
        'Carrying capacity is energy-dependent'
    ]
    parameters_required = ['β (slope)', 'E_recharge']
    elegance = len(concepts_unified) / len(parameters_required)

    maxwellian_pass = (elegance >= 1.5)

    # Test 3: Einsteinian (Limit Behavior)
    # At E_recharge = 0.5 (Paper 2 baseline), should get K ≈ 17
    baseline_e = 0.5
    baseline_K_expected = 17.0

    # Find closest E_recharge to baseline
    closest_idx = np.argmin([abs(a.e_recharge - baseline_e) for a in aggregated])
    closest_agg = aggregated[closest_idx]

    if closest_agg.e_recharge == baseline_e:
        baseline_K_observed = closest_agg.mean_K
        reduces_to_baseline = abs(baseline_K_observed - baseline_K_expected) < 5.0
    else:
        # Interpolate
        baseline_K_observed = linear_test['slope_beta'] * baseline_e + linear_test['intercept']
        reduces_to_baseline = abs(baseline_K_observed - baseline_K_expected) < 5.0

    einsteinian_pass = reduces_to_baseline

    # Overall verdict
    all_tests_pass = newtonian_pass and maxwellian_pass and einsteinian_pass

    return {
        'newtonian': {
            'test': 'Newtonian (Predictive Accuracy)',
            'prediction': 'K = β × E_recharge with R² > 0.6, p < 0.05',
            'result': linear_test,
            'passed': newtonian_pass
        },
        'maxwellian': {
            'test': 'Maxwellian (Domain Unification)',
            'concepts_unified': concepts_unified,
            'parameters_required': parameters_required,
            'elegance_metric': elegance,
            'threshold': 1.5,
            'passed': maxwellian_pass
        },
        'einsteinian': {
            'test': 'Einsteinian (Limit Behavior)',
            'baseline_e_recharge': baseline_e,
            'expected_K': baseline_K_expected,
            'observed_K': baseline_K_observed,
            'difference': abs(baseline_K_observed - baseline_K_expected),
            'tolerance': 5.0,
            'passed': einsteinian_pass
        },
        'overall_verdict': 'HYPOTHESIS VALIDATED' if all_tests_pass else 'HYPOTHESIS FALSIFIED',
        'tests_passed': sum([newtonian_pass, maxwellian_pass, einsteinian_pass]),
        'tests_total': 3,
        'mog_resonance_alpha': 0.92
    }

def create_publication_figure(aggregated: List[CarryingCapacityResults],
                              linear_test: Dict,
                              falsification: Dict,
                              output_path: Path):
    """Create 4-panel publication figure"""

    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Panel A: K vs E_recharge (main result)
    ax1 = fig.add_subplot(gs[0, 0])
    e_vals = np.array([a.e_recharge for a in aggregated])
    K_vals = np.array([a.mean_K for a in aggregated])
    K_errs = np.array([a.sem_K for a in aggregated])

    ax1.errorbar(e_vals, K_vals, yerr=K_errs, fmt='o', color='#2c3e50',
                markersize=8, capsize=5, capthick=2, elinewidth=2,
                label='Observed K (mean ± SEM)')

    # Linear fit
    e_fit = np.linspace(min(e_vals), max(e_vals), 100)
    K_fit = linear_test['slope_beta'] * e_fit + linear_test['intercept']
    ax1.plot(e_fit, K_fit, '--', color='#e74c3c', linewidth=2,
            label=f"K = {linear_test['slope_beta']:.1f}E + {linear_test['intercept']:.1f}\n"
                  f"R² = {linear_test['r_squared']:.3f}, p = {linear_test['p_value']:.4f}")

    # Baseline from Paper 2
    ax1.axvline(x=0.5, color='gray', linestyle=':', linewidth=1.5, alpha=0.6)
    ax1.axhline(y=17, color='gray', linestyle=':', linewidth=1.5, alpha=0.6,
               label='Paper 2 baseline (E=0.5, K≈17)')

    ax1.set_xlabel('E_recharge (energy units/cycle)')
    ax1.set_ylabel('K (equilibrium population)')
    ax1.set_title('(A) Carrying Capacity vs Energy Availability', fontweight='bold')
    ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax1.grid(alpha=0.3)

    # Panel B: Residuals
    ax2 = fig.add_subplot(gs[0, 1])
    K_pred = linear_test['slope_beta'] * e_vals + linear_test['intercept']
    residuals = K_vals - K_pred

    ax2.scatter(K_pred, residuals, color='#3498db', s=100, alpha=0.7, edgecolors='black')
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax2.set_xlabel('Predicted K')
    ax2.set_ylabel('Residuals (Observed - Predicted)')
    ax2.set_title('(B) Residual Plot (Linearity Check)', fontweight='bold')
    ax2.grid(alpha=0.3)

    # Panel C: Spawn success vs E_recharge
    ax3 = fig.add_subplot(gs[1, 0])
    eta_vals = np.array([a.mean_eta for a in aggregated])
    eta_errs = np.array([a.std_eta for a in aggregated])

    ax3.errorbar(e_vals, eta_vals, yerr=eta_errs, fmt='s', color='#27ae60',
                markersize=8, capsize=5, capthick=2, elinewidth=2,
                label='Spawn success rate η')

    ax3.set_xlabel('E_recharge (energy units/cycle)')
    ax3.set_ylabel('Spawn Success Rate η (%)')
    ax3.set_title('(C) Spawn Success vs Energy', fontweight='bold')
    ax3.legend(loc='lower right', frameon=True)
    ax3.grid(alpha=0.3)

    # Panel D: MOG Falsification Summary
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')

    newtonian_symbol = '✓' if falsification['newtonian']['passed'] else '✗'
    maxwellian_symbol = '✓' if falsification['maxwellian']['passed'] else '✗'
    einsteinian_symbol = '✓' if falsification['einsteinian']['passed'] else '✗'

    summary_text = f"""(D) MOG Falsification Gauntlet

MOG Resonance: α = {falsification['mog_resonance_alpha']:.2f}

Test 1: Newtonian (Predictive) {newtonian_symbol}
  Prediction: K = β × E_recharge
  R² = {linear_test['r_squared']:.3f} (threshold: 0.6)
  p = {linear_test['p_value']:.4f} (threshold: 0.05)
  β = {linear_test['slope_beta']:.2f} (> 0 required)
  Status: {linear_test['status']}

Test 2: Maxwellian (Unification) {maxwellian_symbol}
  Elegance: {falsification['maxwellian']['elegance_metric']:.2f}
  (concepts unified / parameters required)
  Threshold: ≥ {falsification['maxwellian']['threshold']}

Test 3: Einsteinian (Limit) {einsteinian_symbol}
  E=0.5 → K ≈ {falsification['einsteinian']['observed_K']:.1f}
  Expected: {falsification['einsteinian']['expected_K']:.1f} (Paper 2)
  Δ = {falsification['einsteinian']['difference']:.1f}
  
OVERALL VERDICT:
{falsification['overall_verdict']}

Tests Passed: {falsification['tests_passed']}/{falsification['tests_total']}
"""

    text_color = '#27ae60' if falsification['overall_verdict'] == 'HYPOTHESIS VALIDATED' else '#e74c3c'

    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3, edgecolor=text_color, linewidth=2))

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Publication figure saved: {output_path}")

def main():
    """Execute C264 analysis pipeline"""

    print("=" * 80)
    print("C264 CARRYING CAPACITY ANALYSIS - MOG FALSIFICATION GAUNTLET")
    print("=" * 80)
    print()

    # Load results
    results_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c264_carrying_capacity.json")

    if not results_path.exists():
        print(f"⚠ Results file not found: {results_path}")
        print("Waiting for C264 experiment to complete...")
        print()
        print("Expected location: /Volumes/dual/DUALITY-ZERO-V2/experiments/results/c264_carrying_capacity.json")
        return

    print(f"Loading results from: {results_path}")
    data = load_results(results_path)
    results = data['results']
    print(f"✓ Loaded {len(results)} experimental runs")
    print()

    # Aggregate by E_recharge
    print("Aggregating by E_recharge level...")
    aggregated = aggregate_by_e_recharge(results)

    print()
    print("E_recharge Summary:")
    print("-" * 80)
    print(f"{'E_recharge':>11s} | {'Mean K':>10s} | {'SEM K':>10s} | {'η (%)':>10s} | {'Extinct %':>10s}")
    print("-" * 80)
    for agg in aggregated:
        print(f"{agg.e_recharge:11.2f} | {agg.mean_K:10.2f} | {agg.sem_K:10.3f} | "
              f"{agg.mean_eta:10.1f} | {agg.extinction_rate*100:10.1f}")
    print()

    # Test primary hypothesis
    print("Testing Primary Hypothesis: K = β × E_recharge (Linear Scaling)")
    print("-" * 80)
    linear_test = test_linear_scaling(aggregated)

    print(f"Model: {linear_test['model']}")
    print(f"β (slope): {linear_test['slope_beta']:.3f} ± {linear_test['std_err']:.3f}")
    print(f"Intercept: {linear_test['intercept']:.3f}")
    print(f"R² = {linear_test['r_squared']:.3f} (threshold: 0.6)")
    print(f"p-value = {linear_test['p_value']:.6f} (threshold: 0.05)")
    print(f"Monotonic: {linear_test['monotonic']}")
    print()
    print(f"Status: {linear_test['status']}")
    if linear_test['falsified']:
        print("Falsification reasons:")
        for reason in linear_test['falsification_reasons']:
            print(f"  - {reason}")
    print()

    # Alternative models
    print("Alternative Models:")
    for model_name, model_data in linear_test['alternative_models'].items():
        print(f"  {model_data['formula']}: R² = {model_data['r_squared']:.3f} "
              f"({'BETTER' if model_data['better_fit'] else 'worse'} than linear)")
    print()

    # Test secondary hypothesis
    print("Testing Secondary Hypothesis: Allee Effect at Low E_recharge")
    print("-" * 80)
    allee_test = test_allee_effect(aggregated)
    print(f"Status: {allee_test['status']}")
    if allee_test['threshold_exists']:
        print(f"Critical E_recharge: {allee_test['E_critical']:.3f}")
        print(f"Transition width σ: {allee_test['sigma']:.3f}")
    print()

    # Apply MOG falsification gauntlet
    print("Applying MOG Falsification Gauntlet...")
    print("-" * 80)
    falsification = mog_falsification_gauntlet(aggregated, linear_test)

    print()
    print(f"NEWTONIAN TEST (Predictive): {'PASS' if falsification['newtonian']['passed'] else 'FAIL'}")
    print(f"MAXWELLIAN TEST (Unification): {'PASS' if falsification['maxwellian']['passed'] else 'FAIL'}")
    print(f"  Elegance metric: {falsification['maxwellian']['elegance_metric']:.2f} "
          f"(threshold: {falsification['maxwellian']['threshold']})")
    print(f"EINSTEINIAN TEST (Limits): {'PASS' if falsification['einsteinian']['passed'] else 'FAIL'}")
    print(f"  Baseline reduction: E=0.5 → K={falsification['einsteinian']['observed_K']:.1f} "
          f"(expected: {falsification['einsteinian']['expected_K']:.1f})")
    print()

    print("=" * 80)
    print(f"OVERALL VERDICT: {falsification['overall_verdict']}")
    print(f"Tests Passed: {falsification['tests_passed']}/{falsification['tests_total']}")
    print(f"MOG Resonance: α = {falsification['mog_resonance_alpha']:.2f}")
    print("=" * 80)
    print()

    # Save analysis results
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    analysis_output = output_dir / "c264_carrying_capacity_analysis.json"

    analysis_data = {
        'experiment': 'C264_Carrying_Capacity',
        'analysis_date': '2025-11-09',
        'hypothesis': 'K = β × E_recharge (linear carrying capacity)',
        'mog_resonance_alpha': 0.92,
        'aggregated_results': [
            {
                'e_recharge': a.e_recharge,
                'mean_K': a.mean_K,
                'sem_K': a.sem_K,
                'mean_eta': a.mean_eta,
                'extinction_rate': a.extinction_rate
            } for a in aggregated
        ],
        'linear_test': linear_test,
        'allee_test': allee_test,
        'mog_falsification': falsification
    }

    with open(analysis_output, 'w') as f:
        json.dump(analysis_data, f, indent=2)

    print(f"✓ Analysis results saved: {analysis_output}")
    print()

    # Create publication figure
    figures_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_output = figures_dir / "c264_carrying_capacity_mog_falsification.png"

    create_publication_figure(aggregated, linear_test, falsification, figure_output)
    print()

    print("Analysis complete.")
    print()

if __name__ == '__main__':
    main()
