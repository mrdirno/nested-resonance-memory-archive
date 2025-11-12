#!/usr/bin/env python3
"""
C189 Alternative Mechanisms Analysis

Purpose: Test whether alternative mechanisms create topology-dependent spawn advantage
         following C188's inequality-advantage dissociation discovery

Hypotheses:
    H4.1 (Spatial): Scale-Free > Random > Lattice for composition rate (p < 3e-07)
    H4.2 (Memory): Scale-Free > Random > Lattice for spawn rate (p < 3e-07)
    H4.3 (Threshold): Scale-Free > Random > Lattice for spawn rate (p < 3e-07)

Statistical Rigor: 5σ standard (p < 3e-07)
MOG Falsification Gauntlet: Newtonian + Maxwellian + Einsteinian + Feynman

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-10 (Cycle 1423)
License: GPL-3.0
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from datetime import datetime

# File paths
RESULTS_PATH = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c189/c189_alternative_mechanisms.json")
OUTPUT_DIR = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/code/analysis/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Statistical significance thresholds
SIGMA_3 = 0.0027  # 3σ
SIGMA_5 = 3e-07   # 5σ (ultra-rigorous standard)

def load_results() -> Dict:
    """Load C189 results from JSON"""
    print(f"Loading results from: {RESULTS_PATH}")
    with open(RESULTS_PATH, 'r') as f:
        data = json.load(f)

    results = data['results']
    print(f"  Loaded {len(results)} experiments")
    print(f"  Mechanisms: {data['parameters']['mechanisms']}")
    print(f"  Topologies: {data['parameters']['topologies']}")
    print(f"  Seeds: {len(data['parameters']['seeds'])}")
    print()

    return data

def aggregate_by_condition(results: List[Dict]) -> pd.DataFrame:
    """Aggregate results by mechanism × topology"""
    records = []

    for exp in results:
        records.append({
            'mechanism': exp['mechanism'],
            'topology': exp['topology'],
            'seed': exp['seed'],
            'spawn_rate': exp['spawn_rate'],
            'final_population': exp['final_population'],
            'composition_rate': exp['composition_rate'],
            'mean_memory': exp['final_metrics']['mean_memory'],
            'gini_energy': exp['final_metrics']['gini_energy'],
        })

    df = pd.DataFrame(records)
    print(f"Aggregated data shape: {df.shape}")
    print()

    return df

def calculate_cohen_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    # Cohen's d
    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    return d

def test_h41_spatial_composition(df: pd.DataFrame) -> Dict:
    """
    H4.1: Spatial mechanism creates topology ranking for composition rate

    Prediction: Scale-Free > Random > Lattice (p < 3e-07)
    Mechanism: Short paths → high composition probability
    """
    print("=" * 80)
    print("H4.1: SPATIAL COMPOSITION RATE RANKING")
    print("=" * 80)
    print()

    # Filter spatial mechanism only
    spatial_df = df[df['mechanism'] == 'spatial'].copy()

    # Extract composition rates by topology
    sf_rates = spatial_df[spatial_df['topology'] == 'scale_free']['composition_rate']
    rand_rates = spatial_df[spatial_df['topology'] == 'random']['composition_rate']
    latt_rates = spatial_df[spatial_df['topology'] == 'lattice']['composition_rate']

    print(f"Scale-Free composition rate: {sf_rates.mean():.6f} ± {sf_rates.std():.6f} (n={len(sf_rates)})")
    print(f"Random composition rate:     {rand_rates.mean():.6f} ± {rand_rates.std():.6f} (n={len(rand_rates)})")
    print(f"Lattice composition rate:    {latt_rates.mean():.6f} ± {latt_rates.std():.6f} (n={len(latt_rates)})")
    print()

    # ANOVA (omnibus test)
    f_stat, p_anova = stats.f_oneway(sf_rates, rand_rates, latt_rates)
    print(f"ANOVA: F={f_stat:.6f}, p={p_anova:.6e}")
    print()

    # Pairwise comparisons (Mann-Whitney U, two-sided)
    _, p_sf_rand = stats.mannwhitneyu(sf_rates, rand_rates, alternative='two-sided')
    _, p_rand_latt = stats.mannwhitneyu(rand_rates, latt_rates, alternative='two-sided')
    _, p_sf_latt = stats.mannwhitneyu(sf_rates, latt_rates, alternative='two-sided')

    print(f"SF vs Random:  p={p_sf_rand:.6e}")
    print(f"Random vs Lattice: p={p_rand_latt:.6e}")
    print(f"SF vs Lattice: p={p_sf_latt:.6e}")
    print()

    # Effect sizes
    d_sf_rand = calculate_cohen_d(sf_rates.values, rand_rates.values)
    d_rand_latt = calculate_cohen_d(rand_rates.values, latt_rates.values)
    d_sf_latt = calculate_cohen_d(sf_rates.values, latt_rates.values)

    print(f"Effect sizes (Cohen's d):")
    print(f"  SF vs Random: d={d_sf_rand:.4f}")
    print(f"  Random vs Lattice: d={d_rand_latt:.4f}")
    print(f"  SF vs Lattice: d={d_sf_latt:.4f}")
    print()

    # Check monotonic ordering
    monotonic = (sf_rates.mean() > rand_rates.mean()) and (rand_rates.mean() > latt_rates.mean())

    # Falsification criteria
    passed_3sigma = (p_sf_rand < SIGMA_3) and (p_rand_latt < SIGMA_3)
    passed_5sigma = (p_sf_rand < SIGMA_5) and (p_rand_latt < SIGMA_5)

    print(f"Monotonic ordering (SF > Rand > Latt): {monotonic}")
    print(f"Passed 3σ standard: {passed_3sigma}")
    print(f"Passed 5σ standard: {passed_5sigma}")
    print()

    result = {
        'hypothesis': 'H4.1_Spatial_Composition',
        'mean_sf': float(sf_rates.mean()),
        'mean_rand': float(rand_rates.mean()),
        'mean_latt': float(latt_rates.mean()),
        'std_sf': float(sf_rates.std()),
        'std_rand': float(rand_rates.std()),
        'std_latt': float(latt_rates.std()),
        'f_stat': float(f_stat),
        'p_anova': float(p_anova),
        'p_sf_rand': float(p_sf_rand),
        'p_rand_latt': float(p_rand_latt),
        'p_sf_latt': float(p_sf_latt),
        'd_sf_rand': float(d_sf_rand),
        'd_rand_latt': float(d_rand_latt),
        'd_sf_latt': float(d_sf_latt),
        'monotonic': bool(monotonic),
        'passed_3sigma': bool(passed_3sigma),
        'passed_5sigma': bool(passed_5sigma),
    }

    return result

def test_h42_memory_spawn(df: pd.DataFrame) -> Dict:
    """
    H4.2: Memory mechanism creates topology ranking for spawn rate

    Prediction: Scale-Free > Random > Lattice (p < 3e-07)
    Mechanism: Hub memory accumulation → spawn boost
    """
    print("=" * 80)
    print("H4.2: MEMORY TRANSPORT SPAWN RATE RANKING")
    print("=" * 80)
    print()

    # Filter memory mechanism only
    memory_df = df[df['mechanism'] == 'memory'].copy()

    # Extract spawn rates by topology
    sf_rates = memory_df[memory_df['topology'] == 'scale_free']['spawn_rate']
    rand_rates = memory_df[memory_df['topology'] == 'random']['spawn_rate']
    latt_rates = memory_df[memory_df['topology'] == 'lattice']['spawn_rate']

    print(f"Scale-Free spawn rate: {sf_rates.mean():.6f} ± {sf_rates.std():.6f} (n={len(sf_rates)})")
    print(f"Random spawn rate:     {rand_rates.mean():.6f} ± {rand_rates.std():.6f} (n={len(rand_rates)})")
    print(f"Lattice spawn rate:    {latt_rates.mean():.6f} ± {latt_rates.std():.6f} (n={len(latt_rates)})")
    print()

    # ANOVA
    f_stat, p_anova = stats.f_oneway(sf_rates, rand_rates, latt_rates)
    print(f"ANOVA: F={f_stat:.6f}, p={p_anova:.6e}")
    print()

    # Pairwise comparisons
    _, p_sf_rand = stats.mannwhitneyu(sf_rates, rand_rates, alternative='two-sided')
    _, p_rand_latt = stats.mannwhitneyu(rand_rates, latt_rates, alternative='two-sided')
    _, p_sf_latt = stats.mannwhitneyu(sf_rates, latt_rates, alternative='two-sided')

    print(f"SF vs Random:  p={p_sf_rand:.6e}")
    print(f"Random vs Lattice: p={p_rand_latt:.6e}")
    print(f"SF vs Lattice: p={p_sf_latt:.6e}")
    print()

    # Effect sizes
    d_sf_rand = calculate_cohen_d(sf_rates.values, rand_rates.values)
    d_rand_latt = calculate_cohen_d(rand_rates.values, latt_rates.values)
    d_sf_latt = calculate_cohen_d(sf_rates.values, latt_rates.values)

    print(f"Effect sizes (Cohen's d):")
    print(f"  SF vs Random: d={d_sf_rand:.4f}")
    print(f"  Random vs Lattice: d={d_rand_latt:.4f}")
    print(f"  SF vs Lattice: d={d_sf_latt:.4f}")
    print()

    # Check monotonic ordering
    monotonic = (sf_rates.mean() > rand_rates.mean()) and (rand_rates.mean() > latt_rates.mean())

    # Falsification criteria
    passed_3sigma = (p_sf_rand < SIGMA_3) and (p_rand_latt < SIGMA_3)
    passed_5sigma = (p_sf_rand < SIGMA_5) and (p_rand_latt < SIGMA_5)

    print(f"Monotonic ordering (SF > Rand > Latt): {monotonic}")
    print(f"Passed 3σ standard: {passed_3sigma}")
    print(f"Passed 5σ standard: {passed_5sigma}")
    print()

    result = {
        'hypothesis': 'H4.2_Memory_Spawn',
        'mean_sf': float(sf_rates.mean()),
        'mean_rand': float(rand_rates.mean()),
        'mean_latt': float(latt_rates.mean()),
        'std_sf': float(sf_rates.std()),
        'std_rand': float(rand_rates.std()),
        'std_latt': float(latt_rates.std()),
        'f_stat': float(f_stat),
        'p_anova': float(p_anova),
        'p_sf_rand': float(p_sf_rand),
        'p_rand_latt': float(p_rand_latt),
        'p_sf_latt': float(p_sf_latt),
        'd_sf_rand': float(d_sf_rand),
        'd_rand_latt': float(d_rand_latt),
        'd_sf_latt': float(d_sf_latt),
        'monotonic': bool(monotonic),
        'passed_3sigma': bool(passed_3sigma),
        'passed_5sigma': bool(passed_5sigma),
    }

    return result

def test_h43_threshold_spawn(df: pd.DataFrame) -> Dict:
    """
    H4.3: Threshold mechanism creates topology ranking for spawn rate

    Prediction: Scale-Free > Random > Lattice (p < 3e-07)
    Mechanism: High energy (C188) → lower threshold → easier spawning
    """
    print("=" * 80)
    print("H4.3: THRESHOLD SCALING SPAWN RATE RANKING")
    print("=" * 80)
    print()

    # Filter threshold mechanism only
    threshold_df = df[df['mechanism'] == 'threshold'].copy()

    # Extract spawn rates by topology
    sf_rates = threshold_df[threshold_df['topology'] == 'scale_free']['spawn_rate']
    rand_rates = threshold_df[threshold_df['topology'] == 'random']['spawn_rate']
    latt_rates = threshold_df[threshold_df['topology'] == 'lattice']['spawn_rate']

    print(f"Scale-Free spawn rate: {sf_rates.mean():.6f} ± {sf_rates.std():.6f} (n={len(sf_rates)})")
    print(f"Random spawn rate:     {rand_rates.mean():.6f} ± {rand_rates.std():.6f} (n={len(rand_rates)})")
    print(f"Lattice spawn rate:    {latt_rates.mean():.6f} ± {latt_rates.std():.6f} (n={len(latt_rates)})")
    print()

    # ANOVA
    f_stat, p_anova = stats.f_oneway(sf_rates, rand_rates, latt_rates)
    print(f"ANOVA: F={f_stat:.6f}, p={p_anova:.6e}")
    print()

    # Pairwise comparisons
    _, p_sf_rand = stats.mannwhitneyu(sf_rates, rand_rates, alternative='two-sided')
    _, p_rand_latt = stats.mannwhitneyu(rand_rates, latt_rates, alternative='two-sided')
    _, p_sf_latt = stats.mannwhitneyu(sf_rates, latt_rates, alternative='two-sided')

    print(f"SF vs Random:  p={p_sf_rand:.6e}")
    print(f"Random vs Lattice: p={p_rand_latt:.6e}")
    print(f"SF vs Lattice: p={p_sf_latt:.6e}")
    print()

    # Effect sizes
    d_sf_rand = calculate_cohen_d(sf_rates.values, rand_rates.values)
    d_rand_latt = calculate_cohen_d(rand_rates.values, latt_rates.values)
    d_sf_latt = calculate_cohen_d(sf_rates.values, latt_rates.values)

    print(f"Effect sizes (Cohen's d):")
    print(f"  SF vs Random: d={d_sf_rand:.4f}")
    print(f"  Random vs Lattice: d={d_rand_latt:.4f}")
    print(f"  SF vs Lattice: d={d_sf_latt:.4f}")
    print()

    # Check monotonic ordering
    monotonic = (sf_rates.mean() > rand_rates.mean()) and (rand_rates.mean() > latt_rates.mean())

    # Falsification criteria
    passed_3sigma = (p_sf_rand < SIGMA_3) and (p_rand_latt < SIGMA_3)
    passed_5sigma = (p_sf_rand < SIGMA_5) and (p_rand_latt < SIGMA_5)

    print(f"Monotonic ordering (SF > Rand > Latt): {monotonic}")
    print(f"Passed 3σ standard: {passed_3sigma}")
    print(f"Passed 5σ standard: {passed_5sigma}")
    print()

    # Additional analysis: Energy-Gini correlation (sanity check C188 replication)
    print("Sanity check: C188 energy inequality replication")
    sf_gini = threshold_df[threshold_df['topology'] == 'scale_free']['gini_energy'].mean()
    rand_gini = threshold_df[threshold_df['topology'] == 'random']['gini_energy'].mean()
    latt_gini = threshold_df[threshold_df['topology'] == 'lattice']['gini_energy'].mean()

    print(f"  SF Gini: {sf_gini:.4f}")
    print(f"  Random Gini: {rand_gini:.4f}")
    print(f"  Lattice Gini: {latt_gini:.4f}")
    print(f"  Ordering matches C188: {sf_gini > rand_gini > latt_gini}")
    print()

    result = {
        'hypothesis': 'H4.3_Threshold_Spawn',
        'mean_sf': float(sf_rates.mean()),
        'mean_rand': float(rand_rates.mean()),
        'mean_latt': float(latt_rates.mean()),
        'std_sf': float(sf_rates.std()),
        'std_rand': float(rand_rates.std()),
        'std_latt': float(latt_rates.std()),
        'f_stat': float(f_stat),
        'p_anova': float(p_anova),
        'p_sf_rand': float(p_sf_rand),
        'p_rand_latt': float(p_rand_latt),
        'p_sf_latt': float(p_sf_latt),
        'd_sf_rand': float(d_sf_rand),
        'd_rand_latt': float(d_rand_latt),
        'd_sf_latt': float(d_sf_latt),
        'monotonic': bool(monotonic),
        'passed_3sigma': bool(passed_3sigma),
        'passed_5sigma': bool(passed_5sigma),
        'gini_sf': float(sf_gini),
        'gini_rand': float(rand_gini),
        'gini_latt': float(latt_gini),
    }

    return result

def mog_falsification_summary(h41: Dict, h42: Dict, h43: Dict) -> Dict:
    """
    Apply MOG falsification gauntlet (5σ standard)

    Target: 70-80% falsification rate
    """
    print("=" * 80)
    print("MOG FALSIFICATION GAUNTLET SUMMARY")
    print("=" * 80)
    print()

    hypotheses = [
        ('H4.1 (Spatial Composition)', h41['passed_5sigma']),
        ('H4.2 (Memory Spawn)', h42['passed_5sigma']),
        ('H4.3 (Threshold Spawn)', h43['passed_5sigma']),
    ]

    passed_count = sum(1 for _, passed in hypotheses if passed)
    falsified_count = len(hypotheses) - passed_count
    falsification_rate = falsified_count / len(hypotheses)

    print(f"Total hypotheses: {len(hypotheses)}")
    print(f"Passed 5σ standard: {passed_count}")
    print(f"Falsified: {falsified_count}")
    print(f"Falsification rate: {falsification_rate:.1%}")
    print()

    print("Individual results:")
    for name, passed in hypotheses:
        status = "✓ PASSED" if passed else "✗ FALSIFIED"
        print(f"  {name}: {status}")
    print()

    # MOG evaluation
    if 0.7 <= falsification_rate <= 0.8:
        print("✓ MOG target met (70-80% falsification)")
    elif falsification_rate < 0.7:
        print(f"⚠ Falsification rate low ({falsification_rate:.1%}) - insufficient skepticism")
    else:
        print(f"✓ Falsification rate high ({falsification_rate:.1%}) - rigorous discipline")
    print()

    return {
        'n_hypotheses': len(hypotheses),
        'n_passed': passed_count,
        'n_falsified': falsified_count,
        'falsification_rate': float(falsification_rate),
        'hypotheses': [
            {'hypothesis': name, 'passed': bool(passed)}
            for name, passed in hypotheses
        ]
    }

def main():
    """Execute C189 analysis with 5σ standard"""
    print("=" * 80)
    print("C189 ALTERNATIVE MECHANISMS ANALYSIS")
    print("Statistical Rigor: 5σ standard (p < 3e-07)")
    print("=" * 80)
    print()

    # Load data
    data = load_results()
    df = aggregate_by_condition(data['results'])

    # Test hypotheses
    h41 = test_h41_spatial_composition(df)
    h42 = test_h42_memory_spawn(df)
    h43 = test_h43_threshold_spawn(df)

    # MOG falsification summary
    mog_summary = mog_falsification_summary(h41, h42, h43)

    # Save results
    output = {
        'analysis_date': datetime.now().isoformat(),
        'experiment': 'C189_Alternative_Mechanisms',
        'n_experiments': len(data['results']),
        'statistical_standard': '5sigma',
        'p_threshold': SIGMA_5,
        'h41_spatial_composition': h41,
        'h42_memory_spawn': h42,
        'h43_threshold_spawn': h43,
        'mog_falsification': mog_summary,
    }

    output_file = OUTPUT_DIR / 'c189_falsification_summary.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 80)
    print(f"Analysis complete. Results saved to:")
    print(f"  {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
