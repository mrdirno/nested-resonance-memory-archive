import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3209: PHASE 168 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 168).
# Context: Phase 167 (Human Resources) Complete. 82 Domains unified.
# Candidates:
#   1. Retail & E-Commerce (Inventory, Pricing, Recommendations)
#   2. Hospitality (Revenue Mgmt, Staffing, Guest Exp)
#   3. Real Estate (Valuation, Market Dynamics, Development)
#   4. Consulting (Knowledge Mgmt, Project Allocation)
#   5. Non-Profit (Donor fatigue, Impact allocation)
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=3.0):
    """
    Calculate BCP score for a research candidate.
    V(research) = Gain - lambda(B) * Cost
    """
    # Lambda (scarcity) decreases with budget
    # lambda = k / (epsilon + B)
    # k=1.0, epsilon=0.1
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
        "lambda": metabolic_pressure,
        "value": value
    }

def main():
    print("======================================================================")
    print("CYCLE 3209: PHASE 168 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Retail & E-Commerce", "novelty": 0.85, "impact": 0.90, "tractability": 0.90}, # High data, high relevance
        {"name": "Hospitality",         "novelty": 0.80, "impact": 0.80, "tractability": 0.85},
        {"name": "Real Estate",         "novelty": 0.75, "impact": 0.85, "tractability": 0.80},
        {"name": "Consulting",          "novelty": 0.70, "impact": 0.70, "tractability": 0.75},
        {"name": "Non-Profit",          "novelty": 0.90, "impact": 0.80, "tractability": 0.60}, # Harder data
    ]
    
    current_budget = 3.0 # Abundance phase after Phase 167 success
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
    print(f"Rationale: Highest BCP value. Combination of high tractability")
    print(f"and high impact makes it the optimal next step.")
    print("======================================================================")
    
    # Save result
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3209_phase168_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
