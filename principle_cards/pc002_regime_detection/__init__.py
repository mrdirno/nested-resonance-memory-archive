"""
PC002: Regime Detection in Population Dynamics
===============================================

Compositional Principle Card depending on PC001 for baseline dynamics.
Classifies population regimes: baseline, growth, collapse, oscillatory.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from .principle import PC002_RegimeDetection
from .features import (
    RegimeFeatureExtractor,
    BaselineParams,
    RegimeFeatures
)
from .classifier import (
    RegimeClassifier,
    ClassificationMetrics,
    REGIME_TYPES,
    BASELINE,
    GROWTH,
    COLLAPSE,
    OSCILLATORY
)

__version__ = "1.0.0"
__status__ = "draft"
__dependencies__ = ["PC001"]

__all__ = [
    # Core principle
    'PC002_RegimeDetection',
    # Feature extraction
    'RegimeFeatureExtractor',
    'BaselineParams',
    'RegimeFeatures',
    # Classification
    'RegimeClassifier',
    'ClassificationMetrics',
    'REGIME_TYPES',
    'BASELINE',
    'GROWTH',
    'COLLAPSE',
    'OSCILLATORY',
]
