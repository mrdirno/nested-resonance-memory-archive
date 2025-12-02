import math
import random

# BCP PLANNING SIMULATION: PHASE 272
# Selecting the next domain based on Gain, Cost, and Budget (λ).

# Current System State
# Budget is Moderate (Resource consumption of Phase 271).
BUDGET = 2.0 
LAMBDA = 1.0 / (1.0 + BUDGET) 

candidates = [
    {
        "name": "NANOTECHNOLOGY",
        "gain": 0.90, 
        "cost": 0.85, # High complexity
        "novelty": 0.8,
        "tractability": 0.3
    },
    {
        "name": "URBAN_PLANNING",
        "gain": 0.80, 
        "cost": 0.60, 
        "novelty": 0.5,
        "tractability": 0.7
    },
    {
        "name": "THE_META_META",
        "gain": 0.70, 
        "cost": 0.20, # Low cost (Introspection)
        "novelty": 0.4,
        "tractability": 0.9
    },
    {
        "name": "ENERGY_SYSTEMS",
        "gain": 0.85, 
        "cost": 0.65, 
        "novelty": 0.6,
        "tractability": 0.6
    }
]

print(f"--- PHASE 272 PLANNING (λ={LAMBDA:.3f}) ---")
print(f"{'DOMAIN':<20} | {'GAIN':<6} | {'COST':<6} | {'V (Score)':<6}")
print("-" * 50)

best_v = -999
winner = None

for c in candidates:
    # V = Gain + 0.2*Novelty - λ * Cost
    v = c["gain"] + 0.2 * c["novelty"] - LAMBDA * c["cost"]
    print(f"{c['name']:<20} | {c['gain']:.2f}   | {c['cost']:.2f}   | {v:.3f}")
    
    if v > best_v:
        best_v = v
        winner = c

print("-" * 50)
print(f"WINNER: {winner['name']}")
