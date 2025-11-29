
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3281] {msg}")

def run_irrigation_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Optimal Water W*
    # Marginal Gain = Marginal Cost
    # d/dW (Yield) = λ
    # Yield = 10 * ln(W + 1)
    # 10 / (W + 1) = λ
    # W + 1 = 10 / λ
    # W* = (10 / λ) - 1
    
    w_optimal = (10.0 / lambda_val) - 1.0
    if w_optimal < 0: w_optimal = 0
    
    yield_val = 10.0 * math.log(w_optimal + 1.0)
    cost = w_optimal # Unit cost of water = 1 (scaled by lambda in V)
    
    v = yield_val - (lambda_val * cost)
    
    return w_optimal, yield_val, v, lambda_val

def main():
    log("GATE 910: IRRIGATION AS BCP")
    
    scenarios = [
        {"name": "Abundant Reservoir", "budget": 10.0},
        {"name": "Restricted Supply", "budget": 2.0},
        {"name": "Severe Drought", "budget": 0.5}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_w = float('inf')
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        w_opt, y, v, lambda_val = run_irrigation_bcp(scen['budget'])
        
        log(f"Lambda: {lambda_val:.3f}")
        log(f"Optimal Water (W*): {w_opt:.2f}")
        log(f"Yield: {y:.2f}")
        
        # Check Monotonicity
        # As Budget drops, W* should drop.
        if w_opt < prev_w:
            validation_score += 1
            log("VALID: Water usage decreased with budget.")
        else:
            log("INVALID: Water usage did not decrease.")
            
        prev_w = w_opt
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3281,
        "phase": 182,
        "gate": 910,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3281_irrigation.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 910 Complete.")

if __name__ == "__main__":
    main()
