
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3327] {msg}")

def run_training_bcp(fitness_budget):
    k = 1.0
    epsilon = 0.1
    lambda_fatigue = k / (epsilon + fitness_budget)
    
    # Training Load L
    # Gain = Fitness(L) = 10 * (1 - e^-0.1L)
    # Cost = InjuryRisk(L) = 0.01 * L^2
    
    best_L = 0
    best_v = -float('inf')
    
    for L in range(0, 50):
        import math
        fitness = 10.0 * (1.0 - math.exp(-0.1 * L))
        risk = 0.01 * (L ** 2)
        
        v = fitness - (lambda_fatigue * risk)
        
        if v > best_v:
            best_v = v
            best_L = L
            
    return best_L, best_v, lambda_fatigue

def main():
    log("GATE 946: TRAINING LOAD AS BCP")
    
    scenarios = [
        {"name": "Fresh Athlete (High B)", "budget": 10.0},
        {"name": "Mid-Season (Med B)", "budget": 5.0},
        {"name": "Injured/Fatigued (Low B)", "budget": 1.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_L = 100
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        L, v, lam = run_training_bcp(scen['budget'])
        log(f"Lambda: {lam:.3f}")
        log(f"Optimal Load: {L}")
        
        if L <= prev_L:
            validation_score += 1
            log("VALID: Load reduced as fatigue increased.")
        else:
            log("INVALID: Load increased?")
            
        prev_L = L
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3327,
        "phase": 191,
        "gate": 946,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3327_training_load.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 946 Complete.")

if __name__ == "__main__":
    main()
