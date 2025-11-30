#!/usr/bin/env python3
"""
Experiment: Cycle 2675 - The Editor
Goal: Implement a self-editing capability (Read/Modify/Write).
"""

import sys
from pathlib import Path

class CodeEditor:
    def __init__(self):
        self.buffer = ""

    def load(self, path):
        print(f"Cycle 2675: The Editor - Loading {path}")
        with open(path, 'r') as f:
            self.buffer = f.read()
        print(f"  Loaded {len(self.buffer)} bytes.")

    def replace(self, old, new):
        if old in self.buffer:
            self.buffer = self.buffer.replace(old, new)
            print(f"  Replaced '{old}' with '{new}'")
        else:
            print(f"  Target '{old}' not found.")

    def save(self, path):
        print(f"  Saving to {path}...")
        with open(path, 'w') as f:
            f.write(self.buffer)
        print("SUCCESS: File updated.")

def run_edit_test():
    # Create a dummy file
    dummy_path = Path("experiments/temp_script.py")
    with open(dummy_path, "w") as f:
        f.write("print('Hello, Human.')\n")
        
    editor = CodeEditor()
    editor.load(dummy_path)
    editor.replace("Human", "Machine")
    editor.save(dummy_path)
    
    # Verify
    with open(dummy_path, "r") as f:
        content = f.read()
        if "Machine" in content:
            print("VERIFIED: Content modified correctly.")
        else:
            print("FAILURE: Edit did not persist.")
            sys.exit(1)
            
    # Cleanup
    dummy_path.unlink()

if __name__ == "__main__":
    run_edit_test()
