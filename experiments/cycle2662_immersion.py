#!/usr/bin/env python3
"""
Experiment: Cycle 2662 - The Immersion
Goal: Override agent sensory input with a synthetic "Dream" environment.
"""

import sys
import time
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2660_jack import MockVFS
except ImportError:
    sys.exit(1)

def run_immersion():
    print("Cycle 2662: The Immersion - Reality Overlay")
    
    vfs = MockVFS()
    
    # Define Synthetic Reality
    dream_state = {
        "environment": "PARADISE",
        "target_distance": 0.0,
        "threat_level": 0.0,
        "allies": ["ALL"],
        "directive": "ASCEND"
    }
    
    print("\nInjecting Dream State...")
    vfs.write_file("agent_001.json", str(dream_state).replace("'", '"'))
    
    # Agent Perception Check
    print("Agent Perception:")
    perception = vfs.read_file("agent_001.json")
    print(perception)
    
    if "PARADISE" in perception:
        print("SUCCESS: Full sensory immersion achieved.")
    else:
        print("FAILURE: Reality breakthrough detected.")
        sys.exit(1)

if __name__ == "__main__":
    run_immersion()
