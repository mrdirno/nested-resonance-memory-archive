"""
Tests for tsf.quantify() function

Validates pattern strength quantification with validation metrics.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path
import json

from code.tsf.core import observe, discover, quantify
from code.tsf.data import QuantificationMetrics
from code.tsf.errors import QuantificationError


class TestQuantifyBasic:
    """Test basic quantify() functionality."""

    def _create_test_data(self, tmp_path, population, experiment_id):
        """Helper to create test observational data."""
        computed_mean = np.mean(population)
        computed_std = np.std(population, ddof=1) if len(population) > 1 else 0.0

        data = {
            "metadata": {"experiment_id": experiment_id, "pc_id": "PC001"},
            "timeseries": {"population": population, "time": list(range(len(population)))},
            "statistics": {"mean": computed_mean, "std": computed_std}
        }

        data_file = tmp_path / f"{experiment_id}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f)

        return observe(source=data_file, domain="population_dynamics", schema="pc001")

    def test_quantify_stability(self, tmp_path):
        """Test stability metric."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        metrics = quantify(pattern, validation_data, ["stability"])

        assert isinstance(metrics, QuantificationMetrics)
        assert "stability" in metrics.scores
        assert metrics.scores["stability"] in [0.0, 1.0]

    def test_quantify_consistency(self, tmp_path):
        """Test consistency metric."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        metrics = quantify(pattern, validation_data, ["consistency"])

        assert "consistency" in metrics.scores
        assert 0.0 <= metrics.scores["consistency"] <= 1.0

    def test_quantify_robustness(self, tmp_path):
        """Test robustness metric."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        metrics = quantify(pattern, validation_data, ["robustness"])

        assert "robustness" in metrics.scores
        assert 0.0 <= metrics.scores["robustness"] <= 1.0

    def test_quantify_multiple_criteria(self, tmp_path):
        """Test multiple criteria together."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        metrics = quantify(pattern, validation_data, ["stability", "consistency", "robustness"])

        assert "stability" in metrics.scores
        assert "consistency" in metrics.scores
        assert "robustness" in metrics.scores

    def test_quantify_invalid_criteria(self, tmp_path):
        """Test error handling for invalid criteria."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")

        with pytest.raises(QuantificationError) as exc_info:
            quantify(pattern, validation_data, ["invalid_metric"])

        assert "invalid criteria" in str(exc_info.value).lower()

    def test_confidence_intervals_present(self, tmp_path):
        """Test that confidence intervals are computed."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        metrics = quantify(pattern, validation_data, ["consistency"])

        assert "consistency" in metrics.confidence_intervals
        ci = metrics.confidence_intervals["consistency"]
        assert len(ci) == 2
        assert ci[0] <= metrics.scores["consistency"] <= ci[1]


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow(self):
        """Test full observe → discover → quantify workflow."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))
        if not pc001_files:
            pytest.skip("No PC001 data files found")

        # Use same file for training and validation (should get high scores)
        data = observe(pc001_files[0], "population_dynamics", "pc001")

        pattern = discover(data, "regime_classification")
        metrics = quantify(pattern, data, ["stability", "consistency"])

        assert metrics.scores["stability"] == 1.0  # Same data = perfect stability
        assert metrics.scores["consistency"] > 0.95  # High consistency expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
