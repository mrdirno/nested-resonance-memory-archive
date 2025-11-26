
import os
import re
import json
import glob
from collections import defaultdict

# Configuration
ROOT_DIR = "."
OUTPUT_FILE = "data/knowledge_graph.json"
PATTERNS = {
    "PRINCIPLE": r"PRIN-[A-Z0-9-]+",
    "CYCLE": r"Cycle\s*(\d+)",
    "PHASE": r"Phase\s*(\d+)",
    "TASK": r"Task:\s*Cycle\s*(\d+)"
}

IGNORE_DIRS = {
    ".git", ".venv", ".gemini", "__pycache__", "node_modules", "dist", "build", ".pytest_cache"
}

def scan_file(filepath):
    """Scans a single file for patterns."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {}

    found = {}
    for key, pattern in PATTERNS.items():
        matches = set(re.findall(pattern, content, re.IGNORECASE))
        if matches:
            found[key] = list(matches)
    return found

def build_graph():
    """Scans the repository and builds the knowledge graph."""
    graph = {
        "files": {},
        "principles": defaultdict(list),
        "cycles": defaultdict(list),
        "phases": defaultdict(list)
    }

    print(f"Scanning repository from {os.getcwd()}...")
    
    file_count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(('.md', '.py', '.txt', '.json')):
                filepath = os.path.join(root, file)
                # Skip large files or generated data
                if "data/" in filepath and file.endswith(".json"):
                    continue
                
                matches = scan_file(filepath)
                if matches:
                    graph["files"][filepath] = matches
                    
                    # Invert index
                    if "PRINCIPLE" in matches:
                        for p in matches["PRINCIPLE"]:
                            graph["principles"][p.upper()].append(filepath)
                    if "CYCLE" in matches:
                        for c in matches["CYCLE"]:
                            graph["cycles"][c].append(filepath)
                    if "PHASE" in matches:
                        for p in matches["PHASE"]:
                            graph["phases"][p].append(filepath)
                
                file_count += 1
                if file_count % 1000 == 0:
                    print(f"Scanned {file_count} files...")

    print(f"Scan complete. Found {len(graph['principles'])} principles, {len(graph['cycles'])} cycles.")
    
    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge Graph written to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_graph()
