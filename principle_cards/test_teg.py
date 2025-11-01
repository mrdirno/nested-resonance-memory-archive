"""
Tests for Temporal Embedding Graph (TEG)
==========================================

Comprehensive test suite for TEG functionality.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import pytest
from pathlib import Path
import tempfile
import json

from .teg import (
    PCNode,
    TemporalEmbeddingGraph,
    create_teg_from_pcs
)
from .base import PrincipleCard, PCMetadata


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_nodes():
    """Create sample PC nodes for testing."""
    nodes = [
        PCNode(
            pc_id="PC001",
            version="1.0.0",
            title="NRM Population Dynamics",
            author="Aldrin Payopay",
            created="2025-11-01",
            status="validated",
            domain="NRM",
            dependencies=[],  # Foundational
            enables=["PC002", "PC004"]
        ),
        PCNode(
            pc_id="PC002",
            version="1.0.0",
            title="Regime Detection",
            author="Aldrin Payopay",
            created="2025-11-02",
            status="proposed",
            domain="NRM",
            dependencies=["PC001"],
            enables=["PC003"]
        ),
        PCNode(
            pc_id="PC003",
            version="1.0.0",
            title="Overhead Authentication",
            author="Aldrin Payopay",
            created="2025-11-03",
            status="proposed",
            domain="TSF",
            dependencies=["PC001", "PC002"],
            enables=[]
        ),
        PCNode(
            pc_id="PC004",
            version="1.0.0",
            title="Multi-scale Dynamics",
            author="Aldrin Payopay",
            created="2025-11-04",
            status="draft",
            domain="NRM",
            dependencies=["PC001"],
            enables=[]
        )
    ]
    return nodes


@pytest.fixture
def populated_teg(sample_nodes):
    """Create populated TEG for testing."""
    teg = TemporalEmbeddingGraph()
    for node in sample_nodes:
        teg.add_node(node)
    return teg


# ============================================================================
# PCNODE TESTS
# ============================================================================

class TestPCNode:
    """Tests for PCNode dataclass."""

    def test_pcnode_creation(self):
        """Test PCNode creation."""
        node = PCNode(
            pc_id="PC001",
            version="1.0.0",
            title="Test PC",
            author="Test Author",
            created="2025-11-01",
            status="validated",
            domain="NRM"
        )

        assert node.pc_id == "PC001"
        assert node.version == "1.0.0"
        assert node.title == "Test PC"
        assert node.dependencies == []
        assert node.enables == []

    def test_pcnode_with_dependencies(self):
        """Test PCNode with dependencies."""
        node = PCNode(
            pc_id="PC002",
            version="1.0.0",
            title="Test PC",
            author="Test Author",
            created="2025-11-01",
            status="proposed",
            domain="NRM",
            dependencies=["PC001"],
            enables=["PC003"]
        )

        assert node.dependencies == ["PC001"]
        assert node.enables == ["PC003"]

    def test_pcnode_to_dict(self):
        """Test PCNode serialization."""
        node = PCNode(
            pc_id="PC001",
            version="1.0.0",
            title="Test PC",
            author="Test Author",
            created="2025-11-01",
            status="validated",
            domain="NRM",
            dependencies=[],
            enables=["PC002"]
        )

        data = node.to_dict()
        assert data['pc_id'] == "PC001"
        assert data['enables'] == ["PC002"]

    def test_pcnode_from_dict(self):
        """Test PCNode deserialization."""
        data = {
            'pc_id': "PC001",
            'version': "1.0.0",
            'title': "Test PC",
            'author': "Test Author",
            'created': "2025-11-01",
            'status': "validated",
            'domain': "NRM",
            'dependencies': [],
            'enables': ["PC002"]
        }

        node = PCNode.from_dict(data)
        assert node.pc_id == "PC001"
        assert node.enables == ["PC002"]


# ============================================================================
# TEG INITIALIZATION TESTS
# ============================================================================

class TestTEGInitialization:
    """Tests for TEG initialization."""

    def test_empty_teg(self):
        """Test empty TEG creation."""
        teg = TemporalEmbeddingGraph()
        assert len(teg) == 0
        assert len(teg.nodes) == 0

    def test_add_single_node(self, sample_nodes):
        """Test adding single node."""
        teg = TemporalEmbeddingGraph()
        teg.add_node(sample_nodes[0])

        assert len(teg) == 1
        assert "PC001" in teg
        assert teg.has_node("PC001")

    def test_add_multiple_nodes(self, sample_nodes):
        """Test adding multiple nodes."""
        teg = TemporalEmbeddingGraph()
        for node in sample_nodes:
            teg.add_node(node)

        assert len(teg) == 4
        assert "PC001" in teg
        assert "PC002" in teg
        assert "PC003" in teg
        assert "PC004" in teg

    def test_add_duplicate_node(self, sample_nodes):
        """Test adding duplicate node raises error."""
        teg = TemporalEmbeddingGraph()
        teg.add_node(sample_nodes[0])

        with pytest.raises(ValueError, match="already exists"):
            teg.add_node(sample_nodes[0])


# ============================================================================
# TEG NODE OPERATIONS TESTS
# ============================================================================

class TestTEGNodeOperations:
    """Tests for TEG node operations."""

    def test_get_node(self, populated_teg):
        """Test getting node by ID."""
        node = populated_teg.get_node("PC001")
        assert node.pc_id == "PC001"
        assert node.title == "NRM Population Dynamics"

    def test_get_nonexistent_node(self, populated_teg):
        """Test getting nonexistent node raises error."""
        with pytest.raises(KeyError, match="not found"):
            populated_teg.get_node("PC999")

    def test_has_node(self, populated_teg):
        """Test checking node existence."""
        assert populated_teg.has_node("PC001")
        assert not populated_teg.has_node("PC999")

    def test_remove_node(self, populated_teg):
        """Test removing node."""
        assert "PC001" in populated_teg
        populated_teg.remove_node("PC001")
        assert "PC001" not in populated_teg
        assert len(populated_teg) == 3

    def test_remove_nonexistent_node(self, populated_teg):
        """Test removing nonexistent node raises error."""
        with pytest.raises(KeyError, match="not found"):
            populated_teg.remove_node("PC999")


# ============================================================================
# TEG DEPENDENCY TESTS
# ============================================================================

class TestTEGDependencies:
    """Tests for TEG dependency tracking."""

    def test_get_dependencies(self, populated_teg):
        """Test getting direct dependencies."""
        # PC001 has no dependencies (foundational)
        assert populated_teg.get_dependencies("PC001") == []

        # PC002 depends on PC001
        deps = populated_teg.get_dependencies("PC002")
        assert "PC001" in deps

        # PC003 depends on PC001 and PC002
        deps = populated_teg.get_dependencies("PC003")
        assert "PC001" in deps
        assert "PC002" in deps

    def test_get_dependents(self, populated_teg):
        """Test getting direct dependents."""
        # PC001 is depended on by PC002, PC003, PC004
        dependents = populated_teg.get_dependents("PC001")
        assert "PC002" in dependents
        assert "PC003" in dependents
        assert "PC004" in dependents

        # PC002 is depended on by PC003
        dependents = populated_teg.get_dependents("PC002")
        assert "PC003" in dependents

        # PC004 has no dependents (leaf node)
        assert populated_teg.get_dependents("PC004") == []

    def test_get_all_dependencies_transitive(self, populated_teg):
        """Test getting transitive dependencies."""
        # PC003 depends on PC002, which depends on PC001
        # So PC003's transitive dependencies are {PC001, PC002}
        all_deps = populated_teg.get_all_dependencies("PC003")
        assert "PC001" in all_deps
        assert "PC002" in all_deps
        assert len(all_deps) == 2

        # PC002 depends only on PC001
        all_deps = populated_teg.get_all_dependencies("PC002")
        assert all_deps == {"PC001"}

        # PC001 has no dependencies
        all_deps = populated_teg.get_all_dependencies("PC001")
        assert len(all_deps) == 0

    def test_get_all_dependents_transitive(self, populated_teg):
        """Test getting transitive dependents."""
        # PC001 is depended on by PC002, PC003, PC004
        # PC002 is depended on by PC003
        # So PC001's transitive dependents are {PC002, PC003, PC004}
        all_deps = populated_teg.get_all_dependents("PC001")
        assert "PC002" in all_deps
        assert "PC003" in all_deps
        assert "PC004" in all_deps

        # PC002's transitive dependents are {PC003}
        all_deps = populated_teg.get_all_dependents("PC002")
        assert all_deps == {"PC003"}


# ============================================================================
# TEG TOPOLOGICAL SORT TESTS
# ============================================================================

class TestTEGTopologicalSort:
    """Tests for TEG topological sorting."""

    def test_topological_sort(self, populated_teg):
        """Test topological sort produces valid order."""
        order = populated_teg.topological_sort()

        # PC001 must come before PC002, PC003, PC004
        assert order.index("PC001") < order.index("PC002")
        assert order.index("PC001") < order.index("PC003")
        assert order.index("PC001") < order.index("PC004")

        # PC002 must come before PC003
        assert order.index("PC002") < order.index("PC003")

    def test_topological_sort_empty_graph(self):
        """Test topological sort on empty graph."""
        teg = TemporalEmbeddingGraph()
        order = teg.topological_sort()
        assert order == []

    def test_topological_sort_with_cycle(self):
        """Test topological sort detects cycles."""
        teg = TemporalEmbeddingGraph()

        # Create cycle: PC001 → PC002 → PC003 → PC001
        node1 = PCNode(
            pc_id="PC001",
            version="1.0.0",
            title="Test 1",
            author="Test",
            created="2025-11-01",
            status="draft",
            domain="TSF",
            dependencies=["PC003"],  # Cycle!
            enables=["PC002"]
        )
        node2 = PCNode(
            pc_id="PC002",
            version="1.0.0",
            title="Test 2",
            author="Test",
            created="2025-11-01",
            status="draft",
            domain="TSF",
            dependencies=["PC001"],
            enables=["PC003"]
        )
        node3 = PCNode(
            pc_id="PC003",
            version="1.0.0",
            title="Test 3",
            author="Test",
            created="2025-11-01",
            status="draft",
            domain="TSF",
            dependencies=["PC002"],
            enables=["PC001"]
        )

        teg.add_node(node1)
        teg.add_node(node2)
        teg.add_node(node3)

        with pytest.raises(ValueError, match="contains cycles"):
            teg.topological_sort()

    def test_has_cycle(self):
        """Test cycle detection."""
        # Create a simple TEG with no cycles
        teg = TemporalEmbeddingGraph()

        # PC001 → PC002 → PC003 (no cycle)
        node1 = PCNode("PC001", "1.0.0", "Test 1", "Test", "2025-11-01", "draft", "NRM", [], [])
        node2 = PCNode("PC002", "1.0.0", "Test 2", "Test", "2025-11-01", "draft", "NRM", ["PC001"], [])
        node3 = PCNode("PC003", "1.0.0", "Test 3", "Test", "2025-11-01", "draft", "NRM", ["PC002"], [])

        teg.add_node(node1)
        teg.add_node(node2)
        teg.add_node(node3)

        assert not teg.has_cycle()

        # Add a cycle: PC003 → PC001 (creates cycle PC001 → PC002 → PC003 → PC001)
        node4 = PCNode("PC004", "1.0.0", "Test 4", "Test", "2025-11-01", "draft", "NRM", ["PC003"], [])
        node1_cyclic = PCNode("PC001", "1.0.0", "Test 1 Modified", "Test", "2025-11-01", "draft", "NRM", ["PC004"], [])

        teg.add_node(node4)

        # Remove old PC001 and add new one with cyclic dependency
        teg.remove_node("PC001")
        teg.add_node(node1_cyclic)

        assert teg.has_cycle()


# ============================================================================
# TEG VALIDATION ORDER TESTS
# ============================================================================

class TestTEGValidationOrder:
    """Tests for validation order computation."""

    def test_get_validation_order_all(self, populated_teg):
        """Test getting validation order for all PCs."""
        order = populated_teg.get_validation_order()

        # Should be same as topological sort
        assert order == populated_teg.topological_sort()

    def test_get_validation_order_subset(self, populated_teg):
        """Test getting validation order for subset of PCs."""
        # To validate PC003, we need PC001 and PC002 first
        order = populated_teg.get_validation_order(["PC003"])

        assert "PC001" in order
        assert "PC002" in order
        assert "PC003" in order
        assert len(order) == 3

        # Correct order: PC001 before PC002 before PC003
        assert order.index("PC001") < order.index("PC002")
        assert order.index("PC002") < order.index("PC003")

    def test_get_validation_order_foundational(self, populated_teg):
        """Test validation order for foundational PC."""
        # PC001 has no dependencies
        order = populated_teg.get_validation_order(["PC001"])
        assert order == ["PC001"]


# ============================================================================
# TEG QUERY TESTS
# ============================================================================

class TestTEGQueries:
    """Tests for TEG query operations."""

    def test_get_foundational_pcs(self, populated_teg):
        """Test getting foundational PCs."""
        foundational = populated_teg.get_foundational_pcs()
        assert foundational == ["PC001"]

    def test_get_leaf_pcs(self, populated_teg):
        """Test getting leaf PCs."""
        leaves = populated_teg.get_leaf_pcs()
        assert "PC003" in leaves
        assert "PC004" in leaves

    def test_filter_by_status(self, populated_teg):
        """Test filtering by status."""
        validated = populated_teg.filter_by_status("validated")
        assert validated == ["PC001"]

        proposed = populated_teg.filter_by_status("proposed")
        assert "PC002" in proposed
        assert "PC003" in proposed

        draft = populated_teg.filter_by_status("draft")
        assert draft == ["PC004"]

    def test_filter_by_domain(self, populated_teg):
        """Test filtering by domain."""
        nrm_pcs = populated_teg.filter_by_domain("NRM")
        assert "PC001" in nrm_pcs
        assert "PC002" in nrm_pcs
        assert "PC004" in nrm_pcs

        tsf_pcs = populated_teg.filter_by_domain("TSF")
        assert tsf_pcs == ["PC003"]


# ============================================================================
# TEG SERIALIZATION TESTS
# ============================================================================

class TestTEGSerialization:
    """Tests for TEG serialization."""

    def test_to_dict(self, populated_teg):
        """Test TEG to dictionary conversion."""
        data = populated_teg.to_dict()

        assert 'nodes' in data
        assert 'adjacency' in data
        assert 'reverse_adjacency' in data

        assert len(data['nodes']) == 4
        assert "PC001" in data['nodes']

    def test_from_dict(self, populated_teg):
        """Test TEG from dictionary creation."""
        data = populated_teg.to_dict()
        teg2 = TemporalEmbeddingGraph.from_dict(data)

        assert len(teg2) == len(populated_teg)
        assert teg2.get_node("PC001").title == populated_teg.get_node("PC001").title

    def test_save_load(self, populated_teg):
        """Test TEG save and load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "teg.json"

            # Save
            populated_teg.save(path)
            assert path.exists()

            # Load
            teg2 = TemporalEmbeddingGraph.load(path)
            assert len(teg2) == len(populated_teg)
            assert teg2.topological_sort() == populated_teg.topological_sort()

    def test_roundtrip_serialization(self, populated_teg):
        """Test roundtrip serialization preserves structure."""
        data = populated_teg.to_dict()
        teg2 = TemporalEmbeddingGraph.from_dict(data)

        # Check all nodes preserved
        assert set(teg2.nodes.keys()) == set(populated_teg.nodes.keys())

        # Check all dependencies preserved
        for pc_id in populated_teg.nodes:
            assert set(teg2.get_dependencies(pc_id)) == set(populated_teg.get_dependencies(pc_id))
            assert set(teg2.get_dependents(pc_id)) == set(populated_teg.get_dependents(pc_id))


# ============================================================================
# TEG VISUALIZATION TESTS
# ============================================================================

class TestTEGVisualization:
    """Tests for TEG visualization."""

    def test_to_graphviz(self, populated_teg):
        """Test Graphviz export."""
        dot = populated_teg.to_graphviz()

        assert 'digraph TEG' in dot
        assert 'PC001' in dot
        assert 'PC002' in dot
        assert 'validated' in dot
        assert 'enables' in dot

    def test_save_graphviz(self, populated_teg):
        """Test Graphviz file save."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "teg.dot"

            populated_teg.save_graphviz(path)
            assert path.exists()

            # Check content
            content = path.read_text()
            assert 'digraph TEG' in content
            assert 'PC001' in content


# ============================================================================
# TEG CONVENIENCE FUNCTION TESTS
# ============================================================================

class TestTEGConvenienceFunctions:
    """Tests for TEG convenience functions."""

    def test_create_teg_from_pcs(self):
        """Test creating TEG from PrincipleCard instances."""
        # Create mock PrincipleCard for testing
        class MockPC(PrincipleCard):
            def __init__(self, metadata, deps, enables):
                super().__init__(metadata)
                self._deps = deps
                self._enables = enables

            def principle_statement(self): return ""
            def mathematical_formulation(self): return {}
            def validation_protocol(self): return {}
            def reality_grounding(self): return {}
            def validate(self, data, tolerance=None): pass
            def temporal_encoding(self): return {}
            def dependencies(self): return self._deps
            def enables(self): return self._enables

        # Create mock PCs
        pc001 = MockPC(
            PCMetadata(
                pc_id="PC001",
                version="1.0.0",
                title="Test PC 1",
                author="Test Author",
                created="2025-11-01",
                status="validated",
                dependencies=[],
                domain="NRM"
            ),
            deps=[],
            enables=["PC002"]
        )

        pc002 = MockPC(
            PCMetadata(
                pc_id="PC002",
                version="1.0.0",
                title="Test PC 2",
                author="Test Author",
                created="2025-11-02",
                status="proposed",
                dependencies=["PC001"],
                domain="NRM"
            ),
            deps=["PC001"],
            enables=[]
        )

        # Create TEG
        teg = create_teg_from_pcs([pc001, pc002])

        assert len(teg) == 2
        assert "PC001" in teg
        assert "PC002" in teg
        assert teg.get_dependencies("PC002") == ["PC001"]
        assert teg.get_dependents("PC001") == ["PC002"]


# ============================================================================
# TEG INTEGRATION TESTS
# ============================================================================

class TestTEGIntegration:
    """Integration tests for TEG."""

    def test_complex_dependency_graph(self):
        """Test complex dependency graph."""
        teg = TemporalEmbeddingGraph()

        # Create diamond dependency:
        #     PC001
        #    /     \
        #  PC002   PC003
        #    \     /
        #     PC004

        nodes = [
            PCNode(
                pc_id="PC001",
                version="1.0.0",
                title="Base",
                author="Test",
                created="2025-11-01",
                status="validated",
                domain="NRM",
                dependencies=[],
                enables=["PC002", "PC003"]
            ),
            PCNode(
                pc_id="PC002",
                version="1.0.0",
                title="Left",
                author="Test",
                created="2025-11-02",
                status="validated",
                domain="NRM",
                dependencies=["PC001"],
                enables=["PC004"]
            ),
            PCNode(
                pc_id="PC003",
                version="1.0.0",
                title="Right",
                author="Test",
                created="2025-11-03",
                status="validated",
                domain="NRM",
                dependencies=["PC001"],
                enables=["PC004"]
            ),
            PCNode(
                pc_id="PC004",
                version="1.0.0",
                title="Top",
                author="Test",
                created="2025-11-04",
                status="proposed",
                domain="NRM",
                dependencies=["PC002", "PC003"],
                enables=[]
            )
        ]

        for node in nodes:
            teg.add_node(node)

        # Test validation order
        order = teg.topological_sort()

        # PC001 must come first
        assert order[0] == "PC001"

        # PC002 and PC003 must come before PC004
        assert order.index("PC002") < order.index("PC004")
        assert order.index("PC003") < order.index("PC004")

        # Test transitive dependencies of PC004
        all_deps = teg.get_all_dependencies("PC004")
        assert all_deps == {"PC001", "PC002", "PC003"}

    def test_validation_order_with_multiple_paths(self):
        """Test validation order with multiple dependency paths."""
        teg = TemporalEmbeddingGraph()

        # PC001 → PC002 → PC004
        # PC001 → PC003 → PC004
        # (Multiple paths from PC001 to PC004)

        nodes = [
            PCNode("PC001", "1.0.0", "Base", "Test", "2025-11-01", "validated", "NRM", [], ["PC002", "PC003"]),
            PCNode("PC002", "1.0.0", "Path1", "Test", "2025-11-02", "validated", "NRM", ["PC001"], ["PC004"]),
            PCNode("PC003", "1.0.0", "Path2", "Test", "2025-11-03", "validated", "NRM", ["PC001"], ["PC004"]),
            PCNode("PC004", "1.0.0", "Target", "Test", "2025-11-04", "proposed", "NRM", ["PC002", "PC003"], [])
        ]

        for node in nodes:
            teg.add_node(node)

        # Validation order for PC004 should include all dependencies
        order = teg.get_validation_order(["PC004"])
        assert set(order) == {"PC001", "PC002", "PC003", "PC004"}
        assert order.index("PC001") < order.index("PC002")
        assert order.index("PC001") < order.index("PC003")
        assert order.index("PC002") < order.index("PC004")
        assert order.index("PC003") < order.index("PC004")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
