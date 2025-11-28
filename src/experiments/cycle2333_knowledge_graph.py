"""
Cycle 2333: The Knowledge Graph (Meta-Cognition)
Goal: Map the internal dependencies and Principle linkages across the entire repository.
Hypothesis: The system can construct a graph where Nodes = Files/Experiments and Edges = PRIN-tags/Cycles.

Method:
1. Scan all files in the repository.
2. Extract PRIN-tags (e.g., PRIN-SLEEP) and Cycle tags (e.g., Cycle 2329).
3. Extract import dependencies (Python) and file references (Markdown).
4. Construct a JSON graph:
   - Nodes: Files, Principles, Cycles
   - Edges: "mentions", "implements", "validates", "imports"
5. Save to `data/knowledge_graph.json`.
"""

import sys
import os
import json
import re
import networkx as nx
from pathlib import Path

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def scan_repository(root_dir):
    """Scans the repository for files and content."""
    
    graph = {
        "nodes": {},
        "edges": []
    }
    
    # Regex patterns
    prin_pattern = re.compile(r'PRIN-[A-Z0-9-]+')
    cycle_pattern = re.compile(r'Cycle\s?(\d+)', re.IGNORECASE)
    import_pattern = re.compile(r'from\s+([\w\.]+)\s+import|import\s+([\w\.]+)')
    
    ignore_dirs = {'.git', '__pycache__', '.venv', 'node_modules', 'dist', 'build'}
    
    print(f"Scanning repository: {root_dir}")
    
    for path in Path(root_dir).rglob('*'):
        if any(part in ignore_dirs for part in path.parts):
            continue
            
        if path.is_file() and path.suffix in {'.py', '.md', '.json', '.txt'}:
            file_path = str(path.relative_to(root_dir))
            
            # Add File Node
            graph["nodes"][file_path] = {"type": "file", "ext": path.suffix}
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # 1. Extract Principles
                    principles = set(prin_pattern.findall(content))
                    for prin in principles:
                        # Add Principle Node
                        if prin not in graph["nodes"]:
                            graph["nodes"][prin] = {"type": "principle"}
                        # Add Edge
                        graph["edges"].append({"source": file_path, "target": prin, "relation": "mentions"})
                        
                    # 2. Extract Cycles
                    cycles = set(cycle_pattern.findall(content))
                    for cycle_num in cycles:
                        cycle_id = f"Cycle_{cycle_num}"
                        # Add Cycle Node
                        if cycle_id not in graph["nodes"]:
                            graph["nodes"][cycle_id] = {"type": "cycle"}
                        # Add Edge
                        graph["edges"].append({"source": file_path, "target": cycle_id, "relation": "references"})
                        
                    # 3. Extract Imports (Python only)
                    if path.suffix == '.py':
                        imports = import_pattern.findall(content)
                        for imp in imports:
                            module = imp[0] or imp[1]
                            # Heuristic for internal imports (starts with src, nrm_core, etc)
                            # Simplified: just treat module as a node for now
                            if module not in graph["nodes"]:
                                graph["nodes"][module] = {"type": "module"}
                            graph["edges"].append({"source": file_path, "target": module, "relation": "imports"})
                            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
    return graph

def analyze_graph(graph_data):
    """Performs basic analysis on the extracted graph."""
    G = nx.DiGraph()
    
    for node_id, attrs in graph_data["nodes"].items():
        G.add_node(node_id, **attrs)
        
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], relation=edge["relation"])
        
    print(f"\nGraph Analysis:")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    # Find most connected Principles
    principles = [n for n, d in G.nodes(data=True) if d.get("type") == "principle"]
    degrees = sorted([(n, G.degree(n)) for n in principles], key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Referenced Principles:")
    for p, d in degrees[:5]:
        print(f"  {p}: {d} refs")
        
    return degrees

def run_experiment():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    
    # 1. Scan
    graph_data = scan_repository(root_dir)
    
    # 2. Analyze
    stats = analyze_graph(graph_data)
    
    # 3. Save
    output_path = os.path.join(root_dir, "data", "knowledge_graph.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
        
    print(f"\nKnowledge Graph saved to: {output_path}")

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
