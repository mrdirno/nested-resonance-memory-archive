
"""
Cycle 2336: Structural Integrity Check
Goal: Use the Knowledge Graph to identify critical structural weaknesses.
Method:
1. Identify high-centrality files (The "Central Dogma").
2. Verify existence of tests for these files.
3. Report coverage gaps.
"""

import json
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def check_integrity(graph_path="data/knowledge_graph.json"):
    """Performs a structural integrity audit based on the knowledge graph."""
    
    print(f"Loading Knowledge Graph from {graph_path}...")
    try:
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        print("Error: Graph not found.")
        return

    # 1. Calculate Centrality (Degree)
    node_degrees = {}
    for edge in graph_data["edges"]:
        target = edge["target"]
        node_degrees[target] = node_degrees.get(target, 0) + 1
        
    # Filter for files only (exclude abstract Principles)
    file_nodes = [n for n in node_degrees.keys() if n in graph_data["nodes"] and graph_data["nodes"][n].get("type") == "file"]
    
    sorted_files = sorted(file_nodes, key=lambda n: node_degrees[n], reverse=True)
    top_files = sorted_files[:10]
    
    print("\nTop 10 High-Centrality Files (The Core):")
    for f in top_files:
        print(f"  {f} (Degree: {node_degrees[f]})")
        
    # 2. Verify Test Coverage
    print("\nVerifying Test Coverage for Core Files...")
    coverage_report = {}
    
    for file_node in top_files:
        # Heuristic: Check for test file with similar name in tests/ or experiments/
        base_name = os.path.splitext(os.path.basename(file_node))[0]
        expected_test = f"test_{{base_name}}.py"
        
        # Search for test
        test_found = False
        for node in graph_data["nodes"]:
            if expected_test in node:
                test_found = True
                break
        
        status = "COVERED" if test_found else "EXPOSED"
        coverage_report[file_node] = status
        print(f"  {file_node}: {status}")
        
    # 3. Generate Report
    output_path = "analysis/integrity_report_cycle2336.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(coverage_report, f, indent=2)
        
    exposed_count = list(coverage_report.values()).count("EXPOSED")
    if exposed_count == 0:
        print("\n[SUCCESS] Core Structural Integrity Confirmed.")
    else:
        print(f"\n[WARNING] {exposed_count} Core Files are exposed (missing direct tests).")

if __name__ == "__main__":
    check_integrity()
