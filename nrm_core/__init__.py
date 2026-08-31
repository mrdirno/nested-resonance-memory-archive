"""
NRM Core Package
"""
from .vector import Vector
from .resonance import ResonantField, ResonantNode
from .reality import RealityMonitor, RealityValidator
from .fractal import FractalAgent, Population
from .memory import PatternMemory, ConsolidationEngine
from .soundhack_spectral import (
    MutationSpec, MutationEngine, spectral_mutate, phase_vocoder,
    stft_analyze, stft_resynthesize, OscillatorBank,
)
from .soundhack_bridge import (
    AudioRealityAdapter, AudioEntropy, mutate_series,
    compose_trajectories, SwarmSonifier,
)
from .constants import *
from .exceptions import *

__version__ = "0.0.1"