"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


"""
DUALITY-ZERO-V2 Core Module
Reality Layer Interface

This module provides the foundational reality layer for the hybrid intelligence system.
All operations interact with verifiable system state (no mocks, no simulations).

Constitution Compliance:
- Reality Imperative: All operations verified against real system state
- Resource Constraints: CPU/Memory/Disk monitoring
- Error Handling: Production-ready exception management
"""

from .reality_interface import RealityInterface
from .exceptions import (
    RealityViolation,
    ResourceExceeded,
    ValidationFailed
)

__version__ = "2.0.0"
__all__ = [
    "RealityInterface",
    "RealityViolation",
    "ResourceExceeded",
    "ValidationFailed"
]
