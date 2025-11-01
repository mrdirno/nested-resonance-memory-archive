"""
TEG Example - Demonstrating Temporal Embedding Graph with PC001
================================================================

This example demonstrates how to use the TEG to track dependencies
between Principle Cards and compute validation orders.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from pathlib import Path
from principle_cards import TemporalEmbeddingGraph, create_teg_from_pcs
from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics


def main():
    """Demonstrate TEG usage with PC001."""
    print("=" * 80)
    print("TEG EXAMPLE - TEMPORAL EMBEDDING GRAPH WITH PC001")
    print("=" * 80)
    print()

    # Create PC001 instance
    print("Creating PC001 (NRM Population Dynamics)...")
    pc001 = PC001_NRMPopulationDynamics()
    print(f"✓ PC001 created: {pc001.metadata.title}")
    print(f"  Status: {pc001.metadata.status}")
    print(f"  Dependencies: {pc001.dependencies()}")
    print(f"  Enables: {pc001.enables()}")
    print()

    # Create TEG from PC001
    print("Building TEG from PC001...")
    teg = create_teg_from_pcs([pc001])
    print(f"✓ TEG created: {teg}")
    print()

    # Query TEG
    print("Querying TEG:")
    print(f"  Total nodes: {len(teg)}")
    print(f"  Foundational PCs: {teg.get_foundational_pcs()}")
    print(f"  Leaf PCs: {teg.get_leaf_pcs()}")
    print(f"  Validated PCs: {teg.filter_by_status('validated')}")
    print(f"  NRM domain PCs: {teg.filter_by_domain('NRM')}")
    print()

    # Get PC001 details
    print("PC001 Details:")
    node = teg.get_node("PC001")
    print(f"  PC ID: {node.pc_id}")
    print(f"  Version: {node.version}")
    print(f"  Title: {node.title}")
    print(f"  Author: {node.author}")
    print(f"  Status: {node.status}")
    print(f"  Domain: {node.domain}")
    print(f"  Dependencies (in graph): {teg.get_dependencies('PC001')}")
    print(f"  Dependents (in graph): {teg.get_dependents('PC001')}")
    print(f"  Enables (metadata): {node.enables}")
    print(f"  Note: PC002 and PC004 not yet added to TEG, so no edges created")
    print()

    # Validation order
    print("Validation Order:")
    order = teg.get_validation_order()
    for i, pc_id in enumerate(order, 1):
        print(f"  {i}. {pc_id}")
    print()

    # Save TEG to JSON
    output_dir = Path(__file__).parent
    teg_json_path = output_dir / "teg_example.json"
    teg.save(teg_json_path)
    print(f"✓ TEG saved to: {teg_json_path}")

    # Save TEG to Graphviz DOT
    teg_dot_path = output_dir / "teg_example.dot"
    teg.save_graphviz(teg_dot_path)
    print(f"✓ TEG visualization saved to: {teg_dot_path}")
    print()

    # Load TEG back
    print("Testing TEG serialization...")
    teg2 = TemporalEmbeddingGraph.load(teg_json_path)
    print(f"✓ TEG loaded successfully: {teg2}")
    print(f"  Nodes match: {set(teg.nodes.keys()) == set(teg2.nodes.keys())}")
    print()

    # Display Graphviz DOT content
    print("TEG Graphviz Visualization:")
    print("-" * 80)
    print(teg.to_graphviz())
    print("-" * 80)
    print()

    print("=" * 80)
    print("✓ TEG EXAMPLE COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Create PC002 (Regime Detection)")
    print("  2. Add PC002 to TEG")
    print("  3. Verify PC002 depends on PC001")
    print("  4. Compute validation order (PC001 before PC002)")
    print("  5. Validate compositional dependencies")
    print()
    print("TEG enables:")
    print("  - Automated dependency resolution")
    print("  - Correct validation order (topological sort)")
    print("  - Impact analysis (which PCs affected by falsification?)")
    print("  - Visualization (dependency graph)")
    print()


if __name__ == "__main__":
    main()
