import math
import random

# BCP PLANNING SIMULATION: PHASE 273
# Selecting the next domain based on Gain, Cost, and Budget (λ).

BUDGET = 3.0 # Abundance (High success rate)
LAMBDA = 1.0 / (1.0 + BUDGET) 

candidates = [
    {
        "name": "THE_META_META",
        "gain": 0.95, # Self-improvement
        "cost": 0.30, # Low physical cost
        "novelty": 0.9,
        "tractability": 0.9
    },
    {
        "name": "URBAN_PLANNING",
        "gain": 0.80, 
        "cost": 0.60, 
        "novelty": 0.5,
        "tractability": 0.7
    },
    {
        "name": "ENERGY_SYSTEMS",
        "gain": 0.85, 
        "cost": 0.65, 
        "novelty": 0.6,
        "tractability": 0.6
    },
    {
        "name": "EDUCATION",
        "gain": 0.80,
        "cost": 0.40,
        "novelty": 0.5,
        "tractability": 0.8
    }
]

print(f"--- PHASE 273 PLANNING (λ={LAMBDA:.3f}) ---")
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
