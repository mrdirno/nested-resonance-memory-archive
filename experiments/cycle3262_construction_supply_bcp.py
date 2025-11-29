import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3262: MATERIAL SUPPLY CHAIN BCP
# -----------------------------------------------------------------------------
# Domain: Construction
# Goal: Ensure material availability.
# Hypothesis: BCP (Buffer Management) prevents delays vs Just-in-Time.
# -----------------------------------------------------------------------------

class Site:
    def __init__(self, policy):
        self.policy = policy
        self.cement = 100
        self.delays = 0
        
    def tick(self):
        # Consumption
        usage = int(random.gauss(10, 2))
        if self.cement >= usage:
            self.cement -= usage
        else:
            self.delays += 1 # Work stops
            
        # Reorder
        if self.policy == 'JIT':
            target = 20
        else: # BCP
            target = 50 # Buffer
            
        if self.cement < target:
            # Lead time varies
            lt = 2
            if random.random() < 0.1: lt = 10 # Disruption
            
            # Order arrives in lt ticks (Simulated by instant add for simplicity,
            # but actually we need to queue orders. Simplified here: 
            # If we order, we get it later.
            pass # To implement properly requires order queue. 
            
            # Simplified: Just check probability of stockout based on buffer size
            # With buffer 20, stockout prob is higher than buffer 50 given variance.
            
            # Let's model "Time to Survive Disruption"
            # JIT (20) survives 2 days. Disruption is 10 days. -> 8 days delay.
            # BCP (50) survives 5 days. Disruption is 10 days. -> 5 days delay.
            
            pass

# Re-implementing with explicit simulation for accuracy
class SiteSim:
    def __init__(self, policy):
        self.policy = policy
        self.stock = 100
        self.orders = []
        self.delays = 0
        
    def tick(self, t):
        # Receive
        arrived = [o for o in self.orders if o[0] <= t]
        for o in arrived:
            self.stock += o[1]
            self.orders.remove(o)
            
        # Consume
        usage = 10 + int(random.gauss(0, 2))
        if self.stock >= usage:
            self.stock -= usage
        else:
            self.delays += 1
            self.stock = 0
            
        # Order
        threshold = 20 if self.policy == 'JIT' else 50
        if self.stock < threshold:
            amount = threshold - self.stock + 20 # Top up
            # Lead time
            lt = 2
            if random.random() < 0.05: lt = 10
            self.orders.append((t + lt, amount))

def run_simulation(policy, steps=1000):
    site = SiteSim(policy)
    for t in range(steps):
        site.tick(t)
    return site.delays

def main():
    print("======================================================================")
    print("CYCLE 3262: MATERIAL SUPPLY CHAIN BCP")
    print("======================================================================")
    
    steps = 2000
    
    jit_delay = run_simulation('JIT', steps)
    print(f"JIT Delays: {jit_delay}")
    
    bcp_delay = run_simulation('BCP', steps)
    print(f"BCP Delays: {bcp_delay}")
    
    improvement = ((jit_delay - bcp_delay) / jit_delay) * 100
    print("-" * 60)
    print(f"Delay Improvement: {improvement:.2f}%")
    
    if bcp_delay < jit_delay:
        print("RESULT: SUCCESS. Buffers absorbed variability.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3262_construction_supply.json", "w") as f:
        json.dump({"jit": jit_delay, "bcp": bcp_delay, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
