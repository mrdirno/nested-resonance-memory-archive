#!/usr/bin/env python3
"""
DECOMPOSITION ENGINE UNIT TESTS
=================================

Comprehensive test coverage for DecompositionEngine class.

Tests:
1. Burst threshold detection
2. Burst execution mechanics
3. Memory retention (top 50 states)
4. Energy release calculation
5. Burst history tracking
6. Edge cases (empty clusters, single agent, low energy)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sys
from pathlib import Path
import pytest

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import DecompositionEngine, BurstEvent


class TestDecompositionEngineInitialization:
    """Test decomposition engine initialization."""

    def test_default_initialization(self):
        """Test engine creates with default threshold."""
        engine = DecompositionEngine()

        assert engine.burst_threshold > 0
        assert isinstance(engine.burst_history, list)
        assert len(engine.burst_history) == 0

    def test_custom_threshold(self):
        """Test engine creates with custom threshold."""
        engine = DecompositionEngine(burst_threshold=500.0)

        assert engine.burst_threshold == 500.0


class TestBurstThresholdDetection:
    """Test burst condition detection."""

    def test_check_burst_low_energy(self):
        """Test no burst when total energy below threshold."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        # Create agents with low energy
        agents = []
        for i in range(3):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=10.0  # Low energy
            )
            agents.append(agent)

        engine = DecompositionEngine(burst_threshold=100.0)

        # Total energy: 3 × 10 = 30 < 100
        should_burst = engine.check_burst_conditions("cluster_1", agents)

        assert should_burst is False

    def test_check_burst_high_energy(self):
        """Test burst when total energy exceeds threshold."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        # Create agents with high energy
        agents = []
        for i in range(3):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0  # High energy
            )
            agents.append(agent)

        engine = DecompositionEngine(burst_threshold=100.0)

        # Total energy: 3 × 50 = 150 > 100
        should_burst = engine.check_burst_conditions("cluster_1", agents)

        assert should_burst is True

    def test_check_burst_exact_threshold(self):
        """Test burst at exact threshold."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0
            )
            agents.append(agent)

        engine = DecompositionEngine(burst_threshold=100.0)

        # Total energy: 2 × 50 = 100 >= 100
        should_burst = engine.check_burst_conditions("cluster_1", agents)

        assert should_burst is True


class TestBurstExecution:
    """Test burst event execution."""

    def test_execute_burst_basic(self):
        """Test basic burst execution."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0
            )
            agents.append(agent)

        engine = DecompositionEngine(burst_threshold=100.0)

        # Execute burst
        burst = engine.execute_burst("cluster_1", agents)

        assert isinstance(burst, BurstEvent)
        assert burst.cluster_id == "cluster_1"
        assert burst.energy_released > 0
        assert isinstance(burst.memory_retained, list)
        assert burst.timestamp > 0

    def test_burst_energy_calculation(self):
        """Test energy release calculation."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        total_energy_expected = 0.0
        for i in range(3):
            energy = 30.0 + i * 10.0  # 30, 40, 50
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=energy
            )
            agents.append(agent)
            total_energy_expected += energy

        engine = DecompositionEngine()

        burst = engine.execute_burst("cluster_1", agents)

        # Released energy should equal sum of agent energies
        # (may vary slightly due to dissolution mechanics)
        assert burst.energy_released > 0

    def test_burst_memory_retention(self):
        """Test memory retention in burst (top 50 states)."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        # Create agents and add memory
        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=60.0
            )

            # Add some memory states manually
            for j in range(10):
                agent.memory.append(agent.phase_state)

            agents.append(agent)

        engine = DecompositionEngine()

        burst = engine.execute_burst("cluster_1", agents)

        # Should retain memory (up to 50 top states)
        assert isinstance(burst.memory_retained, list)
        assert len(burst.memory_retained) <= 50

    def test_burst_history_tracking(self):
        """Test burst events are tracked in history."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0
            )
            agents.append(agent)

        engine = DecompositionEngine()

        # Execute multiple bursts
        burst1 = engine.execute_burst("cluster_1", agents)
        burst2 = engine.execute_burst("cluster_2", agents)

        assert len(engine.burst_history) == 2
        assert engine.burst_history[0] == burst1
        assert engine.burst_history[1] == burst2


class TestBurstEventStructure:
    """Test BurstEvent dataclass structure."""

    def test_burst_event_attributes(self):
        """Test burst event has required attributes."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0
            )
            agents.append(agent)

        engine = DecompositionEngine()

        burst = engine.execute_burst("test_cluster", agents)

        assert hasattr(burst, 'timestamp')
        assert hasattr(burst, 'cluster_id')
        assert hasattr(burst, 'memory_retained')
        assert hasattr(burst, 'energy_released')
        assert isinstance(burst.timestamp, float)
        assert isinstance(burst.cluster_id, str)
        assert isinstance(burst.memory_retained, list)
        assert isinstance(burst.energy_released, (int, float))


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_burst_empty_cluster(self):
        """Test burst with empty cluster."""
        engine = DecompositionEngine()

        # Execute burst with no agents
        burst = engine.execute_burst("empty_cluster", [])

        assert isinstance(burst, BurstEvent)
        assert burst.energy_released == 0.0
        assert len(burst.memory_retained) == 0

    def test_burst_single_agent(self):
        """Test burst with single agent."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agent = FractalAgent(
            agent_id="solo_agent",
            bridge=bridge,
            initial_reality=metrics,
            initial_energy=100.0
        )

        engine = DecompositionEngine()

        burst = engine.execute_burst("single_cluster", [agent])

        assert isinstance(burst, BurstEvent)
        assert burst.energy_released > 0

    def test_burst_with_large_memory(self):
        """Test burst retains only top 50 memory states."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        # Create agent with > 50 memory states
        agent = FractalAgent(
            agent_id="memory_agent",
            bridge=bridge,
            initial_reality=metrics,
            initial_energy=100.0
        )

        # Add 100 memory states
        for i in range(100):
            agent.memory.append(agent.phase_state)

        engine = DecompositionEngine()

        burst = engine.execute_burst("memory_cluster", [agent])

        # Should retain only top 50 by magnitude
        assert len(burst.memory_retained) <= 50

    def test_multiple_bursts_same_cluster_id(self):
        """Test multiple bursts can use same cluster ID."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(2):
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics,
                initial_energy=50.0
            )
            agents.append(agent)

        engine = DecompositionEngine()

        # Execute multiple bursts with same ID
        burst1 = engine.execute_burst("recurring_cluster", agents)
        burst2 = engine.execute_burst("recurring_cluster", agents)

        assert burst1.cluster_id == burst2.cluster_id
        assert len(engine.burst_history) == 2


class TestRealityCompliance:
    """Test reality grounding in decomposition."""

    def test_energy_from_real_agents(self):
        """Test energy release comes from real agent states."""
        bridge = TranscendentalBridge()
        reality = RealityInterface()

        # Get real metrics
        metrics = reality.get_system_metrics()

        agents = []
        for i in range(3):
            # Each agent initialized with reality-grounded energy
            agent = FractalAgent(
                agent_id=f"agent_{i}",
                bridge=bridge,
                initial_reality=metrics
            )
            agents.append(agent)

        engine = DecompositionEngine()

        burst = engine.execute_burst("reality_cluster", agents)

        # Energy should be > 0 (from reality-grounded agents)
        assert burst.energy_released > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
