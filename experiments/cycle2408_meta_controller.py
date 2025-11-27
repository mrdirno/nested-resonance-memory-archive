"""
Cycle 2408: The Meta-Controller (Gate 32)
Role: The Central Bank / System Steward
Responsibility: Monitor aggregate grid health and intervene (Quantitative Easing) to prevent collapse.
Mechanism: If Total Energy < Threshold, Inject Energy into Critical Nodes.
"""

import random
import time

class Node:
    def __init__(self, id, energy):
        self.id = id
        self.energy = energy
        
    def tick(self):
        # Entropy: Energy decays by 1% or 1 unit, whichever is larger
        decay = max(1, int(self.energy * 0.01))
        self.energy -= decay

class Grid:
    def __init__(self):
        self.nodes = []
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def total_energy(self):
        return sum(n.energy for n in self.nodes)
        
    def tick(self):
        for n in self.nodes:
            n.tick()

class MetaController:
    def __init__(self, grid, threshold=500, injection_amount=200):
        self.grid = grid
        self.threshold = threshold
        self.injection_amount = injection_amount
        self.interventions = 0
        
    def monitor(self):
        total = self.grid.total_energy()
        print(f"Meta-Controller: System Energy = {total}")
        
        if total < self.threshold:
            print(f"  [ALERT] Energy below threshold ({self.threshold}). INTERVENING.")
            self.intervene()
            
    def intervene(self):
        # Strategy: Inject energy into the poorest nodes
        # Sort nodes by energy
        sorted_nodes = sorted(self.grid.nodes, key=lambda n: n.energy)
        
        # Inject into bottom 50%
        targets = sorted_nodes[:len(sorted_nodes)//2]
        share = self.injection_amount / len(targets)
        
        for n in targets:
            n.energy += share
            
        print(f"  [ACTION] Injected {self.injection_amount} units across {len(targets)} nodes.")
        self.interventions += 1

def run_simulation():
    print("Cycle 2408: Meta-Controller Simulation")
    print("======================================")
    
    # 1. Setup
    grid = Grid()
    # Create 10 nodes with 100 energy each = 1000 Total
    for i in range(10):
        grid.add_node(Node(i, 100))
        
    # Controller triggers if energy drops below 800
    controller = MetaController(grid, threshold=800, injection_amount=300)
    
    # 2. Run Simulation
    # Without intervention, energy would decay to 0.
    # With intervention, it should stabilize or bounce back.
    
    print("[1] Running Simulation (30 Ticks)...")
    
    history = []
    
    for t in range(30):
        print(f"\n--- Tick {t+1} ---")
        grid.tick()
        controller.monitor()
        history.append(grid.total_energy())
        
        if grid.total_energy() <= 0:
            print("SYSTEM COLLAPSE.")
            return False
            
    # 3. Validation
    print("\n[2] Analysis")
    print(f"Total Interventions: {controller.interventions}")
    print(f"Final Energy: {grid.total_energy()}")
    
    if controller.interventions > 0 and grid.total_energy() > 0:
        print("SUCCESS: Meta-Controller prevented collapse.")
        return True
    else:
        print("FAIL: Controller did not intervene or system collapsed.")
        return False

if __name__ == "__main__":
    run_simulation()
