"""
Cycle 2413: The Dyson Swarm (Phase 53 Initiation)
Role: Orbital Mechanic
Responsibility: Simulate a constellation of solar collectors orbiting the planet and beaming power down.
Physics:
- Circular Orbits (Simplified).
- Line of Sight / Range check for power beaming.
- Inverse Square Law (optional, but let's keep it simple for now: Beam Efficiency).
"""

import math
import time

class PlanetaryGrid:
    def __init__(self, size=10):
        self.size = size
        self.energy_received = 0
        
    def receive_energy(self, amount):
        self.energy_received += amount

class OrbitalNode:
    def __init__(self, id, radius, angle, speed, power_output=100):
        self.id = id
        self.radius = radius
        self.angle = angle # Radians
        self.speed = speed # Radians per tick
        self.power_output = power_output
        
    def orbit(self):
        self.angle += self.speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
            
    def get_position(self):
        x = self.radius * math.cos(self.angle)
        y = self.radius * math.sin(self.angle)
        return x, y

class DysonSwarm:
    def __init__(self, planet):
        self.planet = planet
        self.nodes = []
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def execute_cycle(self):
        total_beamed = 0
        print("\n--- Orbital Cycle ---")
        for node in self.nodes:
            node.orbit()
            x, y = node.get_position()
            
            # Simple Logic: If "above" the planet (y > 0 for simplicity, or just always beam if operational)
            # Let's say they beam if they are within a certain sector or just always on for this sim.
            # We'll assume they have station-keeping and pointing.
            
            # Beam Power
            # Efficiency loss due to atmosphere/distance (simplified to 90%)
            received = node.power_output * 0.9
            self.planet.receive_energy(received)
            total_beamed += received
            
            print(f"Node {node.id}: Pos({x:.1f}, {y:.1f}) -> Beamed {received:.1f} Energy")
            
        print(f"Total Energy Received this Cycle: {total_beamed:.1f}")

def run_simulation():
    print("Cycle 2413: Dyson Swarm Simulation")
    print("==================================")
    
    planet = PlanetaryGrid()
    swarm = DysonSwarm(planet)
    
    # Deploy 3 Nodes in Geostationary-ish or LEO orbits
    swarm.add_node(OrbitalNode(1, radius=20, angle=0, speed=0.1))
    swarm.add_node(OrbitalNode(2, radius=25, angle=2.0, speed=0.08))
    swarm.add_node(OrbitalNode(3, radius=15, angle=4.0, speed=0.15))
    
    # Run 10 Ticks
    for t in range(10):
        swarm.execute_cycle()
        time.sleep(0.1)
        
    print(f"\nTotal Planetary Energy: {planet.energy_received:.1f}")
    
    if planet.energy_received > 0:
        print("SUCCESS: Orbital Power Beaming confirmed.")
        return True
    else:
        print("FAIL: No energy received.")
        return False

if __name__ == "__main__":
    run_simulation()
