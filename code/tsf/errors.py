"""
TSF Error Hierarchy

Custom exceptions for TSF operations with detailed error context.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from typing import Optional, Dict, Any


class TSFError(Exception):
    """Base exception for all TSF operations."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize TSF error with message and optional context.

        Args:
            message: Human-readable error description
            context: Additional error context (file paths, parameters, etc.)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Format error with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (context: {context_str})"
        return self.message


class DataLoadError(TSFError):
    """Failed to load observational data."""
    pass


class SchemaValidationError(TSFError):
    """Data does not match expected schema."""
    pass


class DiscoveryError(TSFError):
    """Pattern discovery failed."""
    pass


class RefutationError(TSFError):
    """Pattern refutation test failed."""
    pass


class QuantificationError(TSFError):
    """Pattern quantification failed."""
    pass


class PublicationError(TSFError):
    """Principle Card publication failed."""
    pass
