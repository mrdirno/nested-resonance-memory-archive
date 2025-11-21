#!/usr/bin/env python3
"""
CYCLE 176 ANALYSIS: Ablation Study Results

Purpose: Analyze mechanism isolation experiments to test birth-death coupling hypothesis

Hypothesis:
  Birth-death coupling (β parameter) is critical for homeostasis emergence

Expected Results:
  - BASELINE: Homeostasis (population CV < 15%, ~17 agents)
  - NO_DEATH: No homeostasis (population grows to max_agents)
  - NO_BIRTH: No homeostasis (population decays to 0)
  - SMALL_WINDOW: Homeostasis maintained (mechanism robust to window size)
  - DETERMINISTIC: Homeostasis (control condition)
  - ALT_BASIS: Homeostasis (mechanism independent of π oscillator)

Hypothesis Confirmation:
  - If NO_DEATH and NO_BIRTH both lose homeostasis → CONFIRMED
  - If either maintains homeostasis → REJECTED or MIXED

Date: 2025-10-25 (Cycle 203)
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def load_results(results_path: Path) -> dict:
    """Load C176 experiment results and group by condition."""
    with open(results_path) as f:
        data = json.load(f)

    # Group experiments by condition
    experiments_by_condition = defaultdict(list)
    for exp in data.get('experiments', []):
        experiments_by_condition[exp['condition']].append(exp)

    # Restructure data
    data['results'] = dict(experiments_by_condition)

    print(f"✅ Loaded {len(data['results'])} condition results")
    for condition, exps in data['results'].items():
        print(f"   {condition}: {len(exps)} experiments")

    return data

def analyze_condition(condition_name: str, experiments: List[dict]) -> dict:
    """
    Analyze results for a single ablation condition.

    Returns:
        dict with population stats, composition stats, homeostasis classification
    """
    # Extract data
    populations = []
    compositions = []
    basins = []

    for exp in experiments:
        populations.append(exp['mean_population'])
        compositions.append(exp['avg_composition_events'])
        basins.append(exp['basin'])

    # Population statistics
    pop_mean = np.mean(populations)
    pop_std = np.std(populations, ddof=1)
    pop_cv = (pop_std / pop_mean * 100) if pop_mean > 0 else 999.0
    pop_min = np.min(populations)
    pop_max = np.max(populations)

    # Composition statistics
    comp_mean = np.mean(compositions)
    comp_std = np.std(compositions, ddof=1)
    comp_cv = (comp_std / comp_mean * 100) if comp_mean > 0 else 999.0

    # Basin classification
    basin_a_count = sum(1 for b in basins if b == 'A')
    basin_a_pct = basin_a_count / len(basins) * 100

    # Homeostasis classification (CV < 15% criterion from C171)
    is_homeostatic = pop_cv < 15.0

    return {
        'condition': condition_name,
        'n_experiments': len(experiments),
        'population': {
            'mean': pop_mean,
            'std': pop_std,
            'cv': pop_cv,
            'min': pop_min,
            'max': pop_max,
            'range': pop_max - pop_min
        },
        'composition': {
            'mean': comp_mean,
            'std': comp_std,
            'cv': comp_cv
        },
        'basin': {
            'basin_a_pct': basin_a_pct,
            'basin_a_count': basin_a_count,
            'basin_b_count': len(basins) - basin_a_count
        },
        'homeostatic': is_homeostatic,
        'classification': 'HOMEOSTATIC' if is_homeostatic else 'NON-HOMEOSTATIC'
    }

def test_hypothesis(results: Dict[str, dict]) -> dict:
    """
    Test birth-death coupling hypothesis.

    Hypothesis CONFIRMED if:
      - BASELINE: homeostatic
      - NO_DEATH: non-homeostatic
      - NO_BIRTH: non-homeostatic

    Hypothesis REJECTED if:
      - NO_DEATH or NO_BIRTH maintain homeostasis

    Hypothesis MIXED if:
      - One of NO_DEATH/NO_BIRTH loses homeostasis but not both
    """
    baseline = results.get('BASELINE', {})
    no_death = results.get('NO_DEATH', {})
    no_birth = results.get('NO_BIRTH', {})

    # Check conditions
    baseline_homeostatic = baseline.get('homeostatic', False)
    no_death_homeostatic = no_death.get('homeostatic', False)
    no_birth_homeostatic = no_birth.get('homeostatic', False)

    # Hypothesis test
    if baseline_homeostatic and not no_death_homeostatic and not no_birth_homeostatic:
        verdict = 'CONFIRMED'
        interpretation = (
            "Birth-death coupling is critical for homeostasis. "
            "Removing either birth or death eliminates homeostatic regulation. "
            "Baseline exhibits homeostasis (CV < 15%), while NO_DEATH and NO_BIRTH "
            "both fail to maintain population stability."
        )
    elif not baseline_homeostatic:
        verdict = 'BASELINE_FAILED'
        interpretation = (
            "Baseline condition failed to replicate C171 homeostasis. "
            "Cannot test hypothesis without baseline validation."
        )
    elif no_death_homeostatic or no_birth_homeostatic:
        verdict = 'REJECTED'
        interpretation = (
            "Birth-death coupling is NOT necessary for homeostasis. "
            f"NO_DEATH homeostatic: {no_death_homeostatic}. "
            f"NO_BIRTH homeostatic: {no_birth_homeostatic}. "
            "Other mechanisms may contribute to population regulation."
        )
    else:
        verdict = 'MIXED'
        interpretation = (
            "Hypothesis partially supported but requires further investigation."
        )

    return {
        'verdict': verdict,
        'interpretation': interpretation,
        'conditions_tested': {
            'BASELINE': baseline_homeostatic,
            'NO_DEATH': no_death_homeostatic,
            'NO_BIRTH': no_birth_homeostatic
        }
    }

def generate_summary_table(condition_results: Dict[str, dict]) -> str:
    """Generate markdown summary table."""
    table = []
    table.append("\n## Ablation Study Results Summary")
    table.append("\n| Condition | n | Pop Mean | Pop CV | Comp Mean | Basin A % | Homeostatic |")
    table.append("|-----------|---|----------|--------|-----------|-----------|-------------|")

    for cond_name, cond_data in condition_results.items():
        pop = cond_data['population']
        comp = cond_data['composition']
        basin = cond_data['basin']
        homeostatic = "✅ YES" if cond_data['homeostatic'] else "❌ NO"

        table.append(
            f"| {cond_name:12s} | {cond_data['n_experiments']:2d} | "
            f"{pop['mean']:8.2f} | {pop['cv']:6.1f}% | "
            f"{comp['mean']:9.2f} | {basin['basin_a_pct']:7.1f}% | "
            f"{homeostatic:11s} |"
        )

    return '\n'.join(table)

def generate_detailed_report(condition_results: Dict[str, dict],
                            hypothesis_test: dict,
                            metadata: dict) -> str:
    """Generate detailed analysis report."""
    report = []
    report.append("=" * 80)
    report.append("CYCLE 176 ABLATION STUDY ANALYSIS")
    report.append("=" * 80)
    report.append("")

    # Metadata
    report.append(f"Total Experiments: {metadata.get('total_experiments', 'N/A')}")
    report.append(f"Frequency: {metadata.get('frequency', 'N/A')}%")
    report.append(f"Seeds: {metadata.get('seeds', 'N/A')}")
    report.append(f"Cycles per experiment: {metadata.get('cycles', 'N/A')}")
    report.append(f"Duration: {metadata.get('duration_minutes', 'N/A'):.2f} minutes")
    report.append("")

    # Summary table
    report.append(generate_summary_table(condition_results))
    report.append("")

    # Hypothesis test
    report.append("\n## Hypothesis Test: Birth-Death Coupling Critical for Homeostasis")
    report.append("=" * 80)
    report.append(f"**Verdict:** {hypothesis_test['verdict']}")
    report.append("")
    report.append(f"**Interpretation:**")
    report.append(hypothesis_test['interpretation'])
    report.append("")

    # Conditions tested
    report.append("**Conditions Tested:**")
    for cond, homeostatic in hypothesis_test['conditions_tested'].items():
        status = "✅ Homeostatic" if homeostatic else "❌ Non-homeostatic"
        report.append(f"  - {cond}: {status}")
    report.append("")

    # Detailed condition results
    report.append("\n## Detailed Condition Results")
    report.append("=" * 80)

    for cond_name, cond_data in condition_results.items():
        report.append(f"\n### {cond_name}")
        report.append("-" * 80)
        report.append(f"Classification: {cond_data['classification']}")
        report.append(f"Experiments: n={cond_data['n_experiments']}")
        report.append("")
        report.append("**Population Statistics:**")
        pop = cond_data['population']
        report.append(f"  Mean: {pop['mean']:.2f} ± {pop['std']:.2f} agents")
        report.append(f"  CV: {pop['cv']:.1f}%")
        report.append(f"  Range: [{pop['min']:.1f}, {pop['max']:.1f}]")
        report.append("")
        report.append("**Composition Statistics:**")
        comp = cond_data['composition']
        report.append(f"  Mean: {comp['mean']:.2f} ± {comp['std']:.2f} events/window")
        report.append(f"  CV: {comp['cv']:.1f}%")
        report.append("")
        report.append("**Basin Classification:**")
        basin = cond_data['basin']
        report.append(f"  Basin A: {basin['basin_a_count']}/{cond_data['n_experiments']} ({basin['basin_a_pct']:.1f}%)")
        report.append(f"  Basin B: {basin['basin_b_count']}/{cond_data['n_experiments']} ({100-basin['basin_a_pct']:.1f}%)")
        report.append("")

    return '\n'.join(report)

def main():
    """Main analysis pipeline."""
    # Paths
    results_path = Path('results/cycle176_ablation_study.json')
    output_dir = Path('results')
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("CYCLE 176 ANALYSIS: Ablation Study - Mechanism Isolation")
    print("=" * 80)
    print()

    # Load results
    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        print("   C176 experiment may not have completed yet.")
        sys.exit(1)

    data = load_results(results_path)

    # Analyze each condition
    condition_results = {}

    print("\nAnalyzing conditions...")
    print("-" * 80)

    for condition_name, experiments in data['results'].items():
        result = analyze_condition(condition_name, experiments)
        condition_results[condition_name] = result

        homeostatic_icon = "✅" if result['homeostatic'] else "❌"
        print(f"{homeostatic_icon} {condition_name:15s}: "
              f"Pop={result['population']['mean']:5.1f} (CV={result['population']['cv']:4.1f}%), "
              f"Comp={result['composition']['mean']:5.1f}, "
              f"BasinA={result['basin']['basin_a_pct']:5.1f}%")

    print()

    # Test hypothesis
    print("\nTesting Hypothesis...")
    print("-" * 80)
    hypothesis_test = test_hypothesis(condition_results)

    print(f"Verdict: {hypothesis_test['verdict']}")
    print()
    print(hypothesis_test['interpretation'])
    print()

    # Generate report
    report = generate_detailed_report(
        condition_results,
        hypothesis_test,
        data.get('metadata', {})
    )

    # Save report
    report_path = output_dir / 'cycle176_analysis_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Analysis complete")
    print(f"   Report saved: {report_path}")
    print()

    # Print summary table
    print(generate_summary_table(condition_results))
    print()

    # Save JSON summary
    summary = {
        'condition_results': condition_results,
        'hypothesis_test': hypothesis_test,
        'metadata': data.get('metadata', {})
    }

    summary_path = output_dir / 'cycle176_analysis_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Summary saved: {summary_path}")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
