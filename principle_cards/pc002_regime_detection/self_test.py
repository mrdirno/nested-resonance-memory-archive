"""
PC002: Self-Test Validation on Synthetic Regime Data
====================================================

Validate PC002 on synthetic regime data with known ground truth.
Expected accuracy: ≥95% (synthetic data is clean).

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import numpy as np
from pathlib import Path
import json
from datetime import datetime

from principle_cards.pc002_regime_detection import (
    PC002_RegimeDetection,
    BaselineParams,
    BASELINE,
    GROWTH,
    COLLAPSE,
    OSCILLATORY
)
from principle_cards.base import ValidationResult


def generate_synthetic_regime_data(
    regime_type: str,
    n_samples: int,
    window_size: int = 100,
    K: float = 50.0,
    r: float = 0.1,
    sigma: float = 0.5,
    seed: int = None
) -> np.ndarray:
    """
    Generate synthetic population data for specified regime.

    Args:
        regime_type: One of BASELINE, GROWTH, COLLAPSE, OSCILLATORY
        n_samples: Number of windows to generate
        window_size: Window size (points per sample)
        K: Carrying capacity
        r: Growth rate
        sigma: Noise intensity
        seed: Random seed

    Returns:
        Array of shape (n_samples, window_size)
    """
    if seed is not None:
        np.random.seed(seed)

    windows = []

    for _ in range(n_samples):
        if regime_type == BASELINE:
            # Near carrying capacity with demographic noise
            noise_level = sigma * np.sqrt(K)
            window = np.random.normal(K, noise_level, window_size)
            # Ensure positive
            window = np.clip(window, 1, None)

        elif regime_type == GROWTH:
            # Linear growth from below K to above K
            start = K * 0.4 + np.random.uniform(-5, 5)
            end = K * 1.6 + np.random.uniform(-5, 5)
            window = np.linspace(start, end, window_size)
            # Add noise
            noise = np.random.normal(0, sigma * 2, window_size)
            window = window + noise
            window = np.clip(window, 1, None)

        elif regime_type == COLLAPSE:
            # Exponential decay from above K to below K
            start = K * 1.8 + np.random.uniform(-5, 5)
            decay_rate = 0.02 + np.random.uniform(0, 0.01)
            t = np.arange(window_size)
            window = start * np.exp(-decay_rate * t)
            # Add noise
            noise = np.random.normal(0, sigma * 2, window_size)
            window = window + noise
            window = np.clip(window, 1, None)

        elif regime_type == OSCILLATORY:
            # Sinusoidal oscillation around K
            period = 20 + np.random.uniform(-5, 5)
            amplitude = K * 0.3 + np.random.uniform(-5, 5)
            phase = np.random.uniform(0, 2 * np.pi)
            t = np.arange(window_size)
            window = K + amplitude * np.sin(2 * np.pi * t / period + phase)
            # Add noise
            noise = np.random.normal(0, sigma, window_size)
            window = window + noise
            window = np.clip(window, 1, None)

        else:
            raise ValueError(f"Unknown regime type: {regime_type}")

        windows.append(window)

    return np.array(windows)


def create_mock_pc001(K: float = 50.0, r: float = 0.1, sigma: float = 0.5, CV_baseline: float = 0.10):
    """Create mock PC001 instance for testing."""
    class MockPC001:
        def __init__(self):
            from principle_cards.base import PCMetadata
            self.metadata = PCMetadata(
                pc_id="PC001",
                version="1.0.0",
                title="NRM Population Dynamics",
                author="Aldrin Payopay <aldrin.gdf@gmail.com>",
                created="2025-11-01",
                status="validated",
                dependencies=[],
                domain="NRM"
            )
            self.carrying_capacity = K
            self.growth_rate = r
            self.noise_intensity = sigma
            self._cv_baseline = CV_baseline

        def predict_cv(self):
            return self._cv_baseline

    return MockPC001()


def run_self_test(
    n_samples_per_regime: int = 100,
    train_fraction: float = 0.7,
    window_size: int = 100,
    tolerance: float = 0.90,
    random_state: int = 42
) -> ValidationResult:
    """
    Run PC002 self-test on synthetic regime data.

    Args:
        n_samples_per_regime: Number of windows per regime type
        train_fraction: Fraction of data for training
        window_size: Window size (points)
        tolerance: Accuracy threshold (default: 90%)
        random_state: Random seed

    Returns:
        ValidationResult with performance metrics
    """
    print("=" * 70)
    print("PC002: Self-Test Validation on Synthetic Regime Data")
    print("=" * 70)
    print()

    # Parameters
    K = 50.0
    r = 0.1
    sigma = 0.5
    CV_baseline = 0.10

    print(f"Baseline Parameters:")
    print(f"  K (carrying capacity): {K}")
    print(f"  r (growth rate): {r}")
    print(f"  σ (noise intensity): {sigma}")
    print(f"  CV_baseline: {CV_baseline}")
    print()

    print(f"Test Configuration:")
    print(f"  Samples per regime: {n_samples_per_regime}")
    print(f"  Window size: {window_size}")
    print(f"  Train fraction: {train_fraction:.0%}")
    print(f"  Accuracy threshold: {tolerance:.0%}")
    print(f"  Random seed: {random_state}")
    print()

    # Generate synthetic data for all 4 regimes
    print("Generating synthetic regime data...")
    regime_types = [BASELINE, GROWTH, COLLAPSE, OSCILLATORY]
    all_windows = []
    all_labels = []

    for regime_type in regime_types:
        windows = generate_synthetic_regime_data(
            regime_type=regime_type,
            n_samples=n_samples_per_regime,
            window_size=window_size,
            K=K,
            r=r,
            sigma=sigma,
            seed=random_state
        )
        labels = np.array([regime_type] * n_samples_per_regime)

        all_windows.append(windows)
        all_labels.append(labels)

        print(f"  {regime_type:12s}: {len(windows)} windows generated")

    # Combine and shuffle
    all_windows = np.vstack(all_windows)
    all_labels = np.concatenate(all_labels)

    # Shuffle
    np.random.seed(random_state)
    indices = np.random.permutation(len(all_labels))
    all_windows = all_windows[indices]
    all_labels = all_labels[indices]

    print(f"\nTotal dataset: {len(all_labels)} windows")

    # Train/test split
    n_train = int(len(all_labels) * train_fraction)
    train_windows = all_windows[:n_train]
    train_labels = all_labels[:n_train]
    test_windows = all_windows[n_train:]
    test_labels = all_labels[n_train:]

    print(f"  Training set: {len(train_labels)} windows")
    print(f"  Test set: {len(test_labels)} windows")
    print()

    # Create mock PC001
    print("Creating mock PC001 (validated)...")
    mock_pc001 = create_mock_pc001(K=K, r=r, sigma=sigma, CV_baseline=CV_baseline)
    print(f"  PC001 status: {mock_pc001.metadata.status}")
    print()

    # Create PC002
    print("Initializing PC002...")
    pc002 = PC002_RegimeDetection(
        window_size=window_size,
        n_estimators=100,
        random_state=random_state
    )
    print(f"  Window size: {pc002.window_size}")
    print(f"  Classifier: RandomForest (n_estimators=100)")
    print()

    # Prepare validation data
    data = {
        'pc001': mock_pc001,
        'train_data': (train_windows, train_labels),
        'test_data': (test_windows, test_labels)
    }

    # Run validation
    print("Running PC002 validation...")
    print(f"  Step 1: Setting baseline from PC001...")
    print(f"  Step 2: Training classifier on {len(train_labels)} samples...")
    print(f"  Step 3: Evaluating on {len(test_labels)} test samples...")
    print()

    result = pc002.validate(data, tolerance=tolerance)

    # Print results
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print()

    print(f"Status: {'✓ PASSED' if result.passes else '✗ FAILED'}")
    print(f"  PC ID: {result.pc_id}")
    print(f"  Criterion: Accuracy ≥ {result.criterion:.0%}")
    print(f"  Test Accuracy: {result.evidence['test_accuracy']:.2%}")
    print(f"  Error: {result.error:.2%}")
    print()

    print(f"Performance Metrics:")
    print(f"  Precision: {result.evidence['test_precision']:.2%}")
    print(f"  Recall: {result.evidence['test_recall']:.2%}")
    print(f"  F1-score: {result.evidence['test_f1']:.2%}")
    print()

    print(f"Confusion Matrix:")
    cm = np.array(result.evidence['test_confusion_matrix'])
    print(f"  Predicted →  {BASELINE:12s} {GROWTH:12s} {COLLAPSE:12s} {OSCILLATORY:12s}")
    for i, true_regime in enumerate(regime_types):
        row = cm[i]
        print(f"  {true_regime:12s}  {row[0]:12d} {row[1]:12d} {row[2]:12d} {row[3]:12d}")
    print()

    print(f"Feature Importances:")
    importances = result.evidence['feature_importances']
    for feature, importance in sorted(importances.items(), key=lambda x: -x[1]):
        print(f"  {feature:15s}: {importance:.3f}")
    print()

    print(f"Training Performance:")
    print(f"  Train Accuracy: {result.evidence['train_accuracy']:.2%}")
    print(f"  Train Samples: {result.evidence['n_train_samples']}")
    print()

    print(f"PC002 Status: {pc002.metadata.status}")
    print()

    # Save validation result
    output_dir = Path(__file__).parent
    result_path = output_dir / "validation_result_self_test.json"
    result.save(result_path)
    print(f"Validation result saved: {result_path}")
    print()

    # Save PC002 metadata
    pc002_path = output_dir / "principle_card.json"
    pc002.save(pc002_path)
    print(f"Principle card saved: {pc002_path}")
    print()

    print("=" * 70)
    if result.passes:
        print("✓ PC002 SELF-TEST PASSED")
        print(f"  Achieved {result.evidence['test_accuracy']:.2%} accuracy")
        print(f"  Exceeds {result.criterion:.0%} threshold")
    else:
        print("✗ PC002 SELF-TEST FAILED")
        print(f"  Achieved {result.evidence['test_accuracy']:.2%} accuracy")
        print(f"  Below {result.criterion:.0%} threshold")
    print("=" * 70)
    print()

    return result


if __name__ == "__main__":
    # Run self-test
    result = run_self_test(
        n_samples_per_regime=100,  # 400 total samples
        train_fraction=0.7,         # 280 train, 120 test
        window_size=100,
        tolerance=0.90,             # 90% accuracy threshold
        random_state=42
    )

    # Exit with appropriate code
    exit(0 if result.passes else 1)
