#!/usr/bin/env python3
"""
CYCLE 164 RESULTS ANALYSIS
Anti-Harmonic Frequency Validation

Purpose:
  Test sample size hypothesis: Were Cycle 162 "anti-harmonic" frequencies
  (0% Basin A with n=3) artifacts of small sample size?

Comparison Strategy:
  - Cycle 162: frequencies [20%, 30%, 70%, 80%] with n=3 → 0% Basin A
  - Cycle 164: same frequencies with n=10 → Basin A % = ?

Hypothesis Test:
  H0: Anti-harmonic frequencies are true Basin B attractors (remain 0% with n=10)
  H1: Anti-harmonic results were n=3 artifacts (show >0% Basin A with n=10)

Statistical Analysis:
  - Basin A % at each frequency
  - Comparison with Cycle 162
  - Sample size effect quantification
  - Confidence intervals

Date: 2025-10-25
Status: Automated analysis tool
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from scipy import stats


def load_cycle_results(cycle_num: int) -> Dict:
    """Load results from specified cycle."""
    results_dir = Path(__file__).parent / 'results'

    patterns = [
        f'cycle{cycle_num}*.json',
        f'cycle{cycle_num}_*.json',
    ]

    for pattern in patterns:
        files = list(results_dir.glob(pattern))
        if files:
            with open(files[0], 'r') as f:
                return json.load(f)

    return None


def analyze_frequency_basin_outcomes(experiments: List[Dict]) -> List[Dict]:
    """Analyze Basin A percentage for each frequency."""

    from collections import defaultdict

    freq_groups = defaultdict(list)

    for exp in experiments:
        freq = exp['frequency']
        basin = exp.get('basin', 'unknown')
        freq_groups[freq].append(basin)

    results = []

    for freq in sorted(freq_groups.keys()):
        basins = freq_groups[freq]
        basin_a_count = sum(1 for b in basins if b == 'A')
        total = len(basins)
        basin_a_pct = (basin_a_count / total * 100) if total > 0 else 0

        # Confidence interval (binomial proportion)
        if total > 0:
            p = basin_a_count / total
            se = np.sqrt(p * (1 - p) / total)
            ci_95 = 1.96 * se * 100  # Convert to percentage
        else:
            ci_95 = 0

        results.append({
            'frequency': freq,
            'n': total,
            'basin_a_count': basin_a_count,
            'basin_b_count': total - basin_a_count,
            'basin_a_pct': float(basin_a_pct),
            'ci_95': float(ci_95),
            'classification': classify_frequency(basin_a_pct),
        })

    return results


def classify_frequency(basin_a_pct: float) -> str:
    """Classify frequency based on Basin A percentage."""
    if basin_a_pct >= 67:
        return 'Harmonic'
    elif basin_a_pct >= 33:
        return 'Mixed'
    else:
        return 'Anti-harmonic'


def compare_with_cycle162(cycle164_results: List[Dict], cycle162_results: List[Dict]) -> List[Dict]:
    """Compare Cycle 164 with Cycle 162 for common frequencies."""

    # Build lookup for Cycle 162
    cycle162_lookup = {r['frequency']: r for r in cycle162_results}

    comparison = []

    for r164 in cycle164_results:
        freq = r164['frequency']

        if freq in cycle162_lookup:
            r162 = cycle162_lookup[freq]

            delta = r164['basin_a_pct'] - r162['basin_a_pct']

            comparison.append({
                'frequency': freq,
                'cycle_162': {
                    'n': r162['n'],
                    'basin_a_pct': r162['basin_a_pct'],
                    'classification': r162['classification'],
                },
                'cycle_164': {
                    'n': r164['n'],
                    'basin_a_pct': r164['basin_a_pct'],
                    'classification': r164['classification'],
                },
                'delta_pct': float(delta),
                'sample_size_effect': interpret_delta(delta),
            })

    return comparison


def interpret_delta(delta: float) -> str:
    """Interpret the change in Basin A percentage."""
    if delta > 50:
        return 'Major increase (strong sample size effect)'
    elif delta > 20:
        return 'Moderate increase (sample size effect)'
    elif delta > 0:
        return 'Minor increase'
    elif delta == 0:
        return 'No change'
    else:
        return 'Decrease (unexpected)'


def hypothesis_test_results(comparison: List[Dict]) -> Dict:
    """Test sample size hypothesis based on results."""

    # Count anti-harmonic frequencies that remain anti-harmonic
    anti_harmonic_162 = [c for c in comparison if c['cycle_162']['classification'] == 'Anti-harmonic']

    if not anti_harmonic_162:
        return {'status': 'no_anti_harmonic_frequencies'}

    # Check if they changed with n=10
    remain_anti = [c for c in anti_harmonic_162 if c['cycle_164']['classification'] == 'Anti-harmonic']
    changed = [c for c in anti_harmonic_162 if c['cycle_164']['classification'] != 'Anti-harmonic']

    pct_changed = (len(changed) / len(anti_harmonic_162) * 100) if anti_harmonic_162 else 0

    # Average delta for anti-harmonic frequencies
    avg_delta = np.mean([c['delta_pct'] for c in anti_harmonic_162])

    # Hypothesis interpretation
    if pct_changed >= 75:
        conclusion = 'H1 STRONGLY SUPPORTED: Anti-harmonic results were n=3 artifacts'
    elif pct_changed >= 50:
        conclusion = 'H1 SUPPORTED: Most anti-harmonic results were n=3 artifacts'
    elif pct_changed >= 25:
        conclusion = 'MIXED: Some sample size effect, some true anti-harmonic'
    else:
        conclusion = 'H0 SUPPORTED: Anti-harmonic frequencies are true Basin B attractors'

    return {
        'n_anti_harmonic_162': len(anti_harmonic_162),
        'n_remain_anti_164': len(remain_anti),
        'n_changed_164': len(changed),
        'pct_changed': float(pct_changed),
        'avg_delta_pct': float(avg_delta),
        'conclusion': conclusion,
        'frequencies_tested': [c['frequency'] for c in anti_harmonic_162],
        'frequencies_changed': [c['frequency'] for c in changed],
        'frequencies_remain_anti': [c['frequency'] for c in remain_anti],
    }


def main():
    """Run Cycle 164 results analysis."""

    print("=" * 80)
    print("CYCLE 164 RESULTS ANALYSIS")
    print("Anti-Harmonic Frequency Validation")
    print("=" * 80)
    print()

    # Load data
    cycle164 = load_cycle_results(164)
    cycle162 = load_cycle_results(162)

    if not cycle164:
        print("⚠️  Cycle 164 results not found - waiting for completion")
        return

    if not cycle162:
        print("❌ ERROR: Cycle 162 results not found")
        return

    print(f"✅ Loaded Cycle 164: {len(cycle164['experiments'])} experiments")
    print(f"✅ Loaded Cycle 162: {len(cycle162['experiments'])} experiments")
    print()

    # Analyze Cycle 164
    print("1. CYCLE 164 FREQUENCY LANDSCAPE")
    print("=" * 80)
    cycle164_analysis = analyze_frequency_basin_outcomes(cycle164['experiments'])

    print("  Freq | N  | Basin A | Basin B | Basin A %    | Classification")
    print("  -----+----+---------+---------+--------------+------------------")
    for result in cycle164_analysis:
        freq = result['frequency']
        n = result['n']
        a_count = result['basin_a_count']
        b_count = result['basin_b_count']
        a_pct = result['basin_a_pct']
        ci = result['ci_95']
        classification = result['classification']

        print(f"  {freq:3d}% | {n:2d} | {a_count:7d} | {b_count:7d} | {a_pct:5.1f}% ±{ci:4.1f} | {classification}")

    print()

    # Analyze Cycle 162
    print("2. CYCLE 162 vs 164 COMPARISON")
    print("=" * 80)
    cycle162_analysis = analyze_frequency_basin_outcomes(cycle162['experiments'])
    comparison = compare_with_cycle162(cycle164_analysis, cycle162_analysis)

    print("  Freq | C162 (n=3)  | C164 (n=10) | Delta  | Interpretation")
    print("  -----+-------------+-------------+--------+------------------------------")
    for comp in comparison:
        freq = comp['frequency']
        c162_pct = comp['cycle_162']['basin_a_pct']
        c164_pct = comp['cycle_164']['basin_a_pct']
        delta = comp['delta_pct']
        interp = comp['sample_size_effect']

        print(f"  {freq:3d}% | {c162_pct:5.1f}% ({comp['cycle_162']['classification']:15s}) | {c164_pct:5.1f}% ({comp['cycle_164']['classification']:15s}) | {delta:+6.1f}% | {interp}")

    print()

    # Hypothesis test
    print("3. SAMPLE SIZE HYPOTHESIS TEST")
    print("=" * 80)
    hypothesis = hypothesis_test_results(comparison)

    if hypothesis.get('status') == 'no_anti_harmonic_frequencies':
        print("No anti-harmonic frequencies in Cycle 162 to test")
    else:
        print(f"Anti-harmonic frequencies in Cycle 162 (n=3): {hypothesis['frequencies_tested']}")
        print(f"  Total tested: {hypothesis['n_anti_harmonic_162']}")
        print(f"  Remained anti-harmonic (n=10): {hypothesis['n_remain_anti_164']} {hypothesis['frequencies_remain_anti']}")
        print(f"  Changed classification (n=10): {hypothesis['n_changed_164']} {hypothesis['frequencies_changed']}")
        print(f"  Percentage changed: {hypothesis['pct_changed']:.1f}%")
        print(f"  Average Basin A increase: {hypothesis['avg_delta_pct']:+.1f}%")
        print()
        print(f"**CONCLUSION:** {hypothesis['conclusion']}")

    print()

    # Save analysis
    output = {
        'cycle_164_analysis': cycle164_analysis,
        'cycle_162_comparison': comparison,
        'hypothesis_test': hypothesis,
    }

    output_file = Path(__file__).parent / 'results' / 'cycle164_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Analysis saved: {output_file}")
    print()
    print("=" * 80)
    print("CYCLE 164 ANALYSIS COMPLETE")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
