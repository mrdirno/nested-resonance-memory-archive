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
