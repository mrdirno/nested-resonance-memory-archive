"""
PrincipleCard Base Class - Temporal Structure Framework (TSF)

Defines the abstract interface that all Principle Cards must implement.
Principle Cards are runnable, composable, falsifiable scientific artifacts.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import hashlib
import json


@dataclass
class PCMetadata:
    """Metadata structure for Principle Cards."""

    pc_id: str
    version: str
    name: str
    type: str  # "validation_protocol", "exploratory_hypothesis", etc.
    domain: str
    phase: int
    status: str  # "design", "validated", "refuted"
    design_date: Optional[str] = None
    validation_date: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    author: str = "Aldrin Payopay"
    repository: str = "https://github.com/mrdirno/nested-resonance-memory-archive"
    license: str = "GPL-3.0"
    additional_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pc_id": self.pc_id,
            "version": self.version,
            "name": self.name,
            "type": self.type,
            "domain": self.domain,
            "phase": self.phase,
            "status": self.status,
            "design_date": self.design_date,
            "validation_date": self.validation_date,
            "dependencies": self.dependencies,
            "successors": self.successors,
            "author": self.author,
            "repository": self.repository,
            "license": self.license,
            **self.additional_metadata
        }


@dataclass
class ValidationResult:
    """Result from principle card validation."""

    pc_id: str
    pc_version: str
    passes: bool
    metrics: Dict[str, float]
    evidence: Dict[str, Any]
    timestamp: str
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pc_id": self.pc_id,
            "pc_version": self.pc_version,
            "passes": self.passes,
            "metrics": self.metrics,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "error_message": self.error_message
        }

    def to_json(self, filepath: Union[str, Path]) -> None:
        """Save to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "✓ PASS" if self.passes else "✗ FAIL"
        lines = [
            f"Principle Card: {self.pc_id} v{self.pc_version}",
            f"Status: {status}",
            f"Timestamp: {self.timestamp}",
            "",
            "Metrics:"
        ]

        for metric, value in self.metrics.items():
            lines.append(f"  {metric}: {value}")

        if self.error_message:
            lines.extend(["", f"Error: {self.error_message}"])

        return "\n".join(lines)


class PrincipleCard(ABC):
    """
    Abstract base class for all Principle Cards.

    Principle Cards are runnable, composable, falsifiable scientific artifacts
    that encode validated principles, hypotheses, and methodologies.

    Each PC must implement:
    1. principle_statement - Natural language description
    2. mathematical_formulation - Math/computational representation
    3. validation_protocol - How to validate the principle
    4. validate() - Execute validation and return results
    5. falsification_criteria - Conditions that would falsify
    6. applications - Practical use cases

    Subclasses represent specific principles (PC1, PC2, PC3, etc.)
    """

    def __init__(self, metadata: PCMetadata):
        """
        Initialize principle card.

        Args:
            metadata: PC metadata structure
        """
        self.metadata = metadata
        self._loaded_from_file: Optional[Path] = None

    @property
    @abstractmethod
    def principle_statement(self) -> str:
        """
        Core principle in natural language.

        Should be clear, concise statement of the principle being encoded.
        Example: "NRM population dynamics follow logistic growth with demographic noise"

        Returns:
            Natural language principle statement
        """
        pass

    @abstractmethod
    def mathematical_formulation(self) -> Dict[str, str]:
        """
        Mathematical or computational representation of the principle.

        Returns:
            Dictionary mapping formulas/equations to their expressions
            Example: {"sde": "dN = μ(N)dt + σ(N)dW", ...}
        """
        pass

    @abstractmethod
    def validation_protocol(self) -> Dict[str, Any]:
        """
        Validation methodology and criteria.

        Returns:
            Dictionary describing:
            - method: How to validate
            - criterion: Success threshold
            - data_requirements: What data is needed
            - statistical_tests: Which tests to apply
        """
        pass

    @abstractmethod
    def validate(self, data: Any, tolerance: float = 0.10) -> ValidationResult:
        """
        Execute validation protocol and return results.

        This is the core method that runs the actual validation.
        Must interact with real data, perform actual computations.

        Args:
            data: Observed data to validate against
            tolerance: Tolerance for validation (default: 10%)

        Returns:
            ValidationResult with pass/fail, metrics, evidence
        """
        pass

    @abstractmethod
    def falsification_criteria(self) -> List[str]:
        """
        Conditions that would falsify this principle.

        Returns:
            List of falsification conditions (Popperian criterion)
        """
        pass

    @abstractmethod
    def applications(self) -> List[str]:
        """
        Practical applications of this principle.

        Returns:
            List of domains/use cases where principle applies
        """
        pass

    # Non-abstract utility methods

    def get_dependencies(self) -> List[str]:
        """
        Get list of PC dependencies.

        Returns:
            List of PC IDs this PC depends on
        """
        return self.metadata.dependencies

    def get_successors(self) -> List[str]:
        """
        Get list of PCs enabled by this PC.

        Returns:
            List of PC IDs enabled by this PC
        """
        return self.metadata.successors

    def is_validated(self) -> bool:
        """
        Check if PC is validated.

        Returns:
            True if status is "validated"
        """
        return self.metadata.status == "validated"

    def can_validate(self, validated_pcs: List[str]) -> bool:
        """
        Check if all dependencies are validated.

        Args:
            validated_pcs: List of validated PC IDs

        Returns:
            True if all dependencies are in validated_pcs
        """
        return all(dep in validated_pcs for dep in self.metadata.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PC to dictionary representation.

        Returns:
            Dictionary with metadata, principle, formulation, etc.
        """
        return {
            "metadata": self.metadata.to_dict(),
            "principle_statement": self.principle_statement,
            "mathematical_formulation": self.mathematical_formulation(),
            "validation_protocol": self.validation_protocol(),
            "falsification_criteria": self.falsification_criteria(),
            "applications": self.applications()
        }

    def to_yaml(self, filepath: Union[str, Path]) -> None:
        """
        Save PC to YAML file.

        Args:
            filepath: Output YAML file path
        """
        with open(filepath, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of PC content for provenance.

        Returns:
            SHA-256 hexadecimal digest
        """
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'PrincipleCard':
        """
        Load principle card from YAML file.

        Args:
            filepath: YAML file path

        Returns:
            PrincipleCard instance

        Raises:
            FileNotFoundError: File doesn't exist
            ValueError: Invalid YAML format
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Principle card file not found: {filepath}")

        with open(filepath) as f:
            data = yaml.safe_load(f)

        # Extract metadata
        metadata_dict = data.get("metadata", {})
        metadata = PCMetadata(**metadata_dict)

        # Determine which subclass to instantiate
        # This will be extended as we add PC1, PC2, etc.
        # For now, return a minimal instance
        # Subclasses will override this method

        raise NotImplementedError(
            f"Loading PCs from YAML requires subclass implementation for {metadata.pc_id}"
        )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PrincipleCard(pc_id={self.metadata.pc_id}, "
            f"version={self.metadata.version}, "
            f"status={self.metadata.status})"
        )

    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.metadata.pc_id} v{self.metadata.version}: {self.metadata.name}"


# Exception classes for PC operations

class PCValidationError(Exception):
    """Raised when principle card validation fails."""
    pass


class PCDependencyError(Exception):
    """Raised when PC dependencies are not satisfied."""
    pass


class InsufficientDataError(Exception):
    """Raised when dataset is too small for reliable validation."""
    pass


class RealityCheckFailedError(Exception):
    """Raised when data fails reality grounding checks."""
    pass


# Utility functions for PC management

def check_dependencies(pc: PrincipleCard, validated_pcs: List[str]) -> None:
    """
    Verify all PC dependencies are validated.

    Args:
        pc: Principle card to check
        validated_pcs: List of validated PC IDs

    Raises:
        PCDependencyError: If dependencies not satisfied
    """
    unmet_deps = [dep for dep in pc.get_dependencies() if dep not in validated_pcs]

    if unmet_deps:
        raise PCDependencyError(
            f"{pc.metadata.pc_id} has unmet dependencies: {unmet_deps}. "
            f"These PCs must be validated first."
        )


def validate_reality_grounding(data: Any) -> None:
    """
    Verify data is reality-grounded (not mocked/simulated).

    Args:
        data: Data to check

    Raises:
        RealityCheckFailedError: If data appears fabricated
    """
    # Basic reality checks
    # More sophisticated checks will be added as needed

    if data is None:
        raise RealityCheckFailedError("Data is None (no actual data loaded)")

    # Additional checks will be implemented in observe() function
    pass


def compute_validation_order(pcs: List[PrincipleCard]) -> List[str]:
    """
    Compute topological sort for PC validation order.

    Args:
        pcs: List of principle cards

    Returns:
        Ordered list of PC IDs respecting dependencies

    Raises:
        ValueError: If circular dependencies detected
    """
    from collections import deque, defaultdict

    # Build adjacency graph
    in_degree = defaultdict(int)
    adj_list = defaultdict(list)
    pc_dict = {pc.metadata.pc_id: pc for pc in pcs}

    for pc in pcs:
        if pc.metadata.pc_id not in in_degree:
            in_degree[pc.metadata.pc_id] = 0

        for dep in pc.get_dependencies():
            adj_list[dep].append(pc.metadata.pc_id)
            in_degree[pc.metadata.pc_id] += 1

    # Kahn's algorithm for topological sort
    queue = deque([pc_id for pc_id in in_degree if in_degree[pc_id] == 0])
    order = []

    while queue:
        pc_id = queue.popleft()
        order.append(pc_id)

        for neighbor in adj_list[pc_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles
    if len(order) != len(pcs):
        raise ValueError("Circular dependencies detected in PC graph")

    return order
