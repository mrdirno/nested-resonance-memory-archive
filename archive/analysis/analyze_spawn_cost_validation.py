#!/usr/bin/env python3
"""
Spawn Cost Scaling Validation Analysis

Analyzes 40-experiment campaign testing buffer factor k ≈ 95 universality hypothesis.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (Anthropic)
Date: November 18, 2025
License: GPL-3.0
"""

import json
import glob
import numpy as np
from pathlib import Path
from scipy import stats
import matplotlib.pyplot as plt

# Analysis configuration
RESULTS_DIR = Path('/Volumes/dual/DUALITY-ZERO-V2/experiments/results')
OUTPUT_DIR = Path('/Volumes/dual/DUALITY-ZERO-V2/analysis/spawn_cost_validation')
OUTPUT_DIR.mkdir(exist_ok=True)

def load_all_results():
    """Load all 40 spawn_cost validation experiment results."""
    pattern = str(RESULTS_DIR / 'c186_spawn_cost_SPAWN_COST_*.json')
    json_files = glob.glob(pattern)

    results = []
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)
            results.append(data)

    return results

def extract_metrics(results):
    """Extract key metrics from experiment results."""
    data = []

    for result in results:
        spawn_cost = result['parameters']['spawn_cost']
        seed = result['seed']

        # Final state
        final_pop = result['results']['final_population']
        final_energy = result['results']['final_energy']

        # Calculate E_min (energy per agent at final state)
        e_min = final_energy / final_pop if final_pop > 0 else np.nan

        # Calculate buffer factor k
        k = e_min / spawn_cost if spawn_cost > 0 else np.nan

        # Check if completed or terminated early
        runtime = result['results']['runtime_seconds']

        data.append({
            'spawn_cost': spawn_cost,
            'seed': seed,
            'final_population': final_pop,
            'final_energy': final_energy,
            'e_min': e_min,
            'k': k,
            'runtime_seconds': runtime,
            'success': result['results']['success']
        })

    return data

def statistical_analysis(data):
    """Perform statistical validation of k universality hypothesis."""
    # Convert to numpy arrays
    spawn_costs = np.array([d['spawn_cost'] for d in data])
    e_min_values = np.array([d['e_min'] for d in data])
    k_values = np.array([d['k'] for d in data])

    # Remove any NaN values
    valid_idx = ~np.isnan(k_values)
    k_values = k_values[valid_idx]
    spawn_costs_valid = spawn_costs[valid_idx]
    e_min_values_valid = e_min_values[valid_idx]

    # Overall statistics on k
    k_mean = np.mean(k_values)
    k_std = np.std(k_values, ddof=1)
    k_cv = k_std / k_mean  # Coefficient of variation
    k_sem = k_std / np.sqrt(len(k_values))  # Standard error of mean

    # By spawn_cost group
    unique_spawn_costs = np.unique(spawn_costs_valid)
    k_by_spawn_cost = {}

    for sc in unique_spawn_costs:
        mask = spawn_costs_valid == sc
        k_group = k_values[mask]
        k_by_spawn_cost[sc] = {
            'mean': np.mean(k_group),
            'std': np.std(k_group, ddof=1),
            'n': len(k_group)
        }

    # Linear regression: E_min vs spawn_cost
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        spawn_costs_valid, e_min_values_valid
    )
    r_squared = r_value ** 2

    # Test if slope ≈ k_mean
    slope_matches_k = np.abs(slope - k_mean) / k_mean < 0.05  # Within 5%

    # ANOVA: Test if k differs significantly across spawn_cost groups
    k_groups = [k_values[spawn_costs_valid == sc] for sc in unique_spawn_costs]
    f_stat, anova_p = stats.f_oneway(*k_groups)

    return {
        'k_mean': k_mean,
        'k_std': k_std,
        'k_cv': k_cv,
        'k_sem': k_sem,
        'k_min': np.min(k_values),
        'k_max': np.max(k_values),
        'k_median': np.median(k_values),
        'k_by_spawn_cost': k_by_spawn_cost,
        'linear_regression': {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'p_value': p_value,
            'std_err': std_err
        },
        'anova': {
            'f_statistic': f_stat,
            'p_value': anova_p
        },
        'n_experiments': len(k_values),
        'slope_matches_k': slope_matches_k
    }

def hypothesis_test(stats_dict):
    """Test k ≈ 95 universality hypothesis."""
    k_mean = stats_dict['k_mean']
    k_cv = stats_dict['k_cv']
    r_squared = stats_dict['linear_regression']['r_squared']
    anova_p = stats_dict['anova']['p_value']

    # Hypothesis tests
    tests = {
        'cv_test': {
            'criterion': 'CV(k) < 0.10',
            'value': k_cv,
            'passed': k_cv < 0.10,
            'description': 'Low variation across conditions'
        },
        'r_squared_test': {
            'criterion': 'R² > 0.99',
            'value': r_squared,
            'passed': r_squared > 0.99,
            'description': 'Strong linear E_min vs spawn_cost'
        },
        'range_test': {
            'criterion': '85 < k < 105',
            'value': k_mean,
            'passed': 85 < k_mean < 105,
            'description': 'k near expected value ~95'
        },
        'anova_test': {
            'criterion': 'p > 0.05',
            'value': anova_p,
            'passed': anova_p > 0.05,
            'description': 'No significant k difference across spawn_costs'
        }
    }

    # Overall validation
    all_passed = all(t['passed'] for t in tests.values())

    return {
        'tests': tests,
        'validated': all_passed,
        'verdict': 'VALIDATED' if all_passed else 'PARTIAL' if sum(t['passed'] for t in tests.values()) >= 3 else 'FALSIFIED'
    }

def create_visualizations(data, stats_dict, output_dir):
    """Create publication-quality figures."""
    spawn_costs = np.array([d['spawn_cost'] for d in data])
    e_min_values = np.array([d['e_min'] for d in data])
    k_values = np.array([d['k'] for d in data])

    # Remove NaN
    valid_idx = ~np.isnan(k_values)
    spawn_costs = spawn_costs[valid_idx]
    e_min_values = e_min_values[valid_idx]
    k_values = k_values[valid_idx]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. E_min vs spawn_cost scatter with linear fit
    ax = axes[0, 0]
    for sc in np.unique(spawn_costs):
        mask = spawn_costs == sc
        ax.scatter(spawn_costs[mask], e_min_values[mask],
                  alpha=0.6, s=80, label=f'spawn_cost={sc}')

    # Linear fit
    slope = stats_dict['linear_regression']['slope']
    intercept = stats_dict['linear_regression']['intercept']
    r_squared = stats_dict['linear_regression']['r_squared']

    x_fit = np.array([2.5, 10.0])
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, 'k--', linewidth=2,
            label=f'Linear fit: R²={r_squared:.4f}')

    ax.set_xlabel('spawn_cost', fontsize=12)
    ax.set_ylabel('E_min (energy/agent)', fontsize=12)
    ax.set_title('E_min vs spawn_cost Scaling', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. k distribution histogram
    ax = axes[0, 1]
    ax.hist(k_values, bins=20, alpha=0.7, edgecolor='black')
    ax.axvline(stats_dict['k_mean'], color='red', linestyle='--',
               linewidth=2, label=f"Mean k={stats_dict['k_mean']:.2f}")
    ax.axvline(95, color='green', linestyle=':', linewidth=2,
               label='Predicted k=95')
    ax.set_xlabel('Buffer factor k', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f"k Distribution (CV={stats_dict['k_cv']:.4f})",
                fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 3. k by spawn_cost boxplot
    ax = axes[1, 0]
    k_by_spawn_cost = {}
    for sc in np.unique(spawn_costs):
        k_by_spawn_cost[sc] = k_values[spawn_costs == sc]

    ax.boxplot(k_by_spawn_cost.values(), labels=[f'{sc}' for sc in k_by_spawn_cost.keys()])
    ax.axhline(stats_dict['k_mean'], color='red', linestyle='--',
               linewidth=2, label=f"Overall mean={stats_dict['k_mean']:.2f}")
    ax.axhline(95, color='green', linestyle=':', linewidth=2, label='Predicted=95')
    ax.set_xlabel('spawn_cost', fontsize=12)
    ax.set_ylabel('Buffer factor k', fontsize=12)
    ax.set_title('k Variation Across spawn_cost Values', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Population trajectories (if data available)
    ax = axes[1, 1]
    final_pops = [d['final_population'] for d in data]
    spawn_cost_labels = [d['spawn_cost'] for d in data]

    for sc in np.unique(spawn_costs):
        mask = np.array(spawn_cost_labels) == sc
        pops = np.array(final_pops)[mask]
        ax.scatter([sc]*len(pops), pops, alpha=0.6, s=80, label=f'spawn_cost={sc}')

    ax.set_xlabel('spawn_cost', fontsize=12)
    ax.set_ylabel('Final Population', fontsize=12)
    ax.set_title('Final Population by spawn_cost', fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'spawn_cost_validation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_dir / 'spawn_cost_validation_analysis.png'}")
    plt.close()

def generate_report(data, stats_dict, hypothesis_result, output_dir):
    """Generate markdown analysis report."""
    report = f"""# Spawn Cost Scaling Validation Analysis

**Date:** November 18, 2025
**Experiments:** 40 (4 spawn_cost values × 10 seeds)
**Hypothesis:** Buffer factor k ≈ 95 is universal across spawn_cost values

---

## EXECUTIVE SUMMARY

**Verdict:** {hypothesis_result['verdict']}

**Key Findings:**
- Buffer factor k = {stats_dict['k_mean']:.2f} ± {stats_dict['k_std']:.2f}
- Coefficient of variation: CV = {stats_dict['k_cv']:.4f} ({stats_dict['k_cv']*100:.2f}%)
- Linear scaling: R² = {stats_dict['linear_regression']['r_squared']:.6f}
- ANOVA p-value: {stats_dict['anova']['p_value']:.6f}

---

## STATISTICAL RESULTS

### Overall k Statistics

| Metric | Value |
|--------|-------|
| Mean | {stats_dict['k_mean']:.4f} |
| Std Dev | {stats_dict['k_std']:.4f} |
| CV | {stats_dict['k_cv']:.4f} |
| SEM | {stats_dict['k_sem']:.4f} |
| Min | {stats_dict['k_min']:.4f} |
| Max | {stats_dict['k_max']:.4f} |
| Median | {stats_dict['k_median']:.4f} |
| N | {stats_dict['n_experiments']} |

### k by spawn_cost Group

| spawn_cost | Mean k | Std Dev | N |
|------------|--------|---------|---|
"""

    for sc in sorted(stats_dict['k_by_spawn_cost'].keys()):
        group = stats_dict['k_by_spawn_cost'][sc]
        report += f"| {sc} | {group['mean']:.4f} | {group['std']:.4f} | {group['n']} |\n"

    report += f"""
### Linear Regression (E_min vs spawn_cost)

- **Slope:** {stats_dict['linear_regression']['slope']:.4f}
- **Intercept:** {stats_dict['linear_regression']['intercept']:.4f}
- **R²:** {stats_dict['linear_regression']['r_squared']:.6f}
- **p-value:** {stats_dict['linear_regression']['p_value']:.2e}
- **Std Error:** {stats_dict['linear_regression']['std_err']:.4f}

### ANOVA (k across spawn_cost groups)

- **F-statistic:** {stats_dict['anova']['f_statistic']:.4f}
- **p-value:** {stats_dict['anova']['p_value']:.6f}

---

## HYPOTHESIS TESTS

"""

    for test_name, test in hypothesis_result['tests'].items():
        status = "✅ PASS" if test['passed'] else "❌ FAIL"
        report += f"### {test_name.upper()}\n\n"
        report += f"**Criterion:** {test['criterion']}\n"
        report += f"**Value:** {test['value']:.6f}\n"
        report += f"**Status:** {status}\n"
        report += f"**Description:** {test['description']}\n\n"

    report += f"""---

## RAW DATA SUMMARY

"""

    for i, d in enumerate(data):
        if i % 10 == 0:  # Show every 10th entry
            report += f"- spawn_cost={d['spawn_cost']}, seed={d['seed']}: "
            report += f"E_min={d['e_min']:.2f}, k={d['k']:.2f}, "
            report += f"pop={d['final_population']}, success={d['success']}\n"

    report += "\n---\n\n**Analysis complete.**\n"

    # Save report
    report_path = output_dir / 'analysis_report.md'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Report saved: {report_path}")
    return report

def main():
    """Main analysis pipeline."""
    print("="*80)
    print("SPAWN COST SCALING VALIDATION ANALYSIS")
    print("="*80)
    print()

    # Load results
    print("Loading experiment results...")
    results = load_all_results()
    print(f"Loaded {len(results)} experiment results")
    print()

    # Extract metrics
    print("Extracting metrics...")
    data = extract_metrics(results)
    print(f"Extracted metrics for {len(data)} experiments")
    print()

    # Statistical analysis
    print("Performing statistical analysis...")
    stats_dict = statistical_analysis(data)
    print(f"k_mean = {stats_dict['k_mean']:.4f} ± {stats_dict['k_std']:.4f}")
    print(f"CV(k) = {stats_dict['k_cv']:.4f}")
    print(f"R² = {stats_dict['linear_regression']['r_squared']:.6f}")
    print()

    # Hypothesis testing
    print("Testing hypothesis...")
    hypothesis_result = hypothesis_test(stats_dict)
    print(f"Verdict: {hypothesis_result['verdict']}")
    print()

    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(data, stats_dict, OUTPUT_DIR)
    print()

    # Generate report
    print("Generating report...")
    report = generate_report(data, stats_dict, hypothesis_result, OUTPUT_DIR)
    print()

    # Save structured results
    results_dict = {
        'data': data,
        'statistics': {k: v for k, v in stats_dict.items() if k != 'k_by_spawn_cost'},
        'k_by_spawn_cost': {str(k): v for k, v in stats_dict['k_by_spawn_cost'].items()},
        'hypothesis_test': hypothesis_result
    }

    results_path = OUTPUT_DIR / 'analysis_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"Results saved: {results_path}")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return hypothesis_result

if __name__ == '__main__':
    result = main()
