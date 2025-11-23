"""
Gate 1.2 Validation: Regime Detector on C255 Experimental Data

Validates the regime detection classifier (TSF v0.2.0) on real experimental
data from Cycle 255 (H1×H2 pairwise factorial validation).

This script:
1. Loads C255 experimental trajectories (4 conditions × 2 capacity levels = 8 trajectories)
2. Labels regimes based on Paper 3 known results (ANTAGONISTIC interaction)
3. Tests classifier accuracy on real data
4. Computes performance metrics (precision, recall, F1-score)
5. Advances Gate 1.2 toward ≥90% accuracy target

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-01
Cycle: 861
License: GPL-3.0
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Add paths for imports
code_dir = Path(__file__).parent.parent
sys.path.insert(0, str(code_dir.parent))  # Add DUALITY-ZERO-V2 to path
sys.path.insert(0, str(code_dir))  # Add code/ to path

from src.tsf import detect_regime, RegimeType

# Data paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
LIGHTWEIGHT_FILE = RESULTS_DIR / "cycle255_h1h2_lightweight_results.json"
HIGH_CAPACITY_FILE = RESULTS_DIR / "cycle255_h1h2_high_capacity_results.json"


def load_c255_data() -> Dict[str, Dict]:
    """
    Load C255 experimental data.

    Returns:
        Dictionary with trajectory data and metadata
    """
    with open(LIGHTWEIGHT_FILE) as f:
        lightweight = json.load(f)

    with open(HIGH_CAPACITY_FILE) as f:
        high_capacity = json.load(f)

    return {
        "lightweight": lightweight,
        "high_capacity": high_capacity
    }


def extract_trajectories(data: Dict) -> List[Dict]:
    """
    Extract population trajectories from C255 data.

    Args:
        data: Loaded C255 JSON data

    Returns:
        List of trajectory dictionaries with population, condition, and capacity info
    """
    trajectories = []

    for capacity_level, dataset in data.items():
        conditions = dataset['conditions']

        for condition_name, condition_data in conditions.items():
            trajectory = {
                'name': f"{capacity_level}_{condition_name}",
                'capacity': capacity_level,
                'condition': condition_name,
                'h1_pooling': condition_data['h1_pooling'],
                'h2_sources': condition_data['h2_sources'],
                'population': np.array(condition_data['population_history']),
                'mean_population': condition_data['mean_population'],
                'final_population': condition_data['final_population'],
                'max_population': condition_data['max_population']
            }
            trajectories.append(trajectory)

    return trajectories


def label_regimes_from_paper3(trajectories: List[Dict]) -> List[Tuple[Dict, RegimeType]]:
    """
    Label trajectories based on Paper 3 known results.

    From Paper 3 (Cycle 255):
    - H1×H2 interaction is ANTAGONISTIC (mechanisms interfere)
    - Lightweight: synergy = -85.68, ceiling ~100 (vs 185 predicted)
    - High capacity: synergy = -975.58, ceiling ~995 (vs 1970 predicted)
    - Expected: ON-ON shows COLLAPSE (resource competition)
    - Expected: OFF-OFF shows BISTABILITY (baseline persistence)
    - Expected: ON-OFF, OFF-ON show intermediate behavior

    Args:
        trajectories: List of trajectory dictionaries

    Returns:
        List of (trajectory, expected_regime) tuples
    """
    labeled = []

    for traj in trajectories:
        h1 = traj['h1_pooling']
        h2 = traj['h2_sources']
        mean_pop = traj['mean_population']
        final_pop = traj['final_population']

        # Labeling logic based on Paper 3 findings
        if h1 and h2:
            # ON-ON: Both mechanisms active, ANTAGONISTIC interaction
            # Expected: COLLAPSE (interference, resource competition)
            expected = RegimeType.COLLAPSE
        elif not h1 and not h2:
            # OFF-OFF: Baseline condition
            # Expected: BISTABILITY (sustained population, low variance)
            expected = RegimeType.BISTABILITY
        else:
            # ON-OFF or OFF-ON: Single mechanism active
            # Expected: ACCUMULATION or BISTABILITY (moderate performance)
            # Use mean_population as heuristic
            if mean_pop > 50:
                expected = RegimeType.BISTABILITY
            else:
                expected = RegimeType.ACCUMULATION

        labeled.append((traj, expected))

    return labeled


def compute_metrics(labeled_trajectories: List[Tuple[Dict, RegimeType]]) -> Dict:
    """
    Compute classifier performance metrics.

    Args:
        labeled_trajectories: List of (trajectory, expected_regime) tuples

    Returns:
        Dictionary with performance metrics
    """
    predictions = []
    true_labels = []
    confidence_scores = []

    for traj, expected in labeled_trajectories:
        # Classify trajectory
        result = detect_regime(
            population=traj['population'],
            time=None,  # Use default time array
            parameters={}
        )

        predictions.append(result.regime)
        true_labels.append(expected)
        confidence_scores.append(result.confidence)

        print(f"\n{traj['name']}:")
        print(f"  Expected: {expected.name}")
        print(f"  Predicted: {result.regime.name}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Match: {'✓' if result.regime == expected else '✗'}")
        print(f"  Metrics: CV={result.metrics['cv']:.2f}, mean={result.metrics['mean']:.1f}")

    # Compute accuracy
    correct = sum(1 for pred, true in zip(predictions, true_labels) if pred == true)
    total = len(predictions)
    accuracy = correct / total if total > 0 else 0.0

    # Per-regime statistics
    regime_stats = {}
    for regime in [RegimeType.COLLAPSE, RegimeType.BISTABILITY, RegimeType.ACCUMULATION]:
        true_pos = sum(1 for pred, true in zip(predictions, true_labels)
                      if pred == regime and true == regime)
        false_pos = sum(1 for pred, true in zip(predictions, true_labels)
                       if pred == regime and true != regime)
        false_neg = sum(1 for pred, true in zip(predictions, true_labels)
                       if pred != regime and true == regime)

        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0.0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        regime_stats[regime.name] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'support': sum(1 for true in true_labels if true == regime)
        }

    return {
        'accuracy': accuracy,
        'total_samples': total,
        'correct_predictions': correct,
        'mean_confidence': np.mean(confidence_scores),
        'regime_statistics': regime_stats,
        'predictions': [(traj['name'], pred.name, true.name, conf)
                       for traj, pred, true, conf in zip(
                           [t for t, _ in labeled_trajectories],
                           predictions, true_labels, confidence_scores)]
    }


def main():
    """Main validation routine."""
    print("=" * 80)
    print("Gate 1.2 Validation: Regime Detector on C255 Experimental Data")
    print("=" * 80)
    print()

    # Load data
    print("Loading C255 experimental data...")
    data = load_c255_data()
    print(f"✓ Loaded {len(data)} capacity levels")

    # Extract trajectories
    print("\nExtracting population trajectories...")
    trajectories = extract_trajectories(data)
    print(f"✓ Extracted {len(trajectories)} trajectories")
    for traj in trajectories:
        print(f"  - {traj['name']}: {len(traj['population'])} timesteps")

    # Label regimes
    print("\nLabeling regimes based on Paper 3 results...")
    labeled = label_regimes_from_paper3(trajectories)
    print(f"✓ Labeled {len(labeled)} trajectories")

    # Test classifier
    print("\nTesting regime classifier...")
    print("-" * 80)
    metrics = compute_metrics(labeled)

    # Print results
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"\nOverall Accuracy: {metrics['accuracy']:.1%} ({metrics['correct_predictions']}/{metrics['total_samples']})")
    print(f"Mean Confidence: {metrics['mean_confidence']:.3f}")

    print("\nPer-Regime Performance:")
    print("-" * 80)
    for regime, stats in metrics['regime_statistics'].items():
        if stats['support'] > 0:
            print(f"\n{regime}:")
            print(f"  Precision: {stats['precision']:.1%}")
            print(f"  Recall: {stats['recall']:.1%}")
            print(f"  F1-Score: {stats['f1_score']:.3f}")
            print(f"  Support: {stats['support']}")

    # Gate 1.2 assessment
    print("\n" + "=" * 80)
    print("GATE 1.2 ASSESSMENT")
    print("=" * 80)
    print(f"\nTarget: ≥90% cross-validated accuracy")
    print(f"Current: {metrics['accuracy']:.1%} on C255 experimental data")

    if metrics['accuracy'] >= 0.90:
        print("✓ GATE 1.2 TARGET MET")
        print("  Next: Expand validation to C256/C257 when complete")
    else:
        gap = 0.90 - metrics['accuracy']
        print(f"⚠ Gap to target: {gap:.1%}")
        print("  Next: Tune classification thresholds based on real data")
        print("  Next: Expand training set with additional experimental data")

    print("\n" + "=" * 80)
    print("Validation complete. Results logged.")
    print("=" * 80)


if __name__ == "__main__":
    main()
