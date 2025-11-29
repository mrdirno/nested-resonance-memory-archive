import os
import sys
import json

# -----------------------------------------------------------------------------
# CYCLE 3224: PHASE 171 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 171).
# Context: 
#   Phase 170 (Logistics) -> Validated Matter Flow.
#   Phase 169 (Energy) -> Validated Energy Flow.
#   Gap: Information Flow (Networks) or Biological Time.
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
    print("CYCLE 3224: PHASE 171 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Telecommunications", "novelty": 0.85, "impact": 0.90, "tractability": 0.80}, # Info Flow
        {"name": "Real Estate",        "novelty": 0.75, "impact": 0.85, "tractability": 0.80}, # Space Asset
        {"name": "Agriculture",        "novelty": 0.85, "impact": 0.85, "tractability": 0.65}, # Bio Time
        {"name": "Environmental",      "novelty": 0.90, "impact": 0.90, "tractability": 0.50}, # Complex System
        {"name": "Manufacturing",      "novelty": 0.80, "impact": 0.90, "tractability": 0.75}, # Process
    ]
    
    current_budget = 3.0 
    
    results = []
    for c in candidates:
        res = calculate_bcp_score(c["name"], c["novelty"], c["impact"], c["tractability"], current_budget)
        results.append(res)
        print(f"{res['domain']:<25} | Gain: {res['gain']:.3f} | Cost: {res['cost']:.3f} | Value: {res['value']:.3f}")
        
    winner = max(results, key=lambda x: x['value'])
    print("======================================================================")
    print(f"WINNER: {winner['domain'].upper()} (Score: {winner['value']:.3f})")
    print("======================================================================")
    
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3224_phase171_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()