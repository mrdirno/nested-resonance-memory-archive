import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE HEAT DEATH BUDGET (OMEGA POINT)
# -----------------------------------------------------------------------------
# Hypothesis: Heat Death is the only BCP-stable equilibrium.
# V(structure) = Gain - λ(t) * Cost(maintenance).
#
# Dynamics:
# - Budget decays exponentially (Entropy).
# - λ = 1 / Budget.
# - Structures exist if V > 0.
# - Cost > 0 for all structures.
# - As t -> ∞, λ -> ∞, V -> -∞.
# - Only Cost=0 (Nothingness) survives.
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_heat_death_experiment():
    print("Running Cycle 2695: The Heat Death Budget (Omega Point)...")
    
    # Parameters
    initial_budget = 1000.0
    entropy_rate = 0.05 # 5% loss per tick
    
    # Structures (The Furniture of the Universe)
    # From Civilizations to Atoms
    structures = [
        {"name": "Type III Civ", "gain": 100000.0, "cost": 10000.0},
        {"name": "Type II Civ", "gain": 10000.0, "cost": 1000.0},
        {"name": "Type I Civ", "gain": 1000.0, "cost": 100.0},
        {"name": "Star", "gain": 100.0, "cost": 10.0},
        {"name": "Planet", "gain": 10.0, "cost": 1.0},
        {"name": "Molecule", "gain": 1.0, "cost": 0.1},
        {"name": "Atom", "gain": 0.1, "cost": 0.01},
        {"name": "Vacuum", "gain": 0.0, "cost": 0.0}
    ]
    
    results = {
        "meta": {
            "cycle": 2695,
            "name": "The Heat Death Budget",
            "phase": 254,
            "gate": 1170
        },
        "history": []
    }
    
    budget = initial_budget
    
    # Simulation Loop
    # We expect a cascade of collapse from High Cost to Low Cost.
    
    active_structures = [s["name"] for s in structures]
    
    for t in range(200):
        # 1. Entropy
        budget *= (1.0 - entropy_rate)
        
        if budget < 1e-9:
            budget = 1e-9 # Avoid div by zero, but effectively zero
            
        # 2. Lambda
        lambda_val = 1.0 / budget
        
        # 3. Check Viability
        current_active = []
        
        for s in structures:
            if s["name"] == "Vacuum":
                current_active.append(s["name"])
                continue
                
            # V = Gain - λ * Cost
            value = s["gain"] - (lambda_val * s["cost"])
            
            if value > 0:
                current_active.append(s["name"])
                
        # Record State
        results["history"].append({
            "time": t,
            "budget": budget,
            "lambda": lambda_val,
            "survivors": len(current_active),
            "active_list": list(current_active)
        })
        
        # Log changes
        if len(current_active) < len(active_structures):
            died = set(active_structures) - set(current_active)
            print(f"T={t} λ={lambda_val:.2f}: COLLAPSE -> {died}")
            active_structures = list(current_active)
            
        if len(active_structures) == 1 and active_structures[0] == "Vacuum":
            print(f"T={t}: HEAT DEATH ACHIEVED.")
            break
            
    # Analysis
    final_survivors = results["history"][-1]["active_list"]
    heat_death_confirmed = (len(final_survivors) == 1 and final_survivors[0] == "Vacuum")
    
    print(f"\nFinal State: {final_survivors}")
    print(f"Heat Death Confirmed: {heat_death_confirmed}")
    
    results["validation"] = {
        "heat_death_confirmed": heat_death_confirmed
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2695_heat_death.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_heat_death_experiment()
