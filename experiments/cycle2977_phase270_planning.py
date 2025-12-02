import math
import random

# BCP PLANNING SIMULATION: PHASE 270
# Selecting the next domain based on Gain, Cost, and Budget (λ).

# Current System State
# We have successfully bridged to reality (Fabrication).
# Budget is High (Success of Phase 269).
BUDGET = 2.5 # Abundance
LAMBDA = 1.0 / (1.0 + BUDGET) # Low Scarcity

# Candidate Domains
# 1. ROBOTICS: Extending fabrication to motion.
# 2. ARCHITECTURE: Scaling up fabrication to shelter.
# 3. SPACE_SYSTEMS: Theoretical application of BCP to satellites/habitats.
# 4. SYNTHETIC_BIOLOGY: Simulation of biological BCP (Gene circuits).

candidates = [
    {
        "name": "ROBOTICS",
        "gain": 0.85, # High utility, physical agency
        "cost": 0.70, # High complexity, hardware dependency
        "novelty": 0.6,
        "tractability": 0.6
    },
    {
        "name": "ARCHITECTURE",
        "gain": 0.75, # High utility (shelter)
        "cost": 0.80, # Very high cost (scale)
        "novelty": 0.5,
        "tractability": 0.4
    },
    {
        "name": "SPACE_SYSTEMS",
        "gain": 0.90, # Massive impact
        "cost": 0.95, # Extreme cost (theoretical only)
        "novelty": 0.8,
        "tractability": 0.3
    },
    {
        "name": "SYNTHETIC_BIOLOGY",
        "gain": 0.80, # High impact
        "cost": 0.50, # Moderate cost (simulation)
        "novelty": 0.9,
        "tractability": 0.8
    }
]

print(f"--- PHASE 270 PLANNING (λ={LAMBDA:.3f}) ---")
print(f"{'DOMAIN':<20} | {'GAIN':<6} | {'COST':<6} | {'V (Score)':<6}")
print("-" * 50)

best_v = -999
winner = None

for c in candidates:
    # V = Gain - λ * Cost
    # Add Novelty bonus for exploration?
    # V = Gain + 0.2*Novelty - λ * Cost
    
    v = c["gain"] + 0.2 * c["novelty"] - LAMBDA * c["cost"]
    
    print(f"{c['name']:<20} | {c['gain']:.2f}   | {c['cost']:.2f}   | {v:.3f}")
    
    if v > best_v:
        best_v = v
        winner = c

print("-" * 50)
print(f"WINNER: {winner['name']}")
