import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3214: PHASE 169 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 169).
# Context: Phase 168 (Retail & E-Commerce) Complete. 83 Domains unified.
# Candidates:
#   1. Hospitality (Revenue Mgmt, Staffing, Guest Exp)
#   2. Real Estate (Valuation, Market Dynamics, Development)
#   3. Consulting (Knowledge Mgmt, Project Allocation)
#   4. Non-Profit (Donor fatigue, Impact allocation)
#   5. Energy (Grid optimization, Consumption forecasting)
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=3.5):
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
    print("CYCLE 3214: PHASE 169 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    candidates = [
        {"name": "Hospitality",         "novelty": 0.80, "impact": 0.80, "tractability": 0.85}, # Service heavy
        {"name": "Real Estate",         "novelty": 0.75, "impact": 0.85, "tractability": 0.80}, # Asset heavy
        {"name": "Consulting",          "novelty": 0.70, "impact": 0.70, "tractability": 0.75}, # Human capital heavy
        {"name": "Non-Profit",          "novelty": 0.90, "impact": 0.80, "tractability": 0.60}, # Metric heavy (hard)
        {"name": "Energy",              "novelty": 0.85, "impact": 0.95, "tractability": 0.85}, # Physical heavy (High impact)
    ]
    
    current_budget = 3.5 # Increased due to Phase 168 success
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
    print(f"Rationale: Highest BCP value. {winner['domain']} offers optimal balance")
    print(f"of impact and tractability given the current resource surplus.")
    print("======================================================================")
    
    # Save result
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3214_phase169_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()
