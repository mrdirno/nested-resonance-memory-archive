#!/usr/bin/env python3
"""
Experiment: Cycle 2636 - The Grid
Goal: Implement a persistent 2D grid map for agents to inhabit and modify.
"""

import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

class PersistentGrid:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = [[0.0 for _ in range(width)] for _ in range(height)] # 0.0 = Empty, >0 = Pheromone

    def update_cell(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = value
            
    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def decay(self, rate=0.9):
        """Simulate evaporation of traces."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] *= rate
                if self.grid[y][x] < 0.01:
                    self.grid[y][x] = 0.0

    def render(self):
        print("-" * (self.width + 2))
        for row in self.grid:
            line = "|"
            for cell in row:
                if cell > 0.8: line += "#"
                elif cell > 0.5: line += "+"
                elif cell > 0.2: line += "."
                else: line += " "
            line += "|"
            print(line)
        print("-" * (self.width + 2))

def run_grid_test():
    print("Cycle 2636: The Grid - Persistence Test")
    
    world = PersistentGrid(width=10, height=5)
    
    print("Initial State:")
    world.render()
    
    print("\nAgent Action: Depositing Pheromone Trail...")
    # Simulate agent moving (0,0) -> (4,4)
    for i in range(5):
        world.update_cell(i, i, 1.0)
        
    world.render()
    
    print("\nTime Passing (Decay)...")
    for _ in range(3):
        world.decay(0.8)
        
    world.render()
    
    if world.get_cell(4, 4) > 0.0:
        print("SUCCESS: Grid retained state modifications.")
    else:
        print("FAILURE: State lost.")
        sys.exit(1)

if __name__ == "__main__":
    run_grid_test()
