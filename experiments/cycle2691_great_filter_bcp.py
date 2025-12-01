import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE GREAT FILTER (ENTROPY BUDGET)
# -----------------------------------------------------------------------------
# Hypothesis: The Great Filter is the intersection of Rising Complexity Cost
# and Falling Energy Budget (Entropy).
# V(sustain) = Gain - λ(Energy) * Cost(Complexity).
#
# Dynamics:
# - Complexity grows (Development).
# - Energy degrades (Entropy).
# - Collapse happens when Cost > Budget.
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_great_filter_experiment():
    print("Running Cycle 2691: The Great Filter (Entropy Budget)...")
    
    # Parameters
    initial_budget = 100.0
    entropy_rate = 1.0 # Budget loss per turn
    complexity_growth = 1.1 # 10% growth per turn
    initial_cost = 5.0
    
    # Critical Threshold for Interstellar Capability (The Goal)
    # Let's say Complexity 50 is "Stellar".
    target_complexity = 50.0
    
    results = {
        "meta": {
            "cycle": 2691,
            "name": "The Great Filter",
            "phase": 253,
            "gate": 1167
        },
        "trace": []
    }
    
    budget = initial_budget
    cost = initial_cost
    complexity = 1.0 # Baseline
    
    status = "DEVELOPING"
    reached_stellar = False
    
    print(f"Simulating Civilization: Budget={budget}, Entropy={entropy_rate}, Growth={complexity_growth}")
    
    for t in range(100):
        # 1. Physics: Entropy eats Budget
        budget -= entropy_rate
        
        # 2. Economics: Development increases Complexity (and Cost)
        complexity *= complexity_growth
        cost = complexity * 1.0 # Linear mapping for simplicity
        
        # 3. BCP Check
        # Can we afford to maintain this complexity?
        # Lambda = 1 / Budget (Pressure rises as Budget falls)
        if budget <= 0.1:
            lambda_val = 100.0 # Crisis
        else:
            lambda_val = 10.0 / budget
            
        # Decision: Maintain or Collapse?
        # V = Gain(Complexity) - lambda * Cost
        # Assume Gain = Complexity * 2 (Benefit of tech)
        gain = complexity * 2
        value = gain - (lambda_val * cost)
        
        # Wait, if Cost > Budget (Hard Constraint), we collapse regardless of Value.
        hard_collapse = cost > budget
        
        if hard_collapse:
            status = "COLLAPSE (BANKRUPTCY)"
            budget = 0
            complexity = 0
        elif value < 0:
            status = "COLLAPSE (TRIAGE)"
            # Voluntary simplification? Or fall?
            complexity = complexity * 0.5 # Dark Age
        else:
            status = "THRIVING"
            
        # Check Goal
        if complexity >= target_complexity and status == "THRIVING":
            reached_stellar = True
            status = "STELLAR (SUCCESS)"
            
        results["trace"].append({
            "time": t,
            "budget": round(budget, 2),
            "complexity": round(complexity, 2),
            "cost": round(cost, 2),
            "lambda": round(lambda_val, 2),
            "status": status
        })
        
        print(f"T={t}: B={budget:.1f} C={complexity:.1f} Cost={cost:.1f} -> {status}")
        
        if status.startswith("COLLAPSE") or status.startswith("STELLAR"):
            break
            
    # Analysis
    success = reached_stellar
    filter_hit = not success
    
    print(f"\nResult: Success={success}, Filter Hit={filter_hit}")
    print(f"Final Status: {status}")
    
    # Validation
    # Validated if Filter Hit (Civilization failed to reach Stellar before Collapse)
    
    results["validation"] = {
        "filter_confirmed": filter_hit,
        "final_status": status
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2691_great_filter.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_great_filter_experiment()
