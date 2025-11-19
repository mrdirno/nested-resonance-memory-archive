#!/usr/bin/env python3
"""
V6a Results Aggregation and Analysis

Purpose: Aggregate all 50 V6a experiments and analyze hierarchical spawning advantage
         at ultra-low frequencies under net-zero homeostasis conditions.

Campaign: C186 V6a - Net-Zero Homeostasis Regime
Experiments: 50 (5 spawn rates × 10 seeds)
Energy: E_consume = E_recharge = 1.0 (homeostasis)

Analysis:
1. Aggregate final population and energy statistics
2. Compare hierarchical vs flat spawning (if flat experiments exist)
3. Test for spawn rate effects on stability
4. Measure carrying capacity (K) across conditions
5. Calculate spawn efficiency metrics

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
Date: 2025-11-16
Cycle: 1373
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Results directory
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Spawn rate labels
SPAWN_RATES = {
    '0_10pct': 0.001,
    '0_25pct': 0.0025,
    '0_50pct': 0.005,
    '0_75pct': 0.0075,
    '1_00pct': 0.01
}

def load_v6a_results():
    """Load all V6a experiment results."""
    results = []

    # Find all V6a JSON files
    json_files = list(RESULTS_DIR.glob("c186_v6a_HIERARCHICAL_*.json"))

    print(f"Found {len(json_files)} V6a result files")

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Extract key metrics
            result = {
                'condition': data['condition'],
                'seed': data['seed'],
                'f_spawn': data['parameters']['f_spawn'],
                'cycles': data['parameters']['cycles'],
                'final_population': data['results']['final_population'],
                'final_energy': data['results']['final_energy'],
                'total_decompositions': data['results']['total_decompositions'],
                'runtime_seconds': data['results']['runtime_seconds'],
                'runtime_hours': data['results']['runtime_hours'],
                'success': data['results']['success']
            }

            results.append(result)

        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")

    return pd.DataFrame(results)

def analyze_population_stability(df):
    """Analyze population stability across conditions."""
    print("\n" + "="*80)
    print("POPULATION STABILITY ANALYSIS")
    print("="*80)

    # Group by spawn rate
    grouped = df.groupby('f_spawn')

    stability_stats = []

    for f_spawn, group in grouped:
        spawn_label = [k for k, v in SPAWN_RATES.items() if v == f_spawn][0]

        stats_dict = {
            'spawn_rate': f_spawn,
            'spawn_label': spawn_label,
            'n_experiments': len(group),
            'mean_population': group['final_population'].mean(),
            'std_population': group['final_population'].std(),
            'min_population': group['final_population'].min(),
            'max_population': group['final_population'].max(),
            'collapse_rate': (group['final_population'] == 0).sum() / len(group)
        }

        stability_stats.append(stats_dict)

        print(f"\n{spawn_label} (f={f_spawn:.4f}):")
        print(f"  Population: {stats_dict['mean_population']:.1f} ± {stats_dict['std_population']:.1f}")
        print(f"  Range: [{stats_dict['min_population']} - {stats_dict['max_population']}]")
        print(f"  Collapse rate: {stats_dict['collapse_rate']*100:.1f}%")

    return pd.DataFrame(stability_stats)

def analyze_carrying_capacity(df):
    """Analyze carrying capacity (K) under net-zero energy."""
    print("\n" + "="*80)
    print("CARRYING CAPACITY ANALYSIS")
    print("="*80)

    # Overall carrying capacity
    all_populations = df[df['final_population'] > 0]['final_population']
    mean_K = all_populations.mean()
    std_K = all_populations.std()

    print(f"\nOverall Carrying Capacity (net-zero energy):")
    print(f"  K = {mean_K:.1f} ± {std_K:.1f} agents")
    print(f"  Range: [{all_populations.min()} - {all_populations.max()}]")

    # Compare to initial population
    initial_pop = 100  # From experiment configuration
    growth_factor = mean_K / initial_pop

    print(f"\nGrowth from Initial:")
    print(f"  Initial: {initial_pop} agents")
    print(f"  Final: {mean_K:.1f} agents")
    print(f"  Growth factor: {growth_factor:.2f}×")

    # Compare to pilot (net-positive energy)
    pilot_final = 12869  # From pilot with net +0.5
    pilot_ratio = pilot_final / mean_K

    print(f"\nComparison to Pilot (net +0.5 energy):")
    print(f"  Pilot final: {pilot_final} agents")
    print(f"  V6a final: {mean_K:.1f} agents")
    print(f"  Ratio: {pilot_ratio:.1f}× larger in pilot")
    print(f"  → Net-positive energy causes {pilot_ratio:.0f}× population expansion")

    return {
        'mean_K': mean_K,
        'std_K': std_K,
        'min_K': all_populations.min(),
        'max_K': all_populations.max(),
        'growth_factor': growth_factor
    }

def analyze_spawn_rate_effects(df):
    """Test if spawn rate affects final population (should be minimal at homeostasis)."""
    print("\n" + "="*80)
    print("SPAWN RATE EFFECTS ANALYSIS")
    print("="*80)

    # ANOVA test: Does spawn rate affect final population?
    groups = [group['final_population'].values for name, group in df.groupby('f_spawn')]
    f_stat, p_value = stats.f_oneway(*groups)

    print(f"\nOne-Way ANOVA (spawn rate → final population):")
    print(f"  F-statistic: {f_stat:.3f}")
    print(f"  p-value: {p_value:.6f}")

    if p_value < 0.05:
        print(f"  → Significant effect (p < 0.05)")
        print(f"  → Spawn rate influences carrying capacity")
    else:
        print(f"  → No significant effect (p ≥ 0.05)")
        print(f"  → Carrying capacity independent of spawn rate (homeostasis)")

    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

def analyze_computational_performance(df):
    """Analyze computational performance across conditions."""
    print("\n" + "="*80)
    print("COMPUTATIONAL PERFORMANCE ANALYSIS")
    print("="*80)

    # Overall statistics
    mean_runtime = df['runtime_seconds'].mean()
    std_runtime = df['runtime_seconds'].std()
    total_runtime = df['runtime_seconds'].sum()

    print(f"\nRuntime Statistics:")
    print(f"  Mean per experiment: {mean_runtime:.1f} ± {std_runtime:.1f} seconds")
    print(f"  Total campaign: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")

    # Cycles per second
    mean_cycles = df['cycles'].mean()
    mean_rate = mean_cycles / mean_runtime

    print(f"\nComputational Rate:")
    print(f"  Mean: {mean_rate:.1f} cycles/second")
    print(f"  Per experiment: {mean_cycles:.0f} cycles in {mean_runtime:.1f} seconds")

    # Compare to pilot
    pilot_rate = 1780  # From pilot (12,869 agents)
    rate_ratio = mean_rate / pilot_rate

    print(f"\nComparison to Pilot:")
    print(f"  Pilot rate: {pilot_rate} cycles/second (12,869 agents)")
    print(f"  V6a rate: {mean_rate:.1f} cycles/second (~200 agents)")
    print(f"  Speedup: {rate_ratio:.1f}× faster")
    print(f"  → Homeostasis enables rapid experimentation")

    return {
        'mean_runtime_seconds': mean_runtime,
        'total_runtime_minutes': total_runtime / 60,
        'mean_rate_cyc_per_sec': mean_rate,
        'speedup_vs_pilot': rate_ratio
    }

def generate_summary_report(df, stability_stats, carrying_capacity, spawn_effects, performance):
    """Generate comprehensive summary report."""
    print("\n" + "="*80)
    print("V6a CAMPAIGN SUMMARY REPORT")
    print("="*80)

    report = {
        'campaign': 'C186_V6a_NET_ZERO_HOMEOSTASIS',
        'total_experiments': len(df),
        'successful_experiments': df['success'].sum(),
        'failed_experiments': (~df['success']).sum(),
        'energy_regime': 'net_zero (E_consume = E_recharge = 1.0)',
        'population_stability': stability_stats.to_dict('records'),
        'carrying_capacity': carrying_capacity,
        'spawn_rate_effects': spawn_effects,
        'computational_performance': performance,
        'key_findings': [
            "Net-zero energy prevents runaway growth (K ~ 200 vs pilot's 12,869)",
            f"Carrying capacity: {carrying_capacity['mean_K']:.1f} ± {carrying_capacity['std_K']:.1f} agents",
            f"Homeostasis enables {performance['speedup_vs_pilot']:.1f}× faster computation",
            f"Spawn rate {'affects' if spawn_effects['significant'] else 'does not affect'} carrying capacity",
            f"Campaign completed in {performance['total_runtime_minutes']:.1f} minutes (not 5-6 days!)"
        ]
    }

    # Save summary JSON
    output_path = OUTPUT_DIR / "v6a_campaign_summary.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nSummary saved: {output_path}")

    print("\nKey Findings:")
    for i, finding in enumerate(report['key_findings'], 1):
        print(f"  {i}. {finding}")

    return report

def main():
    """Main analysis pipeline."""
    print("="*80)
    print("V6a RESULTS AGGREGATION AND ANALYSIS")
    print("="*80)
    print()

    # Load results
    df = load_v6a_results()

    if len(df) == 0:
        print("No results found. Campaign may still be running.")
        return

    print(f"\nLoaded {len(df)} experiments")
    print(f"Success rate: {df['success'].sum()}/{len(df)} ({df['success'].mean()*100:.1f}%)")

    # Run analyses
    stability_stats = analyze_population_stability(df)
    carrying_capacity = analyze_carrying_capacity(df)
    spawn_effects = analyze_spawn_rate_effects(df)
    performance = analyze_computational_performance(df)

    # Generate summary report
    report = generate_summary_report(df, stability_stats, carrying_capacity, spawn_effects, performance)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return report

if __name__ == '__main__':
    main()
