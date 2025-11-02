"""
Temporal Structure Framework (TSF) - Core Science Engine

A domain-agnostic framework for systematic pattern discovery, validation, and
encoding as falsifiable Principle Cards.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Phase: 2 (TSF Science Engine)
Gate: 2.1 (Core API)
Cycle: 833+ (v0.2.0) → 880+ (v1.0.0-dev with PrincipleCard system)

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
    - Principle Cards as first-class objects (runnable, composable artifacts)
"""

# Core API (Cycle 833+)
from code.tsf.core import (
    observe,
    discover,
    refute,
    quantify,
    publish,
)

# Data structures (Cycle 833+)
from code.tsf.data import (
    ObservationalData,
    DiscoveredPattern,
    RefutationResult,
    QuantificationMetrics,
)

# Errors (Cycle 833+)
from code.tsf.errors import (
    TSFError,
    DataLoadError,
    SchemaValidationError,
    DiscoveryError,
    RefutationError,
    QuantificationError,
    PublicationError,
)

# Regime detection (Gate 1.2, Cycle 833+)
from code.tsf.regime_detection import (
    RegimeType,
    RegimeClassification,
    RegimeDetector,
    detect_regime,
)

# Principle Card system (Cycle 880+)
from code.tsf.principle_card import (
    PrincipleCard,
    PCMetadata,
    ValidationResult,
    PCValidationError,
    PCDependencyError,
    InsufficientDataError,
    RealityCheckFailedError,
    check_dependencies,
    validate_reality_grounding,
    compute_validation_order,
)

# Concrete Principle Card implementations (Cycle 880+)
from code.tsf.pc001_nrm_population_dynamics import (
    PC001_NRM_Population_Dynamics,
    load_pc001,
)

__version__ = "1.0.0-dev"  # Upgraded from 0.2.0 with PrincipleCard system
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

    # Regime detection (Gate 1.2)
    "RegimeType",
    "RegimeClassification",
    "RegimeDetector",
    "detect_regime",

    # Errors
    "TSFError",
    "DataLoadError",
    "SchemaValidationError",
    "DiscoveryError",
    "RefutationError",
    "QuantificationError",
    "PublicationError",

    # Principle Card system (NEW in v1.0.0)
    "PrincipleCard",
    "PCMetadata",
    "ValidationResult",
    "PCValidationError",
    "PCDependencyError",
    "InsufficientDataError",
    "RealityCheckFailedError",
    "check_dependencies",
    "validate_reality_grounding",
    "compute_validation_order",

    # Concrete Principle Cards (NEW in v1.0.0)
    "PC001_NRM_Population_Dynamics",
    "load_pc001",
]
