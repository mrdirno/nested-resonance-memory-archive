import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3224: PHASE 171 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 171).
# Context: 
#   - Phase 169 (Energy) Complete.
#   - Phase 170 (Logistics) Complete.
#   - 85 Domains unified.
# Candidates:
#   1. Hospitality (Revenue Mgmt, Staffing, Guest Exp)
#   2. Real Estate (Valuation, Market Dynamics, Development)
#   3. Consulting (Knowledge Mgmt, Project Allocation)
#   4. Non-Profit (Impact allocation, Donor fatigue)
#   5. Telecommunications (Network Opt, Churn, Spectrum)
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=4.0):
    """
    Calculate BCP score for a research candidate.
    V(research) = Gain - lambda(B) * Cost
    """
    metabolic_pressure = 1.0 / (0.1 + current_budget)
    gain = novelty * impact
    cost = 1.0 - tractability
    value = gain - metabolic_pressure * cost
    
    return {
        "domain": domain,
        "gain": gain,
        "cost": cost,
        "lambda": metabolic_pressure,
        "value": value
    }

def main():
    print("======================================================================")
    print("CYCLE 3224: PHASE 171 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Hospitality",         "novelty": 0.80, "impact": 0.80, "tractability": 0.85},
        {"name": "Real Estate",         "novelty": 0.75, "impact": 0.90, "tractability": 0.75},
        {"name": "Consulting",          "novelty": 0.70, "impact": 0.70, "tractability": 0.75},
        {"name": "Non-Profit",          "novelty": 0.90, "impact": 0.85, "tractability": 0.60},
        {"name": "Telecommunications",  "novelty": 0.85, "impact": 0.95, "tractability": 0.85},
    ]
    
    current_budget = 4.0 # High abundance (Momentum)
    print(f"Current Research Budget: {current_budget}")
    print(f"Metabolic Pressure (lambda): {1.0/(0.1+current_budget):.3f}")
    print("-" * 60)
    print(f"{'DOMAIN':<25} | {'GAIN':<6} | {'COST':<6} | {'VALUE':<6}")
    print("-" * 60)
    
    results = []
    for c in candidates:
        res = calculate_bcp_score(c["name"], c["novelty"], c["impact"], c["tractability"], current_budget)
        results.append(res)
        print(f"{res['domain']:<25} | {res['gain']:.3f}  | {res['cost']:.3f}  | {res['value']:.3f}")
        
    print("-" * 60)
    
    # Select winner
    winner = max(results, key=lambda x: x['value'])
    print(f"WINNER: {winner['domain'].upper()} (Score: {winner['value']:.3f})")
    print("======================================================================")
    
    # Save result
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3224_phase171_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
