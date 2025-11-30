#!/usr/bin/env python3
"""
Experiment: Cycle 2676 - The Compiler
Goal: Validate Python syntax of generated/edited code.
"""

import sys
import py_compile
from pathlib import Path

def validate_syntax(path):
    print(f"Cycle 2676: The Compiler - Checking {path}")
    
    try:
        py_compile.compile(path, doraise=True)
        print("  [OK] Syntax Valid.")
        return True
    except py_compile.PyCompileError as e:
        print(f"  [ERR] Syntax Error: {e}")
        return False

def run_compiler_test():
    # 1. Valid Script
    valid_path = Path("experiments/valid_test.py")
    with open(valid_path, "w") as f:
        f.write("x = 10\nprint(x)")
    
    if not validate_syntax(valid_path):
        print("FAILURE: Valid script rejected.")
        sys.exit(1)
        
    # 2. Invalid Script
    invalid_path = Path("experiments/invalid_test.py")
    with open(invalid_path, "w") as f:
        f.write("x = 10\nprint(x") # Missing paren
        
    if validate_syntax(invalid_path):
        print("FAILURE: Invalid script accepted.")
        sys.exit(1)
    else:
        print("SUCCESS: Compiler correctly identified errors.")
        
    # Cleanup
    valid_path.unlink()
    invalid_path.unlink()

if __name__ == "__main__":
    run_compiler_test()
