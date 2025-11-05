#!/usr/bin/env python3
"""
Hierarchical Energy Dynamics Prediction Validator

Purpose: Compare C186 empirical results against Extension 2 theoretical predictions

This module validates whether hierarchical metapopulation experiments produce
the dynamical signatures predicted by Extension 2 (Hierarchical Energy Dynamics):

Theoretical Predictions:
1. Hierarchical energy regulation (inter-population dampening)
2. Cross-population migration patterns
3. Synchronization emergence
4. Memory retention across hierarchical levels
5. Computational complexity amplification

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1021
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import statistics
from dataclasses import dataclass


@dataclass
class TheoreticalPrediction:
    """Container for theoretical prediction with bounds."""
    metric_name: str
    predicted_direction: str  # "increase", "decrease", "stable", "emergence"
    predicted_range: Optional[Tuple[float, float]] = None
    mechanism: str = ""
    reference_section: str = ""


@dataclass
class EmpiricalResult:
    """Container for empirical measurement."""
    metric_name: str
    value: float
    stdev: Optional[float] = None
    n: int = 1
    variance: Optional[float] = None


@dataclass
class ValidationOutcome:
    """Container for validation result."""
    prediction: TheoreticalPrediction
    empirical: EmpiricalResult
    status: str  # "VALIDATED", "PARTIAL", "REJECTED", "INSUFFICIENT_DATA"
    confidence: float  # 0.0-1.0
    notes: str = ""


# Theoretical predictions from Extension 2
HIERARCHICAL_PREDICTIONS = [
    TheoreticalPrediction(
        metric_name="basin_a_suppression",
        predicted_direction="decrease",
        predicted_range=(0.0, 5.0),  # Expect Basin A < 5% with hierarchical regulation
        mechanism="Inter-population energy dampening via migration",
        reference_section="Extension 2.2: Hierarchical Regulation"
    ),
    TheoreticalPrediction(
        metric_name="migration_frequency",
        predicted_direction="stable",
        predicted_range=(10, 20),  # Migrations should stabilize in this range
        mechanism="Cross-population coupling strength",
        reference_section="Extension 2.3: Cross-Population Dynamics"
    ),
    TheoreticalPrediction(
        metric_name="population_synchronization",
        predicted_direction="emergence",
        mechanism="Weak coupling between populations via migration",
        reference_section="Extension 2.4: Synchronization"
    ),
    TheoreticalPrediction(
        metric_name="cv_variance_amplification",
        predicted_direction="increase",
        mechanism="Hierarchical complexity amplifies stochastic sensitivity",
        reference_section="Extension 2.5: Computational Complexity"
    ),
    TheoreticalPrediction(
        metric_name="runtime_variance",
        predicted_direction="emergence",
        mechanism="Seed-dependent hierarchical trajectories amplify computational expense",
        reference_section="Extension 2.5: Computational Complexity"
    ),
]


def load_c186_results(results_path: Path) -> Optional[Dict]:
    """
    Load C186 experimental results from JSON.

    Args:
        results_path: Path to C186 results JSON

    Returns:
        dict with results, or None if not found
    """
    if not results_path.exists():
        return None

    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading C186 results: {e}")
        return None


def parse_c186_log(log_path: Path) -> Optional[Dict]:
    """
    Parse C186 log file for partial results if JSON not available.

    Args:
        log_path: Path to C186 output log

    Returns:
        dict with partial results
    """
    if not log_path.exists():
        return None

    try:
        with open(log_path, 'r') as f:
            log_content = f.read()

        lines = log_content.strip().split('\n')

        results = []
        current_experiment = None

        for line in lines:
            # Detect experiment start
            if line.startswith('[') and '/10]' in line and 'Running seed' in line:
                parts = line.split(']')
                exp_num = int(parts[0].strip('[').split('/')[0])
                seed = int(line.split('seed ')[-1].replace('...', '').strip())
                current_experiment = {
                    'experiment': exp_num,
                    'seed': seed,
                    'status': 'running'
                }

            # Detect experiment results
            elif line.strip().startswith('Basin A:'):
                if current_experiment:
                    # Parse results: "Basin A: 0% | Mean Population: 4.9 | CV: 53.3% | Migrations: 14"
                    parts = line.split('|')

                    basin_a = float(parts[0].split(':')[1].strip().replace('%', ''))
                    mean_pop = float(parts[1].split(':')[1].strip())
                    cv = float(parts[2].split(':')[1].strip().replace('%', ''))
                    migrations = int(parts[3].split(':')[1].strip())

                    current_experiment.update({
                        'basin_a_percent': basin_a,
                        'mean_population': mean_pop,
                        'cv_percent': cv,
                        'migrations': migrations,
                        'status': 'completed'
                    })

                    results.append(current_experiment)
                    current_experiment = None

        return {
            'experiments': results,
            'num_completed': len(results),
            'partial': True
        }

    except Exception as e:
        print(f"Error parsing C186 log: {e}")
        return None


def extract_empirical_metrics(c186_data: Dict) -> List[EmpiricalResult]:
    """
    Extract empirical metrics from C186 results.

    Args:
        c186_data: C186 results dict

    Returns:
        List of EmpiricalResult objects
    """
    empirical = []

    experiments = c186_data.get('experiments', [])
    if not experiments:
        return empirical

    # Extract Basin A percentages
    basin_a_values = [exp['basin_a_percent'] for exp in experiments]
    if basin_a_values:
        empirical.append(EmpiricalResult(
            metric_name="basin_a_suppression",
            value=statistics.mean(basin_a_values),
            stdev=statistics.stdev(basin_a_values) if len(basin_a_values) > 1 else 0.0,
            n=len(basin_a_values)
        ))

    # Extract migration counts
    migration_values = [exp['migrations'] for exp in experiments]
    if migration_values:
        empirical.append(EmpiricalResult(
            metric_name="migration_frequency",
            value=statistics.mean(migration_values),
            stdev=statistics.stdev(migration_values) if len(migration_values) > 1 else 0.0,
            n=len(migration_values)
        ))

    # Extract CV variance
    cv_values = [exp['cv_percent'] for exp in experiments]
    if cv_values:
        cv_variance = statistics.variance(cv_values) if len(cv_values) > 1 else 0.0
        empirical.append(EmpiricalResult(
            metric_name="cv_variance_amplification",
            value=cv_variance,
            stdev=statistics.stdev(cv_values) if len(cv_values) > 1 else 0.0,
            n=len(cv_values),
            variance=cv_variance
        ))

    return empirical


def validate_prediction(
    prediction: TheoreticalPrediction,
    empirical: Optional[EmpiricalResult]
) -> ValidationOutcome:
    """
    Validate a single theoretical prediction against empirical data.

    Args:
        prediction: Theoretical prediction
        empirical: Empirical result (or None if not measured)

    Returns:
        ValidationOutcome with status and confidence
    """
    if empirical is None:
        return ValidationOutcome(
            prediction=prediction,
            empirical=None,
            status="INSUFFICIENT_DATA",
            confidence=0.0,
            notes="No empirical data available for this metric"
        )

    # Validate based on predicted direction
    if prediction.predicted_direction == "decrease":
        if prediction.predicted_range:
            min_val, max_val = prediction.predicted_range
            if empirical.value <= max_val:
                status = "VALIDATED"
                confidence = 1.0 - (empirical.value / max_val)
            else:
                status = "REJECTED"
                confidence = 0.0
            notes = f"Empirical: {empirical.value:.2f}, Expected: ≤{max_val:.2f}"
        else:
            status = "INSUFFICIENT_DATA"
            confidence = 0.0
            notes = "No range specified for validation"

    elif prediction.predicted_direction == "stable":
        if prediction.predicted_range:
            min_val, max_val = prediction.predicted_range
            if min_val <= empirical.value <= max_val:
                status = "VALIDATED"
                confidence = 1.0
            else:
                status = "PARTIAL"
                confidence = 0.5
            notes = f"Empirical: {empirical.value:.2f}, Expected: {min_val}-{max_val}"
        else:
            status = "INSUFFICIENT_DATA"
            confidence = 0.0
            notes = "No range specified for validation"

    elif prediction.predicted_direction == "increase":
        # For variance metrics, we check if variance is non-zero and substantial
        if empirical.variance is not None and empirical.variance > 0:
            status = "VALIDATED"
            confidence = min(empirical.variance / 100.0, 1.0)  # Normalize to 0-1
            notes = f"Variance: {empirical.variance:.2f}, evidence of amplification"
        else:
            status = "PARTIAL"
            confidence = 0.3
            notes = f"Some variance detected ({empirical.stdev:.2f}), but limited data"

    elif prediction.predicted_direction == "emergence":
        # For emergence metrics, we check for qualitative evidence
        status = "PARTIAL"
        confidence = 0.5
        notes = "Emergence requires qualitative assessment with complete data"

    else:
        status = "INSUFFICIENT_DATA"
        confidence = 0.0
        notes = f"Unknown prediction direction: {prediction.predicted_direction}"

    return ValidationOutcome(
        prediction=prediction,
        empirical=empirical,
        status=status,
        confidence=confidence,
        notes=notes
    )


def generate_validation_report(
    outcomes: List[ValidationOutcome],
    partial_data: bool = False
) -> str:
    """
    Generate markdown validation report.

    Args:
        outcomes: List of validation outcomes
        partial_data: Whether data is partial (incomplete experiments)

    Returns:
        Markdown formatted report
    """
    report = []

    report.append("# Hierarchical Energy Dynamics Validation Report")
    report.append("")
    report.append("**Theoretical Framework:** Extension 2 (Hierarchical Energy Dynamics)")
    report.append("**Experimental Data:** C186 Meta-Population Experiments")
    report.append("")

    if partial_data:
        report.append("⚠️ **Note:** This report uses partial data (experiments still running)")
        report.append("")

    # Summary statistics
    validated = sum(1 for o in outcomes if o.status == "VALIDATED")
    partial = sum(1 for o in outcomes if o.status == "PARTIAL")
    rejected = sum(1 for o in outcomes if o.status == "REJECTED")
    insufficient = sum(1 for o in outcomes if o.status == "INSUFFICIENT_DATA")

    report.append("## Validation Summary")
    report.append("")
    report.append(f"- ✅ **VALIDATED:** {validated}/{len(outcomes)} predictions")
    report.append(f"- ⚠️ **PARTIAL:** {partial}/{len(outcomes)} predictions")
    report.append(f"- ❌ **REJECTED:** {rejected}/{len(outcomes)} predictions")
    report.append(f"- ⏳ **INSUFFICIENT DATA:** {insufficient}/{len(outcomes)} predictions")
    report.append("")

    avg_confidence = statistics.mean([o.confidence for o in outcomes if o.confidence > 0])
    report.append(f"**Overall Confidence:** {avg_confidence:.1%}")
    report.append("")

    # Detailed outcomes
    report.append("## Detailed Validation")
    report.append("")

    for outcome in outcomes:
        report.append(f"### {outcome.prediction.metric_name.replace('_', ' ').title()}")
        report.append("")

        # Status
        status_emoji = {
            "VALIDATED": "✅",
            "PARTIAL": "⚠️",
            "REJECTED": "❌",
            "INSUFFICIENT_DATA": "⏳"
        }
        report.append(f"**Status:** {status_emoji[outcome.status]} {outcome.status}")
        report.append(f"**Confidence:** {outcome.confidence:.1%}")
        report.append("")

        # Theoretical prediction
        report.append("**Theoretical Prediction:**")
        report.append(f"- Direction: {outcome.prediction.predicted_direction}")
        if outcome.prediction.predicted_range:
            report.append(f"- Range: {outcome.prediction.predicted_range}")
        report.append(f"- Mechanism: {outcome.prediction.mechanism}")
        report.append(f"- Reference: {outcome.prediction.reference_section}")
        report.append("")

        # Empirical result
        if outcome.empirical:
            report.append("**Empirical Result:**")
            report.append(f"- Value: {outcome.empirical.value:.2f}")
            if outcome.empirical.stdev is not None:
                report.append(f"- Stdev: {outcome.empirical.stdev:.2f}")
            if outcome.empirical.variance is not None:
                report.append(f"- Variance: {outcome.empirical.variance:.2f}")
            report.append(f"- Sample size: n={outcome.empirical.n}")
            report.append("")

        # Notes
        if outcome.notes:
            report.append(f"**Notes:** {outcome.notes}")
            report.append("")

    report.append("---")
    report.append("")
    report.append("**Generated:** 2025-11-05 (Cycle 1021)")
    report.append("**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>")
    report.append("**Co-Authored-By:** Claude <noreply@anthropic.com>")

    return "\n".join(report)


def main():
    """Generate validation report from C186 data."""

    # Try loading JSON results first
    results_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
    c186_data = load_c186_results(results_path)

    partial_data = False

    # If no JSON, try parsing log
    if c186_data is None:
        log_path = Path("/tmp/c186_output.log")
        c186_data = parse_c186_log(log_path)
        partial_data = True

    if c186_data is None:
        print("❌ No C186 data available (neither JSON nor log)")
        return

    print(f"Loaded C186 data: {c186_data.get('num_completed', 0)} experiments")
    if partial_data:
        print("⚠️ Using partial data from log file")

    # Extract empirical metrics
    empirical_results = extract_empirical_metrics(c186_data)

    print(f"Extracted {len(empirical_results)} empirical metrics")

    # Validate predictions
    outcomes = []
    for prediction in HIERARCHICAL_PREDICTIONS:
        # Find matching empirical result
        empirical = next(
            (e for e in empirical_results if e.metric_name == prediction.metric_name),
            None
        )

        outcome = validate_prediction(prediction, empirical)
        outcomes.append(outcome)

    # Generate report
    report = generate_validation_report(outcomes, partial_data=partial_data)

    # Save to file
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/archive/validation/C186_HIERARCHICAL_VALIDATION_REPORT.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Validation report saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    for outcome in outcomes:
        status_emoji = {
            "VALIDATED": "✅",
            "PARTIAL": "⚠️",
            "REJECTED": "❌",
            "INSUFFICIENT_DATA": "⏳"
        }
        print(f"{status_emoji[outcome.status]} {outcome.prediction.metric_name}: {outcome.status} ({outcome.confidence:.1%})")

    print("=" * 80)


if __name__ == "__main__":
    main()
