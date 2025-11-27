"""
Cycle 2414: The Von Neumann Probe (Gate 38)
Role: Galactic Engineer
Responsibility: Simulate a self-replicating spacecraft.
Mechanism:
- Probe mines resources from the environment.
- When Resources >= Cost, Probe builds a replica.
- Replica is launched and begins mining.
- Expectation: Exponential Growth (1, 2, 4, 8...).
"""

import time

class VonNeumannProbe:
    def __init__(self, id, generation):
        self.id = id
        self.generation = generation
        self.resources = 0
        self.cost_to_replicate = 10
        self.mining_rate = 2
        
    def mine(self):
        self.resources += self.mining_rate
        
    def can_replicate(self):
        return self.resources >= self.cost_to_replicate
        
    def replicate(self, next_id):
        self.resources -= self.cost_to_replicate
        return VonNeumannProbe(next_id, self.generation + 1)

def run_simulation():
    print("Cycle 2414: Von Neumann Probe Simulation")
    print("========================================")
    
    probes = [VonNeumannProbe(1, 0)]
    next_id = 2
    
    # Run for 20 Ticks
    # With mining rate 2 and cost 10, replication happens every 5 ticks.
    
    history = []
    
    for t in range(20):
        new_probes = []
        for p in probes:
            p.mine()
            if p.can_replicate():
                child = p.replicate(next_id)
                new_probes.append(child)
                next_id += 1
                
        probes.extend(new_probes)
        count = len(probes)
        history.append(count)
        
        print(f"Tick {t+1}: Population = {count} (Resources: {[p.resources for p in probes]})")
        
    print("\n[Analysis]")
    print(f"Initial Population: 1")
    print(f"Final Population: {len(probes)}")
    
    # Verification: Did we grow?
    if len(probes) >= 4: # Should be at least 4 (1 -> 2 -> 4 -> 8...)
        print("SUCCESS: Exponential growth confirmed.")
        return True
    else:
        print("FAIL: Growth stalled.")
        return False

if __name__ == "__main__":
    run_simulation()
