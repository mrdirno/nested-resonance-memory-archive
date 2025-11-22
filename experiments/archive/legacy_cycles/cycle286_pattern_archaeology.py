import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.pattern_archaeologist import PatternArchaeologist

def count_nodes(tree: Dict[str, Any], key: str) -> int:
    """Recursively count nodes in an ancestry or descendancy tree."""
    count = 0
    if key in tree:
        for node in tree[key]:
            count += 1 + count_nodes(node["pattern"], key)
    return count

def get_max_depth(tree: Dict[str, Any], key: str) -> int:
    """Recursively find max depth."""
    max_d = 0
    if key in tree:
        for node in tree[key]:
            d = 1 + get_max_depth(node["pattern"], key)
            if d > max_d:
                max_d = d
    return max_d

def main():
    print("CYCLE 286: PATTERN ARCHAEOLOGY - MEMORY LINEAGE ANALYSIS")
    print("========================================================")
    
    archaeologist = PatternArchaeologist()
    
    # 1. Fetch all patterns
    print("Fetching patterns from memory...")
    # Using search_patterns with high limit to get everything
    patterns = archaeologist.memory.search_patterns(limit=10000)
    print(f"Found {len(patterns)} patterns in database.")
    
    results = []
    
    print("Analyzing lineage metrics...")
    start_time = time.time()
    
    for i, p in enumerate(patterns):
        if i % 50 == 0:
            print(f"  Processing {i}/{len(patterns)}...", end="\r")
            
        # Trace Lineage
        # Ancestry
        ancestry_tree = archaeologist.trace_ancestry(p.pattern_id, max_depth=10)
        ancestry_depth = get_max_depth(ancestry_tree, "parents")
        ancestry_count = count_nodes(ancestry_tree, "parents")
        
        # Descendancy
        descendancy_tree = archaeologist.trace_descendancy(p.pattern_id, max_depth=10)
        descendancy_depth = get_max_depth(descendancy_tree, "children")
        descendancy_count = count_nodes(descendancy_tree, "children")
        
        # Semantic Connections
        semantic_neighbors = archaeologist.get_semantically_related_patterns(p.pattern_id, min_weight=0.1)
        
        results.append({
            "id": p.pattern_id,
            "name": p.name,
            "type": p.pattern_type.value,
            "confidence": p.confidence,
            "occurrences": p.occurrences,
            "ancestry_depth": ancestry_depth,
            "ancestry_count": ancestry_count,
            "descendancy_depth": descendancy_depth,
            "descendancy_count": descendancy_count,
            "semantic_connections": len(semantic_neighbors)
        })
        
    print(f"  Processing {len(patterns)}/{len(patterns)}... Done.")
    duration = time.time() - start_time
    print(f"Analysis complete in {duration:.2f} seconds.")
    
    # 2. Identify Key Patterns
    
    # Sort by Descendancy Count (Foundational Patterns)
    by_descendants = sorted(results, key=lambda x: x["descendancy_count"], reverse=True)
    
    # Sort by Ancestry Depth (Highly Derivative/Complex Patterns)
    by_ancestry = sorted(results, key=lambda x: x["ancestry_depth"], reverse=True)
    
    # Sort by Semantic Centrality
    by_semantic = sorted(results, key=lambda x: x["semantic_connections"], reverse=True)
    
    print("\n--- TOP FOUNDATIONAL PATTERNS (Most Descendants) ---")
    for p in by_descendants[:5]:
        print(f"  [{p['descendancy_count']} descendants] {p['name']} (ID: {p['id'][:8]}...)")
        
    print("\n--- TOP DERIVATIVE PATTERNS (Deepest Ancestry) ---")
    for p in by_ancestry[:5]:
        print(f"  [{p['ancestry_depth']} depth] {p['name']} (ID: {p['id'][:8]}...)")

    print("\n--- TOP SEMANTIC HUBS (Most Connections) ---")
    for p in by_semantic[:5]:
        print(f"  [{p['semantic_connections']} connections] {p['name']} (ID: {p['id'][:8]}...)")

    # Save Results
    os.makedirs("experiments/results", exist_ok=True)
    output_path = "experiments/results/c286_pattern_lineage.json"
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "total_patterns": len(patterns),
            "analysis": results
        }, f, indent=2)
        
    print(f"\nFull results saved to {output_path}")

if __name__ == "__main__":
    main()
