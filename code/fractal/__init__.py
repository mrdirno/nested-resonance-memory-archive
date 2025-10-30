"""
DUALITY-ZERO-V2 Fractal Module

Nested agent architecture implementing Nested Resonance Memory (NRM) framework.

Exports:
- FractalAgent: Individual agent with internal universe
- FractalSwarm: Multi-agent orchestration
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

from .fractal_swarm import FractalSwarm

__all__ = [
    'FractalAgent',
    'FractalSwarm',
    'AgentState',
    'ClusterEvent',
    'BurstEvent'
]

__version__ = '2.0.0'
