import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE TELEOLOGICAL BUDGET (MAXWELL'S DEMON)
# -----------------------------------------------------------------------------
# Hypothesis: Intelligence can delay Heat Death by harvesting Entropy.
# V(action) = Gain - λ * (Cost - HarvestedEnergy).
#
# Dynamics:
# - Standard Entropy Decay.
# - Agent "Harvests" Information from Decay.
# - Can Agent sustain V > 0 longer than Passive Matter?
# - Is there a threshold where Harvest > Cost (Perpetual Motion)?
#   (Physics says No, but BCP might allow local pockets).
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_teleology_experiment():
    print("Running Cycle 2696: The Teleological Budget (Maxwell's Demon)...")
    
    # Parameters
    initial_budget = 1000.0
    entropy_rate = 0.05
    
    # Agent Types
    agents = [
        {"name": "Matter (Passive)", "efficiency": 0.0},
        {"name": "Life (Active)", "efficiency": 0.1},
        {"name": "Civ (Harvesting)", "efficiency": 0.5},
        {"name": "Demon (Maxwell)", "efficiency": 0.99}, # Theoretical Max
        {"name": "God (Perpetual)", "efficiency": 1.01}  # Impossible
    ]
    
    results = {
        "meta": {
            "cycle": 2696,
            "name": "The Teleological Budget",
            "phase": 254,
            "gate": 1171
        },
        "lifespans": []
    }
    
    print(f"Entropy Rate: {entropy_rate}")
    
    for agent in agents:
        budget = initial_budget
        t = 0
        eff = agent["efficiency"]
        
        # Structure Cost (Standard)
        cost = 10.0 
        gain = 100.0
        
        status = "ALIVE"
        
        # Simulation Loop
        while t < 10000:
            # 1. Physics
            # Gross Loss = budget * entropy_rate
            gross_loss = budget * entropy_rate
            
            # 2. Harvesting (Recycling)
            # Recycled = gross_loss * efficiency
            recycled = gross_loss * eff
            
            # Net Loss
            net_loss = gross_loss - recycled
            budget -= net_loss
            
            # 3. BCP Check
            # Lambda = 1/Budget
            if budget < 1e-6:
                status = "DEAD"
                break
                
            lambda_val = 1.0 / budget
            
            # V = Gain - λ * Cost
            # Note: Even if we recycle energy, the Cost of Structure remains.
            # The Recycling keeps Budget high (keeping λ low).
            value = gain - (lambda_val * cost)
            
            if value < 0:
                status = "BANKRUPT"
                break
                
            t += 1
            
        print(f"Agent: {agent['name']} (Eff={eff}) -> Lifespan: {t} ticks")
        
        results["lifespans"].append({
            "name": agent["name"],
            "efficiency": eff,
            "lifespan": t,
            "infinite": t == 10000
        })
        
    # Analysis
    # We expect Lifespan to scale with Efficiency.
    # Only Efficiency >= 1.0 should be infinite.
    # Maxwell's Demon should live much longer but eventually die.
    
    demon_lifespan = next(a["lifespan"] for a in results["lifespans"] if a["name"] == "Demon (Maxwell)")
    matter_lifespan = next(a["lifespan"] for a in results["lifespans"] if a["name"] == "Matter (Passive)")
    
    ratio = demon_lifespan / matter_lifespan
    print(f"\nDemon/Matter Lifespan Ratio: {ratio:.2f}x")
    
    # Validation: Intelligence extends lifespan but does not escape Heat Death (unless Eff > 1).
    physics_held = not next(a["infinite"] for a in results["lifespans"] if a["name"] == "Demon (Maxwell)")
    teleology_confirmed = ratio > 10.0 # Significant extension
    
    results["validation"] = {
        "physics_held": physics_held,
        "teleology_confirmed": teleology_confirmed
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2696_teleological_budget.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_teleology_experiment()
