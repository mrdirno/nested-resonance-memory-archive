"""
Tests for tsf.publish() function

Validates Principle Card creation from validated patterns.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path
import json

from src.tsf.core import observe, discover, refute, quantify, publish
from src.tsf.errors import PublicationError


class TestPublishBasic:
    """Test basic publish() functionality."""

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

    def test_publish_valid_pattern(self, tmp_path):
        """Test publishing a valid pattern."""
        # Create training and validation data
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        # Full workflow
        pattern = discover(training_data, "regime_classification")
        refutation = refute(pattern, "10x", tolerance=0.2, validation_data=validation_data)
        metrics = quantify(pattern, validation_data, ["stability", "consistency"])

        # Publish
        pc_path = publish(
            pattern=pattern,
            metrics=metrics,
            refutation=refutation,
            pc_id="PC999",
            title="Test Principle Card",
            author="Test Author <test@example.com>"
        )

        # Validate PC file created
        assert pc_path.exists()
        assert pc_path.name == "pc999_specification.json"

        # Validate PC content
        with open(pc_path) as f:
            pc_spec = json.load(f)

        assert pc_spec["pc_id"] == "PC999"
        assert pc_spec["title"] == "Test Principle Card"
        assert pc_spec["status"] == "validated"
        assert "discovery" in pc_spec
        assert "refutation" in pc_spec
        assert "quantification" in pc_spec

    def test_publish_failed_refutation(self, tmp_path):
        """Test that failed refutation blocks publication."""
        # Create training data (sustained)
        training_pop = [100.0] * 100
        training_data = self._create_test_data(tmp_path, training_pop, "training")

        # Create validation data (collapse - different regime)
        validation_pop = [2.0] * 100
        validation_data = self._create_test_data(tmp_path, validation_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        refutation = refute(pattern, "10x", tolerance=0.1, validation_data=validation_data)
        metrics = quantify(pattern, validation_data, ["stability"])

        # Should fail - refutation did not pass
        with pytest.raises(PublicationError) as exc_info:
            publish(
                pattern=pattern,
                metrics=metrics,
                refutation=refutation,
                pc_id="PC998",
                title="Failed Pattern",
                author="Test Author <test@example.com>"
            )

        assert "failed refutation" in str(exc_info.value).lower()

    def test_publish_invalid_pc_id(self, tmp_path):
        """Test error handling for invalid PC ID."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        refutation = refute(pattern, "10x", tolerance=0.2, validation_data=validation_data)
        metrics = quantify(pattern, validation_data, ["stability"])

        # Invalid PC ID (doesn't start with "PC")
        with pytest.raises(PublicationError) as exc_info:
            publish(
                pattern=pattern,
                metrics=metrics,
                refutation=refutation,
                pc_id="INVALID",
                title="Test",
                author="Test <test@example.com>"
            )

        assert "must start with" in str(exc_info.value).lower()

    def test_publish_with_dependencies(self, tmp_path):
        """Test publishing with dependencies."""
        training_pop = [100.0 + np.random.normal(0, 2) for _ in range(100)]
        training_data = self._create_test_data(tmp_path, training_pop, "training")
        validation_data = self._create_test_data(tmp_path, training_pop, "validation")

        pattern = discover(training_data, "regime_classification")
        refutation = refute(pattern, "10x", tolerance=0.2, validation_data=validation_data)
        metrics = quantify(pattern, validation_data, ["stability"])

        # Publish with dependencies
        pc_path = publish(
            pattern=pattern,
            metrics=metrics,
            refutation=refutation,
            pc_id="PC997",
            title="Dependent PC",
            author="Test <test@example.com>",
            dependencies=["PC001", "PC002"]
        )

        # Validate dependencies in spec
        with open(pc_path) as f:
            pc_spec = json.load(f)

        assert pc_spec["dependencies"] == ["PC001", "PC002"]


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow_end_to_end(self):
        """Test complete observe → discover → refute → quantify → publish workflow."""
        data_dir = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/data/results")

        pc001_files = list(data_dir.glob("test_pc001_pc_validation_*.json"))
        if not pc001_files:
            pytest.skip("No PC001 data files found")

        # Use same file for training and validation (should pass all checks)
        data = observe(pc001_files[0], "population_dynamics", "pc001")

        # Full TSF workflow
        pattern = discover(data, "regime_classification")
        refutation = refute(pattern, "10x", tolerance=0.1, validation_data=data)
        metrics = quantify(pattern, data, ["stability", "consistency"])

        # Publish
        pc_path = publish(
            pattern=pattern,
            metrics=metrics,
            refutation=refutation,
            pc_id="PC996",
            title="End-to-End Test PC",
            author="Aldrin Payopay <aldrin.gdf@gmail.com>"
        )

        # Validate created PC
        assert pc_path.exists()

        with open(pc_path) as f:
            pc_spec = json.load(f)

        # Validate all sections present
        assert pc_spec["status"] == "validated"
        assert pc_spec["discovery"]["method"] == "regime_classification"
        assert pc_spec["refutation"]["passed"] is True
        assert "stability" in pc_spec["quantification"]["scores"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
