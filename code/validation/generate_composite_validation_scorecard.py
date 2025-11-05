#!/usr/bin/env python3
"""
Composite Validation Scorecard Generator

Purpose: Generate unified 24-point validation scorecard across C186-C189
Validates Extension 2 hierarchical framework predictions across all experiments.

Scorecard Structure:
- C186 (5 predictions): Hierarchical energy dynamics
- C187 (6 predictions): Network structure effects
- C188 (7 predictions): Memory effects
- C189 (6 predictions): Burst clustering

Scoring:
- VALIDATED: Prediction confirmed with high confidence (green)
- PARTIAL: Partial support or moderate confidence (yellow)
- REJECTED: Prediction contradicted (red)
- INSUFFICIENT: Not enough data to evaluate (gray)

Publication Target: Paper 4 Figure 5 (composite heatmap)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1024
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ValidationStatus(Enum):
    """Validation status categories."""
    VALIDATED = "VALIDATED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass
class ValidationPoint:
    """Single validation criterion."""
    experiment_id: str
    criterion_id: str
    prediction_name: str
    prediction_description: str
    status: ValidationStatus
    confidence: float  # 0.0 - 1.0
    evidence: str
    reference_section: str


@dataclass
class CompositeScorecard:
    """Complete validation scorecard across all experiments."""
    timestamp: str
    total_points: int
    validated_count: int
    partial_count: int
    rejected_count: int
    insufficient_count: int
    validation_rate: float
    mean_confidence: float
    validation_points: List[ValidationPoint]


def load_experiment_validations(experiment_id: str, results_path: Path) -> List[ValidationPoint]:
    """
    Load validation results for a single experiment.

    Args:
        experiment_id: Experiment identifier (C186, C187, etc.)
        results_path: Path to experiment validation results

    Returns:
        List of ValidationPoint objects
    """
    if not results_path.exists():
        print(f"⏳ {experiment_id} validation results not found: {results_path}")
        return []

    try:
        with open(results_path, 'r') as f:
            data = json.load(f)

        validation_points = []

        for validation in data.get('validations', []):
            status_str = validation.get('status', 'INSUFFICIENT')

            try:
                status = ValidationStatus[status_str]
            except KeyError:
                status = ValidationStatus.INSUFFICIENT

            point = ValidationPoint(
                experiment_id=experiment_id,
                criterion_id=validation['criterion_id'],
                prediction_name=validation['prediction_name'],
                prediction_description=validation.get('description', ''),
                status=status,
                confidence=validation.get('confidence', 0.0),
                evidence=validation.get('evidence', ''),
                reference_section=validation.get('reference_section', '')
            )

            validation_points.append(point)

        return validation_points

    except Exception as e:
        print(f"Error loading {experiment_id} validations: {e}")
        return []


def generate_c186_validations(c186_results_path: Path) -> List[ValidationPoint]:
    """
    Generate C186 validation points from results.

    Args:
        c186_results_path: Path to C186 results JSON

    Returns:
        List of 5 ValidationPoint objects
    """
    if not c186_results_path.exists():
        print(f"⏳ C186 results not found: {c186_results_path}")
        return []

    try:
        with open(c186_results_path, 'r') as f:
            data = json.load(f)

        experiments = data.get('experiments', [])

        if not experiments:
            return []

        # Extract metrics
        basin_a = [exp['basin_a_percent'] for exp in experiments]
        migrations = [exp['migration_count'] for exp in experiments]
        cvs = [exp['cv_percent'] for exp in experiments]

        import numpy as np

        # Validation Point 1: Basin A suppression (≤5%)
        mean_basin = np.mean(basin_a)
        status_1 = ValidationStatus.VALIDATED if mean_basin <= 5.0 else ValidationStatus.REJECTED
        confidence_1 = 1.0 if mean_basin == 0.0 else max(0.0, 1.0 - (mean_basin / 5.0))

        point_1 = ValidationPoint(
            experiment_id="C186",
            criterion_id="C186-1",
            prediction_name="Basin A Suppression",
            prediction_description="Inter-population coupling suppresses Basin A occupation to ≤5%",
            status=status_1,
            confidence=confidence_1,
            evidence=f"Mean Basin A = {mean_basin:.2f}% (n={len(basin_a)})",
            reference_section="Extension 2, Section 2.1"
        )

        # Validation Point 2: Migration frequency (10-20 events)
        mean_mig = np.mean(migrations)
        status_2 = ValidationStatus.VALIDATED if 10 <= mean_mig <= 20 else ValidationStatus.PARTIAL
        confidence_2 = 1.0 if 10 <= mean_mig <= 20 else 0.5

        point_2 = ValidationPoint(
            experiment_id="C186",
            criterion_id="C186-2",
            prediction_name="Migration Consistency",
            prediction_description="Cross-population migrations in range 10-20 per 3000 cycles",
            status=status_2,
            confidence=confidence_2,
            evidence=f"Mean migrations = {mean_mig:.1f} (range: {min(migrations)}-{max(migrations)})",
            reference_section="Extension 2, Section 2.2"
        )

        # Validation Point 3: CV variance amplification
        cv_variance = np.var(cvs, ddof=1)
        status_3 = ValidationStatus.VALIDATED if cv_variance > 50 else ValidationStatus.PARTIAL
        confidence_3 = min(1.0, cv_variance / 100)

        point_3 = ValidationPoint(
            experiment_id="C186",
            criterion_id="C186-3",
            prediction_name="CV Variance Amplification",
            prediction_description="Hierarchical coupling amplifies dynamical variance",
            status=status_3,
            confidence=confidence_3,
            evidence=f"CV variance = {cv_variance:.2f} (mean CV = {np.mean(cvs):.1f}%)",
            reference_section="Extension 2, Section 2.3"
        )

        # Validation Point 4: Population homeostasis
        mean_pops = [exp['mean_population'] for exp in experiments]
        pop_cv = (np.std(mean_pops, ddof=1) / np.mean(mean_pops)) * 100
        status_4 = ValidationStatus.VALIDATED if pop_cv < 5 else ValidationStatus.PARTIAL
        confidence_4 = max(0.0, 1.0 - (pop_cv / 10))

        point_4 = ValidationPoint(
            experiment_id="C186",
            criterion_id="C186-4",
            prediction_name="Population Homeostasis",
            prediction_description="Mean population size remains stable across seeds",
            status=status_4,
            confidence=confidence_4,
            evidence=f"Population CV = {pop_cv:.2f}% (mean = {np.mean(mean_pops):.2f})",
            reference_section="Extension 2, Section 2.4"
        )

        # Validation Point 5: Runtime variance (pending full data)
        point_5 = ValidationPoint(
            experiment_id="C186",
            criterion_id="C186-5",
            prediction_name="Runtime Variance",
            prediction_description="Computational complexity amplifies with hierarchical structure",
            status=ValidationStatus.INSUFFICIENT,
            confidence=0.0,
            evidence="Requires complete runtime data with timestamps",
            reference_section="Extension 2, Section 2.5"
        )

        return [point_1, point_2, point_3, point_4, point_5]

    except Exception as e:
        print(f"Error generating C186 validations: {e}")
        return []


def generate_composite_scorecard(
    c186_path: Path,
    c187_path: Path,
    c188_path: Path,
    c189_path: Path,
    output_path: Path
) -> Optional[CompositeScorecard]:
    """
    Generate composite validation scorecard from all experiments.

    Args:
        c186_path: Path to C186 results
        c187_path: Path to C187 results
        c188_path: Path to C188 results
        c189_path: Path to C189 results
        output_path: Path to save scorecard JSON

    Returns:
        CompositeScorecard object or None if insufficient data
    """
    print("=" * 80)
    print("GENERATING COMPOSITE VALIDATION SCORECARD")
    print("=" * 80)
    print()

    # Load validation points from each experiment
    all_points = []

    print("Loading experiment validations...")

    # C186: Generate from results
    print("  C186: Hierarchical Energy Dynamics...")
    c186_points = generate_c186_validations(c186_path)
    all_points.extend(c186_points)
    print(f"    ✓ {len(c186_points)}/5 validation points")

    # C187: Load from validation results (if available)
    print("  C187: Network Structure Effects...")
    c187_points = load_experiment_validations("C187", c187_path)
    all_points.extend(c187_points)
    if c187_points:
        print(f"    ✓ {len(c187_points)}/6 validation points")
    else:
        print("    ⏳ Pending (0/6 points)")

    # C188: Load from validation results (if available)
    print("  C188: Memory Effects...")
    c188_points = load_experiment_validations("C188", c188_path)
    all_points.extend(c188_points)
    if c188_points:
        print(f"    ✓ {len(c188_points)}/7 validation points")
    else:
        print("    ⏳ Pending (0/7 points)")

    # C189: Load from validation results (if available)
    print("  C189: Burst Clustering...")
    c189_points = load_experiment_validations("C189", c189_path)
    all_points.extend(c189_points)
    if c189_points:
        print(f"    ✓ {len(c189_points)}/6 validation points")
    else:
        print("    ⏳ Pending (0/6 points)")

    print()

    if not all_points:
        print("⚠️ No validation points available. Cannot generate scorecard.")
        return None

    # Calculate statistics
    total_points = len(all_points)
    validated_count = sum(1 for p in all_points if p.status == ValidationStatus.VALIDATED)
    partial_count = sum(1 for p in all_points if p.status == ValidationStatus.PARTIAL)
    rejected_count = sum(1 for p in all_points if p.status == ValidationStatus.REJECTED)
    insufficient_count = sum(1 for p in all_points if p.status == ValidationStatus.INSUFFICIENT)

    validation_rate = (validated_count + 0.5 * partial_count) / total_points if total_points > 0 else 0.0

    # Mean confidence (excluding insufficient)
    valid_confidences = [p.confidence for p in all_points
                         if p.status != ValidationStatus.INSUFFICIENT]
    mean_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0

    # Create scorecard
    scorecard = CompositeScorecard(
        timestamp=datetime.now().isoformat(),
        total_points=total_points,
        validated_count=validated_count,
        partial_count=partial_count,
        rejected_count=rejected_count,
        insufficient_count=insufficient_count,
        validation_rate=validation_rate,
        mean_confidence=mean_confidence,
        validation_points=all_points
    )

    # Save to JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, 'w') as f:
            json.dump({
                'scorecard': asdict(scorecard),
                'validation_points': [asdict(p) for p in all_points]
            }, f, indent=2, default=str)

        print(f"✓ Scorecard saved to: {output_path}")

    except Exception as e:
        print(f"Error saving scorecard: {e}")

    # Print summary
    print()
    print("=" * 80)
    print("VALIDATION SCORECARD SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Validation Points: {total_points}/24")
    print(f"  ✅ VALIDATED: {validated_count}")
    print(f"  ⚠️  PARTIAL: {partial_count}")
    print(f"  ❌ REJECTED: {rejected_count}")
    print(f"  ⏸️  INSUFFICIENT: {insufficient_count}")
    print()
    print(f"Overall Validation Rate: {validation_rate * 100:.1f}%")
    print(f"Mean Confidence: {mean_confidence * 100:.1f}%")
    print()

    # Interpretation
    if validation_rate >= 0.75:
        print("✅ STRONG SUPPORT for Extension 2 framework (≥75% validation)")
    elif validation_rate >= 0.50:
        print("⚠️  MODERATE SUPPORT for Extension 2 framework (50-75% validation)")
    else:
        print("❌ WEAK SUPPORT for Extension 2 framework (<50% validation)")

    print()
    print("=" * 80)

    return scorecard


def main():
    """Generate composite validation scorecard."""

    # Paths
    c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
    c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
    c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
    c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")

    scorecard = generate_composite_scorecard(
        c186_path, c187_path, c188_path, c189_path, output_path
    )

    if scorecard:
        print()
        print("📊 Composite validation scorecard generated successfully.")
        print(f"   Use for Paper 4 Figure 5 (validation heatmap)")
        print(f"   Publication threshold: ≥18/24 points validated (75%)")


if __name__ == "__main__":
    main()
