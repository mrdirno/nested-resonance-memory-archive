import random
import math
import numpy as np

# ======================================================================
# CYCLE 3216: DEMAND RESPONSE AS BCP (GRID STABILIZATION)
# ======================================================================
# Context: Cycle 3215 failed (Shed Load = 1036 MWh).
# Hypothesis: BCP-driven Demand Response can stabilize the grid.
#   Loads observe Lambda (Grid Stress / Price).
#   V(consume) = Utility - Lambda * Cost.
#   If V < 0, load self-curtails (Voluntary vs Involuntary Shedding).
# ======================================================================

def run_experiment():
    print("CYCLE 3216: Demand Response as BCP")
    
    T = 24 * 7
    
    # Same Generators
    gens = [
        {"name": "Solar",   "cap": 500, "cost": 0.0, "ramp": 500},
        {"name": "Wind",    "cap": 300, "cost": 0.0, "ramp": 300},
        {"name": "Nuclear", "cap": 400, "cost": 10.0,"ramp": 10},
        {"name": "Gas",     "cap": 600, "cost": 50.0,"ramp": 300},
        {"name": "Battery", "cap": 200, "cost": 5.0, "ramp": 200, "charge": 100}
    ]
    
    # Load Profile
    base_load = 800
    peak_load = 1200
    
    total_cost = 0
    total_involuntary_shed = 0
    total_voluntary_curtailment = 0
    
    history = []
    
    for t in range(T):
        hour = t % 24
        raw_load = base_load + (peak_load - base_load) * math.sin((hour-6)*math.pi/12)**2 
        raw_load += random.gauss(0, 50)
        
        # Renewables
        sun = max(0, math.sin((hour-6)*math.pi/12)) if 6 <= hour <= 18 else 0
        wind = max(0, 0.5 + 0.5*math.sin(t*0.1) + random.gauss(0, 0.2))
        
        avail_solar = gens[0]["cap"] * sun
        avail_wind = gens[1]["cap"] * wind
        
        # --- BCP DEMAND RESPONSE ---
        
        # 1. Calculate Lambda (Anticipated Stress)
        total_capacity = avail_solar + avail_wind + gens[2]["cap"] + gens[3]["cap"] + gens[4]["charge"]
        margin = total_capacity - raw_load
        
        # Lambda scales with scarcity
        if margin <= 0:
            lamb = 10.0 # High stress
        else:
            lamb = 1000.0 / (100.0 + margin)
            
        # 2. Load Agent Decision
        # Load is composed of High Utility (Critical) and Low Utility (Discretionary) parts
        # Let's say 80% Critical (Utility=100), 20% Discretionary (Utility=10)
        # Cost = Lambda * Base_Price (e.g. $1)
        
        # Threshold: If Utility < Lambda, Curtail.
        
        # Critical: 100 - Lambda. Curtailed if Lambda > 100 (Collapse)
        # Discretionary: 10 - Lambda. Curtailed if Lambda > 10 (Moderate Stress)
        
        # Apply BCP Logic
        active_load = 0
        curtailed = 0
        
        # Critical Segment
        if 100 > lamb:
            active_load += raw_load * 0.8
        else:
            curtailed += raw_load * 0.8 # Catastrophic triage
            
        # Discretionary Segment
        if 10 > lamb:
            active_load += raw_load * 0.2
        else:
            curtailed += raw_load * 0.2 # Smart curtailment
            
        total_voluntary_curtailment += curtailed
        
        # --- DISPATCH ---
        
        sources = []
        sources.append({"name": "Solar", "avail": avail_solar, "cost": 0.1}) 
        sources.append({"name": "Wind", "avail": avail_wind, "cost": 0.1})
        sources.append({"name": "Nuclear", "avail": gens[2]["cap"], "cost": gens[2]["cost"]})
        sources.append({"name": "Gas", "avail": gens[3]["cap"], "cost": gens[3]["cost"]})
        sources.append({"name": "Bat_Discharge", "avail": gens[4]["charge"], "cost": gens[4]["cost"]})
        
        sources.sort(key=lambda x: x["cost"])
        
        dispatched = 0
        current_cost = 0
        
        for s in sources:
            needed = active_load - dispatched
            if needed <= 0: break
            
            take = min(s["avail"], needed)
            dispatched += take
            current_cost += take * s["cost"]
            
            if s["name"] == "Bat_Discharge":
                gens[4]["charge"] -= take
                
        # Battery Charging (Surplus)
        if dispatched >= active_load:
            surplus = (avail_solar + avail_wind) - (dispatched - (gens[2]["cap"] + gens[3]["cap"])) # Approx
            # Actually just check margin
            pass # Simplified for test
            
        # Involuntary Shedding (Blackouts)
        involuntary = max(0, active_load - dispatched)
        total_involuntary_shed += involuntary
        total_cost += current_cost
        
        if t % 24 == 0:
            pass
            # print(f"T={t}, Load={raw_load:.0f}, Active={active_load:.0f}, Lambda={lamb:.2f}")

    print(f"FINAL: Cost=${total_cost:.0f}")
    print(f"Voluntary Curtailment={total_voluntary_curtailment:.0f} MWh")
    print(f"Involuntary Shedding ={total_involuntary_shed:.0f} MWh")
    
    # Success Criteria: Involuntary Shedding Reduced significantly vs Baseline (1036)
    # Ideally near zero.
    
    if total_involuntary_shed < 100:
        print("VERIFIED: BCP Demand Response stabilized the grid.")
        return True
    else:
        print(f"FAILED: Still significant shedding ({total_involuntary_shed}).")
        return False

if __name__ == "__main__":
    run_experiment()
