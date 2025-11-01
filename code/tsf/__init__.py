"""
Temporal Stewardship Framework (TSF) - Core Science Engine

A domain-agnostic framework for systematic pattern discovery, validation, and
encoding as falsifiable Principle Cards.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Phase: 2 (TSF Science Engine)
Gate: 2.1 (Core API)
Cycle: 833+

Architecture:
    1. observe()  - Load and prepare observational data
    2. discover() - Find patterns in observations
    3. refute()   - Test patterns at extended horizons
    4. quantify() - Measure pattern strength
    5. publish()  - Create validated Principle Cards

Design Principles:
    - Domain agnosticism (works across physics, biology, economics, etc.)
    - Reality grounding (all operations bound to actual data)
    - Falsifiability (every pattern must be refutable)
    - Composability (PCs can depend on other PCs via TEG)
    - Temporal awareness (multi-timescale validation)
"""

from code.tsf.core import (
    observe,
    discover,
    refute,
    quantify,
    publish,
)

from code.tsf.data import (
    ObservationalData,
    DiscoveredPattern,
    RefutationResult,
    QuantificationMetrics,
)

from code.tsf.errors import (
    TSFError,
    DataLoadError,
    SchemaValidationError,
    DiscoveryError,
    RefutationError,
    QuantificationError,
    PublicationError,
)

__version__ = "0.1.0"
__author__ = "Aldrin Payopay <aldrin.gdf@gmail.com>"

__all__ = [
    # Core API
    "observe",
    "discover",
    "refute",
    "quantify",
    "publish",
    # Data structures
    "ObservationalData",
    "DiscoveredPattern",
    "RefutationResult",
    "QuantificationMetrics",
    # Errors
    "TSFError",
    "DataLoadError",
    "SchemaValidationError",
    "DiscoveryError",
    "RefutationError",
    "QuantificationError",
    "PublicationError",
]
