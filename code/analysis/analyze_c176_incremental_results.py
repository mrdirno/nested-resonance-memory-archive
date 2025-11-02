#!/usr/bin/env python3
"""
Comprehensive Analysis of C176 V6 Incremental Validation Results

Processes all 5 seeds from C176 V6 incremental validation (1000 cycles) and
generates complete statistics, confidence intervals, and threshold zone analysis.

Outputs:
- Summary statistics JSON file
- Per-seed trajectory JSON file
- Statistical test results
- Console summary report

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-02
License: GPL-3.0
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from datetime import datetime


def load_c176_data(data_dir: Path) -> Dict:
    """
    Load C176 V6 incremental validation results.

    Args:
        data_dir: Path to data/results directory

    Returns:
        Dictionary with raw experimental data
    """
    filepath = data_dir / 'c176_v6_incremental_validation_results.json'

    if not filepath.exists():
        raise FileNotFoundError(
            f"C176 V6 data not found: {filepath}\n"
            f"Run experiments first: python code/experiments/cycle176_v6_incremental_validation.py"
        )

    with open(filepath, 'r') as f:
        data = json.load(f)

    return data


def calculate_confidence_interval(data: np.ndarray, confidence=0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for data.

    Args:
        data: Array of values
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        (lower_bound, upper_bound)
    """
    if len(data) == 0:
        return (0.0, 0.0)

    mean = np.mean(data)
    sem = stats.sem(data)  # Standard error of mean
    ci = stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)

    return ci


def calculate_spawns_per_agent(population_trajectory: List[int],
                               total_spawn_attempts: int) -> float:
    """Calculate spawns per agent metric."""
    if not population_trajectory:
        return 0.0

    avg_population = np.mean(population_trajectory)
    if avg_population == 0:
        return 0.0

    return total_spawn_attempts / avg_population


def classify_basin(mean_population: float, cv_percent: float,
                  spawn_success: float) -> str:
    """
    Classify basin attractor.

    Args:
        mean_population: Mean population size
        cv_percent: Coefficient of variation (%)
        spawn_success: Spawn success rate (decimal)

    Returns:
        Basin classification: 'A', 'B', or 'C'
    """
    if mean_population >= 20 and cv_percent < 5 and spawn_success > 0.80:
        return 'A'
    elif mean_population >= 10 and spawn_success > 0.50:
        return 'B'
    else:
        return 'C'


def analyze_seeds(c176_data: Dict) -> Dict:
    """
    Analyze all seeds and generate summary statistics.

    Args:
        c176_data: Raw C176 V6 experimental data

    Returns:
        Dictionary with comprehensive analysis results
    """
    results = c176_data.get('results', [])

    if len(results) == 0:
        raise ValueError("No seed results found in C176 data")

    print(f"\nAnalyzing {len(results)} seeds...")
    print("=" * 80)

    # Extract per-seed metrics
    seeds = []
    final_populations = []
    mean_populations = []
    cvs = []
    spawn_successes = []
    total_attempts_list = []
    spawns_per_agent_list = []
    basins = []

    for result in results:
        seed = result['seed']
        seeds.append(seed)

        # Population metrics
        final_pop = result.get('final_population', 0)
        final_populations.append(final_pop)

        mean_pop = result.get('mean_population', 0)
        mean_populations.append(mean_pop)

        cv = result.get('cv_percent', 0)
        cvs.append(cv)

        # Spawn success
        success = result.get('spawn_success', 0.0)
        if success <= 1.0:  # Convert to percentage if in decimal
            success *= 100.0
        spawn_successes.append(success)

        # Spawn attempts
        attempts = result.get('total_spawn_attempts', 0)
        total_attempts_list.append(attempts)

        # Spawns per agent
        if 'population_trajectory' in result:
            metric = calculate_spawns_per_agent(
                result['population_trajectory'],
                attempts
            )
            spawns_per_agent_list.append(metric)
        else:
            spawns_per_agent_list.append(0.0)

        # Basin classification
        basin = result.get('basin', classify_basin(mean_pop, cv, success/100.0))
        basins.append(basin)

        # Print per-seed summary
        print(f"\nSeed {seed}:")
        print(f"  Final population: {final_pop}")
        print(f"  Mean population: {mean_pop:.2f}")
        print(f"  CV: {cv:.2f}%")
        print(f"  Spawn success: {success:.1f}%")
        print(f"  Total attempts: {attempts}")
        print(f"  Spawns/agent: {metric:.2f}")
        print(f"  Basin: {basin}")

    # Convert to arrays for statistics
    final_populations = np.array(final_populations)
    mean_populations = np.array(mean_populations)
    cvs = np.array(cvs)
    spawn_successes = np.array(spawn_successes)
    total_attempts_arr = np.array(total_attempts_list)
    spawns_per_agent_arr = np.array(spawns_per_agent_list)

    # Calculate summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS (n={})".format(len(seeds)))
    print("=" * 80)

    summary = {
        'n_seeds': len(seeds),
        'seeds': seeds,
        'final_population': {
            'mean': float(np.mean(final_populations)),
            'sd': float(np.std(final_populations, ddof=1)),
            'min': float(np.min(final_populations)),
            'max': float(np.max(final_populations)),
            'ci_95': calculate_confidence_interval(final_populations)
        },
        'mean_population': {
            'mean': float(np.mean(mean_populations)),
            'sd': float(np.std(mean_populations, ddof=1)),
            'min': float(np.min(mean_populations)),
            'max': float(np.max(mean_populations)),
            'ci_95': calculate_confidence_interval(mean_populations)
        },
        'cv_percent': {
            'mean': float(np.mean(cvs)),
            'sd': float(np.std(cvs, ddof=1)),
            'min': float(np.min(cvs)),
            'max': float(np.max(cvs)),
        },
        'spawn_success_percent': {
            'mean': float(np.mean(spawn_successes)),
            'sd': float(np.std(spawn_successes, ddof=1)),
            'min': float(np.min(spawn_successes)),
            'max': float(np.max(spawn_successes)),
            'ci_95': calculate_confidence_interval(spawn_successes)
        },
        'total_spawn_attempts': {
            'mean': float(np.mean(total_attempts_arr)),
            'sd': float(np.std(total_attempts_arr, ddof=1)),
            'min': float(np.min(total_attempts_arr)),
            'max': float(np.max(total_attempts_arr)),
        },
        'spawns_per_agent': {
            'mean': float(np.mean(spawns_per_agent_arr)),
            'sd': float(np.std(spawns_per_agent_arr, ddof=1)),
            'min': float(np.min(spawns_per_agent_arr)),
            'max': float(np.max(spawns_per_agent_arr)),
            'ci_95': calculate_confidence_interval(spawns_per_agent_arr)
        },
        'basin_distribution': {
            'A': basins.count('A'),
            'B': basins.count('B'),
            'C': basins.count('C'),
        }
    }

    # Print summary
    print(f"\nFinal Population: {summary['final_population']['mean']:.1f} ± "
          f"{summary['final_population']['sd']:.1f}")
    print(f"  Range: [{summary['final_population']['min']:.0f}, "
          f"{summary['final_population']['max']:.0f}]")
    print(f"  95% CI: [{summary['final_population']['ci_95'][0]:.1f}, "
          f"{summary['final_population']['ci_95'][1]:.1f}]")

    print(f"\nMean Population: {summary['mean_population']['mean']:.2f} ± "
          f"{summary['mean_population']['sd']:.2f}")
    print(f"  Range: [{summary['mean_population']['min']:.1f}, "
          f"{summary['mean_population']['max']:.1f}]")
    print(f"  95% CI: [{summary['mean_population']['ci_95'][0]:.2f}, "
          f"{summary['mean_population']['ci_95'][1]:.2f}]")

    print(f"\nCV: {summary['cv_percent']['mean']:.2f}% ± "
          f"{summary['cv_percent']['sd']:.2f}%")

    print(f"\nSpawn Success: {summary['spawn_success_percent']['mean']:.1f}% ± "
          f"{summary['spawn_success_percent']['sd']:.1f}%")
    print(f"  Range: [{summary['spawn_success_percent']['min']:.1f}%, "
          f"{summary['spawn_success_percent']['max']:.1f}%]")
    print(f"  95% CI: [{summary['spawn_success_percent']['ci_95'][0]:.1f}%, "
          f"{summary['spawn_success_percent']['ci_95'][1]:.1f}%]")

    print(f"\nTotal Spawn Attempts: {summary['total_spawn_attempts']['mean']:.1f} ± "
          f"{summary['total_spawn_attempts']['sd']:.1f}")

    print(f"\nSpawns Per Agent: {summary['spawns_per_agent']['mean']:.2f} ± "
          f"{summary['spawns_per_agent']['sd']:.2f}")
    print(f"  Range: [{summary['spawns_per_agent']['min']:.2f}, "
          f"{summary['spawns_per_agent']['max']:.2f}]")
    print(f"  95% CI: [{summary['spawns_per_agent']['ci_95'][0]:.2f}, "
          f"{summary['spawns_per_agent']['ci_95'][1]:.2f}]")

    print(f"\nBasin Distribution:")
    print(f"  A: {summary['basin_distribution']['A']} "
          f"({100*summary['basin_distribution']['A']/len(seeds):.0f}%)")
    print(f"  B: {summary['basin_distribution']['B']} "
          f"({100*summary['basin_distribution']['B']/len(seeds):.0f}%)")
    print(f"  C: {summary['basin_distribution']['C']} "
          f"({100*summary['basin_distribution']['C']/len(seeds):.0f}%)")

    return summary


def test_threshold_hypothesis(spawns_per_agent_arr: np.ndarray,
                              spawn_successes: np.ndarray) -> Dict:
    """
    Test threshold zone hypothesis with statistical tests.

    Args:
        spawns_per_agent_arr: Array of spawns/agent values
        spawn_successes: Array of success rates (%)

    Returns:
        Dictionary with test results
    """
    print("\n" + "=" * 80)
    print("THRESHOLD ZONE HYPOTHESIS TESTING")
    print("=" * 80)

    # Test hypothesis: spawns/agent values fall in <2 zone (high success)
    # Null: mean spawns/agent >= 2
    # Alternative: mean spawns/agent < 2

    mean_metric = np.mean(spawns_per_agent_arr)
    sd_metric = np.std(spawns_per_agent_arr, ddof=1)
    n = len(spawns_per_agent_arr)

    # One-sample t-test (one-tailed)
    t_stat, p_value_two_tailed = stats.ttest_1samp(spawns_per_agent_arr, 2.0)
    p_value_one_tailed = p_value_two_tailed / 2 if t_stat < 0 else 1 - (p_value_two_tailed / 2)

    print(f"\nHypothesis: Mean spawns/agent < 2.0 (high success zone)")
    print(f"  Mean: {mean_metric:.2f} ± {sd_metric:.2f} (n={n})")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value (one-tailed): {p_value_one_tailed:.4f}")

    if p_value_one_tailed < 0.05:
        print(f"  ✓ Reject null hypothesis (p < 0.05)")
        print(f"    Evidence supports mean < 2.0 (high success zone)")
    else:
        print(f"  ✗ Fail to reject null (p >= 0.05)")

    # Correlation test: spawns/agent vs success rate (expect negative correlation)
    corr, p_corr = stats.pearsonr(spawns_per_agent_arr, spawn_successes)

    print(f"\nCorrelation: Spawns/agent vs Success rate")
    print(f"  Pearson r: {corr:.3f}")
    print(f"  p-value: {p_corr:.4f}")

    if p_corr < 0.05:
        if corr < 0:
            print(f"  ✓ Significant negative correlation (p < 0.05)")
            print(f"    Higher spawns/agent → lower success")
        else:
            print(f"  ⚠ Significant positive correlation (unexpected)")
    else:
        print(f"  ✗ No significant correlation (p >= 0.05)")

    return {
        't_statistic': float(t_stat),
        'p_value_one_tailed': float(p_value_one_tailed),
        'correlation_r': float(corr),
        'correlation_p': float(p_corr),
        'hypothesis_supported': bool(p_value_one_tailed < 0.05 and corr < 0)
    }


def save_results(summary: Dict, test_results: Dict, output_dir: Path):
    """
    Save analysis results to JSON files.

    Args:
        summary: Summary statistics dictionary
        test_results: Statistical test results
        output_dir: Where to save output files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Combined results
    results = {
        'analysis_date': datetime.now().isoformat(),
        'experiment': 'C176_V6_Incremental_Validation',
        'timescale': '1000_cycles',
        'summary_statistics': summary,
        'statistical_tests': test_results
    }

    # Save summary
    summary_path = output_dir / 'c176_v6_incremental_stats.json'
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved: {summary_path}")
    print(f"  File size: {summary_path.stat().st_size / 1024:.1f} KB")


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent.parent
    data_dir = repo_root / 'data' / 'results'
    output_dir = data_dir

    print("=" * 80)
    print("C176 V6 INCREMENTAL VALIDATION: COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    try:
        c176_data = load_c176_data(data_dir)
        print(f"✓ Data loaded successfully")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return

    # Analyze seeds
    try:
        summary = analyze_seeds(c176_data)
    except Exception as e:
        print(f"✗ Analysis error: {e}")
        return

    # Statistical tests
    try:
        # Extract arrays for testing
        spawns_per_agent_arr = np.array([
            summary['spawns_per_agent']['mean']  # Placeholder - should extract per-seed
        ])
        spawn_successes = np.array([
            summary['spawn_success_percent']['mean']
        ])

        # Properly extract per-seed values from raw data
        results = c176_data.get('results', [])
        spawns_per_agent_arr = []
        spawn_successes = []

        for result in results:
            if 'population_trajectory' in result:
                metric = calculate_spawns_per_agent(
                    result['population_trajectory'],
                    result.get('total_spawn_attempts', 0)
                )
                spawns_per_agent_arr.append(metric)

                success = result.get('spawn_success', 0.0)
                if success <= 1.0:
                    success *= 100.0
                spawn_successes.append(success)

        spawns_per_agent_arr = np.array(spawns_per_agent_arr)
        spawn_successes = np.array(spawn_successes)

        test_results = test_threshold_hypothesis(spawns_per_agent_arr, spawn_successes)
    except Exception as e:
        print(f"✗ Statistical test error: {e}")
        test_results = {}

    # Save results
    try:
        save_results(summary, test_results, output_dir)
    except Exception as e:
        print(f"✗ Save error: {e}")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  • {summary['n_seeds']} seeds analyzed")
    print(f"  • Mean spawn success: {summary['spawn_success_percent']['mean']:.1f}% ± "
          f"{summary['spawn_success_percent']['sd']:.1f}%")
    print(f"  • Mean spawns/agent: {summary['spawns_per_agent']['mean']:.2f} ± "
          f"{summary['spawns_per_agent']['sd']:.2f}")
    print(f"  • Basin distribution: {summary['basin_distribution']['A']} A, "
          f"{summary['basin_distribution']['B']} B, {summary['basin_distribution']['C']} C")

    if test_results.get('hypothesis_supported'):
        print(f"  • ✓ Threshold hypothesis supported (spawns/agent < 2 → high success)")
    else:
        print(f"  • ⚠ Threshold hypothesis not conclusively supported")

    print()
    print("Next steps:")
    print("  1. Update manuscript with final statistics")
    print("  2. Regenerate figures with complete data")
    print("  3. Execute integration checklist")
    print("  4. Finalize Paper 2 for submission")
    print()


if __name__ == '__main__':
    main()
