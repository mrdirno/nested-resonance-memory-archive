#!/usr/bin/env python3
"""
Experiment: Cycle 2654 - The Edge
Goal: Verify agent behavior at the boundaries of the simulation grid (Torus topology vs Hard Wall).
"""

import sys
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

class BoundedGrid:
    def __init__(self, width=10, height=10, wrap=True):
        self.width = width
        self.height = height
        self.wrap = wrap

    def move(self, x, y, dx, dy):
        new_x = x + dx
        new_y = y + dy
        
        if self.wrap:
            # Torus
            new_x = new_x % self.width
            new_y = new_y % self.height
        else:
            # Wall
            new_x = max(0, min(new_x, self.width - 1))
            new_y = max(0, min(new_y, self.height - 1))
            
        return new_x, new_y

def run_edge_test():
    print("Cycle 2654: The Edge - Boundary Testing")
    
    # Test 1: Hard Wall
    print("\n--- Test 1: Hard Wall ---")
    wall_grid = BoundedGrid(10, 10, wrap=False)
    x, y = 9, 9
    nx, ny = wall_grid.move(x, y, 1, 1)
    print(f"Start(9,9) + (1,1) -> End({nx},{ny})")
    
    if nx == 9 and ny == 9:
        print("SUCCESS: Agent hit the wall and stopped.")
    else:
        print(f"FAILURE: Agent escaped to {nx},{ny}.")
        sys.exit(1)

    # Test 2: Torus Wrap
    print("\n--- Test 2: Torus Wrap ---")
    torus_grid = BoundedGrid(10, 10, wrap=True)
    x, y = 9, 9
    nx, ny = torus_grid.move(x, y, 1, 1)
    print(f"Start(9,9) + (1,1) -> End({nx},{ny})")
    
    if nx == 0 and ny == 0:
        print("SUCCESS: Agent wrapped around to the beginning.")
    else:
        print(f"FAILURE: Wrap logic failed {nx},{ny}.")
        sys.exit(1)

if __name__ == "__main__":
    run_edge_test()
