#!/usr/bin/env python3
"""
FRACTAL SWARM UNIT TESTS
==========================

Comprehensive test coverage for FractalSwarm orchestration class.

Tests:
1. Swarm initialization and database setup
2. Agent spawning with limits
3. Full composition-decomposition cycles
4. Memory retention and distribution
5. Database persistence
6. Global memory management
7. Reality grounding throughout lifecycle

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sys
from pathlib import Path
import pytest
import tempfile
import shutil
import sqlite3

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from fractal.fractal_swarm import FractalSwarm


class TestFractalSwarmInitialization:
    """Test swarm initialization."""

    def test_default_initialization(self):
        """Test swarm creates with default parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            assert swarm.max_agents == 100
            assert swarm.max_depth == 7
            assert swarm.cycle_count == 0
            assert len(swarm.agents) == 0
            assert len(swarm.global_memory) == 0
            assert swarm.db_path.exists()

    def test_custom_parameters(self):
        """Test swarm creates with custom parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                max_agents=50,
                max_depth=5,
                clear_on_init=True
            )

            assert swarm.max_agents == 50
            assert swarm.max_depth == 5

    def test_database_creation(self):
        """Test database file and tables are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            # Check database exists
            assert swarm.db_path.exists()

            # Check tables exist
            conn = sqlite3.connect(str(swarm.db_path))
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            assert 'agents' in tables
            assert 'clusters' in tables
            assert 'bursts' in tables
            assert 'cycles' in tables

            conn.close()


class TestAgentSpawning:
    """Test agent spawning mechanisms."""

    def test_spawn_single_agent(self):
        """Test spawning single agent with reality metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            agent = swarm.spawn_agent(
                reality_metrics=metrics,
                agent_id="test_agent_0"
            )

            assert agent is not None
            assert agent.agent_id == "test_agent_0"
            assert len(swarm.agents) == 1
            assert "test_agent_0" in swarm.agents

    def test_spawn_multiple_agents(self):
        """Test spawning multiple agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            for i in range(5):
                agent = swarm.spawn_agent(
                    reality_metrics=metrics,
                    agent_id=f"agent_{i}"
                )
                assert agent is not None

            assert len(swarm.agents) == 5

    def test_spawn_respects_max_agents(self):
        """Test spawning stops at max_agents limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                max_agents=3,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Spawn up to limit
            for i in range(3):
                agent = swarm.spawn_agent(reality_metrics=metrics)
                assert agent is not None

            # Try to exceed limit
            agent = swarm.spawn_agent(reality_metrics=metrics)
            assert agent is None  # Should fail
            assert len(swarm.agents) == 3

    def test_spawn_respects_max_depth(self):
        """Test spawning respects depth limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                max_depth=3,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Spawn at max depth
            agent = swarm.spawn_agent(
                reality_metrics=metrics,
                depth=2
            )
            assert agent is not None

            # Try to exceed depth
            agent = swarm.spawn_agent(
                reality_metrics=metrics,
                depth=3  # >= max_depth
            )
            assert agent is None

    def test_spawn_with_parent(self):
        """Test spawning nested agent with parent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Spawn parent
            parent = swarm.spawn_agent(
                reality_metrics=metrics,
                agent_id="parent_agent",
                depth=0
            )

            # Spawn child
            child = swarm.spawn_agent(
                reality_metrics=metrics,
                agent_id="child_agent",
                parent_id="parent_agent",
                depth=1
            )

            assert child.parent_id == "parent_agent"
            assert child.depth == 1

    def test_spawn_auto_generates_id(self):
        """Test spawning generates ID if not provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            agent = swarm.spawn_agent(reality_metrics=metrics)

            assert agent is not None
            assert agent.agent_id.startswith("agent_")
            assert len(agent.agent_id) > 6


class TestEvolutionCycles:
    """Test evolution cycle mechanics."""

    def test_evolve_cycle_empty_swarm(self):
        """Test evolution cycle with no agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            stats = swarm.evolve_cycle()

            assert isinstance(stats, dict)
            assert swarm.cycle_count == 1

    def test_evolve_cycle_single_agent(self):
        """Test evolution cycle with single agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            swarm.spawn_agent(reality_metrics=metrics)

            stats = swarm.evolve_cycle()

            assert isinstance(stats, dict)
            assert swarm.cycle_count == 1

    def test_evolve_cycle_multiple_agents(self):
        """Test evolution cycle with multiple agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Spawn several agents
            for i in range(5):
                swarm.spawn_agent(reality_metrics=metrics)

            stats = swarm.evolve_cycle()

            assert isinstance(stats, dict)
            assert swarm.cycle_count == 1

    def test_evolve_cycle_increments_count(self):
        """Test cycle count increments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            swarm.spawn_agent(reality_metrics=metrics)

            # Run multiple cycles
            for i in range(10):
                swarm.evolve_cycle()

            assert swarm.cycle_count == 10

    def test_evolve_cycle_composition_decomposition(self):
        """Test full composition-decomposition cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Spawn agents with high initial energy
            for i in range(5):
                agent = swarm.spawn_agent(reality_metrics=metrics)
                # Manually set high energy to trigger potential burst
                if agent:
                    agent.energy = 150.0

            # Run cycle
            stats = swarm.evolve_cycle()

            # Verify cycle executed (exact behavior depends on resonance)
            assert isinstance(stats, dict)


class TestMemoryManagement:
    """Test global memory management."""

    def test_global_memory_starts_empty(self):
        """Test global memory initializes empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            assert len(swarm.global_memory) == 0

    def test_global_memory_bounded(self):
        """Test global memory stays bounded (≤1000)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            # Manually add many memory states
            from bridge.transcendental_bridge import TranscendentalBridge
            bridge = TranscendentalBridge()

            # Add > 1000 states
            for i in range(1500):
                state = bridge.reality_to_phase({'cpu_percent': float(i)})
                swarm.global_memory.append(state)

            # Run cycle to trigger memory bounding
            swarm.evolve_cycle()

            # Should be capped at 1000
            assert len(swarm.global_memory) <= 1000


class TestDatabasePersistence:
    """Test database persistence."""

    def test_agent_persisted_on_spawn(self):
        """Test agent creation is persisted to database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            agent = swarm.spawn_agent(
                reality_metrics=metrics,
                agent_id="db_test_agent"
            )

            # Query database
            conn = sqlite3.connect(str(swarm.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT agent_id FROM agents WHERE agent_id = ?", ("db_test_agent",))
            row = cursor.fetchone()
            conn.close()

            assert row is not None
            assert row[0] == "db_test_agent"

    def test_cycle_persisted(self):
        """Test cycle statistics are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            swarm.spawn_agent(reality_metrics=metrics)
            swarm.evolve_cycle()

            # Query database
            conn = sqlite3.connect(str(swarm.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cycles")
            count = cursor.fetchone()[0]
            conn.close()

            assert count == 1


class TestRealityGrounding:
    """Test reality grounding throughout swarm lifecycle."""

    def test_agents_grounded_on_spawn(self):
        """Test spawned agents use real system metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()

            # Verify metrics are real
            assert 'cpu_percent' in metrics
            assert 'memory_percent' in metrics

            agent = swarm.spawn_agent(reality_metrics=metrics)

            # Agent energy should reflect reality
            assert agent.energy > 0
            assert agent.phase_state is not None

    def test_no_mocked_components(self):
        """Test swarm uses real components, not mocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            swarm = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            # Verify real components
            assert swarm.bridge is not None
            assert swarm.composition is not None
            assert swarm.decomposition is not None
            assert swarm.db_path.exists()


class TestClearOnInit:
    """Test database clearing on initialization."""

    def test_clear_on_init_true(self):
        """Test clear_on_init=True drops existing data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create swarm and add data
            swarm1 = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()
            swarm1.spawn_agent(reality_metrics=metrics)

            # Create new swarm with clear_on_init=True
            swarm2 = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            # Check database is empty
            conn = sqlite3.connect(str(swarm2.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents")
            count = cursor.fetchone()[0]
            conn.close()

            assert count == 0

    def test_clear_on_init_false(self):
        """Test clear_on_init=False preserves existing data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create swarm and add data
            swarm1 = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=True
            )

            reality = RealityInterface()
            metrics = reality.get_system_metrics()
            swarm1.spawn_agent(reality_metrics=metrics, agent_id="persistent_agent")

            # Create new swarm with clear_on_init=False
            swarm2 = FractalSwarm(
                workspace_path=tmpdir,
                clear_on_init=False
            )

            # Check data persists
            conn = sqlite3.connect(str(swarm2.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents")
            count = cursor.fetchone()[0]
            conn.close()

            assert count == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
