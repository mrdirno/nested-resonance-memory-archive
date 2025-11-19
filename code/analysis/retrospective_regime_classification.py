#!/usr/bin/env python3
"""
Retrospective Regime Classification Analysis

Applies Gate 1.2 regime detector to historical experimental data using
summary statistics (mean, std, CV) to validate classifier performance
on real NRM agent system outcomes.

Compares regime classifications with basin classifications (A/B) from
original experiments to identify alignment or discrepancies.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
Cycle: 870+
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from code.tsf.regime_detection import RegimeType, RegimeDetector


def classify_from_statistics(
    mean: float, std: float, cv: float, detector: RegimeDetector
) -> Tuple[RegimeType, float]:
    """
    Classify regime using summary statistics.

    Args:
        mean: Mean population
        std: Standard deviation
        cv: Coefficient of variation (%)
        detector: RegimeDetector instance

    Returns:
        Tuple of (regime_type, confidence)
    """
    # Convert CV from percentage to ratio if needed
    cv_ratio = cv / 100.0 if cv > 1.0 else cv

    # Construct metrics dict (minimal version for classification)
    metrics = {
        "mean": mean,
        "std": std,
        "cv": cv_ratio,
        "relative_change": 0.0,  # Not available from summary stats
        "extinction_fraction": 0.0 if mean > 1.0 else 0.5,
        "trend": 0.0,
        "kurtosis": 0.0,
        "min": 0.0,
        "max": 0.0,
        "median": mean,
    }

    # Use detector's internal classification logic
    regime, confidence, evidence = detector._classify(metrics, parameters={})

    return regime, confidence


def analyze_cycle_results(
    results_path: Path, detector: RegimeDetector
) -> Dict[str, any]:
    """
    Analyze experimental results and apply regime classification.

    Args:
        results_path: Path to JSON results file
        detector: RegimeDetector instance

    Returns:
        Analysis results dictionary
    """
    with open(results_path) as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    experiments = data.get("experiments", [])

    # Classify each experiment
    classifications = []
    regime_counts = {r: 0 for r in RegimeType}
    basin_regime_map = {}  # Map basin -> regime counts
    condition_regime_map = {}  # Map condition -> regime counts

    for exp in experiments:
        mean_pop = exp.get("mean_population", 0.0)
        std_pop = exp.get("std_population", 0.0)
        cv_pop = exp.get("cv_population", 0.0)
        basin = exp.get("basin", "UNKNOWN")
        condition = exp.get("condition", "UNKNOWN")

        regime, confidence = classify_from_statistics(
            mean_pop, std_pop, cv_pop, detector
        )

        classifications.append({
            "condition": condition,
            "frequency": exp.get("frequency", 0.0),
            "seed": exp.get("seed", 0),
            "basin": basin,
            "regime": regime.value,
            "confidence": confidence,
            "cv_percent": cv_pop,
            "mean_population": mean_pop,
        })

        regime_counts[regime] += 1

        # Track basin-regime mapping
        if basin not in basin_regime_map:
            basin_regime_map[basin] = {r: 0 for r in RegimeType}
        basin_regime_map[basin][regime] += 1

        # Track condition-regime mapping
        if condition not in condition_regime_map:
            condition_regime_map[condition] = {r: 0 for r in RegimeType}
        condition_regime_map[condition][regime] += 1

    return {
        "metadata": metadata,
        "classifications": classifications,
        "regime_counts": {r.value: count for r, count in regime_counts.items()},
        "basin_regime_map": {
            basin: {r.value: count for r, count in regimes.items()}
            for basin, regimes in basin_regime_map.items()
        },
        "condition_regime_map": {
            cond: {r.value: count for r, count in regimes.items()}
            for cond, regimes in condition_regime_map.items()
        },
        "total_experiments": len(experiments),
    }


def main():
    """Main analysis routine."""
    import sys

    # Initialize detector with default thresholds
    detector = RegimeDetector(
        bistability_cv_threshold=0.20,
        collapse_cv_threshold=0.80,
        collapse_mean_threshold=1.0,
    )

    # Allow command-line argument for file selection
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")

    if len(sys.argv) > 1:
        # Use specified file
        target_file = sys.argv[1]
        analysis_path = results_dir / target_file
    else:
        # Default to C176 original
        analysis_path = results_dir / "cycle176_ablation_study.json"

    if not analysis_path.exists():
        print(f"❌ Results file not found: {analysis_path}")
        return 1

    print("=" * 80)
    print("RETROSPECTIVE REGIME CLASSIFICATION ANALYSIS")
    print("=" * 80)
    print(f"\nAnalyzing: {analysis_path.name}")
    print(f"Detector thresholds: CV_bistability<{detector.bistability_cv_threshold*100}%, "
          f"CV_collapse>{detector.collapse_cv_threshold*100}%\n")

    # Perform analysis
    results = analyze_cycle_results(analysis_path, detector)

    # Display results
    metadata = results["metadata"]
    print(f"Cycle: {metadata.get('cycle', 'N/A')}")
    print(f"Scenario: {metadata.get('scenario', 'N/A')}")
    print(f"Frequency: {metadata.get('frequency', 'N/A')}%")
    print(f"Total experiments: {results['total_experiments']}")
    print()

    print("REGIME DISTRIBUTION:")
    print("-" * 40)
    for regime, count in results["regime_counts"].items():
        percent = (count / results["total_experiments"]) * 100
        print(f"  {regime:15s}: {count:3d} ({percent:5.1f}%)")
    print()

    print("BASIN → REGIME MAPPING:")
    print("-" * 40)
    for basin, regimes in results["basin_regime_map"].items():
        print(f"\n  Basin {basin}:")
        for regime, count in regimes.items():
            if count > 0:
                print(f"    {regime:15s}: {count:3d}")
    print()

    print("CONDITION → REGIME MAPPING:")
    print("-" * 40)
    for condition, regimes in results["condition_regime_map"].items():
        print(f"\n  {condition}:")
        for regime, count in regimes.items():
            if count > 0:
                print(f"    {regime:15s}: {count:3d}")
    print()

    # Sample classifications
    print("SAMPLE CLASSIFICATIONS (first 10):")
    print("-" * 100)
    print(f"{'Condition':<20} {'Basin':<8} {'Regime':<15} {'CV%':<10} {'Mean':<10} {'Conf':<8}")
    print("-" * 100)
    for cls in results["classifications"][:10]:
        print(f"{cls['condition']:<20} "
              f"{cls['basin']:<8} "
              f"{cls['regime']:<15} "
              f"{cls['cv_percent']:<10.1f} "
              f"{cls['mean_population']:<10.3f} "
              f"{cls['confidence']:<8.3f}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    # Save results with file-specific name
    output_name = f"regime_classification_{analysis_path.stem}.json"
    output_path = results_dir / output_name
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
