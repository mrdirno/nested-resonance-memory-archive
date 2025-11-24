"""
Cycle 476: The Mirror of Code (Codebase Archaeology)
Role: The Archaeologist
Responsibility: Analyze the fossil record of the code itself.
"""
import os
import ast
import re
import statistics

ARCHIVE_DIR = "archive/experiments"

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
        
    loc = len(content.splitlines())
    classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    
    # Extract Cycle Number
    filename = os.path.basename(filepath)
    match = re.search(r"cycle(\d+)", filename)
    cycle_num = int(match.group(1)) if match else 0
    
    return {
        "cycle": cycle_num,
        "loc": loc,
        "classes": classes,
        "functions": functions,
        "imports": imports
    }

def run_experiment():
    print("Cycle 476: Codebase Archaeology")
    print("===============================")
    
    if not os.path.exists(ARCHIVE_DIR):
        print("Archive not found.")
        return

    files = [os.path.join(ARCHIVE_DIR, f) for f in os.listdir(ARCHIVE_DIR) if f.endswith(".py") and "cycle" in f]
    data = []
    
    for f in files:
        res = analyze_file(f)
        if res:
            data.append(res)
            
    data.sort(key=lambda x: x["cycle"])
    
    if not data:
        print("No data found.")
        return
        
    # Trends
    locs = [d["loc"] for d in data]
    avg_loc = statistics.mean(locs)
    max_loc = max(locs)
    
    print(f"Analyzed {len(data)} files.")
    print(f"Average LOC: {avg_loc:.1f}")
    print(f"Max LOC: {max_loc}")
    
    # Complexity Growth
    first_10 = data[:10]
    last_10 = data[-10:]
    
    avg_loc_start = statistics.mean([d["loc"] for d in first_10]) if first_10 else 0
    avg_loc_end = statistics.mean([d["loc"] for d in last_10]) if last_10 else 0
    
    print(f"Avg LOC (Start): {avg_loc_start:.1f}")
    print(f"Avg LOC (End):   {avg_loc_end:.1f}")
    
    if avg_loc_end > avg_loc_start:
        print("RESULT: Complexity has increased over time.")
    else:
        print("RESULT: Complexity has stabilized or decreased.")

if __name__ == "__main__":
    run_experiment()
