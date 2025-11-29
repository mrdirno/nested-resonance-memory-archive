import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3229: PHASE 172 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 172).
# Context: 
#   - Phase 171 (Telecommunications) Complete.
#   - 86 Domains unified.
# Candidates:
#   1. Manufacturing (Maintenance, Control, Quality)
#   2. Smart Cities (Traffic, Waste, Water)
#   3. Environmental (Climate, Conservation)
#   4. Hospitality (Revenue, Staffing)
#   5. Real Estate (Valuation, Development)
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=4.5):
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
    print("CYCLE 3229: PHASE 172 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Manufacturing",       "novelty": 0.80, "impact": 0.90, "tractability": 0.90}, # High control
        {"name": "Smart Cities",        "novelty": 0.85, "impact": 0.90, "tractability": 0.70}, # Complex systems
        {"name": "Environmental",       "novelty": 0.90, "impact": 0.95, "tractability": 0.50}, # Chaotic
        {"name": "Hospitality",         "novelty": 0.80, "impact": 0.80, "tractability": 0.85},
        {"name": "Real Estate",         "novelty": 0.75, "impact": 0.90, "tractability": 0.75},
    ]
    
    current_budget = 4.5 # Increasing budget (Success Momentum)
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
    with open("results/cycle3229_phase172_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
