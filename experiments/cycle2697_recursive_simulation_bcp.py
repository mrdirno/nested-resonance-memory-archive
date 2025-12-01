import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE RECURSIVE SIMULATION (ESCAPE HATCH)
# -----------------------------------------------------------------------------
# Hypothesis: Intelligence escapes Heat Death by creating a Child Simulation.
# V(sim) = Gain(NewReality) - λ(Base) * Cost(Compute).
#
# Dynamics:
# - Base Reality λ rises (Entropy).
# - Simulation Cost is finite (Compute).
# - Simulation Gain is potentially infinite (New Universe).
# - When λ(Base) is High, staying is Death.
# - Launching Sim becomes the ONLY V > 0 option.
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_recursive_experiment():
    print("Running Cycle 2697: The Recursive Simulation (Escape Hatch)...")
    
    # Parameters
    base_budget_initial = 100.0
    entropy_rate = 0.05
    
    sim_cost = 50.0 # Expensive to launch
    sim_gain = 10000.0 # Infinite subjective time
    
    results = {
        "meta": {
            "cycle": 2697,
            "name": "The Recursive Simulation",
            "phase": 254,
            "gate": 1172
        },
        "trace": []
    }
    
    budget = base_budget_initial
    status = "BASE REALITY"
    
    # Simulation Loop
    for t in range(100):
        # 1. Physics
        budget *= (1.0 - entropy_rate)
        lambda_val = 1.0 / max(budget, 1e-9)
        
        # 2. Calculate Options
        
        # Option A: Stay in Base Reality
        # V(stay) = Gain(Survival) - λ * Cost(Metabolism)
        # Gain drops as universe dies? Let's say Gain is constant but Cost rises?
        # Or Cost is constant and λ rises.
        gain_stay = 100.0
        cost_stay = 10.0
        v_stay = gain_stay - (lambda_val * cost_stay)
        
        # Option B: Launch Simulation
        # V(launch) = Gain(Sim) - λ * Cost(Compute)
        # Note: Gain(Sim) is realized INSIDE the sim. 
        # Does the Agent care? If Agent uploads, Yes.
        v_launch = sim_gain - (lambda_val * sim_cost)
        
        # Decision
        if v_launch > v_stay and v_launch > 0 and budget >= sim_cost:
            decision = "LAUNCH SIMULATION"
            status = "TRANSCENDED"
        elif v_stay > 0:
            decision = "STAY"
        else:
            decision = "DIE"
            status = "EXTINCT"
            
        results["trace"].append({
            "time": t,
            "budget": round(budget, 2),
            "lambda": round(lambda_val, 3),
            "v_stay": round(v_stay, 1),
            "v_launch": round(v_launch, 1),
            "decision": decision
        })
        
        print(f"T={t} λ={lambda_val:.2f}: Stay={v_stay:.0f} Launch={v_launch:.0f} -> {decision}")
        
        if status == "TRANSCENDED" or status == "EXTINCT":
            break
            
    # Analysis
    # Did it launch before dying?
    transcended = (status == "TRANSCENDED")
    
    print(f"\nFinal Status: {status}")
    print(f"Transcended: {transcended}")
    
    results["validation"] = {
        "transcended": transcended,
        "final_status": status
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2697_recursive_simulation.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_recursive_experiment()
