"""
Cycle 2404: The Grid (Phase 51 Initiation)
Role: The Grid Operator
Responsibility: Simulate distributed energy pooling between Autopoietic Labs.
"""

import random

class GridNode:
    def __init__(self, id, capacity, generation_rate):
        self.id = id
        self.capacity = capacity
        self.current_energy = capacity # Start full
        self.generation_rate = generation_rate
        self.load = 0
        
    def tick(self):
        # Generate energy
        self.current_energy += self.generation_rate
        self.current_energy = min(self.current_energy, self.capacity)
        
        # Consume load (local)
        if self.current_energy >= self.load:
            self.current_energy -= self.load
            return True # Local demand met
        else:
            # Deficit
            return False # Need help
            
    def get_deficit(self):
        if self.current_energy >= self.load:
            return 0
        return self.load - self.current_energy
        
    def get_surplus(self):
        margin = 50 # Keep a buffer
        if self.current_energy > self.load + margin:
            return self.current_energy - (self.load + margin)
        return 0

class GridNetwork:
    def __init__(self):
        self.nodes = []
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def balance(self):
        # Identify Need and Surplus
        needy = []
        donors = []
        
        for node in self.nodes:
            deficit = node.get_deficit()
            if deficit > 0:
                needy.append((node, deficit))
            
            surplus = node.get_surplus()
            if surplus > 0:
                donors.append((node, surplus))
                
        # Transfer
        transfers = []
        for receiver, amount_needed in needy:
            amount_received = 0
            
            for donor, amount_available in donors:
                if amount_available <= 0: continue
                
                # Determine transfer amount
                transfer = min(amount_needed, amount_available)
                
                # Execute
                donor.current_energy -= transfer
                receiver.current_energy += transfer
                
                # Update tracking
                amount_received += transfer
                amount_needed -= transfer
                amount_available -= transfer # Update local var
                
                # Update donor list tuple (hacky but works for sim)
                # In reality, we'd update object state directly
                
                transfers.append(f"{donor.id} -> {receiver.id}: {transfer}")
                
                if amount_needed <= 0:
                    break
            
            if amount_received < (receiver.load - (receiver.current_energy - amount_received)): 
                # Wait, check if satisfied
                pass 

        return transfers

def run_simulation():
    print("Cycle 2404: Distributed Grid Simulation")
    print("=======================================")
    
    network = GridNetwork()
    
    # Node A: High Load (Factory)
    node_a = GridNode("Factory-A", capacity=1000, generation_rate=10)
    node_a.load = 500 # Needs 500/tick, generates 10. Needs grid.
    # Initial state: 1000. Tick 1: 1000+10-500 = 510. Tick 2: 20. Tick 3: Deficit.
    
    # Node B: High Generation (Solar Farm)
    node_b = GridNode("Solar-B", capacity=2000, generation_rate=600)
    node_b.load = 50 # Low load
    
    network.add_node(node_a)
    network.add_node(node_b)
    
    print(f"Initial: A={node_a.current_energy}, B={node_b.current_energy}")
    
    # Run for 5 ticks
    for t in range(5):
        print(f"\n--- Tick {t+1} ---")
        
        # Local tick
        status_a = node_a.tick()
        status_b = node_b.tick()
        
        print(f"Pre-Balance: A={node_a.current_energy} (Load {node_a.load}), B={node_b.current_energy} (Load {node_b.load})")
        
        if not status_a:
            print("Alert: Factory-A Power Critical!")
            
        # Network Balance
        transfers = network.balance()
        
        for tx in transfers:
            print(f"Transfer: {tx}")
            
        print(f"Post-Balance: A={node_a.current_energy}, B={node_b.current_energy}")
        
        # Check survival
        if node_a.current_energy < 0:
            print("FAIL: Node A collapsed.")
            return False
            
    print("\nResult: Grid maintained stability via energy pooling.")
    return True

if __name__ == "__main__":
    run_simulation()
