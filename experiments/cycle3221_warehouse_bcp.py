import random
import math
import numpy as np

# ======================================================================
# CYCLE 3221: WAREHOUSE LOCATION AS BCP
# ======================================================================
# Hypothesis: Facility location is a BCP allocation.
#   V(loc) = Demand_Coverage - lambda(Capital) * Cost(Rent/Ops)
#   High lambda (Scarcity) -> Centralize (Few, cheap hubs).
#   Low lambda (Abundance) -> Decentralize (Many local hubs).
# ======================================================================

def run_experiment():
    print("CYCLE 3221: Warehouse Location as BCP")
    
    # Map 100x100
    # Demand Clusters
    customers = []
    for _ in range(1000):
        # 3 Cities
        center = random.choice([(20,20), (80,20), (50,80)])
        x = center[0] + random.gauss(0, 10)
        y = center[1] + random.gauss(0, 10)
        customers.append((x,y))
        
    # Candidates (Grid)
    candidates = [(x,y) for x in range(0,101,10) for y in range(0,101,10)]
    
    # Parameters
    rent_cost = 1000.0 # Per warehouse
    transport_cost = 0.1 # Per unit distance
    
    # Scenarios: Scarcity vs Abundance
    budgets = [5000, 20000]
    
    results = {}
    
    for B in budgets:
        lamb = 10000.0 / (100.0 + B) # Scarcity pressure
        
        # Select Warehouses using BCP
        # Iterative Greedy: Add warehouse that maximizes V
        
        warehouses = []
        remaining_budget = B
        
        while True:
            best_v = -float('inf')
            best_loc = None
            
            # Evaluate candidates
            for loc in candidates:
                if loc in warehouses: continue
                if rent_cost > remaining_budget: continue
                
                # Gain: Reduction in Total Transport Cost
                # Baseline transport cost (if no new warehouse)
                # If 0 warehouses, cost is huge (outsourced penalty)
                current_cost = 0
                new_cost = 0
                
                for c in customers:
                    # Distance to nearest existing
                    dist_existing = min([math.hypot(c[0]-w[0], c[1]-w[1]) for w in warehouses]) if warehouses else 1000
                    dist_new = math.hypot(c[0]-loc[0], c[1]-loc[1])
                    
                    current_cost += min(dist_existing, 1000) * transport_cost
                    new_cost += min(dist_existing, dist_new) * transport_cost
                    
                gain = current_cost - new_cost
                
                # Cost: Rent
                cost = rent_cost
                
                # V = Gain - lambda * Cost
                v = gain - lamb * cost
                
                if v > best_v:
                    best_v = v
                    best_loc = loc
            
            if best_v > 0 and best_loc:
                warehouses.append(best_loc)
                remaining_budget -= rent_cost
            else:
                break
                
        # Evaluate Performance
        total_dist = 0
        for c in customers:
            d = min([math.hypot(c[0]-w[0], c[1]-w[1]) for w in warehouses]) if warehouses else 1000
            total_dist += d
            
        avg_dist = total_dist / len(customers)
        results[B] = {"n": len(warehouses), "avg_dist": avg_dist}
        print(f"Budget {B}: {len(warehouses)} Warehouses, Avg Dist {avg_dist:.2f}")

    # Analysis
    # Scarcity (5000) should have FEWER warehouses, HIGHER dist.
    # Abundance (20000) should have MORE warehouses, LOWER dist.
    
    res_scarce = results[5000]
    res_abund = results[20000]
    
    if res_scarce["n"] < res_abund["n"] and res_scarce["avg_dist"] > res_abund["avg_dist"]:
        print("VERIFIED: BCP adapts topology to budget.")
        return True
    else:
        print("FAILED: Topology did not adapt correctly.")
        return False

if __name__ == "__main__":
    run_experiment()
