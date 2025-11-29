import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3241: WASTE COLLECTION ROUTING BCP
# -----------------------------------------------------------------------------
# Domain: Smart Cities
# Goal: Optimize garbage truck routing.
# Hypothesis: BCP (Fill-Level Prediction) outperforms Static Schedule.
# -----------------------------------------------------------------------------

class Bin:
    def __init__(self, id):
        self.id = id
        self.fill_level = 0.0
        self.fill_rate = random.uniform(0.05, 0.2)
        self.overflow = 0
        
    def tick(self):
        self.fill_level += self.fill_rate + random.gauss(0, 0.01)
        if self.fill_level > 1.0:
            self.overflow += (self.fill_level - 1.0)
            self.fill_level = 1.0
            
    def empty(self):
        self.fill_level = 0.0

class Truck:
    def __init__(self):
        self.capacity = 5.0
        self.load = 0.0
        self.route = []
        self.pos = 0 # index in route
        
    def visit(self, bin_obj):
        amount = bin_obj.fill_level
        if self.load + amount <= self.capacity:
            self.load += amount
            bin_obj.empty()
            return True
        return False # Truck full

class Manager:
    def route(self, bins, truck):
        raise NotImplementedError

class StaticManager(Manager):
    def route(self, bins, truck):
        # Visit everyone in order, every time
        truck.route = list(range(len(bins)))

class BCPManager(Manager):
    def __init__(self, bins):
        # Track fill rates (Learning)
        self.estimates = {b.id: {"level": 0.0, "rate": 0.1} for b in bins}
        
    def route(self, bins, truck):
        # 1. Predict Levels
        targets = []
        for b in bins:
            # Update estimate
            est = self.estimates[b.id]
            est["level"] += est["rate"]
            
            # If predicted > 0.8, add to route
            if est["level"] > 0.8:
                targets.append(b.id)
                
        # Sort by level (Urgency)
        targets.sort(key=lambda id: self.estimates[id]["level"], reverse=True)
        truck.route = targets
        
    def feedback(self, bin_id, actual_level):
        # Update Kalman-lite
        est = self.estimates[bin_id]
        error = actual_level - est["level"]
        est["level"] = actual_level # Reset to truth
        est["rate"] += 0.1 * error # Adjust rate estimate

def run_simulation(manager_cls, steps=1000):
    bins = [Bin(i) for i in range(20)]
    truck = Truck()
    
    if manager_cls == BCPManager:
        manager = BCPManager(bins)
    else:
        manager = StaticManager()
        
    total_overflow = 0
    total_distance = 0 # Cost of travel
    
    for t in range(steps):
        for b in bins: b.tick()
        
        # Daily Route (once every 10 ticks)
        if t % 10 == 0:
            manager.route(bins, truck)
            
            # Execute Route
            visited_count = 0
            truck.load = 0
            for bin_id in truck.route:
                b = bins[bin_id]
                visited_count += 1
                if truck.visit(b):
                    if isinstance(manager, BCPManager):
                        manager.feedback(b.id, 0.0) # Just emptied
                else:
                    # Truck full, stop route
                    break
            
            total_distance += visited_count
            
        total_overflow += sum(b.overflow for b in bins)
        
    # Metric: Total Cost = Distance + (Overflow * 10)
    return total_distance + (total_overflow * 10)

def main():
    print("======================================================================")
    print("CYCLE 3241: WASTE COLLECTION ROUTING BCP")
    print("======================================================================")
    
    steps = 2000
    
    static_cost = run_simulation(StaticManager, steps)
    print(f"Static Cost: {static_cost:.2f}")
    
    bcp_cost = run_simulation(BCPManager, steps)
    print(f"BCP Cost:    {bcp_cost:.2f}")
    
    improvement = ((static_cost - bcp_cost) / static_cost) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_cost < static_cost:
        print("RESULT: SUCCESS. Predictive routing saved distance and overflow.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3241_waste_routing.json", "w") as f:
        json.dump({"static": static_cost, "bcp": bcp_cost, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
