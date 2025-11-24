#!/usr/bin/env python3
"""
CYCLE 162 vs 163 COMPARATIVE ANALYSIS
Investigate dramatic shift: Mixed basins → Universal Basin A

Key Question: Why did Cycle 163 show 100% Basin A when Cycle 162 was mixed?

Hypotheses:
  H1: Frequency range effect (Cycle 162 included 1%, 20%, 30%, 70%, 80%)
  H2: Sample size effect (Cycle 163 had 10 seeds vs 3)
  H3: Experimental drift or system parameter change
  H4: Basin threshold classification difference

Date: 2025-10-25
Status: Diagnostic comparison tool
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List


def load_cycle_results(cycle_num: int) -> Dict:
    """Load results from specified cycle."""
    results_dir = Path(__file__).parent / 'results'

    # Try different file patterns
    patterns = [
        f'cycle{cycle_num}*.json',
        f'cycle{cycle_num}_*.json',
    ]

    for pattern in patterns:
        files = list(results_dir.glob(pattern))
        if files:
            with open(files[0], 'r') as f:
                data = json.load(f)
            return data

    return None


def compare_basin_distributions(cycle162: Dict, cycle163: Dict) -> Dict:
    """Compare Basin A/B distributions between cycles."""

    exp162 = cycle162['experiments']
    exp163 = cycle163['experiments']

    # Count basin outcomes
    basin_a_162 = sum(1 for exp in exp162 if exp.get('basin') == 'A')
    basin_b_162 = len(exp162) - basin_a_162

    basin_a_163 = sum(1 for exp in exp163 if exp.get('basin') == 'A')
    basin_b_163 = len(exp163) - basin_a_163

    return {
        'cycle_162': {
            'total': len(exp162),
            'basin_a': basin_a_162,
            'basin_b': basin_b_162,
            'basin_a_pct': (basin_a_162 / len(exp162) * 100) if exp162 else 0,
        },
        'cycle_163': {
            'total': len(exp163),
            'basin_a': basin_a_163,
            'basin_b': basin_b_163,
            'basin_a_pct': (basin_a_163 / len(exp163) * 100) if exp163 else 0,
        },
        'shift': {
            'delta_basin_a': basin_a_163 - basin_a_162,
            'delta_basin_a_pct': (basin_a_163 / len(exp163) * 100) - (basin_a_162 / len(exp162) * 100) if exp162 and exp163 else 0,
        }
    }


def compare_frequency_ranges(cycle162: Dict, cycle163: Dict) -> Dict:
    """Compare frequency ranges tested in each cycle."""

    exp162 = cycle162['experiments']
    exp163 = cycle163['experiments']

    freq162 = sorted(set(exp['frequency'] for exp in exp162))
    freq163 = sorted(set(exp['frequency'] for exp in exp163))

    return {
        'cycle_162_frequencies': freq162,
        'cycle_163_frequencies': freq163,
        'common_frequencies': sorted(set(freq162) & set(freq163)),
        'cycle_162_unique': sorted(set(freq162) - set(freq163)),
        'cycle_163_unique': sorted(set(freq163) - set(freq163)),
    }


def analyze_common_frequencies(cycle162: Dict, cycle163: Dict) -> List[Dict]:
    """Analyze basin outcomes for frequencies tested in both cycles."""

    exp162 = cycle162['experiments']
    exp163 = cycle163['experiments']

    # Get common frequencies
    freq162 = set(exp['frequency'] for exp in exp162)
    freq163 = set(exp['frequency'] for exp in exp163)
    common = sorted(freq162 & freq163)

    results = []

    for freq in common:
        # Cycle 162 results for this frequency
        freq_exp162 = [exp for exp in exp162 if exp['frequency'] == freq]
        basin_a_162 = sum(1 for exp in freq_exp162 if exp.get('basin') == 'A')
        pct_162 = (basin_a_162 / len(freq_exp162) * 100) if freq_exp162 else 0

        # Cycle 163 results for this frequency
        freq_exp163 = [exp for exp in exp163 if exp['frequency'] == freq]
        basin_a_163 = sum(1 for exp in freq_exp163 if exp.get('basin') == 'A')
        pct_163 = (basin_a_163 / len(freq_exp163) * 100) if freq_exp163 else 0

        results.append({
            'frequency': freq,
            'cycle_162': {
                'n': len(freq_exp162),
                'basin_a': basin_a_162,
                'basin_a_pct': pct_162,
            },
            'cycle_163': {
                'n': len(freq_exp163),
                'basin_a': basin_a_163,
                'basin_a_pct': pct_163,
            },
            'delta_pct': pct_163 - pct_162,
        })

    return results


def main():
    """Run Cycle 162 vs 163 comparative analysis."""

    print("=" * 80)
    print("CYCLE 162 vs 163 COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    cycle162 = load_cycle_results(162)
    cycle163 = load_cycle_results(163)

    if not cycle162 or not cycle163:
        print("ERROR: Could not load one or both cycle results")
        return

    print(f"Cycle 162: {len(cycle162['experiments'])} experiments")
    print(f"Cycle 163: {len(cycle163['experiments'])} experiments")
    print()

    # Basin distribution comparison
    print("1. BASIN DISTRIBUTION COMPARISON")
    print("=" * 80)
    basin_comp = compare_basin_distributions(cycle162, cycle163)

    print(f"Cycle 162: {basin_comp['cycle_162']['basin_a']}/{basin_comp['cycle_162']['total']} Basin A ({basin_comp['cycle_162']['basin_a_pct']:.1f}%)")
    print(f"Cycle 163: {basin_comp['cycle_163']['basin_a']}/{basin_comp['cycle_163']['total']} Basin A ({basin_comp['cycle_163']['basin_a_pct']:.1f}%)")
    print(f"SHIFT: +{basin_comp['shift']['delta_basin_a_pct']:.1f}% Basin A")
    print()

    # Frequency range comparison
    print("2. FREQUENCY RANGE COMPARISON")
    print("=" * 80)
    freq_comp = compare_frequency_ranges(cycle162, cycle163)

    print(f"Cycle 162 frequencies: {freq_comp['cycle_162_frequencies']}")
    print(f"Cycle 163 frequencies: {freq_comp['cycle_163_frequencies']}")
    print(f"Common frequencies: {freq_comp['common_frequencies']}")
    print(f"Cycle 162 unique: {freq_comp['cycle_162_unique']}")
    print()

    # Common frequency analysis
    print("3. COMMON FREQUENCY BASIN OUTCOMES")
    print("=" * 80)
    common_analysis = analyze_common_frequencies(cycle162, cycle163)

    print("  Freq | C162 Basin A | C163 Basin A | Delta")
    print("  -----+--------------+--------------+--------")
    for result in common_analysis:
        freq = result['frequency']
        c162_pct = result['cycle_162']['basin_a_pct']
        c163_pct = result['cycle_163']['basin_a_pct']
        delta = result['delta_pct']

        print(f"  {freq:3d}% | {c162_pct:5.1f}% ({result['cycle_162']['basin_a']}/{result['cycle_162']['n']}) | {c163_pct:5.1f}% ({result['cycle_163']['basin_a']}/{result['cycle_163']['n']}) | {delta:+6.1f}%")

    print()

    # Interpretation
    print("4. INTERPRETATION")
    print("=" * 80)

    avg_delta = np.mean([r['delta_pct'] for r in common_analysis])

    if basin_comp['cycle_163']['basin_a_pct'] == 100:
        print("✅ UNIVERSAL BASIN A CONVERGENCE in Cycle 163")
        print("   All 50 experiments converged to Basin A regardless of frequency/seed")
        print()
        print("   Possible Causes:")
        print("   1. Sample size effect: 10 seeds >> 3 seeds reveals true attractor")
        print("   2. Frequency range: 5-95% range biased toward Basin A frequencies")
        print("   3. System parameter drift between cycles")
        print("   4. Basin threshold correctly calibrated (all above 2.5)")
    else:
        print(f"Cycle 163 showed {basin_comp['cycle_163']['basin_a_pct']:.1f}% Basin A")
        print(f"Average shift across common frequencies: {avg_delta:+.1f}%")

    print()

    # Save analysis
    output = {
        'basin_comparison': basin_comp,
        'frequency_comparison': freq_comp,
        'common_frequency_analysis': common_analysis,
        'interpretation': {
            'cycle_163_universal_basin_a': basin_comp['cycle_163']['basin_a_pct'] == 100,
            'average_delta_pct': float(avg_delta),
        }
    }

    output_file = Path(__file__).parent / 'results' / 'cycle162_163_comparison.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Comparison saved: {output_file}")
    print()


if __name__ == '__main__':
    main()
