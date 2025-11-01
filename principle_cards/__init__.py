"""
Principle Cards - Executable Scientific Principles
==================================================

Domain-agnostic framework for encoding scientific principles as
runnable, falsifiable, composable artifacts.

Part of TSF (Science Engine) - Phase 2

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from .base import PrincipleCard, ValidationResult, PCMetadata
from .teg import TemporalEmbeddingGraph, PCNode, create_teg_from_pcs

__version__ = "1.0.0"
__all__ = [
    'PrincipleCard',
    'ValidationResult',
    'PCMetadata',
    'TemporalEmbeddingGraph',
    'PCNode',
    'create_teg_from_pcs'
]
