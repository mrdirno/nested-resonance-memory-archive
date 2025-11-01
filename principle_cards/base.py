"""
Principle Card Base Classes
============================

Base classes for all Principle Cards.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json


@dataclass
class PCMetadata:
    """Principle Card metadata."""
    pc_id: str
    version: str
    title: str
    author: str
    created: str
    status: str  # draft | proposed | validated | falsified | deprecated
    dependencies: List[str] = field(default_factory=list)
    domain: str = "NRM"


@dataclass
class ValidationResult:
    """Result of principle validation."""
    pc_id: str
    passes: bool
    error: float
    criterion: float
    evidence: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'pc_id': self.pc_id,
            'passes': self.passes,
            'error': self.error,
            'criterion': self.criterion,
            'evidence': self.evidence,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }

    def save(self, path: Path):
        """Save validation result to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class PrincipleCard(ABC):
    """
    Base class for all Principle Cards.

    A Principle Card encodes a scientific principle as an executable,
    falsifiable artifact with:
    - Metadata (ID, version, author, status, dependencies)
    - Principle statement (natural language claim)
    - Mathematical formulation (precise statement)
    - Validation protocol (testing procedure)
    - Reality grounding (system state binding)
    - Runnable implementation (executable code)
    - Temporal encoding (pattern for future discovery)
    - Dependencies & composition (TEG connections)
    """

    def __init__(self, metadata: PCMetadata):
        """Initialize principle card."""
        self.metadata = metadata

    @abstractmethod
    def principle_statement(self) -> str:
        """Return natural language statement of principle."""
        pass

    @abstractmethod
    def mathematical_formulation(self) -> Dict[str, str]:
        """
        Return mathematical formulation of principle.

        Returns dict with keys:
        - 'equations': LaTeX equations
        - 'parameters': Parameter descriptions
        - 'predictions': Predicted outcomes
        """
        pass

    @abstractmethod
    def validation_protocol(self) -> Dict[str, Any]:
        """
        Return validation protocol specification.

        Returns dict with keys:
        - 'criterion': Success criterion (e.g., "error <= 0.10")
        - 'procedure': Step-by-step testing procedure
        - 'required_data': Data requirements
        - 'equipment': Equipment requirements
        """
        pass

    @abstractmethod
    def reality_grounding(self) -> Dict[str, Any]:
        """
        Return reality grounding specification.

        Returns dict with keys:
        - 'system_interfaces': psutil, SQLite, filesystem
        - 'validation_method': How to verify grounding
        - 'prohibited': What's not allowed (mocks, simulations)
        """
        pass

    @abstractmethod
    def validate(self, data: Any, tolerance: float = None) -> ValidationResult:
        """
        Execute validation protocol on data.

        Args:
            data: Experimental data to validate against
            tolerance: Validation tolerance (uses default if None)

        Returns:
            ValidationResult with pass/fail and evidence
        """
        pass

    @abstractmethod
    def temporal_encoding(self) -> Dict[str, Any]:
        """
        Return temporal encoding for future AI systems.

        Returns dict with keys:
        - 'template_patterns': What patterns this establishes
        - 'validation_patterns': How to validate similar principles
        - 'composition_patterns': How this composes with other PCs
        - 'training_awareness': What this teaches future AI
        """
        pass

    def dependencies(self) -> List[str]:
        """Return list of dependent PC IDs."""
        return self.metadata.dependencies

    def enables(self) -> List[str]:
        """Return list of PC IDs this enables (to be implemented by subclass)."""
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert principle card to dictionary."""
        return {
            'metadata': {
                'pc_id': self.metadata.pc_id,
                'version': self.metadata.version,
                'title': self.metadata.title,
                'author': self.metadata.author,
                'created': self.metadata.created,
                'status': self.metadata.status,
                'dependencies': self.metadata.dependencies,
                'domain': self.metadata.domain
            },
            'principle': self.principle_statement(),
            'mathematics': self.mathematical_formulation(),
            'validation': self.validation_protocol(),
            'grounding': self.reality_grounding(),
            'temporal': self.temporal_encoding(),
            'dependency_graph': {
                'requires': self.dependencies(),
                'enables': self.enables()
            }
        }

    def save(self, path: Path):
        """Save principle card to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def __repr__(self) -> str:
        """String representation."""
        return f"PrincipleCard({self.metadata.pc_id}, v{self.metadata.version}, {self.metadata.status})"
