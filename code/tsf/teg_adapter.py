"""
TEG-TSF Adapter - Bridge between TSF Core API and Temporal Embedding Graph

This module provides integration between TSF-generated Principle Cards and
the TEG dependency tracking system, enabling compositional validation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from pathlib import Path
from typing import Union, Dict, Any, List
import json
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "principle_cards"))

from principle_cards.teg import TemporalEmbeddingGraph, PCNode


class TEGAdapter:
    """
    Adapter between TSF Core API and Temporal Embedding Graph.

    Enables:
    - Loading TSF-generated PC specifications into TEG
    - Dependency tracking between PCs
    - Compositional validation
    - Invalidation propagation
    """

    def __init__(self, teg: TemporalEmbeddingGraph):
        """
        Initialize adapter with TEG instance.

        Args:
            teg: TemporalEmbeddingGraph instance to populate
        """
        self.teg = teg

    def load_pc_specification(
        self,
        spec_path: Union[str, Path]
    ) -> PCNode:
        """
        Load TSF-generated PC specification and add to TEG.

        Args:
            spec_path: Path to PC specification JSON file

        Returns:
            PCNode added to TEG

        Raises:
            FileNotFoundError: If specification file not found
            ValueError: If specification format invalid
        """
        spec_path = Path(spec_path)

        if not spec_path.exists():
            raise FileNotFoundError(f"PC specification not found: {spec_path}")

        # Load specification
        with open(spec_path) as f:
            spec = json.load(f)

        # Validate required fields
        required_fields = ['pc_id', 'version', 'title', 'author', 'created', 'status', 'domain']
        for field in required_fields:
            if field not in spec:
                raise ValueError(f"Missing required field in PC specification: {field}")

        # Create PCNode from TSF specification
        node = PCNode(
            pc_id=spec['pc_id'],
            version=spec['version'],
            title=spec['title'],
            author=spec['author'],
            created=spec['created'],
            status=spec['status'],
            domain=spec['domain'],
            dependencies=spec.get('dependencies', []),
            enables=spec.get('enables', []),
            metadata={
                'tsf_generated': True,
                'spec_path': str(spec_path),
                'discovery_method': spec.get('discovery', {}).get('method'),
                'refutation_passed': spec.get('refutation', {}).get('passed'),
                'quantification_scores': spec.get('quantification', {}).get('scores', {})
            }
        )

        # Add to TEG
        self.teg.add_node(node)

        return node

    def load_pc_directory(
        self,
        directory: Union[str, Path],
        pattern: str = "pc*_specification.json"
    ) -> List[PCNode]:
        """
        Load all PC specifications from a directory.

        Args:
            directory: Directory containing PC specifications
            pattern: Glob pattern for specification files

        Returns:
            List of PCNodes added to TEG
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        nodes = []
        for spec_file in sorted(directory.glob(pattern)):
            try:
                node = self.load_pc_specification(spec_file)
                nodes.append(node)
            except Exception as e:
                print(f"Warning: Failed to load {spec_file}: {e}")
                continue

        return nodes

    def validate_dependencies(self, pc_id: str) -> Dict[str, bool]:
        """
        Check if all dependencies for a PC are validated.

        Args:
            pc_id: PC ID to check

        Returns:
            Dictionary mapping dependency IDs to validation status
        """
        if not self.teg.has_node(pc_id):
            raise KeyError(f"PC {pc_id} not found in TEG")

        node = self.teg.get_node(pc_id)
        dependencies = self.teg.get_dependencies(pc_id)

        validation_status = {}
        for dep_id in dependencies:
            if self.teg.has_node(dep_id):
                dep_node = self.teg.get_node(dep_id)
                validation_status[dep_id] = (dep_node.status == "validated")
            else:
                validation_status[dep_id] = False  # Dependency not in TEG

        return validation_status

    def can_validate(self, pc_id: str) -> bool:
        """
        Check if a PC can be validated (all dependencies validated).

        Args:
            pc_id: PC ID to check

        Returns:
            True if all dependencies are validated, False otherwise
        """
        validation_status = self.validate_dependencies(pc_id)
        return all(validation_status.values())

    def get_validation_order(self) -> List[str]:
        """
        Get topological sort of PCs for validation order.

        Returns:
            List of PC IDs in dependency order (validate in this order)

        Raises:
            ValueError: If graph contains cycles
        """
        return self.teg.topological_sort()

    def propagate_invalidation(self, pc_id: str) -> List[str]:
        """
        Propagate invalidation through dependency graph.

        If a PC is falsified, all PCs that depend on it are also invalidated.

        Args:
            pc_id: PC ID that was falsified

        Returns:
            List of PC IDs that were invalidated (including the original)
        """
        if not self.teg.has_node(pc_id):
            raise KeyError(f"PC {pc_id} not found in TEG")

        # Mark this PC as falsified
        node = self.teg.get_node(pc_id)
        node.status = "falsified"

        # Get all dependents (transitively)
        all_dependents = self.teg.get_all_dependents(pc_id)

        # Mark all dependents as invalidated
        invalidated = [pc_id]
        for dep_id in all_dependents:
            dep_node = self.teg.get_node(dep_id)
            dep_node.status = "falsified"
            invalidated.append(dep_id)

        return invalidated

    def export_teg_summary(self) -> Dict[str, Any]:
        """
        Export TEG summary with validation statistics.

        Returns:
            Dictionary with TEG statistics
        """
        nodes = list(self.teg.nodes.values())

        summary = {
            "total_pcs": len(nodes),
            "validated": sum(1 for n in nodes if n.status == "validated"),
            "draft": sum(1 for n in nodes if n.status == "draft"),
            "proposed": sum(1 for n in nodes if n.status == "proposed"),
            "falsified": sum(1 for n in nodes if n.status == "falsified"),
            "deprecated": sum(1 for n in nodes if n.status == "deprecated"),
            "domains": list(set(n.domain for n in nodes)),
            "tsf_generated": sum(1 for n in nodes if n.metadata.get('tsf_generated', False))
        }

        return summary


def demo_teg_tsf_integration():
    """
    Demonstrate TEG-TSF integration with PC001/PC002.

    Shows:
    - Loading TSF-generated PCs into TEG
    - Dependency tracking
    - Validation order computation
    - Dependency validation checks
    """
    print("=" * 70)
    print("TEG-TSF Integration Demo")
    print("=" * 70)

    # Create TEG and adapter
    teg = TemporalEmbeddingGraph()
    adapter = TEGAdapter(teg)

    # Load PC specifications
    print("\n[1] Loading PC specifications...")
    pc_dir = Path("principle_cards")

    nodes = adapter.load_pc_directory(pc_dir, pattern="pc00*_specification.json")

    print(f"✓ Loaded {len(nodes)} PCs:")
    for node in nodes:
        print(f"  - {node.pc_id}: {node.title}")
        print(f"    Status: {node.status}")
        print(f"    Dependencies: {node.dependencies if node.dependencies else 'None'}")

    # Check dependencies
    print("\n[2] Checking dependencies...")
    for node in nodes:
        deps = adapter.validate_dependencies(node.pc_id)
        can_val = adapter.can_validate(node.pc_id)

        print(f"\n{node.pc_id}:")
        if deps:
            print(f"  Dependencies:")
            for dep_id, is_validated in deps.items():
                status = "✓" if is_validated else "✗"
                print(f"    {status} {dep_id}")
        else:
            print(f"  Dependencies: None (foundational)")
        print(f"  Can validate: {'Yes' if can_val else 'No'}")

    # Get validation order
    print("\n[3] Computing validation order...")
    try:
        order = adapter.get_validation_order()
        print(f"✓ Validation order:")
        for i, pc_id in enumerate(order, 1):
            print(f"  {i}. {pc_id}")
    except ValueError as e:
        print(f"✗ Cannot compute validation order: {e}")

    # Export summary
    print("\n[4] TEG Summary:")
    summary = adapter.export_teg_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ TEG-TSF integration operational!")
    print("=" * 70)


if __name__ == "__main__":
    demo_teg_tsf_integration()
