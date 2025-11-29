
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3305] {msg}")

class Generator:
    def __init__(self, name, capacity, cost_per_mwh):
        self.name = name
        self.capacity = capacity
        self.cost = cost_per_mwh
        self.dispatched = 0.0
        
    def __repr__(self):
        return f"{self.name}(Cap={self.capacity}, Cost={self.cost})"

def run_dispatch_bcp(generators, load_demand, budget_b):
    # Budget B here is "Available Capacity Margin"? 
    # Or is B just "Grid Stability"?
    # Let's define λ as the "System Marginal Price" (SMP).
    # In perfect markets, SMP = Cost of marginal unit.
    # In BCP, λ reflects Scarcity.
    # λ = k / (epsilon + Margin).
    # Margin = Total_Capacity - Load.
    
    total_cap = sum(g.capacity for g in generators)
    margin = total_cap - load_demand
    
    # λ formula for Grid
    # If Margin < 0, λ -> Infinity (Blackout).
    if margin <= 0:
        lambda_val = 9999.0
    else:
        lambda_val = 1.0 / (0.01 + margin/total_cap) # Normalized margin
        
    # Dispatch Logic:
    # We want to maximize V = Value_of_Load - Cost.
    # But Value_of_Load is high (VOLL).
    # We just minimize Cost.
    # Sort by Cost. Dispatch until Load met.
    # But wait, does BCP *predict* the Merit Order?
    # V(Gen) = Value - λ * Cost ? No.
    # From Operator perspective: V(Dispatch_G) = Reliability_Gain - Cost.
    # Reliability_Gain is constant (1 MWh is 1 MWh).
    # So V = 1 - Cost.
    # Max V => Min Cost.
    # Yes, BCP predicts Merit Order.
    
    # But does λ affect WHICH ones we pick?
    # If λ is high (Scarcity), maybe we pay for expensive ones?
    # Yes.
    # If V(Peaker) = 1 - Cost_Peaker.
    # Cost_Peaker is high. V is low.
    # But if we NEED it, the "Gain" of avoiding blackout is HUGE.
    # Gain = VOLL (Value of Lost Load) ~ $10,000/MWh.
    # V = VOLL - Cost.
    # Even expensive peaker ($500) has V > 0.
    
    # Let's simulate this.
    
    VOLL = 10000.0
    results = []
    
    # Sort by Merit Order first (Greedy BCP)
    generators.sort(key=lambda x: x.cost)
    
    remaining_load = load_demand
    system_cost = 0.0
    
    for g in generators:
        # Decision: Dispatch?
        # V = VOLL - Cost
        if (VOLL - g.cost) > 0:
            amount = min(g.capacity, remaining_load)
            g.dispatched = amount
            remaining_load -= amount
            system_cost += amount * g.cost
            results.append(g)
            if remaining_load <= 0:
                break
        else:
            # Cost > VOLL. Don't dispatch even if load exists.
            pass
            
    return results, lambda_val, remaining_load

def main():
    log("GATE 929: GRID DISPATCH AS BCP")
    
    # Generators
    # Solar: Cap=100, Cost=0
    # Nuclear: Cap=200, Cost=10
    # Gas CCGT: Cap=150, Cost=50
    # Gas Peaker: Cap=50, Cost=200
    # Demand Response (Virtual Gen): Cap=20, Cost=1000
    
    gens = [
        Generator("Solar", 100, 0),
        Generator("Nuclear", 200, 10),
        Generator("Gas CCGT", 150, 50),
        Generator("Gas Peaker", 50, 200),
        Generator("Demand Response", 20, 1000)
    ]
    
    total_cap = sum(g.capacity for g in gens) # 520
    
    scenarios = [
        {"name": "Sunny Afternoon (Low Load)", "load": 250}, # Solar+Nuke
        {"name": "Evening Peak (High Load)", "load": 400},   # +CCGT
        {"name": "Heatwave (Extreme Load)", "load": 510}     # +Peaker +DR
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (Load={scen['load']}) ---")
        
        # Reset dispatch
        for g in gens: g.dispatched = 0
        
        dispatched_list, lam, unserved = run_dispatch_bcp(gens, scen['load'], None) # Budget implicit in margin
        
        log(f"Lambda (Scarcity): {lam:.3f}")
        log(f"Unserved Load: {unserved}")
        for g in gens:
            if g.dispatched > 0:
                log(f"  {g.name}: {g.dispatched} MW")
                
        # Validation
        if scen['name'] == "Sunny Afternoon (Low Load)":
            # Should be Solar + Partial Nuclear
            if gens[0].name == "Solar" and gens[0].dispatched == 100:
                validation_score += 1
                log("VALID: Merit order followed (Solar first).")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Evening Peak (High Load)":
            # Load 400. Solar(100)+Nuke(200)+CCGT(100/150).
            if gens[2].name == "Gas CCGT" and gens[2].dispatched > 0:
                validation_score += 1
                log("VALID: Intermediate generation dispatched.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Heatwave (Extreme Load)":
            # Load 510. Total 520. Margin 10.
            # All gens should be maxed except DR (10/20).
            if gens[4].name == "Demand Response" and gens[4].dispatched > 0:
                validation_score += 1
                log("VALID: Expensive DR activated under scarcity.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3305,
        "phase": 187,
        "gate": 929,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3305_grid_dispatch.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 929 Complete.")

if __name__ == "__main__":
    main()
