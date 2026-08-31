"""
NRM Core Package
"""
from .vector import Vector
from .resonance import ResonantField, ResonantNode
from .reality import RealityMonitor, RealityValidator
from .fractal import FractalAgent, Population
from .memory import PatternMemory, ConsolidationEngine
try:  # numpy-dependent (same graceful pattern reality.py uses for psutil)
    from .soundhack_spectral import (
        MutationSpec, MutationEngine, spectral_mutate, phase_vocoder,
        stft_analyze, stft_resynthesize, OscillatorBank,
    )
    from .soundhack_bridge import (
        AudioRealityAdapter, AudioEntropy, mutate_series,
        compose_trajectories, SwarmSonifier,
    )
except ImportError:  # pragma: no cover - numpy absent
    pass
from .constants import *
from .exceptions import *

__version__ = "0.0.1"