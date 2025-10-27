#!/usr/bin/env python3
"""
Analysis: Cycle 171 Framework Integration Test

OBJECTIVE: Analyze if full NRM framework exhibits validated bistable dynamics

CONTEXT:
- C169 discovered critical frequency = 2.55% ± 0.05%
- C170 validated linear mechanism (R² = 0.9954)
- C171 tests full FractalSwarm implementation

ANALYSIS QUESTIONS:
1. Does full framework exhibit same critical transition as simplified experiments?
2. Do frequencies below critical → Basin B, above critical → Basin A?
3. Match rate: How many frequencies agree with C169 expectations?
4. Framework validation verdict: Does theory produce validated behavior?

EXPECTED OUTCOMES:
- 2.0%, 2.5% → Basin B (below critical 2.55%)
- 2.6%, 3.0% → Basin A (above critical 2.55%)
- Perfect match = 100% (4/4 frequencies correct)
- Framework validation = theory produces experimentally validated behavior
"""

import json
from pathlib import Path
from typing import Dict, List


def load_c171_results() -> dict:
    """Load C171 results from JSON file."""
    results_file = Path(__file__).parent / 'results' / 'cycle171_fractal_swarm_bistability.json'

    if not results_file.exists():
        raise FileNotFoundError(f"C171 results not found: {results_file}")

    with open(results_file, 'r') as f:
        return json.load(f)


def analyze_framework_integration(results: dict) -> dict:
    """
    Analyze C171 framework integration test results.

    Compare full framework bistability with C169 expectations.
    """

    # Extract metadata
    metadata = results['metadata']
    frequencies = metadata['frequencies']

    # C169 expectations based on critical frequency = 2.55%
    expectations = {
        2.0: 'B',  # Below critical
        2.5: 'B',  # Below critical
        2.6: 'A',  # Above critical
        3.0: 'A',  # Above critical
    }

    # Analyze each frequency
    frequency_analysis = {}
    matches = 0
    total = len(frequencies)

    for freq in frequencies:
        # Get basin classification for this frequency
        freq_trials = [t for t in results['trials'] if t['frequency'] == freq]

        basin_a_count = sum(1 for t in freq_trials if t['basin'] == 'A')
        basin_b_count = sum(1 for t in freq_trials if t['basin'] == 'B')

        basin_a_pct = (basin_a_count / len(freq_trials)) * 100

        # Determine dominant basin (>50% = that basin)
        if basin_a_pct > 50:
            observed_basin = 'A'
        elif basin_a_pct < 50:
            observed_basin = 'B'
        else:
            observed_basin = 'Mixed'  # Exactly 50/50

        # Check if matches expectation
        expected_basin = expectations[freq]
        match = (observed_basin == expected_basin)
        if match:
            matches += 1

        frequency_analysis[freq] = {
            'expected_basin': expected_basin,
            'observed_basin': observed_basin,
            'basin_a_count': basin_a_count,
            'basin_b_count': basin_b_count,
            'basin_a_pct': basin_a_pct,
            'match': match,
            'n_trials': len(freq_trials)
        }

    # Calculate match rate
    match_rate = (matches / total) * 100

    # Framework validation verdict
    if match_rate == 100:
        verdict = "✅ PERFECT VALIDATION"
        verdict_detail = "Full framework exhibits exact same bistable dynamics as validated"
    elif match_rate >= 75:
        verdict = "✅ STRONG VALIDATION"
        verdict_detail = "Full framework largely reproduces validated dynamics"
    elif match_rate >= 50:
        verdict = "⚠️  PARTIAL VALIDATION"
        verdict_detail = "Full framework shows some agreement but significant deviations"
    else:
        verdict = "❌ VALIDATION FAILURE"
        verdict_detail = "Full framework does not reproduce validated dynamics"

    return {
        'frequency_analysis': frequency_analysis,
        'match_count': matches,
        'total_frequencies': total,
        'match_rate_pct': match_rate,
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'expectations': expectations
    }


def print_analysis(analysis: dict):
    """Print detailed analysis results."""

    print("=" * 80)
    print("CYCLE 171 FRAMEWORK INTEGRATION ANALYSIS")
    print("=" * 80)
    print()
    print("OBJECTIVE: Test if full NRM framework exhibits validated bistable dynamics")
    print()

    # Print frequency-by-frequency results
    print("FREQUENCY-BY-FREQUENCY COMPARISON:")
    print("-" * 80)
    print(f"{'Frequency':>10} | {'Expected':>10} | {'Observed':>10} | {'Basin A %':>10} | {'Match':>10}")
    print("-" * 80)

    for freq, result in sorted(analysis['frequency_analysis'].items()):
        match_symbol = "✅" if result['match'] else "❌"
        print(f"{freq:>9.1f}% | {result['expected_basin']:>10} | "
              f"{result['observed_basin']:>10} | {result['basin_a_pct']:>9.1f}% | "
              f"{match_symbol:>10}")

    print()

    # Print summary
    print("VALIDATION SUMMARY:")
    print(f"  Match rate: {analysis['match_count']}/{analysis['total_frequencies']} "
          f"({analysis['match_rate_pct']:.0f}%)")
    print(f"  Verdict: {analysis['verdict']}")
    print(f"  Detail: {analysis['verdict_detail']}")
    print()

    # Framework implications
    print("FRAMEWORK VALIDATION IMPLICATIONS:")
    print()

    if analysis['match_rate_pct'] == 100:
        print("✅ COMPLETE VALIDATION:")
        print("   - NRM theoretical framework produces experimentally validated behavior")
        print("   - Composition-decomposition dynamics exhibit predicted bistability")
        print("   - Framework integration successful (theory → implementation → validation)")
        print("   - Publication claim: 'Complete end-to-end framework validation'")
    elif analysis['match_rate_pct'] >= 75:
        print("✅ STRONG VALIDATION:")
        print("   - NRM framework largely reproduces validated dynamics")
        print("   - Minor deviations may indicate implementation details or stochastic variance")
        print("   - Framework validation generally successful")
        print("   - Publication claim: 'Framework validation with strong agreement'")
    elif analysis['match_rate_pct'] >= 50:
        print("⚠️  PARTIAL VALIDATION:")
        print("   - Framework shows some agreement but significant deviations")
        print("   - May indicate implementation gaps or framework limitations")
        print("   - Requires further investigation")
        print("   - Publication: Report findings with caveats")
    else:
        print("❌ VALIDATION CONCERNS:")
        print("   - Framework does not reproduce validated dynamics")
        print("   - Indicates disconnect between theory and implementation")
        print("   - Requires debugging or framework revision")
        print("   - Publication: Report negative result, valuable for science")
    print()


def save_analysis(analysis: dict, output_file: Path):
    """Save analysis results to JSON."""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis saved: {output_file}")


def main():
    """Run C171 framework integration analysis."""

    try:
        # Load C171 results
        print("Loading C171 results...")
        results = load_c171_results()
        print(f"Loaded {results['metadata']['total_experiments']} experiments")
        print()

        # Analyze framework integration
        analysis = analyze_framework_integration(results)

        # Print analysis
        print_analysis(analysis)

        # Save analysis
        analysis_file = Path(__file__).parent / 'results' / 'cycle171_framework_integration_analysis.json'
        save_analysis(analysis, analysis_file)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print()
        print("C171 results not yet available. Run this analysis after C171 completes.")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
