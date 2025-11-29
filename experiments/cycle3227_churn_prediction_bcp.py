import random

# ======================================================================
# CYCLE 3227: CHURN PREDICTION AS BCP
# ======================================================================
# Hypothesis: Retention is BCP Triage.
#   V(user) = LTV * Prob(Save) - lambda(Budget) * Cost
#   High lambda -> Save only High LTV / High Save Prob.
#   Low lambda -> Save everyone.
# ======================================================================

def run_experiment():
    print("CYCLE 3227: Churn Prediction as BCP")
    
    N = 1000
    # Users: [LTV, Churn_Prob, Save_Prob, Cost]
    users = []
    for _ in range(N):
        users.append({
            "LTV": random.uniform(10, 1000),
            "Churn": random.uniform(0, 1),
            "Save": random.uniform(0.1, 0.9),
            "Cost": random.uniform(10, 50)
        })
        
    budget = 5000
    
    # BCP Strategy
    # Score = LTV * Save * Churn - lambda * Cost?
    # Gain = LTV (saved). Probability of needing save = Churn. Probability of success = Save.
    # Expected Gain = LTV * Churn * Save
    
    # Lambda = 1 / (epsilon + budget) -> Fixed for single step
    lamb = 10000.0 / (100.0 + budget) # Tuned parameter
    
    for u in users:
        u["score"] = (u["LTV"] * u["Churn"] * u["Save"]) - lamb * u["Cost"]
        
    # Sort and Spend
    users.sort(key=lambda x: x["score"], reverse=True)
    
    spent = 0
    saved_ltv = 0
    
    for u in users:
        if u["score"] > 0 and spent + u["Cost"] <= budget:
            spent += u["Cost"]
            # Outcome
            if random.random() < u["Churn"]: # User was going to churn
                if random.random() < u["Save"]: # We saved them
                    saved_ltv += u["LTV"]
                    
    print(f"BCP Saved LTV: ${saved_ltv:.2f}")
    
    # Threshold Strategy (Standard)
    # Retain if Churn > 0.5
    spent_t = 0
    saved_ltv_t = 0
    random.shuffle(users) # Random order
    
    for u in users:
        if u["Churn"] > 0.5 and spent_t + u["Cost"] <= budget:
            spent_t += u["Cost"]
            if random.random() < u["Churn"]:
                if random.random() < u["Save"]:
                    saved_ltv_t += u["LTV"]
                    
    print(f"Threshold Saved LTV: ${saved_ltv_t:.2f}")
    
    if saved_ltv > saved_ltv_t:
        print("VERIFIED: BCP Churn Triage outperforms Threshold.")
        return True
    else:
        print("FAILED: BCP did not outperform.")
        return False

if __name__ == "__main__":
    run_experiment()