import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3234: PHASE 173 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 173).
# Context: 
#   - Phase 172 (Environmental) Complete.
#   - 87 Domains unified.
# Candidates:
#   1. Manufacturing (Predictive Maint, Quality Control)
#   2. Smart Cities (Traffic, Waste, Water)
#   3. Hospitality (Revenue, Staffing)
#   4. Real Estate (Valuation, Development)
#   5. Legal (Contract Review, Outcome Prediction)
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=5.0):
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
    print("CYCLE 3234: PHASE 173 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Manufacturing",       "novelty": 0.80, "impact": 0.95, "tractability": 0.90}, # High impact physical
        {"name": "Smart Cities",        "novelty": 0.85, "impact": 0.90, "tractability": 0.70},
        {"name": "Hospitality",         "novelty": 0.80, "impact": 0.80, "tractability": 0.85},
        {"name": "Real Estate",         "novelty": 0.75, "impact": 0.90, "tractability": 0.75},
        {"name": "Legal",               "novelty": 0.90, "impact": 0.85, "tractability": 0.60}, # Text heavy
    ]
    
    current_budget = 5.0 # High momentum
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
    with open("results/cycle3234_phase173_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
