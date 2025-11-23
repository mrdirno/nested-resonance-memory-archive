#!/usr/bin/env python3
"""
CYCLE 176 V6: BASELINE VALIDATION RESULTS ANALYSIS

Purpose: Analyze C176 V6 baseline validation results to test energy-regulated homeostasis hypothesis

Hypothesis:
- H1: Energy-regulated spawn mechanism produces homeostatic population (~18-20 agents)
- H2: Population CV < 15% (stable homeostasis)
- H3: Spawn success rate ~30-35% (energy constraint manifests)

Analysis:
- Statistical validation of population homeostasis
- Spawn success rate distribution
- Comparison to C171 reference results
- Decision: Proceed with C176 V7 ablation study?

Date: 2025-11-01
Cycle: 901
Researcher: Claude (DUALITY-ZERO-V2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy import stats

# Expected outcomes from C171
EXPECTED_MEAN_POP = 18.0
EXPECTED_CV_THRESHOLD = 15.0
EXPECTED_SPAWN_RATE_MIN = 25.0  # Conservative range
EXPECTED_SPAWN_RATE_MAX = 40.0

# Results file (will be written by validation script)
RESULTS_FILE = Path("experiments/results/cycle176_v6_baseline_validation.json")


def load_results():
    """Load C176 V6 validation results."""
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(f"Results file not found: {RESULTS_FILE}")

    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    # Validation script saves with 'experiments' key, not 'results'
    if 'experiments' in data:
        data['results'] = data['experiments']

    return data


def analyze_population_homeostasis(results):
    """
    Test H1+H2: Energy-regulated spawn produces homeostatic population.

    Expected:
    - Mean population ~18-20 agents
    - CV < 15% (homeostatic stability)
    """
    print("=" * 80)
    print("HYPOTHESIS 1+2: POPULATION HOMEOSTASIS")
    print("=" * 80)
    print()

    mean_pops = [r['mean_population'] for r in results]
    cvs = [r['cv_population'] for r in results]

    overall_mean = np.mean(mean_pops)
    overall_std = np.std(mean_pops)
    overall_cv = np.mean(cvs)

    print(f"Population Statistics (n={len(results)} seeds):")
    print(f"  Mean population: {overall_mean:.2f} ± {overall_std:.2f} agents")
    print(f"  Range: [{min(mean_pops):.1f}, {max(mean_pops):.1f}]")
    print(f"  Average within-seed CV: {overall_cv:.2f}%")
    print()

    # Test: Mean population ~18-20
    in_range = 16 <= overall_mean <= 22  # Allow ±2 agents tolerance
    print(f"H1 Test: Mean population in range [16, 22]?")
    print(f"  Expected: {EXPECTED_MEAN_POP:.1f} agents")
    print(f"  Observed: {overall_mean:.2f} agents")
    print(f"  Result: {'✅ PASS' if in_range else '❌ FAIL'}")
    print()

    # Test: CV < 15%
    homeostatic = overall_cv < EXPECTED_CV_THRESHOLD
    print(f"H2 Test: Population CV < {EXPECTED_CV_THRESHOLD}%?")
    print(f"  Expected: < {EXPECTED_CV_THRESHOLD}%")
    print(f"  Observed: {overall_cv:.2f}%")
    print(f"  Result: {'✅ PASS' if homeostatic else '❌ FAIL'}")
    print()

    return {
        'h1_pass': in_range,
        'h2_pass': homeostatic,
        'mean_population': overall_mean,
        'std_population': overall_std,
        'cv_population': overall_cv,
    }


def analyze_spawn_success_rate(results):
    """
    Test H3: Spawn success rate ~30-35% (energy constraint manifests).

    Expected:
    - Spawn success rate significantly below 100%
    - Indicates energy depletion limiting reproduction
    """
    print("=" * 80)
    print("HYPOTHESIS 3: ENERGY-CONSTRAINED SPAWNING")
    print("=" * 80)
    print()

    spawn_rates = [r['spawn_success_rate'] for r in results]

    mean_rate = np.mean(spawn_rates)
    std_rate = np.std(spawn_rates)

    print(f"Spawn Success Rate Statistics (n={len(results)} seeds):")
    print(f"  Mean success rate: {mean_rate:.2f}% ± {std_rate:.2f}%")
    print(f"  Range: [{min(spawn_rates):.1f}%, {max(spawn_rates):.1f}%]")
    print()

    # Test: Success rate in expected range
    in_range = EXPECTED_SPAWN_RATE_MIN <= mean_rate <= EXPECTED_SPAWN_RATE_MAX
    print(f"H3 Test: Spawn success rate in range [{EXPECTED_SPAWN_RATE_MIN}%, {EXPECTED_SPAWN_RATE_MAX}%]?")
    print(f"  Expected: ~30-35%")
    print(f"  Observed: {mean_rate:.2f}%")
    print(f"  Result: {'✅ PASS' if in_range else '❌ FAIL'}")
    print()

    # Additional: Test if significantly < 100%
    _, p_value = stats.ttest_1samp(spawn_rates, 100.0, alternative='less')
    significant = p_value < 0.001
    print(f"Energy Constraint Test: Success rate significantly < 100%?")
    print(f"  t-test p-value: {p_value:.2e}")
    print(f"  Result: {'✅ SIGNIFICANT (p < 0.001)' if significant else '❌ NOT SIGNIFICANT'}")
    print()

    return {
        'h3_pass': in_range,
        'mean_spawn_rate': mean_rate,
        'std_spawn_rate': std_rate,
        'energy_constraint_significant': significant,
        'p_value': p_value,
    }


def analyze_basin_distribution(results):
    """Analyze Basin A vs Basin B distribution."""
    print("=" * 80)
    print("BASIN CLASSIFICATION ANALYSIS")
    print("=" * 80)
    print()

    basins = [r['basin'] for r in results]
    basin_a_count = basins.count('A')
    basin_b_count = basins.count('B')

    print(f"Basin Distribution (n={len(results)} seeds):")
    print(f"  Basin A: {basin_a_count} seeds ({basin_a_count/len(results)*100:.1f}%)")
    print(f"  Basin B: {basin_b_count} seeds ({basin_b_count/len(results)*100:.1f}%)")
    print()

    # Expected: Roughly balanced distribution (C171 showed ~50/50)
    # But not critical for hypothesis validation

    return {
        'basin_a_count': basin_a_count,
        'basin_b_count': basin_b_count,
    }


def generate_decision_recommendation(h1_results, h3_results):
    """Generate decision on C176 V7 ablation study launch."""
    print("=" * 80)
    print("DECISION RECOMMENDATION")
    print("=" * 80)
    print()

    h1_pass = h1_results['h1_pass']
    h2_pass = h1_results['h2_pass']
    h3_pass = h3_results['h3_pass']

    all_pass = h1_pass and h2_pass and h3_pass

    print("Hypothesis Validation Summary:")
    print(f"  H1 (Population homeostasis): {'✅ PASS' if h1_pass else '❌ FAIL'}")
    print(f"  H2 (CV < 15%): {'✅ PASS' if h2_pass else '❌ FAIL'}")
    print(f"  H3 (Energy-constrained spawning): {'✅ PASS' if h3_pass else '❌ FAIL'}")
    print()

    if all_pass:
        print("✅ **VALIDATION SUCCESSFUL**")
        print()
        print("Energy-regulated population homeostasis mechanism CONFIRMED:")
        print(f"  - Population self-regulates to ~{h1_results['mean_population']:.1f} agents")
        print(f"  - Homeostatic stability (CV={h1_results['cv_population']:.2f}%)")
        print(f"  - Energy constraint manifest (spawn rate={h3_results['mean_spawn_rate']:.1f}%)")
        print()
        print("**RECOMMENDATION: Proceed with C176 V7 Ablation Study**")
        print()
        print("Next Actions:")
        print("  1. Launch C176 V7 ablation study (6 conditions × 10 seeds)")
        print("  2. Test which components are necessary for homeostasis")
        print("  3. Integrate findings into Paper 2 (energy mechanism as novel contribution)")
        print()
    else:
        print("❌ **VALIDATION UNEXPECTED**")
        print()
        print("Energy-regulated mechanism behaving differently than predicted.")
        print()
        failures = []
        if not h1_pass:
            failures.append(f"Population outside expected range ({h1_results['mean_population']:.1f} vs ~18 expected)")
        if not h2_pass:
            failures.append(f"High variance (CV={h1_results['cv_population']:.2f}% vs <15% expected)")
        if not h3_pass:
            failures.append(f"Spawn rate unexpected ({h3_results['mean_spawn_rate']:.1f}% vs 30-35% expected)")

        for failure in failures:
            print(f"  - {failure}")
        print()
        print("**RECOMMENDATION: Investigate further before C176 V7**")
        print()
        print("Next Actions:")
        print("  1. Analyze individual seed trajectories")
        print("  2. Check for implementation bugs")
        print("  3. Review C171 reference implementation")
        print("  4. Revise mechanism understanding")
        print()

    return {
        'all_hypotheses_pass': all_pass,
        'recommendation': 'PROCEED_WITH_V7' if all_pass else 'INVESTIGATE_FURTHER',
    }


def main():
    """Execute C176 V6 results analysis."""
    print("=" * 80)
    print("CYCLE 176 V6: BASELINE VALIDATION RESULTS ANALYSIS")
    print("=" * 80)
    print()
    print("Hypothesis: Energy-regulated spawn mechanism produces homeostatic populations")
    print()

    start_time = datetime.now()

    # Load results
    print("Loading validation results...")
    try:
        data = load_results()
        results = data['results']
        metadata = data.get('metadata', {})
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Validation results file not found. Has C176 V6 validation completed?")
        return

    print(f"Loaded {len(results)} seed results")
    print()

    # Analyze hypotheses
    h1_h2_results = analyze_population_homeostasis(results)
    h3_results = analyze_spawn_success_rate(results)
    basin_results = analyze_basin_distribution(results)

    # Generate decision
    decision = generate_decision_recommendation(h1_h2_results, h3_results)

    # Save analysis summary
    analysis_summary = {
        'timestamp': datetime.now().isoformat(),
        'n_seeds': len(results),
        'population_analysis': h1_h2_results,
        'spawn_analysis': h3_results,
        'basin_analysis': basin_results,
        'decision': decision,
    }

    summary_file = Path("experiments/results/cycle176_v6_analysis_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(analysis_summary, f, indent=2)

    print(f"Analysis summary saved: {summary_file}")
    print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"Analysis completed in {duration:.1f} seconds")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
