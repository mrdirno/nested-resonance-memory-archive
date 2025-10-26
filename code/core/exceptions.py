"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


"""
DUALITY-ZERO-V2 Core Exceptions
Reality-grounded exception hierarchy
"""


class DualityException(Exception):
    """Base exception for all DUALITY-ZERO-V2 errors"""
    pass


class RealityViolation(DualityException):
    """
    Raised when an operation attempts to violate the Reality Imperative.
    Examples: Using mocks, simulations without validation, placeholder data.
    """
    pass


class ResourceExceeded(DualityException):
    """
    Raised when resource constraints are exceeded.
    Examples: CPU >10% per simulation, Memory >100MB per fractal.
    """
    pass


class ValidationFailed(DualityException):
    """
    Raised when reality validation checks fail.
    Examples: Metrics don't match expected ranges, data integrity violations.
    """
    pass


class OrchestrationError(DualityException):
    """Raised when orchestration operations fail"""
    pass


class DatabaseError(DualityException):
    """Raised when database operations fail"""
    pass


class FileSystemError(DualityException):
    """Raised when file system operations fail"""
    pass
