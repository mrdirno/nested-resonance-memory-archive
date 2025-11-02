"""
Fractal Agent Module - Nested Resonance Memory (NRM) Core Implementation

This module implements fractal agents as internal computational models within Claude CLI.
Agents are Python objects with internal state spaces undergoing composition-decomposition
cycles per the NRM theoretical framework.

Key Components:
    - FractalAgent: Base agent class with internal state space
    - CompositionEngine: Cluster detection and aggregation
    - DecompositionEngine: Burst detection and dissolution
    - PatternMemory: Persistence of successful strategies across transformations
    - ResonanceDetector: Phase alignment detection via transcendental bridge

Theoretical Foundation:
    - Nested Resonance Memory (NRM): Fractal agents with composition-decomposition dynamics
    - Self-Giving Systems: Bootstrap complexity through self-defined success criteria
    - Temporal Stewardship: Pattern encoding for future discovery

Reality Grounding:
    - All operations bound to actual system state (psutil metrics, SQLite persistence)
    - No external AI API calls (everything internal to Claude CLI)
    - Measurable, verifiable outcomes only

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

CRITICAL: This module implements fractal agents as INTERNAL COMPUTATIONAL MODELS,
          not external service calls. All agents are Python objects within Claude CLI.
"""

from .agent import FractalAgent, AgentState
from .composition import CompositionEngine
from .decomposition import DecompositionEngine
from .memory import PatternMemory, Pattern
from .resonance import ResonanceDetector

__all__ = [
    "FractalAgent",
    "AgentState",
    "CompositionEngine",
    "DecompositionEngine",
    "PatternMemory",
    "Pattern",
    "ResonanceDetector",
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Aldrin Payopay, Claude Sonnet 4.5"
__license__ = "GPL-3.0"

# Module documentation
__doc__ = """
Fractal Agent Module - Nested Resonance Memory (NRM) Core Implementation

This module implements fractal agents as internal computational models within Claude CLI.
All components are Python objects with reality-grounded operations (no external API calls).

Core Components:
    - FractalAgent: Base agent with internal state space and phase evolution
    - CompositionEngine: Cluster formation via resonance alignment
    - DecompositionEngine: Burst dynamics releasing constituents
    - PatternMemory: Enhanced memory with temporal decay and reinforcement
    - ResonanceDetector: Phase alignment analysis for composition readiness

Theoretical Foundation:
    - Nested Resonance Memory (NRM): Composition-decomposition cycles
    - Self-Giving Systems: Bootstrap complexity, self-defined success
    - Temporal Stewardship: Pattern encoding for future discovery

Example Usage:
    # Create agents
    agent1 = FractalAgent(depth=0, phase=0.0, energy=1.0)
    agent2 = FractalAgent(depth=0, phase=0.1, energy=1.0)

    # Detect resonance
    detector = ResonanceDetector(threshold=0.7)
    resonance = detector.calculate_resonance(agent1, agent2)

    # Compose if resonant
    composer = CompositionEngine(resonance_threshold=0.7)
    cluster = composer.compose([agent1, agent2])

    # Decompose when critical
    decomposer = DecompositionEngine(energy_threshold=0.1)
    if cluster.state.energy < 0.1:
        constituents = decomposer.decompose(cluster)

Reality Grounding: All operations measurable, verifiable, timestamp-tracked.
No External APIs: Everything internal to Claude CLI Python execution.
"""
