#!/usr/bin/env python3
"""
Tests for Overhead Authenticator - Gate 1.4
============================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path

# Add validation module to path
sys.path.insert(0, str(Path(__file__).parent))

from overhead_authenticator import (
    OverheadAuthenticator,
    OverheadMeasurement,
    OverheadManifest
)


class TestOverheadAuthenticator:
    """Test overhead authentication system."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def authenticator(self, temp_workspace):
        """Create authenticator with temp workspace."""
        return OverheadAuthenticator(workspace_path=str(temp_workspace))

    def test_initialization(self, authenticator, temp_workspace):
        """Test authenticator initializes correctly."""
        assert authenticator.workspace_path == temp_workspace
        assert authenticator.manifest_path.parent == temp_workspace
        assert authenticator.db_path.parent == temp_workspace
        assert authenticator.db_path.exists()

    def test_measure_overhead_within_threshold(self, authenticator):
        """Test measurement that passes ±5% authentication."""
        # C255 data from Paper 1: 99.9% match (well within ±5%)
        measurement = authenticator.measure_overhead(
            operation_name="C255_baseline",
            instrumentation_count=1080000,  # N
            per_call_cost_ms=67.0,  # C (67 milliseconds)
            baseline_runtime_min=30.0,  # T_sim
            measured_runtime_min=1207.5  # T_measured (40.25× overhead)
        )

        assert measurement.passes_authentication
        assert measurement.relative_error < 0.05
        assert measurement.predicted_overhead > 0
        assert measurement.observed_overhead > 0

    def test_measure_overhead_exceeds_threshold(self, authenticator):
        """Test measurement that fails ±5% authentication."""
        # Deliberately bad prediction
        measurement = authenticator.measure_overhead(
            operation_name="bad_prediction",
            instrumentation_count=1000000,
            per_call_cost_ms=30.0,  # Too low (should be ~67ms)
            baseline_runtime_min=30.0,
            measured_runtime_min=1200.0  # High overhead
        )

        assert not measurement.passes_authentication
        assert measurement.relative_error > 0.05

    def test_create_manifest(self, authenticator):
        """Test manifest creation from measurements."""
        # Create several measurements
        measurements = []

        # Good measurements (pass)
        for i in range(3):
            m = authenticator.measure_overhead(
                operation_name=f"operation_{i}",
                instrumentation_count=1000000,
                per_call_cost_ms=67.0,
                baseline_runtime_min=30.0,
                measured_runtime_min=1120.0 + i * 10  # Slight variation
            )
            measurements.append(m)

        # Bad measurement (fail)
        m = authenticator.measure_overhead(
            operation_name="bad_operation",
            instrumentation_count=1000000,
            per_call_cost_ms=10.0,  # Way too low
            baseline_runtime_min=30.0,
            measured_runtime_min=1200.0
        )
        measurements.append(m)

        # Create manifest
        manifest = authenticator.create_manifest(
            measurements=measurements,
            description="Test manifest"
        )

        assert manifest.total_measurements == 4
        assert manifest.passing_measurements == 3
        assert manifest.pass_rate == 0.75
        assert manifest.threshold_percent == 5.0

    def test_save_and_load_manifest(self, authenticator):
        """Test manifest persistence."""
        # Create measurement
        measurement = authenticator.measure_overhead(
            operation_name="test_op",
            instrumentation_count=1080000,
            per_call_cost_ms=67.0,
            baseline_runtime_min=30.0,
            measured_runtime_min=1207.5
        )

        # Create and save manifest
        manifest = authenticator.create_manifest(
            measurements=[measurement],
            description="Test manifest"
        )

        # Load manifest
        loaded = authenticator.load_manifest()

        assert loaded is not None
        assert loaded.version == manifest.version
        assert loaded.total_measurements == 1
        assert loaded.measurements[0].operation_name == "test_op"

    def test_validate_manifest_passing(self, authenticator):
        """Test manifest validation that passes."""
        # Create passing measurement
        measurement = authenticator.measure_overhead(
            operation_name="passing_op",
            instrumentation_count=1080000,
            per_call_cost_ms=67.0,
            baseline_runtime_min=30.0,
            measured_runtime_min=1207.5
        )

        # Create manifest
        authenticator.create_manifest(
            measurements=[measurement],
            description="Passing manifest"
        )

        # Validate
        passed, errors, warnings = authenticator.validate_manifest(strict=True)

        assert passed
        assert len(errors) == 0

    def test_validate_manifest_failing(self, authenticator):
        """Test manifest validation that fails."""
        # Create failing measurement
        measurement = authenticator.measure_overhead(
            operation_name="failing_op",
            instrumentation_count=1000000,
            per_call_cost_ms=30.0,  # Too low (should be ~67ms for 1200min measured)
            baseline_runtime_min=30.0,
            measured_runtime_min=1200.0
        )

        # Create manifest
        authenticator.create_manifest(
            measurements=[measurement],
            description="Failing manifest"
        )

        # Validate
        passed, errors, warnings = authenticator.validate_manifest(strict=True)

        assert not passed
        assert len(errors) > 0
        assert "exceeds" in errors[0]

    def test_get_recent_measurements(self, authenticator):
        """Test retrieving recent measurements."""
        # Create measurements
        for i in range(5):
            authenticator.measure_overhead(
                operation_name=f"op_{i}",
                instrumentation_count=1000000,
                per_call_cost_ms=67.0,
                baseline_runtime_min=30.0,
                measured_runtime_min=1120.0
            )

        # Retrieve
        recent = authenticator.get_recent_measurements(hours=24.0)

        assert len(recent) == 5

        # Filter by operation name
        filtered = authenticator.get_recent_measurements(
            hours=24.0,
            operation_name="op_0"
        )

        assert len(filtered) == 1
        assert filtered[0].operation_name == "op_0"

    def test_get_statistics(self, authenticator):
        """Test statistics generation."""
        # Create measurements (3 pass, 1 fail)
        for i in range(3):
            authenticator.measure_overhead(
                operation_name=f"passing_{i}",
                instrumentation_count=1080000,
                per_call_cost_ms=67.0,
                baseline_runtime_min=30.0,
                measured_runtime_min=1207.5
            )

        authenticator.measure_overhead(
            operation_name="failing",
            instrumentation_count=1000000,
            per_call_cost_ms=30.0,
            baseline_runtime_min=30.0,
            measured_runtime_min=1200.0
        )

        stats = authenticator.get_statistics()

        assert stats['total_measurements'] == 4
        assert stats['passing_measurements'] == 3
        assert stats['pass_rate'] == 0.75
        assert stats['threshold_percent'] == 5.0

    def test_overhead_calculation_accuracy(self, authenticator):
        """Test overhead calculation matches Paper 1 formula."""
        # C255 parameters from Paper 1
        N = 1080000  # Instrumentation calls
        C_ms = 67.0  # Per-call cost (67 milliseconds)
        T_sim_min = 30.0  # Baseline simulation time
        T_measured_min = 1207.5  # Measured runtime (20.125 hours)

        measurement = authenticator.measure_overhead(
            operation_name="C255",
            instrumentation_count=N,
            per_call_cost_ms=C_ms,
            baseline_runtime_min=T_sim_min,
            measured_runtime_min=T_measured_min
        )

        # Expected calculations
        total_instrumentation_min = (N * C_ms) / (1000.0 * 60.0)  # Convert to minutes
        O_pred = total_instrumentation_min / T_sim_min  # Should be ~40.2
        O_obs = T_measured_min / T_sim_min  # Should be ~40.25

        assert abs(measurement.predicted_overhead - O_pred) < 0.01
        assert abs(measurement.observed_overhead - O_obs) < 0.01

        # C255 had 99.9% match, so error should be ~0.1%
        assert measurement.relative_error < 0.01

    def test_database_persistence(self, authenticator):
        """Test measurements persist to database."""
        # Create measurement
        measurement = authenticator.measure_overhead(
            operation_name="persist_test",
            instrumentation_count=1000000,
            per_call_cost_ms=67.0,
            baseline_runtime_min=30.0,
            measured_runtime_min=1120.0,
            metadata={'experiment': 'C255', 'seed': 42}
        )

        # Create new authenticator instance (fresh connection)
        authenticator2 = OverheadAuthenticator(
            workspace_path=str(authenticator.workspace_path)
        )

        # Retrieve measurement
        recent = authenticator2.get_recent_measurements(hours=24.0)

        assert len(recent) > 0
        found = [m for m in recent if m.operation_name == "persist_test"]
        assert len(found) == 1
        assert found[0].metadata.get('experiment') == 'C255'
        assert found[0].metadata.get('seed') == 42


class TestRealityGrounding:
    """Test reality grounding compliance."""

    def test_no_mocks_in_authenticator(self):
        """Verify authenticator uses real implementations."""
        import inspect
        source = inspect.getsource(OverheadAuthenticator)

        # Check for mock patterns
        mock_patterns = ['Mock', 'patch', '@mock', 'fake_', 'dummy_']
        for pattern in mock_patterns:
            assert pattern not in source, f"Found {pattern} in source"

    def test_no_sleep_delays(self):
        """Verify no artificial delays."""
        import inspect
        source = inspect.getsource(OverheadAuthenticator)

        assert 'time.sleep' not in source
        assert 'asyncio.sleep' not in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
