#!/usr/bin/env python3
"""
Analysis: Cycle 172 Extended Threshold Range Validation

OBJECTIVE: Analyze if linear relationship holds outside validated range [1.5-3.5]

CONTEXT:
- C170 validated linear relationship: critical_freq = 0.98t + 0.04 (R² = 0.9954)
- C172 tests extended thresholds: [0.5, 1.0, 4.0, 5.0, 6.0]
- Question: Does mechanism generalize beyond training range?

ANALYSIS QUESTIONS:
1. Does extended R² remain > 0.99 when including new thresholds?
2. Do new critical frequencies fall within ±0.1% of predictions?
3. Any systematic deviation pattern (indicating nonlinearity)?
4. Publication verdict: Universal mechanism or local artifact?

EXPECTED OUTCOMES:
- If R² > 0.99 with extended data: VALIDATES generalizability
- If new points deviate systematically: MAY INDICATE nonlinearity
- If R² drops significantly: Mechanism limited to tested range
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats


def load_c172_results() -> dict:
    """Load C172 extended range results from JSON file."""
    results_file = Path(__file__).parent / 'results' / 'cycle172_extended_threshold_range.json'

    if not results_file.exists():
        raise FileNotFoundError(f"C172 results not found: {results_file}")

    with open(results_file, 'r') as f:
        return json.load(f)


def analyze_extended_range(results: dict) -> dict:
    """
    Analyze C172 extended range validation results.

    Compare extended linear regression with original C170 validation.
    """

    # Extract metadata
    metadata = results['metadata']
    extended_thresholds = metadata['extended_thresholds']

    # C170 validated parameters (from manuscript)
    C170_SLOPE = 0.98
    C170_INTERCEPT = 0.04
    C170_R_SQUARED = 0.9954
    C170_VALIDATED_RANGE = [1.5, 2.0, 2.5, 3.0, 3.5]

    # Extract threshold analyses from C172 results
    threshold_analyses = results.get('threshold_analyses', {})

    # Collect measured critical frequencies
    thresholds = []
    measured_criticals = []
    predicted_criticals = []
    deviations = []

    for thresh_str, analysis in threshold_analyses.items():
        thresh = float(thresh_str)
        measured_crit = analysis.get('measured_critical')
        predicted_crit = analysis.get('predicted_critical')

        if measured_crit is not None:
            thresholds.append(thresh)
            measured_criticals.append(measured_crit)
            predicted_criticals.append(predicted_crit)
            deviations.append(analysis.get('deviation'))

    # Calculate extended linear regression
    if len(thresholds) >= 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            thresholds, measured_criticals
        )
        r_squared = r_value ** 2

        # Calculate deviations from C170 parameters
        slope_deviation = abs(slope - C170_SLOPE)
        slope_deviation_pct = (slope_deviation / C170_SLOPE) * 100

        intercept_deviation = abs(intercept - C170_INTERCEPT)

        # Separate original vs extended thresholds
        original_thresholds = [t for t in thresholds if t in C170_VALIDATED_RANGE]
        extended_only = [t for t in thresholds if t not in C170_VALIDATED_RANGE]

        extended_regression = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'p_value': p_value,
            'std_err': std_err,
            'n_points': len(thresholds),
            'c170_comparison': {
                'validated_slope': C170_SLOPE,
                'validated_intercept': C170_INTERCEPT,
                'validated_r_squared': C170_R_SQUARED,
                'slope_deviation': slope_deviation,
                'slope_deviation_pct': slope_deviation_pct,
                'intercept_deviation': intercept_deviation,
            },
            'threshold_breakdown': {
                'original_range': original_thresholds,
                'extended_only': extended_only,
                'total_thresholds': len(thresholds)
            }
        }
    else:
        extended_regression = None

    # Calculate prediction accuracy
    prediction_accuracies = []
    for i, thresh in enumerate(thresholds):
        deviation = deviations[i]
        if deviation is not None:
            accuracy = {
                'threshold': thresh,
                'predicted': predicted_criticals[i],
                'measured': measured_criticals[i],
                'deviation': deviation,
                'deviation_pct': (deviation / predicted_criticals[i]) * 100 if predicted_criticals[i] > 0 else 0
            }
            prediction_accuracies.append(accuracy)

    # Determine validation verdict
    if extended_regression:
        r2 = extended_regression['r_squared']
        slope_dev_pct = extended_regression['c170_comparison']['slope_deviation_pct']

        if r2 > 0.99 and slope_dev_pct < 5:
            verdict = "✅ GENERALIZATION VALIDATED"
            verdict_detail = "Linear relationship holds beyond training range with exceptional fit"
            publication_claim = "Universal mechanism confirmed across extended parameter space"
        elif r2 > 0.95 and slope_dev_pct < 10:
            verdict = "✅ STRONG GENERALIZATION"
            verdict_detail = "Linear relationship holds with good fit beyond training range"
            publication_claim = "Mechanism generalizes with minor deviations"
        elif r2 > 0.90:
            verdict = "⚠️  PARTIAL GENERALIZATION"
            verdict_detail = "Linear relationship weakens outside training range"
            publication_claim = "Mechanism shows limitations at parameter extremes"
        else:
            verdict = "❌ GENERALIZATION FAILURE"
            verdict_detail = "Linear relationship breaks down outside training range"
            publication_claim = "Mechanism limited to validated range [1.5-3.5]"
    else:
        verdict = "⚠️  INSUFFICIENT DATA"
        verdict_detail = "Cannot calculate regression (need ≥2 valid points)"
        publication_claim = "Insufficient data for generalization assessment"

    return {
        'extended_regression': extended_regression,
        'prediction_accuracies': prediction_accuracies,
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'publication_claim': publication_claim,
        'thresholds_tested': thresholds,
        'measured_criticals': measured_criticals,
        'c170_parameters': {
            'slope': C170_SLOPE,
            'intercept': C170_INTERCEPT,
            'r_squared': C170_R_SQUARED,
            'validated_range': C170_VALIDATED_RANGE
        }
    }


def print_analysis(analysis: dict):
    """Print detailed analysis results."""

    print("=" * 80)
    print("CYCLE 172 EXTENDED RANGE VALIDATION ANALYSIS")
    print("=" * 80)
    print()
    print("OBJECTIVE: Test if linear relationship generalizes beyond validated range")
    print()

    # Print C170 baseline
    c170_params = analysis['c170_parameters']
    print("C170 VALIDATED PARAMETERS (Training Range [1.5-3.5]):")
    print(f"  Equation: f = {c170_params['slope']}t + {c170_params['intercept']}")
    print(f"  R² = {c170_params['r_squared']}")
    print()

    # Print extended regression
    ext_reg = analysis['extended_regression']
    if ext_reg:
        print("C172 EXTENDED REGRESSION:")
        print(f"  Equation: f = {ext_reg['slope']:.4f}t + {ext_reg['intercept']:.4f}")
        print(f"  R² = {ext_reg['r_squared']:.4f}")
        print(f"  p-value = {ext_reg['p_value']:.6f}")
        print(f"  Number of thresholds: {ext_reg['n_points']}")
        print()

        # Print comparison
        comp = ext_reg['c170_comparison']
        print("COMPARISON WITH C170:")
        print(f"  Slope deviation: {comp['slope_deviation']:.4f} ({comp['slope_deviation_pct']:.2f}%)")
        print(f"  Intercept deviation: {comp['intercept_deviation']:.4f}")
        print(f"  ΔR²: {ext_reg['r_squared'] - c170_params['r_squared']:.4f}")
        print()

        # Print threshold breakdown
        breakdown = ext_reg['threshold_breakdown']
        print("THRESHOLD BREAKDOWN:")
        print(f"  Original range (C170): {breakdown['original_range']}")
        print(f"  Extended only (C172): {breakdown['extended_only']}")
        print(f"  Total: {breakdown['total_thresholds']}")
        print()

    # Print prediction accuracies
    if analysis['prediction_accuracies']:
        print("PREDICTION ACCURACY (THRESHOLD-BY-THRESHOLD):")
        print("-" * 80)
        print(f"{'Threshold':>10} | {'Predicted':>10} | {'Measured':>10} | {'Deviation':>12} | {'Status':>10}")
        print("-" * 80)

        for acc in analysis['prediction_accuracies']:
            if acc['deviation'] <= 0.1:
                status = "✅ EXCELLENT"
            elif acc['deviation'] <= 0.2:
                status = "✅ GOOD"
            elif acc['deviation'] <= 0.3:
                status = "⚠️  ACCEPTABLE"
            else:
                status = "❌ POOR"

            print(f"{acc['threshold']:>9.1f} | {acc['predicted']:>9.2f}% | "
                  f"{acc['measured']:>9.2f}% | {acc['deviation']:>10.2f}% | {status:>10}")

        print()

    # Print verdict
    print("=" * 80)
    print("GENERALIZATION VERDICT")
    print("=" * 80)
    print()
    print(f"Verdict: {analysis['verdict']}")
    print(f"Detail: {analysis['verdict_detail']}")
    print()
    print(f"Publication Claim: {analysis['publication_claim']}")
    print()

    # Print publication implications
    print("PUBLICATION IMPLICATIONS:")
    print()

    if "VALIDATED" in analysis['verdict']:
        print("✅ STRENGTHENS MANUSCRIPT:")
        print("   - Demonstrates mechanism universality beyond training data")
        print("   - Validates predictive power at parameter extremes")
        print("   - Supports 'universal mechanism' claim")
        print("   - Increases confidence in theoretical interpretation")
    elif "STRONG" in analysis['verdict']:
        print("✅ SUPPORTS MANUSCRIPT:")
        print("   - Mechanism generally holds outside training range")
        print("   - Minor deviations acceptable for complex stochastic system")
        print("   - Validates main conclusions with caveats")
    elif "PARTIAL" in analysis['verdict']:
        print("⚠️  REQUIRES DISCUSSION:")
        print("   - Mechanism validity may be range-dependent")
        print("   - Discuss limitations in manuscript")
        print("   - May require additional validation")
    else:
        print("❌ CHALLENGES MANUSCRIPT:")
        print("   - Linear relationship may be local artifact")
        print("   - Need to revise generalization claims")
        print("   - May require reinterpretation of mechanism")

    print()


def save_analysis(analysis: dict, output_file: Path):
    """Save analysis results to JSON."""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis saved: {output_file}")


def main():
    """Run C172 extended range analysis."""

    try:
        # Load C172 results
        print("Loading C172 extended range results...")
        results = load_c172_results()
        print(f"Loaded {results['metadata']['total_experiments']} experiments")
        print()

        # Analyze extended range
        analysis = analyze_extended_range(results)

        # Print analysis
        print_analysis(analysis)

        # Save analysis
        analysis_file = Path(__file__).parent / 'results' / 'cycle172_extended_range_analysis.json'
        save_analysis(analysis, analysis_file)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print()
        print("C172 results not yet available. Run this analysis after C172 completes.")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
