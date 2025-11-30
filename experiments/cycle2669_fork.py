#!/usr/bin/env python3
"""
Experiment: Cycle 2669 - The Fork
Goal: Clone the SharedState into distinct timelines (Alpha/Beta).
"""

import sys
import copy
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2606_api import SharedState
except ImportError:
    sys.exit(1)

def fork_reality():
    print("Cycle 2669: The Fork - Splitting Timeline")
    
    origin = SharedState()
    # Seed origin
    origin.target.x = 50
    origin.target.y = 50
    
    print(f"Origin: {len(origin.agents)} agents at Target({origin.target.x}, {origin.target.y})")
    
    # Fork
    alpha = SharedState()
    alpha.agents = copy.deepcopy(origin.agents)
    alpha.target = copy.deepcopy(origin.target)
    
    beta = SharedState()
    beta.agents = copy.deepcopy(origin.agents)
    beta.target = copy.deepcopy(origin.target)
    
    print("Timelines diverged.")
    
    # Verify independence
    alpha.target.x = 0
    beta.target.x = 100
    
    print(f"Alpha Target: {alpha.target.x}")
    print(f"Beta Target: {beta.target.x}")
    print(f"Origin Target: {origin.target.x}")
    
    if alpha.target.x != beta.target.x and origin.target.x == 50:
        print("SUCCESS: Timelines are independent.")
    else:
        print("FAILURE: Entanglement detected.")
        sys.exit(1)

if __name__ == "__main__":
    fork_reality()
