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

__version__ = "1.0.0"
__author__ = "Aldrin Payopay, Claude Sonnet 4.5"
__license__ = "GPL-3.0"

from .agent import FractalAgent
from .composition import CompositionEngine
from .decomposition import DecompositionEngine
from .memory import PatternMemory
from .resonance import ResonanceDetector

__all__ = [
    "FractalAgent",
    "CompositionEngine",
    "DecompositionEngine",
    "PatternMemory",
    "ResonanceDetector",
]
