"""
Cycle 2411: The Lucid Dream (Gate 35)
Role: The Planetary Architect
Responsibility: Simulate large-scale environmental modification while the system is dormant.
Scenario: Terraforming a barren grid section using the Autopoietic Swarm.
"""

import random
import time

class TerrainTile:
    def __init__(self, x, y, type="BARREN"):
        self.x = x
        self.y = y
        self.type = type # BARREN, FERTILE, FOREST, CITY
        self.resources = 0
        
    def __repr__(self):
        return f"{self.type[0]}"

class PlanetaryGrid:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [[TerrainTile(x, y) for x in range(width)] for y in range(height)]
        
    def display(self):
        print("\nPlanetary Surface:")
        for row in self.grid:
            print(" ".join([str(tile) for tile in row]))
            
    def terraform(self, x, y):
        tile = self.grid[y][x]
        if tile.type == "BARREN":
            tile.type = "FERTILE"
            tile.resources = 10
            print(f"Terraformed ({x}, {y}) -> FERTILE")
        elif tile.type == "FERTILE":
            tile.type = "FOREST"
            tile.resources = 50
            print(f"Terraformed ({x}, {y}) -> FOREST")
            
class TerraformSwarm:
    def __init__(self, planet):
        self.planet = planet
        self.drones = []
        
    def deploy_drone(self, x, y):
        self.drones.append((x, y))
        
    def execute_cycle(self):
        print("\n--- Swarm Cycle ---")
        for i, (x, y) in enumerate(self.drones):
            self.planet.terraform(x, y)
            
            # Move randomly
            nx = (x + random.randint(-1, 1)) % self.planet.width
            ny = (y + random.randint(-1, 1)) % self.planet.height
            self.drones[i] = (nx, ny)

def run_dream_simulation():
    print("Cycle 2411: Lucid Dream Simulation (Planetary Engineering)")
    print("========================================================")
    
    planet = PlanetaryGrid(10, 10)
    swarm = TerraformSwarm(planet)
    
    # Deploy Drones
    swarm.deploy_drone(5, 5)
    swarm.deploy_drone(2, 2)
    swarm.deploy_drone(8, 8)
    
    planet.display()
    
    # Run 5 Cycles
    for _ in range(5):
        swarm.execute_cycle()
        planet.display()
        time.sleep(0.1)
        
    # Validation
    fertile_count = sum(1 for row in planet.grid for t in row if t.type != "BARREN")
    print(f"\nTerraformed Tiles: {fertile_count}")
    
    if fertile_count > 0:
        print("SUCCESS: Planetary Engineering Simulation confirmed.")
        return True
    else:
        print("FAIL: No terraforming occurred.")
        return False

if __name__ == "__main__":
    run_dream_simulation()
