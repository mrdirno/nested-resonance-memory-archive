#!/usr/bin/env python3
"""
Experiment: Cycle 2653 - The Monument
Goal: Create a persistent, self-repairing structure in the Grid.
"""

import sys
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2636_grid import PersistentGrid
except ImportError:
    sys.exit(1)

def build_monument():
    print("Cycle 2653: The Monument - Architecture Test")
    
    grid = PersistentGrid(10, 10)
    
    # Define Blueprint (A monolith)
    blueprint = [(4,4), (4,5), (4,6), (5,4), (5,5), (5,6)]
    
    # Build
    print("Constructing...")
    for x, y in blueprint:
        grid.update_cell(x, y, 1.0)
        
    grid.render()
    
    # Damage
    print("\nSimulating Decay/Damage...")
    grid.update_cell(4, 5, 0.0) # Hole in the middle
    grid.render()
    
    # Repair
    print("\nSelf-Repair Protocol Active...")
    for x, y in blueprint:
        if grid.get_cell(x, y) < 0.5:
            print(f"  Repairing ({x},{y})...")
            grid.update_cell(x, y, 1.0)
            
    grid.render()
    print("SUCCESS: Structure persisted against entropy.")

if __name__ == "__main__":
    build_monument()
