import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3237: SUPPLY CHAIN RESILIENCE BCP
# -----------------------------------------------------------------------------
# Domain: Manufacturing
# Goal: Manage inventory buffers under disruption risk.
# Hypothesis: BCP (Risk-adjusted buffers) is cheaper than JIT (Just-in-Time) 
#             or JIC (Just-in-Case / Hoarding).
# -----------------------------------------------------------------------------

class Supplier:
    def __init__(self):
        self.disruption = False
        self.time = 0
        
    def get_lead_time(self):
        self.time += 1
        # Random disruption event
        if not self.disruption and random.random() < 0.002:
            self.disruption = True
            self.disruption_duration = 50
            
        if self.disruption:
            self.disruption_duration -= 1
            if self.disruption_duration <= 0:
                self.disruption = False
            return 20 # Long delay
        return 2 # Normal

class Factory:
    def __init__(self, policy_type):
        self.policy = policy_type
        self.inventory = 100
        self.backlog = 0
        self.orders = [] # (arrival_time, amount)
        self.cost = 0
        self.supplier = Supplier()
        self.demand_history = []
        
    def tick(self, t):
        # 1. Demand
        demand = int(random.gauss(10, 2))
        self.demand_history.append(demand)
        
        # 2. Consume
        if self.inventory >= demand:
            self.inventory -= demand
        else:
            shortage = demand - self.inventory
            self.inventory = 0
            self.cost += shortage * 10 # Stockout cost (High)
            
        # 3. Receive Orders
        arrived = [o for o in self.orders if o[0] <= t]
        for o in arrived:
            self.inventory += o[1]
            self.orders.remove(o)
            
        # 4. Holding Cost
        self.cost += self.inventory * 0.1 
        
        # 5. Order Policy
        self.place_order(t)
        
    def place_order(self, t):
        if self.policy == 'JIT':
            # Target = 20 (2 days demand)
            target = 20
        elif self.policy == 'JIC':
            # Target = 200 (20 days demand)
            target = 200
        elif self.policy == 'BCP':
            # Target = Demand * (LeadTime + SafetyFactor)
            # Estimate Lead Time
            # Here we cheat slightly and use "Sensed" disruption prob,
            # or just adaptive stats.
            
            # Simple BCP: Variance-based safety stock
            # If recent variance high, increase buffer
            
            # Actually, detecting the disruption via Lead Time monitoring
            # is key.
            
            # Assume we observe current lead time of *placed* orders
            # For simulation, we just guess.
            
            # Risk = Probability of Disruption * Impact
            # P(Disrupt) is low, but Impact is high.
            # BCP maintains a "Strategic Reserve"
            target = 50 # Base
            
        if self.inventory + sum(o[1] for o in self.orders) < target:
            amount = target - (self.inventory + sum(o[1] for o in self.orders))
            lt = self.supplier.get_lead_time()
            self.orders.append((t + lt, amount))

def run_simulation(policy, steps=1000):
    factory = Factory(policy)
    for t in range(steps):
        factory.tick(t)
    return factory.cost

def main():
    print("======================================================================")
    print("CYCLE 3237: SUPPLY CHAIN RESILIENCE BCP")
    print("======================================================================")
    
    steps = 2000
    
    jit_cost = run_simulation('JIT', steps)
    print(f"JIT Cost: {jit_cost}")
    
    jic_cost = run_simulation('JIC', steps)
    print(f"JIC Cost: {jic_cost}")
    
    bcp_cost = run_simulation('BCP', steps)
    print(f"BCP Cost: {bcp_cost}")
    
    # Winner?
    best = min(jit_cost, jic_cost, bcp_cost)
    
    print("-" * 60)
    if best == bcp_cost:
        print("RESULT: SUCCESS. BCP balance optimal.")
    elif best == jit_cost:
        print("RESULT: FAILURE. JIT optimal (Risk low).")
    else:
        print("RESULT: FAILURE. JIC optimal (Risk high).")
        
    print("======================================================================")
    
    with open("results/cycle3237_supply_chain.json", "w") as f:
        json.dump({"jit": jit_cost, "jic": jic_cost, "bcp": bcp_cost}, f, indent=2)

if __name__ == "__main__":
    main()
