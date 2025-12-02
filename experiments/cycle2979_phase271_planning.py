import math
import random

# BCP PLANNING SIMULATION: PHASE 271
# Selecting the next domain based on Gain, Cost, and Budget (λ).

# Current System State
# Budget is High (Success of Phase 269/270).
BUDGET = 2.8 
LAMBDA = 1.0 / (1.0 + BUDGET) 

# Candidate Domains
# 1. ROBOTICS: Extending fabrication to motion. (Now higher priority?)
# 2. ARCHITECTURE: Scaling up fabrication to shelter.
# 3. SPACE_SYSTEMS: Re-evaluating.
# 4. CLIMATE_ENGINEERING: Global scale BCP.

candidates = [
    {
        "name": "ROBOTICS",
        "gain": 0.88, # Increased gain (Next logical step after static objects)
        "cost": 0.70, 
        "novelty": 0.6,
        "tractability": 0.5 # Simulation only for now
    },
    {
        "name": "ARCHITECTURE",
        "gain": 0.75,
        "cost": 0.75,
        "novelty": 0.5,
        "tractability": 0.4
    },
    {
        "name": "SPACE_SYSTEMS",
        "gain": 0.90,
        "cost": 0.95,
        "novelty": 0.8,
        "tractability": 0.3
    },
    {
        "name": "CLIMATE_ENGINEERING",
        "gain": 0.95, # Existential gain
        "cost": 0.90, # High complexity
        "novelty": 0.7,
        "tractability": 0.4
    }
]

print(f"--- PHASE 271 PLANNING (λ={LAMBDA:.3f}) ---")
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
