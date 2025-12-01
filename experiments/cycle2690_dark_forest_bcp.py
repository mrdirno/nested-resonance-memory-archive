import json
import math
import sys
import os
import random

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE DARK FOREST (COSMIC SILENCE)
# -----------------------------------------------------------------------------
# Hypothesis: Silence is BCP-optimal when Predation Risk > 0.
# V(broadcast) = Gain(Contact) - λ * (Risk * CostOfDeath)
#
# Dynamics:
# - Agents choose: BROADCAST or SILENT.
# - BROADCAST gains "Contact Value" (small gain).
# - PREDATORS listen. If they hear BROADCAST, they Attack.
# - Attack = Massive Cost (Extinction).
# - Natural Selection removes Loud Agents.
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_dark_forest_experiment():
    print("Running Cycle 2690: The Dark Forest (Cosmic Silence)...")
    
    # Parameters
    num_civs = 100
    generations = 20
    
    gain_contact = 1.0 # Small benefit of trade/knowledge
    cost_death = 1000.0 # Extinction is expensive
    risk_predation = 0.1 # 10% chance a predator hears you per turn
    lambda_safety = 1.0 # Valuation of safety
    
    # Initial Population: 50% Loud, 50% Silent
    population = []
    for i in range(num_civs):
        strategy = "LOUD" if i < num_civs/2 else "SILENT"
        population.append({
            "id": i,
            "strategy": strategy,
            "alive": True,
            "score": 0.0
        })
        
    history = []
    
    print(f"Simulating {generations} generations of Cosmic Selection...")
    
    for gen in range(generations):
        loud_count = sum(1 for c in population if c["strategy"] == "LOUD" and c["alive"])
        silent_count = sum(1 for c in population if c["strategy"] == "SILENT" and c["alive"])
        
        history.append({
            "gen": gen,
            "loud": loud_count,
            "silent": silent_count
        })
        
        print(f"Gen {gen}: Loud={loud_count}, Silent={silent_count}")
        
        if loud_count == 0 and silent_count == 0:
            break
            
        # Simulation Step
        for civ in population:
            if not civ["alive"]:
                continue
                
            if civ["strategy"] == "SILENT":
                # Cost: Opportunity cost (0 gain)
                # Benefit: Safety (0 risk)
                civ["score"] += 0
                
            elif civ["strategy"] == "LOUD":
                # Benefit: Contact
                civ["score"] += gain_contact
                
                # Risk: Predation
                if random.random() < risk_predation:
                    # ATTACK!
                    # Cost = Lambda * DeathCost
                    # In BCP, Cost is subtracted from Value.
                    # In Evolutionary terms, Death = Removal.
                    civ["alive"] = False
                    civ["score"] -= (lambda_safety * cost_death)
                    
        # Reproduction / Cultural Transmission
        # Successful civs (High Score) replicate?
        # Or just observe attrition?
        # Let's just observe attrition for the Dark Forest effect.
        # The theory says "The universe is silent because the loud ones died."
        
    # Results
    final_loud = history[-1]["loud"]
    final_silent = history[-1]["silent"]
    
    print(f"\nFinal State: Loud={final_loud}, Silent={final_silent}")
    
    # Validation
    # Confirmed if Loud < Silent (significant attrition of Loud)
    # Ideally Loud -> 0
    
    dark_forest_confirmed = (final_loud < final_silent) and (final_loud < (num_civs * 0.1))
    
    results = {
        "meta": {
            "cycle": 2690,
            "name": "The Dark Forest",
            "phase": 253,
            "gate": 1166
        },
        "history": history,
        "validation": {
            "confirmed": dark_forest_confirmed,
            "final_loud": final_loud
        }
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2690_dark_forest.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_dark_forest_experiment()
