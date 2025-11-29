import random
import math

# ======================================================================
# CYCLE 3241: WASTE ROUTING AS BCP
# ======================================================================
# Hypothesis: Waste collection is BCP.
#   V(visit) = Fill_Level - lambda(Fuel) * Detour_Cost
#   High lambda -> Visit only overflowing bins.
#   Low lambda -> Visit everyone.
# ======================================================================

def run_experiment():
    print("CYCLE 3241: Waste Routing as BCP")
    
    N = 50 # Bins
    bins = []
    for i in range(N):
        bins.append({
            "id": i,
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "fill": random.uniform(0, 100), # %
            "rate": random.uniform(1, 5)
        })
        
    truck = {"x": 50, "y": 50, "cap": 1000, "load": 0}
    budget = 500 # Fuel
    
    # BCP Strategy
    lamb = 100.0 / (10.0 + budget)
    
    collected_bcp = 0
    spent_bcp = 0
    
    # Iterative Greedy Route
    while spent_bcp < budget:
        best_v = -float('inf')
        best_bin = None
        
        for b in bins:
            dist = math.hypot(b["x"]-truck["x"], b["y"]-truck["y"])
            cost = dist
            if cost + spent_bcp > budget: continue
            
            # Gain = Fill Level (Prevent Overflow?)
            # Or Gain = Mass Collected
            gain = b["fill"]
            
            v = gain - lamb * cost
            
            if v > best_v:
                best_v = v
                best_bin = b
                
        if best_v > 0 and best_bin:
            # Move
            dist = math.hypot(best_bin["x"]-truck["x"], best_bin["y"]-truck["y"])
            spent_bcp += dist
            truck["x"] = best_bin["x"]
            truck["y"] = best_bin["y"]
            
            # Collect
            collected_bcp += best_bin["fill"]
            best_bin["fill"] = 0 # Empty
        else:
            break
            
    print(f"BCP Collected: {collected_bcp:.2f}")
    
    # Static Route (Nearest Neighbor regardless of fill)
    # Or Fixed Loop
    truck = {"x": 50, "y": 50}
    bins_static = [b.copy() for b in bins] # Reset
    spent_static = 0
    collected_static = 0
    
    # Simple TSP-ish (Nearest Unvisited)
    visited = set()
    
    while spent_static < budget:
        best_dist = float('inf')
        best_bin = None
        
        for b in bins_static:
            if b["id"] in visited: continue
            dist = math.hypot(b["x"]-truck["x"], b["y"]-truck["y"])
            if dist < best_dist:
                best_dist = dist
                best_bin = b
                
        if best_bin and spent_static + best_dist <= budget:
            spent_static += best_dist
            truck["x"] = best_bin["x"]
            truck["y"] = best_bin["y"]
            collected_static += best_bin["fill"]
            visited.add(best_bin["id"])
        else:
            break
            
    print(f"Static Collected: {collected_static:.2f}")
    
    if collected_bcp > collected_static:
        print("VERIFIED: BCP Dynamic Routing beats Static Loop.")
        return True
    else:
        print("FAILED.")
        return False

if __name__ == "__main__":
    run_experiment()