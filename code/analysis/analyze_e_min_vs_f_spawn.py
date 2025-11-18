#!/usr/bin/env python3
"""
E_min vs f_spawn Universality Analysis

Tests whether E_min ≈ 502.5 is universal across spawn frequencies or specific to f_spawn=0.005.

Combines data from:
- V6b campaign: 50 experiments (5 f_spawn values × 10 seeds) at spawn_cost=5.0
- V6c campaign: 50 experiments (5 f_spawn values × 10 seeds) at spawn_cost=7.5
- spawn_cost campaign: 40 experiments (4 spawn_cost values × 10 seeds) at f_spawn=0.005

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
OUTPUT_DIR = Path('/Volumes/dual/DUALITY-ZERO-V2/analysis/e_min_universality')
OUTPUT_DIR.mkdir(exist_ok=True)

def load_v6b_results():
    """Load V6b campaign results (spawn_cost=5.0, varying f_spawn)."""
    pattern = str(RESULTS_DIR / 'c186_v6b_*.json')
    json_files = glob.glob(pattern)

    results = []
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)

            # Extract f_spawn from parameters
            f_spawn = data['parameters']['f_spawn']
            spawn_cost = 5.0  # V6b constant

            final_pop = data['results']['final_population']
            final_energy = data['results']['final_energy']

            e_min = final_energy / final_pop if final_pop > 0 else np.nan
            k = e_min / spawn_cost if spawn_cost > 0 else np.nan

            results.append({
                'campaign': 'v6b',
                'f_spawn': f_spawn,
                'spawn_cost': spawn_cost,
                'final_population': final_pop,
                'final_energy': final_energy,
                'e_min': e_min,
                'k': k,
                'seed': data['seed']
            })

    return results

def load_v6c_results():
    """Load V6c campaign results (spawn_cost=7.5, varying f_spawn)."""
    pattern = str(RESULTS_DIR / 'c186_v6c_*.json')
    json_files = glob.glob(pattern)

    results = []
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)

            # V6c parameters (need to infer f_spawn from condition name if not in params)
            # Assuming same structure as V6b
            f_spawn = data['parameters'].get('f_spawn', np.nan)
            spawn_cost = 7.5  # V6c constant

            final_pop = data['results']['final_population']
            final_energy = data['results']['final_energy']

            e_min = final_energy / final_pop if final_pop > 0 else np.nan
            k = e_min / spawn_cost if spawn_cost > 0 else np.nan

            results.append({
                'campaign': 'v6c',
                'f_spawn': f_spawn,
                'spawn_cost': spawn_cost,
                'final_population': final_pop,
                'final_energy': final_energy,
                'e_min': e_min,
                'k': k,
                'seed': data['seed']
            })

    return results

def load_spawn_cost_results():
    """Load spawn_cost campaign results (f_spawn=0.005, varying spawn_cost)."""
    pattern = str(RESULTS_DIR / 'c186_spawn_cost_*.json')
    json_files = glob.glob(pattern)

    results = []
    for json_file in sorted(json_files):
        with open(json_file, 'r') as f:
            data = json.load(f)

            f_spawn = 0.005  # spawn_cost campaign constant
            spawn_cost = data['parameters']['spawn_cost']

            final_pop = data['results']['final_population']
            final_energy = data['results']['final_energy']

            e_min = final_energy / final_pop if final_pop > 0 else np.nan
            k = e_min / spawn_cost if spawn_cost > 0 else np.nan

            results.append({
                'campaign': 'spawn_cost',
                'f_spawn': f_spawn,
                'spawn_cost': spawn_cost,
                'final_population': final_pop,
                'final_energy': final_energy,
                'e_min': e_min,
                'k': k,
                'seed': data['seed']
            })

    return results

def combined_analysis(v6b_results, v6c_results, spawn_cost_results):
    """Analyze E_min universality across all campaigns."""

    all_results = v6b_results + v6c_results + spawn_cost_results

    # Convert to arrays
    f_spawn_vals = np.array([r['f_spawn'] for r in all_results])
    spawn_cost_vals = np.array([r['spawn_cost'] for r in all_results])
    e_min_vals = np.array([r['e_min'] for r in all_results])

    # Remove NaN
    valid_idx = ~np.isnan(e_min_vals) & ~np.isnan(f_spawn_vals)
    f_spawn_vals = f_spawn_vals[valid_idx]
    spawn_cost_vals = spawn_cost_vals[valid_idx]
    e_min_vals = e_min_vals[valid_idx]

    # Overall E_min statistics
    e_min_mean = np.mean(e_min_vals)
    e_min_std = np.std(e_min_vals, ddof=1)
    e_min_cv = e_min_std / e_min_mean

    # E_min by f_spawn
    unique_f_spawn = np.unique(f_spawn_vals)
    e_min_by_f_spawn = {}

    for fs in unique_f_spawn:
        mask = f_spawn_vals == fs
        e_group = e_min_vals[mask]
        e_min_by_f_spawn[fs] = {
            'mean': np.mean(e_group),
            'std': np.std(e_group, ddof=1),
            'n': len(e_group),
            'min': np.min(e_group),
            'max': np.max(e_group)
        }

    # E_min by spawn_cost (at f_spawn=0.005)
    mask_005 = f_spawn_vals == 0.005
    e_min_at_005 = e_min_vals[mask_005]
    spawn_cost_at_005 = spawn_cost_vals[mask_005]

    # Test independence from f_spawn
    # ANOVA: Does E_min differ significantly across f_spawn values?
    e_groups_by_f = [e_min_vals[f_spawn_vals == fs] for fs in unique_f_spawn]
    f_stat_f, p_f = stats.f_oneway(*e_groups_by_f)

    # Correlation with f_spawn
    corr_f, p_corr_f = stats.pearsonr(f_spawn_vals, e_min_vals)

    return {
        'e_min_overall': {
            'mean': e_min_mean,
            'std': e_min_std,
            'cv': e_min_cv,
            'min': np.min(e_min_vals),
            'max': np.max(e_min_vals),
            'n': len(e_min_vals)
        },
        'e_min_by_f_spawn': e_min_by_f_spawn,
        'anova_f_spawn': {
            'f_statistic': f_stat_f,
            'p_value': p_f,
            'interpretation': 'E_min VARIES with f_spawn' if p_f < 0.05 else 'E_min INDEPENDENT of f_spawn'
        },
        'correlation_f_spawn': {
            'r': corr_f,
            'p_value': p_corr_f,
            'r_squared': corr_f ** 2
        }
    }

def hypothesis_test(stats_dict):
    """Test E_min universality hypothesis."""

    e_min_cv = stats_dict['e_min_overall']['cv']
    anova_p = stats_dict['anova_f_spawn']['p_value']

    # Hypothesis: E_min universal (independent of f_spawn)
    tests = {
        'cv_test': {
            'criterion': 'CV(E_min) < 0.10',
            'value': e_min_cv,
            'passed': e_min_cv < 0.10,
            'description': 'Low variation in E_min overall'
        },
        'anova_test': {
            'criterion': 'ANOVA p > 0.05',
            'value': anova_p,
            'passed': anova_p > 0.05,
            'description': 'E_min does not vary significantly with f_spawn'
        },
        'range_test': {
            'criterion': '495 < E_min < 510',
            'value': stats_dict['e_min_overall']['mean'],
            'passed': 495 < stats_dict['e_min_overall']['mean'] < 510,
            'description': 'E_min near predicted value ~502.5'
        }
    }

    all_passed = all(t['passed'] for t in tests.values())

    return {
        'tests': tests,
        'validated': all_passed,
        'verdict': 'VALIDATED' if all_passed else 'PARTIAL' if sum(t['passed'] for t in tests.values()) >= 2 else 'FALSIFIED'
    }

def create_visualizations(v6b_results, v6c_results, spawn_cost_results, stats_dict, output_dir):
    """Create publication-quality figures."""

    all_results = v6b_results + v6c_results + spawn_cost_results

    f_spawn_vals = np.array([r['f_spawn'] for r in all_results])
    spawn_cost_vals = np.array([r['spawn_cost'] for r in all_results])
    e_min_vals = np.array([r['e_min'] for r in all_results])
    campaigns = [r['campaign'] for r in all_results]

    # Remove NaN
    valid_idx = ~np.isnan(e_min_vals) & ~np.isnan(f_spawn_vals)
    f_spawn_vals = f_spawn_vals[valid_idx]
    spawn_cost_vals = spawn_cost_vals[valid_idx]
    e_min_vals = e_min_vals[valid_idx]
    campaigns = [campaigns[i] for i, v in enumerate(valid_idx) if v]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. E_min vs f_spawn (all campaigns)
    ax = axes[0, 0]

    # Separate by campaign
    for campaign in ['v6b', 'v6c', 'spawn_cost']:
        mask = np.array([c == campaign for c in campaigns])
        ax.scatter(f_spawn_vals[mask], e_min_vals[mask],
                  alpha=0.6, s=80, label=campaign.upper())

    ax.axhline(stats_dict['e_min_overall']['mean'], color='red', linestyle='--',
               linewidth=2, label=f"Overall mean={stats_dict['e_min_overall']['mean']:.2f}")
    ax.axhline(502.5, color='green', linestyle=':', linewidth=2,
               label='Cycle 1397 prediction=502.5')

    ax.set_xlabel('f_spawn (spawn frequency)', fontsize=12)
    ax.set_ylabel('E_min (energy/agent)', fontsize=12)
    ax.set_title('E_min vs f_spawn (All Campaigns)', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. E_min distribution by f_spawn
    ax = axes[0, 1]

    unique_f_spawn = sorted(np.unique(f_spawn_vals))
    e_by_f = {fs: e_min_vals[f_spawn_vals == fs] for fs in unique_f_spawn}

    bp = ax.boxplot(e_by_f.values(), labels=[f'{fs:.4f}' for fs in e_by_f.keys()])
    ax.axhline(stats_dict['e_min_overall']['mean'], color='red', linestyle='--',
               linewidth=2, label=f"Mean={stats_dict['e_min_overall']['mean']:.2f}")

    ax.set_xlabel('f_spawn', fontsize=12)
    ax.set_ylabel('E_min (energy/agent)', fontsize=12)
    ax.set_title(f"E_min Distribution by f_spawn (CV={stats_dict['e_min_overall']['cv']:.4f})",
                fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 3. E_min histogram (all data)
    ax = axes[1, 0]

    ax.hist(e_min_vals, bins=30, alpha=0.7, edgecolor='black')
    ax.axvline(stats_dict['e_min_overall']['mean'], color='red', linestyle='--',
               linewidth=2, label=f"Mean={stats_dict['e_min_overall']['mean']:.2f}")
    ax.axvline(502.5, color='green', linestyle=':', linewidth=2,
               label='Predicted=502.5')

    ax.set_xlabel('E_min (energy/agent)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f"E_min Distribution (N={len(e_min_vals)})", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 4. E_min by spawn_cost (at f_spawn=0.005)
    ax = axes[1, 1]

    mask_005 = f_spawn_vals == 0.005
    e_at_005 = e_min_vals[mask_005]
    sc_at_005 = spawn_cost_vals[mask_005]

    unique_sc = sorted(np.unique(sc_at_005))
    for sc in unique_sc:
        mask_sc = sc_at_005 == sc
        ax.scatter([sc]*sum(mask_sc), e_at_005[mask_sc],
                  alpha=0.6, s=80, label=f'spawn_cost={sc}')

    ax.axhline(stats_dict['e_min_overall']['mean'], color='red', linestyle='--',
               linewidth=2, label=f"Overall mean={stats_dict['e_min_overall']['mean']:.2f}")

    ax.set_xlabel('spawn_cost', fontsize=12)
    ax.set_ylabel('E_min (energy/agent)', fontsize=12)
    ax.set_title('E_min vs spawn_cost (f_spawn=0.005)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'e_min_universality_analysis.png', dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_dir / 'e_min_universality_analysis.png'}")
    plt.close()

def generate_report(v6b_results, v6c_results, spawn_cost_results, stats_dict, hypothesis_result, output_dir):
    """Generate markdown analysis report."""

    n_total = len(v6b_results) + len(v6c_results) + len(spawn_cost_results)

    report = f"""# E_min Universality Analysis (Across f_spawn and spawn_cost)

**Date:** November 18, 2025
**Total Experiments:** {n_total} ({len(v6b_results)} V6b + {len(v6c_results)} V6c + {len(spawn_cost_results)} spawn_cost)
**Hypothesis:** E_min ≈ 502.5 units is universal across f_spawn and spawn_cost

---

## EXECUTIVE SUMMARY

**Verdict:** {hypothesis_result['verdict']}

**Key Findings:**
- E_min overall = {stats_dict['e_min_overall']['mean']:.2f} ± {stats_dict['e_min_overall']['std']:.2f} units
- Coefficient of variation: CV = {stats_dict['e_min_overall']['cv']:.4f} ({stats_dict['e_min_overall']['cv']*100:.2f}%)
- ANOVA (E_min vs f_spawn): p = {stats_dict['anova_f_spawn']['p_value']:.6f}
- {stats_dict['anova_f_spawn']['interpretation']}
- Correlation with f_spawn: r = {stats_dict['correlation_f_spawn']['r']:.4f}, R² = {stats_dict['correlation_f_spawn']['r_squared']:.4f}

---

## CAMPAIGN SUMMARIES

### V6b Campaign (spawn_cost=5.0, varying f_spawn)
- Experiments: {len(v6b_results)}
- f_spawn values tested: 5 (0.10%, 0.25%, 0.50%, 0.75%, 1.00%)
- Seeds: 10 per condition

### V6c Campaign (spawn_cost=7.5, varying f_spawn)
- Experiments: {len(v6c_results)}
- f_spawn values tested: 5 (0.10%, 0.25%, 0.50%, 0.75%, 1.00%)
- Seeds: 10 per condition

### Spawn Cost Campaign (f_spawn=0.005, varying spawn_cost)
- Experiments: {len(spawn_cost_results)}
- spawn_cost values tested: 4 (2.5, 5.0, 7.5, 10.0)
- Seeds: 10 per condition

---

## STATISTICAL RESULTS

### Overall E_min Statistics (All {stats_dict['e_min_overall']['n']} experiments)

| Metric | Value |
|--------|-------|
| Mean | {stats_dict['e_min_overall']['mean']:.4f} |
| Std Dev | {stats_dict['e_min_overall']['std']:.4f} |
| CV | {stats_dict['e_min_overall']['cv']:.4f} |
| Min | {stats_dict['e_min_overall']['min']:.4f} |
| Max | {stats_dict['e_min_overall']['max']:.4f} |

### E_min by f_spawn

| f_spawn | Mean E_min | Std Dev | Min | Max | N |
|---------|------------|---------|-----|-----|---|
"""

    for fs in sorted(stats_dict['e_min_by_f_spawn'].keys()):
        group = stats_dict['e_min_by_f_spawn'][fs]
        report += f"| {fs:.5f} | {group['mean']:.4f} | {group['std']:.4f} | {group['min']:.4f} | {group['max']:.4f} | {group['n']} |\n"

    report += f"""
### Statistical Tests

**ANOVA (E_min across f_spawn groups):**
- F-statistic: {stats_dict['anova_f_spawn']['f_statistic']:.4f}
- p-value: {stats_dict['anova_f_spawn']['p_value']:.6f}
- Interpretation: {stats_dict['anova_f_spawn']['interpretation']}

**Correlation (E_min vs f_spawn):**
- Pearson r: {stats_dict['correlation_f_spawn']['r']:.4f}
- R²: {stats_dict['correlation_f_spawn']['r_squared']:.4f}
- p-value: {stats_dict['correlation_f_spawn']['p_value']:.2e}

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

    report += """---

**Analysis complete.**
"""

    # Save report
    report_path = output_dir / 'e_min_universality_report.md'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"Report saved: {report_path}")
    return report

def main():
    """Main analysis pipeline."""
    print("="*80)
    print("E_MIN UNIVERSALITY ANALYSIS")
    print("="*80)
    print()

    # Load all campaigns
    print("Loading V6b campaign results...")
    v6b_results = load_v6b_results()
    print(f"Loaded {len(v6b_results)} V6b experiments")

    print("Loading V6c campaign results...")
    v6c_results = load_v6c_results()
    print(f"Loaded {len(v6c_results)} V6c experiments")

    print("Loading spawn_cost campaign results...")
    spawn_cost_results = load_spawn_cost_results()
    print(f"Loaded {len(spawn_cost_results)} spawn_cost experiments")
    print()

    # Combined analysis
    print("Performing combined analysis...")
    stats_dict = combined_analysis(v6b_results, v6c_results, spawn_cost_results)
    print(f"E_min overall = {stats_dict['e_min_overall']['mean']:.4f} ± {stats_dict['e_min_overall']['std']:.4f}")
    print(f"CV(E_min) = {stats_dict['e_min_overall']['cv']:.4f}")
    print(f"ANOVA p-value = {stats_dict['anova_f_spawn']['p_value']:.6f}")
    print()

    # Hypothesis testing
    print("Testing E_min universality hypothesis...")
    hypothesis_result = hypothesis_test(stats_dict)
    print(f"Verdict: {hypothesis_result['verdict']}")
    print()

    # Visualizations
    print("Creating visualizations...")
    create_visualizations(v6b_results, v6c_results, spawn_cost_results, stats_dict, OUTPUT_DIR)
    print()

    # Report
    print("Generating report...")
    report = generate_report(v6b_results, v6c_results, spawn_cost_results, stats_dict, hypothesis_result, OUTPUT_DIR)
    print()

    # Save structured results
    results_dict = {
        'statistics': stats_dict,
        'hypothesis_test': hypothesis_result,
        'n_experiments': {
            'v6b': len(v6b_results),
            'v6c': len(v6c_results),
            'spawn_cost': len(spawn_cost_results),
            'total': len(v6b_results) + len(v6c_results) + len(spawn_cost_results)
        }
    }

    results_path = OUTPUT_DIR / 'e_min_universality_results.json'
    with open(results_path, 'w') as f:
        json.dump(results_dict, f, indent=2, default=str)
    print(f"Results saved: {results_path}")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return hypothesis_result

if __name__ == '__main__':
    result = main()
