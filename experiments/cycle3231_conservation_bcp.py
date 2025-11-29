import random

# ======================================================================
# CYCLE 3231: CONSERVATION TRIAGE AS BCP
# ======================================================================
# Hypothesis: Conservation is BCP.
#   V(species) = Uniqueness * Prob(Save) - lambda(Budget) * Cost
#   High lambda -> Save only high-value / cheap species (Triage).
#   Low lambda -> Save everyone.
# ======================================================================

def run_experiment():
    print("CYCLE 3231: Conservation Triage as BCP")
    
    N = 100
    species = []
    for _ in range(N):
        species.append({
            "Uniqueness": random.uniform(1, 10),
            "Charisma": random.uniform(1, 10), # Bias
            "Cost": random.uniform(10, 100),
            "ProbSave": random.uniform(0.1, 0.9)
        })
        
    budget = 1000
    
    # BCP Strategy
    lamb = 100.0 / (10.0 + budget)
    
    for s in species:
        # Gain = Genetic Value Preserved = Uniqueness * ProbSave
        s["score"] = (s["Uniqueness"] * s["ProbSave"]) - lamb * s["Cost"]
        
    species.sort(key=lambda x: x["score"], reverse=True)
    
    saved_bcp = 0
    spent = 0
    
    for s in species:
        if s["score"] > 0 and spent + s["Cost"] <= budget:
            spent += s["Cost"]
            if random.random() < s["ProbSave"]:
                saved_bcp += s["Uniqueness"]
                
    print(f"BCP Saved Value: {saved_bcp:.2f}")
    
    # "Cute" Strategy (Charisma)
    species.sort(key=lambda x: x["Charisma"], reverse=True)
    
    saved_cute = 0
    spent = 0
    
    for s in species:
        if spent + s["Cost"] <= budget:
            spent += s["Cost"]
            if random.random() < s["ProbSave"]:
                saved_cute += s["Uniqueness"]
                
    print(f"Cute Saved Value: {saved_cute:.2f}")
    
    if saved_bcp > saved_cute:
        print("VERIFIED: BCP Conservation outperforms Charisma-bias.")
        return True
    else:
        print("FAILED: BCP did not outperform.")
        return False

if __name__ == "__main__":
    run_experiment()