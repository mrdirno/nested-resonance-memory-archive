#!/usr/bin/env python3
"""
TSF Regime Detection - Test Suite

Validates regime classification accuracy for Gate 1.2 requirements.

Target: ≥90% cross-validated accuracy on known experimental runs

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
Cycle: 860+
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from code.tsf.regime_detection import (
    RegimeType,
    RegimeClassification,
    RegimeDetector,
    detect_regime,
)


class TestRegimeDetectorBasic:
    """Basic functionality tests for RegimeDetector."""

    def test_detector_initialization(self):
        """Test detector initializes with default parameters."""
        detector = RegimeDetector()
        assert detector.bistability_cv_threshold == 0.20
        assert detector.collapse_cv_threshold == 0.80
        assert detector.min_samples == 100

    def test_detector_custom_thresholds(self):
        """Test detector accepts custom threshold configuration."""
        detector = RegimeDetector(
            bistability_cv_threshold=0.15,
            collapse_cv_threshold=0.90,
            min_samples=50
        )
        assert detector.bistability_cv_threshold == 0.15
        assert detector.collapse_cv_threshold == 0.90
        assert detector.min_samples == 50

    def test_insufficient_samples_raises_error(self):
        """Test detector rejects trajectories with insufficient samples."""
        detector = RegimeDetector(min_samples=100)
        short_trajectory = np.ones(50)

        with pytest.raises(ValueError, match="Insufficient samples"):
            detector.detect_regime(short_trajectory)

    def test_detect_regime_returns_classification(self):
        """Test detector returns RegimeClassification object."""
        detector = RegimeDetector()
        population = np.ones(200) * 10.0 + np.random.normal(0, 1.0, 200)

        result = detector.detect_regime(population)

        assert isinstance(result, RegimeClassification)
        assert isinstance(result.regime, RegimeType)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.metrics, dict)
        assert isinstance(result.evidence, dict)


class TestCollapseRegimeDetection:
    """Test detection of Regime 3: Collapse."""

    def test_collapse_high_cv_low_mean(self):
        """Test collapse detection with high CV and low mean."""
        # Generate collapse trajectory: exponential decay to near-zero
        population = np.random.exponential(0.5, 500)

        result = detect_regime(population)

        assert result.regime == RegimeType.COLLAPSE
        assert result.confidence > 0.5
        assert result.metrics["cv"] > 0.80
        assert result.metrics["mean"] < 1.0
        assert "high_cv" in result.evidence
        assert "low_mean" in result.evidence

    def test_collapse_catastrophic_failure(self):
        """Test collapse detection with catastrophic failure signature."""
        # Generate trajectory that collapses to zero
        time = np.linspace(0, 100, 500)
        population = 20.0 * np.exp(-time / 10.0) + np.random.exponential(0.1, 500)

        result = detect_regime(population, time)

        assert result.regime == RegimeType.COLLAPSE
        assert result.metrics["cv"] > 0.80
        assert result.metrics["extinction_fraction"] > 0.5

    def test_collapse_paper2_signature(self):
        """Test collapse detection matches Paper 2 signature (CV=101%)."""
        # Replicate Paper 2 Regime 3 statistics
        np.random.seed(42)
        population = np.abs(np.random.normal(0.49, 0.50, 1000))

        result = detect_regime(population)

        assert result.regime == RegimeType.COLLAPSE
        assert result.confidence > 0.7
        # CV should be ~100% (std ≈ mean)
        assert 0.8 < result.metrics["cv"] < 1.2


class TestAccumulationRegimeDetection:
    """Test detection of Regime 2: Accumulation."""

    def test_accumulation_plateau_behavior(self):
        """Test accumulation detection with plateau dynamics."""
        # Generate plateau trajectory
        population = 17.0 + np.random.normal(0, 1.5, 500)

        result = detect_regime(population)

        assert result.regime == RegimeType.ACCUMULATION
        assert result.confidence > 0.5
        assert result.metrics["relative_change"] < 0.15
        assert "plateau" in result.evidence

    def test_accumulation_birth_only_signature(self):
        """Test accumulation detection with birth-only constraint."""
        # Simulate birth-only system: gradual accumulation to plateau
        time = np.linspace(0, 100, 500)
        population = 17.0 * (1 - np.exp(-time / 20.0)) + np.random.normal(0, 1.0, 500)

        result = detect_regime(population, time)

        assert result.regime == RegimeType.ACCUMULATION
        assert result.metrics["mean"] > 10.0  # Sustained population
        assert result.metrics["cv"] < 0.5  # Low variance

    def test_accumulation_paper2_statistics(self):
        """Test accumulation matches Paper 2 Regime 2 (~17 agents)."""
        np.random.seed(123)
        population = np.random.normal(17.0, 2.0, 1000)

        result = detect_regime(population)

        assert result.regime == RegimeType.ACCUMULATION
        assert 15.0 < result.metrics["mean"] < 19.0
        assert result.metrics["relative_change"] < 0.15


class TestBistabilityRegimeDetection:
    """Test detection of Regime 1: Bistability."""

    def test_bistability_low_cv_sustained(self):
        """Test bistability detection with low CV and sustained population."""
        # Generate stable trajectory with low variance
        population = 25.0 + np.random.normal(0, 2.0, 500)

        result = detect_regime(population)

        assert result.regime == RegimeType.BISTABILITY
        assert result.confidence > 0.5
        assert result.metrics["cv"] < 0.20
        assert result.metrics["mean"] > 1.0
        assert "low_cv" in result.evidence
        assert "sustained" in result.evidence

    def test_bistability_bimodal_distribution(self):
        """Test bistability with bimodal population distribution."""
        # Generate bimodal trajectory (two stable states)
        population = np.concatenate([
            np.random.normal(20.0, 1.5, 250),
            np.random.normal(30.0, 1.5, 250)
        ])
        np.random.shuffle(population)

        result = detect_regime(population)

        assert result.regime == RegimeType.BISTABILITY
        assert result.metrics["cv"] < 0.20
        # Bimodal distributions have negative kurtosis
        assert abs(result.metrics["kurtosis"]) > 0.5

    def test_bistability_sharp_transition(self):
        """Test bistability with sharp phase transition signature."""
        # Simulate transition between two states
        population = np.concatenate([
            np.ones(200) * 15.0 + np.random.normal(0, 1.0, 200),
            np.ones(200) * 25.0 + np.random.normal(0, 1.0, 200),
            np.ones(100) * 15.0 + np.random.normal(0, 1.0, 100)
        ])

        result = detect_regime(population)

        assert result.regime == RegimeType.BISTABILITY
        assert result.metrics["cv"] < 0.25


class TestRegimeDetectionEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_population_classified_as_collapse(self):
        """Test all-zero population classified as collapse."""
        population = np.zeros(200)

        result = detect_regime(population)

        # Should handle zero-division gracefully
        assert result.regime == RegimeType.COLLAPSE or result.regime == RegimeType.UNKNOWN

    def test_constant_population_classified(self):
        """Test constant population trajectory classification."""
        population = np.ones(200) * 20.0

        result = detect_regime(population)

        # Constant = plateau behavior (accumulation) or bistability
        assert result.regime in [RegimeType.ACCUMULATION, RegimeType.BISTABILITY]
        assert result.metrics["cv"] < 0.01

    def test_high_variance_intermediate_mean(self):
        """Test ambiguous case: high variance but intermediate mean."""
        population = np.random.uniform(5.0, 15.0, 500)

        result = detect_regime(population)

        # Should classify based on dominant signature
        assert result.regime in [RegimeType.BISTABILITY, RegimeType.ACCUMULATION, RegimeType.UNKNOWN]

    def test_time_array_integration(self):
        """Test regime detection with non-uniform time sampling."""
        # Non-uniform time points
        time = np.sort(np.random.uniform(0, 100, 500))
        population = 20.0 + np.random.normal(0, 2.0, 500)

        result = detect_regime(population, time)

        assert result.regime == RegimeType.BISTABILITY
        assert "trend" in result.metrics


class TestConvenienceFunctionAPI:
    """Test convenience function for TSF integration."""

    def test_detect_regime_function_basic(self):
        """Test detect_regime() convenience function."""
        population = np.ones(200) * 15.0 + np.random.normal(0, 1.5, 200)

        result = detect_regime(population)

        assert isinstance(result, RegimeClassification)
        assert result.regime in [r for r in RegimeType]

    def test_detect_regime_with_parameters(self):
        """Test detect_regime() with experimental parameters."""
        population = np.ones(200) * 15.0
        parameters = {"frequency": 0.025, "threshold": 700}

        result = detect_regime(population, parameters=parameters)

        assert isinstance(result, RegimeClassification)

    def test_detect_regime_custom_kwargs(self):
        """Test detect_regime() with custom detector configuration."""
        population = np.random.exponential(0.8, 500)

        result = detect_regime(
            population,
            collapse_cv_threshold=0.70,
            collapse_mean_threshold=1.5
        )

        assert result.regime == RegimeType.COLLAPSE


class TestMetricsExtraction:
    """Test diagnostic metrics extraction."""

    def test_metrics_completeness(self):
        """Test all expected metrics are extracted."""
        detector = RegimeDetector()
        population = np.random.normal(15.0, 3.0, 500)

        result = detector.detect_regime(population)

        required_metrics = [
            "mean", "std", "cv", "trend", "relative_change",
            "kurtosis", "extinction_fraction", "min", "max", "median"
        ]

        for metric in required_metrics:
            assert metric in result.metrics
            assert isinstance(result.metrics[metric], (int, float))

    def test_cv_calculation_accuracy(self):
        """Test coefficient of variation calculation."""
        detector = RegimeDetector()
        # Known CV: mean=10, std=2 → CV=0.2
        population = np.ones(200) * 10.0 + np.random.normal(0, 2.0, 200)

        result = detector.detect_regime(population)

        # CV should be close to 0.2 (allowing for sampling variance)
        assert 0.15 < result.metrics["cv"] < 0.25

    def test_extinction_fraction_accuracy(self):
        """Test extinction fraction calculation."""
        detector = RegimeDetector()
        # 40% of samples below 1.0
        population = np.concatenate([
            np.zeros(200),
            np.ones(300) * 10.0
        ])
        np.random.shuffle(population)

        result = detector.detect_regime(population)

        # Should detect ~40% extinction
        assert 0.35 < result.metrics["extinction_fraction"] < 0.45


class TestCrossValidationReadiness:
    """Test infrastructure for Gate 1.2 cross-validation."""

    def test_batch_classification(self):
        """Test detector can process multiple trajectories."""
        detector = RegimeDetector()

        # Generate known regimes
        collapse_traj = np.random.exponential(0.5, 500)
        accumulation_traj = 17.0 + np.random.normal(0, 1.5, 500)
        bistability_traj = 25.0 + np.random.normal(0, 2.0, 500)

        trajectories = [collapse_traj, accumulation_traj, bistability_traj]
        expected_regimes = [
            RegimeType.COLLAPSE,
            RegimeType.ACCUMULATION,
            RegimeType.BISTABILITY
        ]

        results = [detector.detect_regime(traj) for traj in trajectories]

        for result, expected in zip(results, expected_regimes):
            assert result.regime == expected

    def test_confidence_thresholding(self):
        """Test confidence scores enable threshold-based filtering."""
        detector = RegimeDetector()

        # High confidence case
        clear_collapse = np.random.exponential(0.3, 500)
        result_high = detector.detect_regime(clear_collapse)

        # Ambiguous case
        ambiguous = np.random.uniform(0, 10, 500)
        result_low = detector.detect_regime(ambiguous)

        # High confidence should exceed low confidence
        assert result_high.confidence > result_low.confidence

    def test_evidence_tracking(self):
        """Test evidence dictionary enables diagnostic review."""
        detector = RegimeDetector()
        population = np.random.exponential(0.5, 500)

        result = detector.detect_regime(population)

        assert len(result.evidence) > 0
        assert all(isinstance(k, str) for k in result.evidence.keys())


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
