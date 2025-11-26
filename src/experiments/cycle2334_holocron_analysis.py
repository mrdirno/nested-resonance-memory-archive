import json
import os
from collections import Counter, defaultdict

# Configuration
GRAPH_FILE = "data/knowledge_graph.json"
OUTPUT_REPORT = "analysis/holocron_report.md"

def analyze_holocron():
    if not os.path.exists(GRAPH_FILE):
        print(f"Error: {GRAPH_FILE} not found.")
        return

    print(f"Loading {GRAPH_FILE}...")
    with open(GRAPH_FILE, 'r') as f:
        graph = json.load(f)

    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])

    # 1. Categorize Nodes
    files = [id for id, attr in nodes.items() if attr.get("type") == "file"]
    principles = [id for id, attr in nodes.items() if attr.get("type") == "principle"]
    cycles = [id for id, attr in nodes.items() if attr.get("type") == "cycle"]
    
    # 2. Analyze Edges (Degree Centrality)
    node_degree = Counter()
    for edge in edges:
        target = edge.get("target")
        if target:
            node_degree[target] += 1

    # 3. Top Principles
    top_principles = []
    for p in principles:
        top_principles.append((p, node_degree[p]))
    top_principles.sort(key=lambda x: x[1], reverse=True)

    # 4. Top Cycles
    top_cycles = []
    for c in cycles:
        top_cycles.append((c, node_degree[c]))
    top_cycles.sort(key=lambda x: x[1], reverse=True)

    # 5. Orphaned Principles (0 references)
    orphan_principles = [p for p, count in top_principles if count == 0]
    # Note: In this graph structure, if a principle node exists but has no incoming edges, it's orphaned.
    # However, scanning likely only creates nodes if found in text.
    # Wait, if a principle is DEFINED, is it a target?
    # The scanner creates edges {source: file, target: principle, relation: mentions}.
    # So degree = count of files mentioning it.

    # 6. File Density (Out-degree)
    file_out_degree = Counter()
    for edge in edges:
        source = edge.get("source")
        if source:
            file_out_degree[source] += 1
    
    top_files = []
    for f in files:
        top_files.append((f, file_out_degree[f]))
    top_files.sort(key=lambda x: x[1], reverse=True)

    # Generate Report
    lines = []
    lines.append("# THE HOLOCRON: Knowledge Graph Analysis")
    lines.append(f"**Date:** {os.popen('date').read().strip()}")
    lines.append(f"**Source:** `{GRAPH_FILE}`")
    lines.append("")
    lines.append("## 1. System Statistics")
    lines.append(f"- **Total Nodes:** {len(nodes)}")
    lines.append(f"- **Total Edges:** {len(edges)}")
    lines.append(f"- **Files Scanned:** {len(files)}")
    lines.append(f"- **Principles Discovered:** {len(principles)}")
    lines.append(f"- **Cycles Logged:** {len(cycles)}")
    lines.append("")
    lines.append("## 2. Core Principles (The Central Dogma)")
    lines.append("These are the most referenced concepts in the system.")
    for p, count in top_principles[:10]:
        lines.append(f"- **{p}:** {count} references")
    lines.append("")
    lines.append("## 3. High-Activity Cycles")
    lines.append("Cycles with the most extensive documentation footprint.")
    for c, count in top_cycles[:10]:
        lines.append(f"- **{c}:** {count} references")
    lines.append("")
    lines.append("## 4. Dense Artifacts")
    lines.append("Files containing the highest density of meta-data (Principles/Cycles).")
    for f, count in top_files[:10]:
        lines.append(f"- `{f}` ({count} tags)")
    lines.append("")
    lines.append(f"## 5. Orphaned Principles")
    lines.append(f"Principles with 0 or 1 reference. Total: {len(orphan_principles)}")
    # Orphans usually have 0 degree if they were added as nodes but never targeted? 
    # Or maybe 1 if defined? 
    # Let's list low-count ones (<=1)
    low_count_principles = [p for p, count in top_principles if count <= 1]
    for p in low_count_principles[:10]:
        lines.append(f"- {p}")
    if len(low_count_principles) > 10:
        lines.append(f"- ... and {len(low_count_principles) - 10} more.")

    # Write Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"Analysis complete. Report written to {OUTPUT_REPORT}")

if __name__ == "__main__":
    analyze_holocron()
