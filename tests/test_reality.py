"""
Tests for nrm_core/reality.py
"""
import pytest
from nrm_core.reality import RealityMonitor, RealityValidator

def test_monitor_capture():
    monitor = RealityMonitor()
    metrics = monitor.capture()
    assert "timestamp" in metrics
    assert "cpu_percent" in metrics
    # We can't guarantee psutil is installed in the test env, so we check 'grounded' flag
    if metrics["grounded"]:
        assert metrics["process_count"] > 0
    else:
        assert metrics["cpu_percent"] == 0.0

def test_validator():
    # Test with current file
    assert RealityValidator.validate_path(__file__)
    assert RealityValidator.get_file_size(__file__) > 0
    assert not RealityValidator.validate_path("non_existent_file.txt")
