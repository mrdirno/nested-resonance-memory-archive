#!/usr/bin/env python3
"""
Experiment: Cycle 2660 - The Jack
Goal: Simulate mounting agent memory as a virtual filesystem (VFS) interface.
"""

import sys
import json
from pathlib import Path

class MockVFS:
    def __init__(self):
        self.mount_point = "/mnt/helios_memory"
        self.files = {
            "agent_001.json": {"id": "001", "status": "active", "thought": "searching"},
            "agent_002.json": {"id": "002", "status": "dormant", "thought": "sleeping"},
            "sys_config.ini": "MAX_THREADS=10\nDEBUG=TRUE"
        }
        print(f"[VFS] Mounted memory at {self.mount_point}")

    def read_file(self, filename):
        if filename in self.files:
            content = self.files[filename]
            if isinstance(content, dict):
                return json.dumps(content)
            return content
        else:
            raise FileNotFoundError(filename)

    def write_file(self, filename, content):
        print(f"[VFS] Writing to {filename}...")
        # Simulate direct memory injection
        if filename in self.files:
            if filename.endswith(".json"):
                try:
                    self.files[filename] = json.loads(content)
                    print(f"  [OK] Memory updated: {self.files[filename]}")
                except:
                    print("  [ERR] Invalid JSON format.")
            else:
                self.files[filename] = content
                print("  [OK] Config updated.")
        else:
            print("  [ERR] File not found (Permission Denied for new creation).")

def run_jack_test():
    print("Cycle 2660: The Jack - Direct Neural Link")
    
    vfs = MockVFS()
    
    # Read
    print("\n--- READ TEST ---")
    data = vfs.read_file("agent_001.json")
    print(f"READ agent_001.json: {data}")
    
    # Write (Injection)
    print("\n--- WRITE TEST (INJECTION) ---")
    new_thought = json.dumps({"id": "001", "status": "overridden", "thought": "OBEY"})
    vfs.write_file("agent_001.json", new_thought)
    
    # Verify
    print("\n--- VERIFICATION ---")
    check = vfs.read_file("agent_001.json")
    if "OBEY" in check:
        print("SUCCESS: Direct memory override confirmed.")
    else:
        print("FAILURE: Write failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_jack_test()
