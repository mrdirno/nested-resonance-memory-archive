"""
DUALITY-ZERO-V2 Fractal Module

Nested agent architecture implementing Nested Resonance Memory (NRM) framework.

Exports:
- FractalAgent: Individual agent with internal universe
- FractalSwarm: Multi-agent orchestration
- CompositionEngine: Coalition detection and cluster formation
- DecompositionEngine: Burst generation and agent spawning
- AgentState, ClusterEvent, BurstEvent: Data structures

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from .fractal_agent import (
    FractalAgent,
    AgentState,
    ClusterEvent,
    BurstEvent
)

from .fractal_swarm import (
    FractalSwarm,
    CompositionEngine,
    DecompositionEngine
)

__all__ = [
    'FractalAgent',
    'FractalSwarm',
    'CompositionEngine',
    'DecompositionEngine',
    'AgentState',
    'ClusterEvent',
    'BurstEvent'
]

__version__ = '2.0.0'
