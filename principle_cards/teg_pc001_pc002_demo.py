"""
TEG Demo: PC001 + PC002 Compositional Validation
=================================================

Demonstrates Temporal Embedding Graph (TEG) with PC001 and PC002.
Shows compositional validation where PC002 depends on PC001.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

from pathlib import Path
from principle_cards.teg import TemporalEmbeddingGraph, PCNode
from principle_cards.pc001_nrm_population_dynamics import PC001_NRMPopulationDynamics
from principle_cards.pc002_regime_detection import PC002_RegimeDetection


def main():
    """Run TEG demonstration with PC001 and PC002."""
    print("=" * 70)
    print("TEG Demo: Compositional Validation (PC001 + PC002)")
    print("=" * 70)
    print()

    # Create TEG
    print("Creating Temporal Embedding Graph...")
    teg = TemporalEmbeddingGraph()
    print(f"  Empty TEG created")
    print()

    # Create PC001 node
    print("Adding PC001 (NRM Population Dynamics)...")
    pc001_node = PCNode(
        pc_id="PC001",
        version="1.0.0",
        title="NRM Population Dynamics",
        author="Aldrin Payopay <aldrin.gdf@gmail.com>",
        created="2025-11-01",
        status="validated",
        domain="NRM",
        dependencies=[],  # Foundation - no dependencies
        enables=["PC002", "PC005", "PC006"]
    )
    teg.add_node(pc001_node)
    print(f"  PC001 added to TEG")
    print(f"    Dependencies: {pc001_node.dependencies}")
    print(f"    Enables: {pc001_node.enables}")
    print()

    # Create PC002 node
    print("Adding PC002 (Regime Detection)...")
    pc002_node = PCNode(
        pc_id="PC002",
        version="1.0.0",
        title="Regime Detection in Population Dynamics",
        author="Aldrin Payopay <aldrin.gdf@gmail.com>",
        created="2025-11-01",
        status="validated",
        domain="NRM",
        dependencies=["PC001"],  # Depends on PC001 for baseline
        enables=["PC005", "PC006"]
    )
    teg.add_node(pc002_node)
    print(f"  PC002 added to TEG")
    print(f"    Dependencies: {pc002_node.dependencies}")
    print(f"    Enables: {pc002_node.enables}")
    print()

    # Inspect TEG structure
    print("=" * 70)
    print("TEG Structure")
    print("=" * 70)
    print()

    print(f"Nodes in TEG: {len(teg.nodes)}")
    for pc_id in teg.nodes:
        node = teg.nodes[pc_id]
        print(f"  {pc_id}: v{node.version}, status={node.status}")
    print()

    # Show dependency graph
    print("Dependency Graph:")
    print("  PC001 (Foundation)")
    print("    └─→ PC002 (Regime Detection)")
    print("          ├─→ PC005 (Multi-Regime Dynamics) [Future]")
    print("          └─→ PC006 (Regime Prediction) [Future]")
    print()

    # Compute validation order
    print("=" * 70)
    print("Validation Order")
    print("=" * 70)
    print()

    validation_order = teg.get_validation_order(["PC002"])
    print(f"To validate PC002, must validate in order:")
    for i, pc_id in enumerate(validation_order, 1):
        print(f"  {i}. {pc_id}")
    print()

    print("TEG enforces: PC001 must be validated before PC002")
    print()

    # Check dependencies
    print("=" * 70)
    print("Dependency Queries")
    print("=" * 70)
    print()

    print("Q: What does PC002 depend on?")
    deps = teg.get_dependencies("PC002")
    print(f"A: {list(deps)}")
    print()

    print("Q: What depends on PC001?")
    dependents = teg.get_dependents("PC001")
    print(f"A: {list(dependents)}")
    print()

    print("Q: What does PC002's node metadata say it enables?")
    pc002_node = teg.nodes["PC002"]
    enabled = pc002_node.enables
    print(f"A: {enabled}")
    print()

    # Check validation status
    print("=" * 70)
    print("Validation Status")
    print("=" * 70)
    print()

    pc001_status = teg.nodes["PC001"].status
    pc002_status = teg.nodes["PC002"].status

    print(f"PC001 status: {pc001_status}")
    print(f"PC002 status: {pc002_status}")
    print()

    if pc001_status == "validated" and pc002_status == "validated":
        print("✓ Both PCs are validated")
    print()

    # Check cycles
    print("=" * 70)
    print("Cycle Detection")
    print("=" * 70)
    print()

    has_cycle = teg.has_cycle()
    print(f"TEG has cycles: {has_cycle}")
    if not has_cycle:
        print("  ✓ TEG is acyclic (valid dependency graph)")
    print()

    # Topological sort
    print("=" * 70)
    print("Topological Sort (Full Validation Order)")
    print("=" * 70)
    print()

    try:
        topo_order = teg.topological_sort()
        print(f"Complete validation order for all PCs:")
        for i, pc_id in enumerate(topo_order, 1):
            print(f"  {i}. {pc_id}")
        print()
    except ValueError as e:
        print(f"  Error: {e}")
        print()

    # Compositional validation demonstration
    print("=" * 70)
    print("Compositional Validation Example")
    print("=" * 70)
    print()

    print("Scenario: User wants to validate PC002")
    print()

    print("Step 1: Query TEG for validation order")
    order = teg.get_validation_order(["PC002"])
    print(f"  Order: {order}")
    print()

    print("Step 2: Validate PC001 first (if not already validated)")
    if teg.nodes["PC001"].status != "validated":
        print("  PC001 not validated - would run PC001.validate() here")
        print("  (Skipping actual validation for demo)")
    else:
        print(f"  PC001 already validated ✓")
    print()

    print("Step 3: Validate PC002 (can now proceed)")
    if teg.nodes["PC002"].status != "validated":
        print("  PC002 not validated - would run PC002.validate() here")
        print("  (Skipping actual validation for demo)")
    else:
        print(f"  PC002 already validated ✓")
    print()

    print("Result: Compositional validation ensures dependencies validated first")
    print()

    # Save TEG
    print("=" * 70)
    print("Persistence")
    print("=" * 70)
    print()

    output_dir = Path(__file__).parent
    teg_path = output_dir / "teg_pc001_pc002.json"
    teg.save(teg_path)
    print(f"TEG saved: {teg_path}")

    dot_path = output_dir / "teg_pc001_pc002.dot"
    teg.save_graphviz(dot_path)
    print(f"DOT graph saved: {dot_path}")
    print()

    print("=" * 70)
    print("✓ TEG Demo Complete")
    print("=" * 70)
    print()

    print("Key Takeaways:")
    print("  1. TEG enforces compositional dependencies (PC002 → PC001)")
    print("  2. Validation order computed automatically via topological sort")
    print("  3. Cycle detection prevents circular dependencies")
    print("  4. Status tracking ensures dependencies validated before dependents")
    print("  5. Serialization enables persistence and visualization")
    print()

    print("Next Steps:")
    print("  - Add PC005 (Multi-Regime Dynamics)")
    print("  - Add PC006 (Regime Prediction)")
    print("  - Implement automated validation pipeline")
    print("  - Generate dependency visualizations (Graphviz)")
    print()


if __name__ == "__main__":
    main()
