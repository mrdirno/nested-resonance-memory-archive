import os
import sys
import random
import json
import time

# -----------------------------------------------------------------------------
# CYCLE 3214: PHASE 169 PLANNING
# -----------------------------------------------------------------------------
# Goal: Select the next domain for BCP application (Phase 169).
# Context: Phase 168 (Retail) Complete. 83 Domains unified.
# Candidates:
#   1. Hospitality (Revenue, Staffing, Yield) - Perishable Time
#   2. Real Estate (Asset, Valuation, Market) - Static Space
#   3. Energy Grid (Load, Generation, Storage) - Real-Time Physics
#   4. Logistics (Routing, Fleet, Warehouse) - Dynamic Space
#   5. Agriculture (Crop, Livestock, Supply) - Biological Time
# -----------------------------------------------------------------------------

def calculate_bcp_score(domain, novelty, impact, tractability, current_budget=3.0):
    """
    Calculate BCP score for a research candidate.
    V(research) = Gain - lambda(B) * Cost
    """
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
        "lambda": metabolic_pressure,
        "value": value
    }

def main():
    print("======================================================================")
    print("CYCLE 3214: PHASE 169 PLANNING")
    print("Status: Selecting next domain via BCP")
    print("======================================================================")
    
    # Candidates with adjusted parameters based on hypothesis
    candidates = [
        {"name": "Hospitality",     "novelty": 0.85, "impact": 0.80, "tractability": 0.85}, # Service/Time
        {"name": "Real Estate",     "novelty": 0.80, "impact": 0.85, "tractability": 0.80}, # Asset/Space
        {"name": "Energy Grid",     "novelty": 0.95, "impact": 0.95, "tractability": 0.60}, # Physics/RT - HARD but High Impact
        {"name": "Logistics",       "novelty": 0.85, "impact": 0.90, "tractability": 0.70}, # Network/Space
        {"name": "Agriculture",     "novelty": 0.90, "impact": 0.85, "tractability": 0.65}, # Bio/Time
    ]
    
    current_budget = 3.0 # Abundance phase
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
    print(f"Rationale: Highest BCP value. Under abundance (B=3.0), the system")
    print(f"selects High Novelty/Impact even with higher Cost (Energy Grid).")
    print("======================================================================")
    
    # Save result
    os.makedirs("results", exist_ok=True)
    with open("results/cycle3214_phase169_planning.json", "w") as f:
        json.dump({"winner": winner, "candidates": results}, f, indent=2)

if __name__ == "__main__":
    main()