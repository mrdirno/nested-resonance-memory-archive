
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

# Add the parent directory to the Python path to import pattern_memory
import sys
sys.path.insert(0, str(Path(__file__).parent))

from memory.pattern_memory import PatternMemory, PatternType, Pattern

class PatternArchaeologist:
    """
    Traces the lineage and relationships of patterns stored in PatternMemory.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        """
        Initialize PatternArchaeologist.

        Args:
            workspace_path: Path to workspace directory where memory.db resides.
        """
        if workspace_path is None:
            self.workspace_path = Path.cwd() / "workspace"
        else:
            self.workspace_path = workspace_path
        
        self.memory = PatternMemory(self.workspace_path)
        print(f"PatternArchaeologist initialized. Using database: {self.memory.db_path}")

    def get_parent_patterns(self, pattern_id: str) -> List[Tuple[str, str, float]]:
        """
        Get all direct parent patterns of a given pattern.

        Returns: List of (parent_pattern_id, relationship_type, strength) tuples.
        """
        with self.memory._db_connection() as conn:
            cursor = conn.execute("""
                SELECT parent_pattern_id, relationship_type, strength
                FROM pattern_relationships
                WHERE child_pattern_id = ?
            """, (pattern_id,))
            return cursor.fetchall()

    def get_child_patterns(self, pattern_id: str) -> List[Tuple[str, str, float]]:
        """
        Get all direct child patterns of a given pattern.

        Returns: List of (child_pattern_id, relationship_type, strength) tuples.
        """
        with self.memory._db_connection() as conn:
            cursor = conn.execute("""
                SELECT child_pattern_id, relationship_type, strength
                FROM pattern_relationships
                WHERE parent_pattern_id = ?
            """, (pattern_id,))
            return cursor.fetchall()

    def trace_ancestry(self, start_pattern_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Recursively trace the ancestry of a pattern.

        Args:
            start_pattern_id: The ID of the pattern to start tracing from.
            max_depth: Maximum recursion depth.

        Returns:
            A dictionary representing the ancestry tree.
        """
        ancestry_tree = {}
        visited = set()

        def _recursive_trace(current_pattern_id: str, current_depth: int) -> Dict[str, Any]:
            if current_pattern_id in visited or current_depth > max_depth:
                return {}
            
            visited.add(current_pattern_id)
            
            pattern_info = self.memory.get_pattern(current_pattern_id)
            node = {
                "id": current_pattern_id,
                "name": pattern_info.name if pattern_info else "Unknown Pattern",
                "type": pattern_info.pattern_type.value if pattern_info else "Unknown Type",
                "confidence": pattern_info.confidence if pattern_info else None,
                "parents": []
            }

            parents = self.get_parent_patterns(current_pattern_id)
            for parent_id, rel_type, strength in parents:
                parent_node = _recursive_trace(parent_id, current_depth + 1)
                if parent_node:
                    node["parents"].append({
                        "pattern": parent_node,
                        "relationship_type": rel_type,
                        "strength": strength
                    })
                elif parent_id not in visited: # If not visited but recursive trace returns empty, it means max_depth reached or problem
                     parent_info = self.memory.get_pattern(parent_id)
                     node["parents"].append({
                        "pattern": {
                            "id": parent_id,
                            "name": parent_info.name if parent_info else "Unknown Pattern",
                            "type": parent_info.pattern_type.value if parent_info else "Unknown Type",
                            "confidence": pattern_info.confidence if pattern_info else None,
                        },
                        "relationship_type": rel_type,
                        "strength": strength
                    })
            return node
        
        return _recursive_trace(start_pattern_id, 0)

    def trace_descendancy(self, start_pattern_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Recursively trace the descendancy of a pattern.

        Args:
            start_pattern_id: The ID of the pattern to start tracing from.
            max_depth: Maximum recursion depth.

        Returns:
            A dictionary representing the descendancy tree.
        """
        descendancy_tree = {}
        visited = set()

        def _recursive_trace(current_pattern_id: str, current_depth: int) -> Dict[str, Any]:
            if current_pattern_id in visited or current_depth > max_depth:
                return {}
            
            visited.add(current_pattern_id)
            
            pattern_info = self.memory.get_pattern(current_pattern_id)
            node = {
                "id": current_pattern_id,
                "name": pattern_info.name if pattern_info else "Unknown Pattern",
                "type": pattern_info.pattern_type.value if pattern_info else "Unknown Type",
                "confidence": pattern_info.confidence if pattern_info else None,
                "children": []
            }

            children = self.get_child_patterns(current_pattern_id)
            for child_id, rel_type, strength in children:
                child_node = _recursive_trace(child_id, current_depth + 1)
                if child_node:
                    node["children"].append({
                        "pattern": child_node,
                        "relationship_type": rel_type,
                        "strength": strength
                    })
                elif child_id not in visited: # If not visited but recursive trace returns empty, it means max_depth reached or problem
                    child_info = self.memory.get_pattern(child_id)
                    node["children"].append({
                        "pattern": {
                            "id": child_id,
                            "name": child_info.name if child_info else "Unknown Pattern",
                            "type": child_info.pattern_type.value if child_info else "Unknown Type",
                            "confidence": child_info.confidence if child_info else None,
                        },
                        "relationship_type": rel_type,
                        "strength": strength
                    })
            return node
        
        return _recursive_trace(start_pattern_id, 0)

    def get_semantically_related_patterns(self, pattern_id: str, min_weight: float = 0.5, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get patterns semantically related to a given pattern based on the semantic graph.

        Args:
            pattern_id: The ID of the pattern.
            min_weight: Minimum semantic weight to consider a pattern related.
            limit: Maximum number of related patterns to return.

        Returns:
            List of (related_pattern_id, weight) tuples.
        """
        return self.memory.get_graph_neighbors(pattern_id, min_weight=min_weight, limit=limit)

    def _check_pattern_relationships(self, pattern_id: str):
        """Diagnostic function to check direct relationships for a pattern ID."""
        print(f"\n--- Diagnostic for Pattern ID: {pattern_id} ---")
        parents = self.get_parent_patterns(pattern_id)
        if parents:
            print(f"  Found {len(parents)} direct parent(s).")
            for p_id, p_type, p_strength in parents:
                print(f"    Parent: {p_id}, Type: {p_type}, Strength: {p_strength:.2f}")
        else:
            print("  No direct parent relationships found.")

        children = self.get_child_patterns(pattern_id)
        if children:
            print(f"  Found {len(children)} direct child(ren).")
            for c_id, c_type, c_strength in children:
                print(f"    Child: {c_id}, Type: {c_type}, Strength: {c_strength:.2f}")
        else:
            print("  No direct child relationships found.")
        
        sem_relations = self.get_semantically_related_patterns(pattern_id, min_weight=0.0, limit=1) # Check with min_weight=0.0
        if sem_relations:
            print(f"  Found {len(sem_relations)} semantically related pattern(s) (min_weight=0.0).")
        else:
            print("  No semantically related patterns found (even with min_weight=0.0).")
        print("------------------------------------------")

    @staticmethod
    def get_depth(node: Dict[str, Any]) -> int:
        """
        Calculates the maximum depth of an ancestry or descendancy tree.
        Assumes the tree structure returned by trace_ancestry or trace_descendancy.
        """
        if not node.get("parents") and not node.get("children"): # Base case: leaf node
            return 1
        
        max_d = 0
        if "parents" in node:
            for p_rel in node["parents"]:
                depth = PatternArchaeologist.get_depth(p_rel["pattern"])
                if depth > max_d:
                    max_d = depth
        if "children" in node:
            for c_rel in node["children"]:
                depth = PatternArchaeologist.get_depth(c_rel["pattern"])
                if depth > max_d:
                    max_d = depth
        return 1 + max_d


def print_pattern_tree(node: Dict[str, Any], indent: int = 0, relation_label: str = ""):
    """Helper function to pretty print the pattern tree."""
    prefix = "  " * indent
    rel_str = f" ({relation_label} {node.get('relationship_type', '')} [{node.get('strength', 0):.2f}])" if relation_label else ""
    
    print(f"{prefix}- {node['name']} (ID: {node['id']}, Type: {node['type']}{rel_str})")
    
    if "parents" in node:
        for parent_rel in node["parents"]:
            print_pattern_tree(parent_rel["pattern"], indent + 1, "Parent of")
    
    if "children" in node:
        for child_rel in node["children"]:
            print_pattern_tree(child_rel["pattern"], indent + 1, "Child of")


if __name__ == "__main__":
    archaeologist = PatternArchaeologist()

    # Find a pattern to start tracing from
    # We will use "459abcffc7b40c78" which we know has child relationships
    start_pattern_id = "459abcffc7b40c78"
    start_pattern = archaeologist.memory.get_pattern(start_pattern_id)
    
    if start_pattern:
        print(f"\nStarting Pattern for Archaeology:")
        print(f"  ID: {start_pattern.pattern_id}")
        print(f"  Name: {start_pattern.name}")
        print(f"  Type: {start_pattern.pattern_type.value}")
        print(f"  Occurrences: {start_pattern.occurrences}")
        print(f"  Confidence: {start_pattern.confidence:.2f}")

        print("\n--- Tracing Ancestry ---")
        ancestry = archaeologist.trace_ancestry(start_pattern.pattern_id, max_depth=2)
        if ancestry:
            print_pattern_tree(ancestry)
        else:
            print(f"No ancestry found for pattern ID: {start_pattern.pattern_id}")

        print("\n--- Tracing Descendancy ---")
        descendancy = archaeologist.trace_descendancy(start_pattern.pattern_id, max_depth=2)
        if descendancy:
            print_pattern_tree(descendancy)
        else:
            print(f"No descendancy found for pattern ID: {start_pattern.pattern_id}")

        print("\n--- Semantically Related Patterns ---")
        related_patterns = archaeologist.get_semantically_related_patterns(start_pattern.pattern_id)
        if related_patterns:
            for related_id, weight in related_patterns:
                related_info = archaeologist.memory.get_pattern(related_id)
                if related_info:
                    print(f"  - {related_info.name} (ID: {related_id}, Type: {related_info.pattern_type.value}, Weight: {weight:.2f})")
                else:
                    print(f"  - Unknown Pattern (ID: {related_id}, Weight: {weight:.2f})")
        else:
            print(f"No semantically related patterns found for pattern ID: {start_pattern.pattern_id}")

    else:
        print(f"\nPattern '{start_pattern_id}' not found. Please ensure patterns are recorded.")
