
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3352] {msg}")

def run_creativity_bcp(cognitive_budget):
    k = 1.0
    epsilon = 0.1
    lambda_cog = k / (epsilon + cognitive_budget)
    
    # Creativity: Novelty (N) vs Familiarity (F).
    # Wundt Curve: Aesthetic value peaks at moderate novelty (MAYA).
    # But BCP says "Cost" is processing unfamiliarity.
    # Cost = Novelty.
    # Gain = Novelty * (1 - Novelty) * Scale? (Inverted U)
    # Or Gain = Stimulation.
    
    # Let's model Value as Linear Novelty (Stimulation)
    # And Cost as Exponential Processing (Confusion).
    # V = 10*N - λ * exp(N).
    
    best_N = 0.0
    best_v = -float('inf')
    
    for n_int in range(0, 100):
        N = n_int / 10.0 # 0 to 10
        cost = math.exp(0.5 * N)
        gain = 10.0 * N
        
        v = gain - (lambda_cog * cost)
        
        if v > best_v:
            best_v = v
            best_N = N
            
    return best_N, best_v, lambda_cog

def main():
    log("GATE 965: CREATIVITY AS BCP")
    
    scenarios = [
        {"name": "Expert (High Budget)", "budget": 10.0},
        {"name": "Novice (Low Budget)", "budget": 1.0},
        {"name": "Child (Very Low Budget)", "budget": 0.1}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_N = -1.0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        N, v, lam = run_creativity_bcp(scen['budget'])
        log(f"Lambda: {lam:.3f}")
        log(f"Optimal Novelty: {N:.1f}")
        
        if prev_N == -1.0:
            pass
        elif N <= prev_N: # Poorer budget -> Less novelty handled
            validation_score += 1
            log("VALID: Novelty preference scales with capacity (Drops with Budget).")
        else:
            log("INVALID: Novelty increased despite lower budget.")
            
        prev_N = N
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}")
    
    # Output results
    output = {
        "cycle": 3352,
        "phase": 196,
        "gate": 965,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3352_creativity_bcp.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 965 Complete.")

if __name__ == "__main__":
    main()
