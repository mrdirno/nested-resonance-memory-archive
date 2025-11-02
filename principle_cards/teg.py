"""
Temporal Embedding Graph (TEG) - Dependency Graph for Principle Cards
======================================================================

The TEG tracks dependencies between Principle Cards, enabling compositional
validation and automated dependency resolution.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
from collections import deque, defaultdict


@dataclass
class PCNode:
    """Node in the Temporal Embedding Graph."""
    pc_id: str
    version: str
    title: str
    author: str
    created: str
    status: str  # draft | proposed | validated | falsified | deprecated
    domain: str
    dependencies: List[str] = field(default_factory=list)  # PC IDs this depends on
    enables: List[str] = field(default_factory=list)      # PC IDs this enables
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'pc_id': self.pc_id,
            'version': self.version,
            'title': self.title,
            'author': self.author,
            'created': self.created,
            'status': self.status,
            'domain': self.domain,
            'dependencies': self.dependencies,
            'enables': self.enables,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PCNode':
        """Create PCNode from dictionary."""
        return cls(
            pc_id=data['pc_id'],
            version=data['version'],
            title=data['title'],
            author=data['author'],
            created=data['created'],
            status=data['status'],
            domain=data['domain'],
            dependencies=data.get('dependencies', []),
            enables=data.get('enables', []),
            metadata=data.get('metadata', {})
        )


class TemporalEmbeddingGraph:
    """
    Temporal Embedding Graph (TEG) - Dependency graph for Principle Cards.

    The TEG tracks dependencies between PCs, enabling:
    - Compositional validation (PC_B cannot validate without PC_A)
    - Dependency resolution (topological sort for validation order)
    - Impact analysis (which PCs are affected by a falsification?)
    - Visualization (export to Graphviz DOT format)

    Graph Structure:
    - Nodes: Principle Cards (PC metadata)
    - Edges: Dependencies (PC_A → PC_B means "PC_B depends on PC_A")

    Example:
        PC001 (NRM Population Dynamics)
          ├─→ PC002 (Regime Detection)
          └─→ PC004 (Multi-scale Dynamics)

        PC002 can only validate if PC001 is validated.
    """

    def __init__(self):
        """Initialize empty TEG."""
        self.nodes: Dict[str, PCNode] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)  # pc_id → set of pc_ids it depends on
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)  # pc_id → set of pc_ids that depend on it

    def add_node(self, node: PCNode):
        """
        Add PC node to graph.

        Args:
            node: PCNode to add

        Raises:
            ValueError: If node with same PC ID already exists
        """
        if node.pc_id in self.nodes:
            raise ValueError(f"Node {node.pc_id} already exists in TEG")

        self.nodes[node.pc_id] = node

        # Update adjacency lists based on dependencies
        # Create edges for dependencies that exist
        for dep_id in node.dependencies:
            if dep_id in self.nodes:
                self.adjacency[node.pc_id].add(dep_id)
                self.reverse_adjacency[dep_id].add(node.pc_id)

        # Also check if any existing nodes have this node as a dependency
        # (i.e., they were waiting for this node to be added)
        for existing_id, existing_node in self.nodes.items():
            if existing_id != node.pc_id and node.pc_id in existing_node.dependencies:
                # Create the edge that was waiting
                self.adjacency[existing_id].add(node.pc_id)
                self.reverse_adjacency[node.pc_id].add(existing_id)

    def remove_node(self, pc_id: str):
        """
        Remove PC node from graph.

        Args:
            pc_id: PC ID to remove

        Raises:
            KeyError: If node does not exist
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")

        # Remove from nodes
        node = self.nodes.pop(pc_id)

        # Remove from adjacency lists (use pop with default to handle missing keys)
        self.adjacency.pop(pc_id, None)
        self.reverse_adjacency.pop(pc_id, None)

        # Remove references from other nodes
        for other_id in self.nodes:
            self.adjacency[other_id].discard(pc_id)
            self.reverse_adjacency[other_id].discard(pc_id)

    def get_node(self, pc_id: str) -> PCNode:
        """
        Get PC node by ID.

        Args:
            pc_id: PC ID to retrieve

        Returns:
            PCNode

        Raises:
            KeyError: If node does not exist
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")
        return self.nodes[pc_id]

    def has_node(self, pc_id: str) -> bool:
        """Check if node exists in graph."""
        return pc_id in self.nodes

    def get_dependencies(self, pc_id: str) -> List[str]:
        """
        Get list of PC IDs that this PC depends on.

        Args:
            pc_id: PC ID to query

        Returns:
            List of PC IDs (dependencies)
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")
        return list(self.adjacency[pc_id])

    def get_dependents(self, pc_id: str) -> List[str]:
        """
        Get list of PC IDs that depend on this PC.

        Args:
            pc_id: PC ID to query

        Returns:
            List of PC IDs (dependents)
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")
        return list(self.reverse_adjacency[pc_id])

    def get_all_dependencies(self, pc_id: str) -> Set[str]:
        """
        Get transitive closure of dependencies (recursive).

        Args:
            pc_id: PC ID to query

        Returns:
            Set of all PC IDs (direct + indirect dependencies)
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")

        all_deps = set()
        queue = deque([pc_id])
        visited = set()

        while queue:
            current_id = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)

            # Add direct dependencies
            for dep_id in self.adjacency[current_id]:
                if dep_id != pc_id:  # Exclude self
                    all_deps.add(dep_id)
                    queue.append(dep_id)

        return all_deps

    def get_all_dependents(self, pc_id: str) -> Set[str]:
        """
        Get transitive closure of dependents (recursive).

        Args:
            pc_id: PC ID to query

        Returns:
            Set of all PC IDs (direct + indirect dependents)
        """
        if pc_id not in self.nodes:
            raise KeyError(f"Node {pc_id} not found in TEG")

        all_deps = set()
        queue = deque([pc_id])
        visited = set()

        while queue:
            current_id = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)

            # Add direct dependents
            for dep_id in self.reverse_adjacency[current_id]:
                if dep_id != pc_id:  # Exclude self
                    all_deps.add(dep_id)
                    queue.append(dep_id)

        return all_deps

    def topological_sort(self) -> List[str]:
        """
        Compute topological sort of PC IDs (dependency-respecting order).

        Returns:
            List of PC IDs in validation order (dependencies before dependents)

        Raises:
            ValueError: If graph contains cycles
        """
        # Kahn's algorithm for topological sort
        in_degree = {pc_id: len(self.adjacency[pc_id]) for pc_id in self.nodes}
        queue = deque([pc_id for pc_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            pc_id = queue.popleft()
            result.append(pc_id)

            # Reduce in-degree of dependents
            for dependent_id in self.reverse_adjacency[pc_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        # Check for cycles
        if len(result) != len(self.nodes):
            raise ValueError("TEG contains cycles - cannot compute topological sort")

        return result

    def has_cycle(self) -> bool:
        """Check if graph contains cycles."""
        try:
            self.topological_sort()
            return False
        except ValueError:
            return True

    def get_validation_order(self, pc_ids: Optional[List[str]] = None) -> List[str]:
        """
        Get validation order for given PCs (including dependencies).

        Args:
            pc_ids: List of PC IDs to validate (default: all PCs)

        Returns:
            List of PC IDs in validation order (dependencies first)
        """
        if pc_ids is None:
            return self.topological_sort()

        # Collect all dependencies
        required = set()
        for pc_id in pc_ids:
            required.add(pc_id)
            required.update(self.get_all_dependencies(pc_id))

        # Topological sort of required PCs
        full_order = self.topological_sort()
        return [pc_id for pc_id in full_order if pc_id in required]

    def get_foundational_pcs(self) -> List[str]:
        """
        Get list of foundational PCs (no dependencies).

        Returns:
            List of PC IDs with no dependencies
        """
        return [pc_id for pc_id in self.nodes if len(self.adjacency[pc_id]) == 0]

    def get_leaf_pcs(self) -> List[str]:
        """
        Get list of leaf PCs (no dependents).

        Returns:
            List of PC IDs with no dependents
        """
        return [pc_id for pc_id in self.nodes if len(self.reverse_adjacency[pc_id]) == 0]

    def filter_by_status(self, status: str) -> List[str]:
        """
        Get list of PC IDs with given status.

        Args:
            status: Status to filter by (e.g., 'validated', 'falsified')

        Returns:
            List of PC IDs
        """
        return [pc_id for pc_id, node in self.nodes.items() if node.status == status]

    def filter_by_domain(self, domain: str) -> List[str]:
        """
        Get list of PC IDs in given domain.

        Args:
            domain: Domain to filter by (e.g., 'NRM', 'TSF')

        Returns:
            List of PC IDs
        """
        return [pc_id for pc_id, node in self.nodes.items() if node.domain == domain]

    def get_status(self, pc_id: str) -> str:
        """
        Get status of a Principle Card.

        Args:
            pc_id: PC ID to query

        Returns:
            Status string (draft | proposed | validated | falsified | deprecated)

        Raises:
            KeyError: If PC not found in TEG
        """
        if pc_id not in self.nodes:
            raise KeyError(f"PC {pc_id} not found in TEG")
        return self.nodes[pc_id].status

    def update_status(self, pc_id: str, status: str):
        """
        Update status of a Principle Card.

        This method is called automatically by TSF when a PC validates.
        Valid status transitions:
        - draft → proposed (when submitted for review)
        - proposed → validated (when validation passes)
        - proposed → draft (when validation fails)
        - validated → falsified (when refutation fails)
        - any → deprecated (when superseded)

        Args:
            pc_id: PC ID to update
            status: New status (draft | proposed | validated | falsified | deprecated)

        Raises:
            KeyError: If PC not found in TEG
            ValueError: If invalid status value
        """
        valid_statuses = {'draft', 'proposed', 'validated', 'falsified', 'deprecated'}
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Must be one of: {', '.join(sorted(valid_statuses))}"
            )

        if pc_id not in self.nodes:
            raise KeyError(f"PC {pc_id} not found in TEG")

        self.nodes[pc_id].status = status

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert TEG to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            'nodes': {pc_id: node.to_dict() for pc_id, node in self.nodes.items()},
            'adjacency': {pc_id: list(deps) for pc_id, deps in self.adjacency.items()},
            'reverse_adjacency': {pc_id: list(deps) for pc_id, deps in self.reverse_adjacency.items()}
        }

    def save(self, path: Path):
        """
        Save TEG to JSON file.

        Args:
            path: Path to save to
        """
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalEmbeddingGraph':
        """
        Load TEG from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            TemporalEmbeddingGraph
        """
        teg = cls()

        # Add nodes
        for pc_id, node_data in data['nodes'].items():
            node = PCNode.from_dict(node_data)
            # Don't use add_node() here to avoid duplicate adjacency updates
            teg.nodes[pc_id] = node

        # Set adjacency lists directly (already in data)
        teg.adjacency = defaultdict(set, {pc_id: set(deps) for pc_id, deps in data['adjacency'].items()})
        teg.reverse_adjacency = defaultdict(set, {pc_id: set(deps) for pc_id, deps in data['reverse_adjacency'].items()})

        return teg

    @classmethod
    def load(cls, path: Path) -> 'TemporalEmbeddingGraph':
        """
        Load TEG from JSON file.

        Args:
            path: Path to load from

        Returns:
            TemporalEmbeddingGraph
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_graphviz(self) -> str:
        """
        Export TEG to Graphviz DOT format.

        Returns:
            DOT format string
        """
        lines = ['digraph TEG {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=rounded];')
        lines.append('')

        # Define nodes
        for pc_id, node in self.nodes.items():
            # Color by status
            color = {
                'validated': 'green',
                'falsified': 'red',
                'proposed': 'yellow',
                'draft': 'lightgray',
                'deprecated': 'gray'
            }.get(node.status, 'white')

            label = f"{node.pc_id}\\n{node.title}\\n({node.status})"
            lines.append(f'  "{pc_id}" [label="{label}", fillcolor={color}, style="rounded,filled"];')

        lines.append('')

        # Define edges (dependencies)
        for pc_id, deps in self.adjacency.items():
            for dep_id in deps:
                lines.append(f'  "{dep_id}" -> "{pc_id}" [label="enables"];')

        lines.append('}')
        return '\n'.join(lines)

    def save_graphviz(self, path: Path):
        """
        Save TEG to Graphviz DOT file.

        Args:
            path: Path to save to (.dot extension)
        """
        with open(path, 'w') as f:
            f.write(self.to_graphviz())

    def __len__(self) -> int:
        """Return number of nodes in graph."""
        return len(self.nodes)

    def __contains__(self, pc_id: str) -> bool:
        """Check if PC ID exists in graph."""
        return pc_id in self.nodes

    def __repr__(self) -> str:
        """String representation."""
        return f"TemporalEmbeddingGraph({len(self.nodes)} nodes, {sum(len(deps) for deps in self.adjacency.values())} edges)"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_teg_from_pcs(principle_cards: List[Any]) -> TemporalEmbeddingGraph:
    """
    Create TEG from list of PrincipleCard instances.

    Args:
        principle_cards: List of PrincipleCard instances

    Returns:
        TemporalEmbeddingGraph
    """
    teg = TemporalEmbeddingGraph()

    for pc in principle_cards:
        node = PCNode(
            pc_id=pc.metadata.pc_id,
            version=pc.metadata.version,
            title=pc.metadata.title,
            author=pc.metadata.author,
            created=pc.metadata.created,
            status=pc.metadata.status,
            domain=pc.metadata.domain,
            dependencies=pc.dependencies(),
            enables=pc.enables()
        )
        teg.add_node(node)

    return teg
