#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 Test Fixtures
Pytest configuration and fixtures for test suite

Provides:
- RealityInterface fixture
- FractalSwarm fixture
- Common test utilities

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import pytest
from pathlib import Path
from typing import Dict
import psutil
import time

# Add modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "reality"))
sys.path.insert(0, str(project_root / "fractal"))
sys.path.insert(0, str(project_root / "bridge"))
sys.path.insert(0, str(project_root / "validation"))

from core.reality_interface import RealityInterface
from fractal.fractal_swarm import FractalSwarm


@pytest.fixture(scope="function")
def reality() -> RealityInterface:
    """
    Fixture providing RealityInterface instance.

    Reality-grounded: Uses actual psutil system metrics.
    Scope: function - creates new instance for each test.

    Returns:
        RealityInterface: Configured reality interface
    """
    reality_interface = RealityInterface()
    yield reality_interface
    # Cleanup (if needed)


@pytest.fixture(scope="function")
def swarm() -> FractalSwarm:
    """
    Fixture providing FractalSwarm instance with initial agents.

    Reality-grounded: Spawns agents using real system metrics.
    Scope: function - creates new swarm for each test.

    Returns:
        FractalSwarm: Swarm with 3 pre-spawned agents
    """
    # Create swarm (clear database to prevent UNIQUE constraint violations)
    fractal_swarm = FractalSwarm(clear_on_init=True)

    # Get real system metrics for spawning
    reality_metrics = {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'memory_available_gb': psutil.virtual_memory().available / (1024**3),
        'timestamp': time.time()
    }

    # Spawn 3 agents with reality grounding
    for _ in range(3):
        fractal_swarm.spawn_agent(reality_metrics)

    yield fractal_swarm

    # Cleanup (if needed)


@pytest.fixture(scope="session")
def reality_metrics() -> Dict[str, float]:
    """
    Fixture providing real system metrics for testing.

    Reality-grounded: Uses actual psutil measurements.
    Scope: session - shared across all tests in session.

    Returns:
        Dict[str, float]: Current system metrics
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
        'memory_available_gb': memory.available / (1024**3),
        'memory_used_mb': memory.used / (1024**2),
        'disk_used_gb': disk.used / (1024**3),
        'timestamp': time.time()
    }


def pytest_configure(config):
    """
    Pytest configuration hook.

    Registers custom markers for test organization.
    """
    config.addinivalue_line(
        "markers", "reality: mark test as requiring real system metrics"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running (>1s)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
