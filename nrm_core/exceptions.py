"""
NRM Core: Exceptions
Reality-grounded exception hierarchy.
"""

class DualityException(Exception):
    """Base exception for all NRM errors."""
    pass

class RealityViolation(DualityException):
    """Raised when an operation attempts to violate the Reality Imperative."""
    pass

class ResourceExceeded(DualityException):
    """Raised when resource constraints are exceeded."""
    pass

class ValidationFailed(DualityException):
    """Raised when reality validation checks fail."""
    pass

class OrchestrationError(DualityException):
    """Raised when orchestration operations fail."""
    pass

class DatabaseError(DualityException):
    """Raised when database operations fail."""
    pass

class FileSystemError(DualityException):
    """Raised when file system operations fail."""
    pass
