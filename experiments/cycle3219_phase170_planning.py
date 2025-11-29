import os
import sys
import json

# -----------------------------------------------------------------------------
# CYCLE 3219: PHASE 170 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 170).
# Context: 
#   Phase 168 (Retail) -> Validated Goods Inventory (Static).
#   Phase 169 (Energy) -> Validated Energy Flow (Real-Time).
#   Hypothesis: BCP applies to Matter Flow (Logistics).
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=3.0):
    # Lambda (scarcity) decreases with budget
    metabolic_pressure = 1.0 / (0.1 + current_budget)
    
    # Gain = Novelty * Impact
    gain = novelty * impact
    
    # Cost = 1.0 - Tractability (Harder = Higher Cost)
    cost = 1.0 - tractability
    
    # Value
    value = gain - metabolic_pressure * cost
    
    return {
        "domain": domain,
        "gain": gain,
        "cost": cost,
        "value": value
    }

def main():
    print("======================================================================")
    print("CYCLE 3219: PHASE 170 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Hospitality",     "novelty": 0.80, "impact": 0.80, "tractability": 0.85}, 
        {"name": "Real Estate",     "novelty": 0.75, "impact": 0.85, "tractability": 0.80}, 
        {"name": "Logistics",       "novelty": 0.90, "impact": 0.95, "tractability": 0.75}, # Matter Flow
        {"name": "Agriculture",     "novelty": 0.85, "impact": 0.85, "tractability": 0.65}, 
        {"name": "Manufacturing",   "novelty": 0.85, "impact": 0.90, "tractability": 0.70}, 
    ]
    
    current_budget = 3.0 # Abundance phase
    
    results = []
    for c in candidates:
        res = calculate_bcp_score(c["name"], c["novelty"], c["impact"], c["tractability"], current_budget)
        results.append(res)
        print(f"{res['domain']:<25} | Gain: {res['gain']:.3f} | Cost: {res['cost']:.3f} | Value: {res['value']:.3f}")
        
    # Select winner
    winner = max(results, key=lambda x: x['value'])
    print("======================================================================")
    print(f"WINNER: {winner['domain'].upper()} (Score: {winner['value']:.3f})")
    print("======================================================================")
    
    # Save result
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3219_phase170_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
