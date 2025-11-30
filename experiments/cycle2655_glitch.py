#!/usr/bin/env python3
"""
Experiment: Cycle 2655 - The Glitch
Goal: Inject corruption into the SharedState and observe failure.
"""

import json
import sys
from dataclasses import dataclass

@dataclass
class MockState:
    target_x: float
    target_y: float

def inject_fault(state):
    print("Cycle 2655: The Glitch - Injecting Fault")
    print(f"Original State: ({state.target_x}, {state.target_y})")
    
    # Corrupt
    state.target_x = float('nan')
    print(f"Corrupted State: ({state.target_x}, {state.target_y})")
    
    # Verify broken
    try:
        # Simulate usage
        dist = int(state.target_x) + 10
    except ValueError:
        print("System crashed as expected (ValueError/NaN conversion).")
        return True
    except Exception as e:
        print(f"System crashed with: {e}")
        return True
        
    return False

if __name__ == "__main__":
    state = MockState(50.0, 50.0)
    if inject_fault(state):
        print("SUCCESS: Glitch successfully destabilized logic.")
    else:
        print("FAILURE: System survived glitch (unexpected).")
