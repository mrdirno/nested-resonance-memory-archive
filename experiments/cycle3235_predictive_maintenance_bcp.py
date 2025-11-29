import random

# ======================================================================
# CYCLE 3235: PREDICTIVE MAINTENANCE AS BCP (SMART CITIES)
# ======================================================================
# Hypothesis: Maintenance is BCP.
#   V(repair) = Prob(Fail) * Cost(Fail) - lambda(Budget) * Cost(Repair)
#   High lambda -> Repair only imminent failures (Firefighting).
#   Low lambda -> Preventive maintenance.
# ======================================================================

def run_experiment():
    print("CYCLE 3235: Predictive Maintenance as BCP")
    
    N = 100 # Bridges/Roads
    assets = []
    for _ in range(N):
        assets.append({
            "P_Fail": random.uniform(0.0, 0.5), # Probability
            "Cost_Fail": random.uniform(1000, 10000), # Crash cost
            "Cost_Repair": random.uniform(10, 100)    # Fix cost
        })
        
    budget = 2000
    
    # BCP Strategy
    lamb = 1000.0 / (100.0 + budget)
    
    for a in assets:
        gain = a["P_Fail"] * a["Cost_Fail"] # Expected Avoided Cost
        a["score"] = gain - lamb * a["Cost_Repair"]
        
    assets.sort(key=lambda x: x["score"], reverse=True)
    
    spent = 0
    avoided_cost = 0
    failures = 0
    
    for a in assets:
        if a["score"] > 0 and spent + a["Cost_Repair"] <= budget:
            spent += a["Cost_Repair"]
            avoided_cost += a["P_Fail"] * a["Cost_Fail"] # Statistical value
        else:
            # Not repaired -> Might fail
            if random.random() < a["P_Fail"]:
                failures += 1
                
    print(f"BCP Avoided Cost: ${avoided_cost:.2f}")
    print(f"Failures: {failures}")
    
    # Scheduled Strategy (Repair every Nth)
    # Random selection until budget full
    random.shuffle(assets)
    spent_s = 0
    avoided_s = 0
    failures_s = 0
    
    for a in assets:
        if spent_s + a["Cost_Repair"] <= budget:
            spent_s += a["Cost_Repair"]
            avoided_s += a["P_Fail"] * a["Cost_Fail"]
        else:
            if random.random() < a["P_Fail"]:
                failures_s += 1
                
    print(f"Scheduled Avoided: ${avoided_s:.2f}")
    print(f"Scheduled Failures: {failures_s}")
    
    if avoided_cost > avoided_s:
        print("VERIFIED: BCP Maintenance outperforms Schedule.")
        return True
    else:
        print("FAILED: No improvement.")
        return False

if __name__ == "__main__":
    run_experiment()