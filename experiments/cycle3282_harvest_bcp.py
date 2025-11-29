
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3282] {msg}")

def run_harvest_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Quality(t) = 10 * (1 - e^-0.1t)  (Saturates at 10)
    # Risk(t) = 0.01 * t^2             (Quadratic risk increase)
    
    best_t = 0
    best_v = -float('inf')
    
    for t in range(0, 100):
        quality = 10.0 * (1.0 - math.exp(-0.1 * t))
        risk = 0.01 * (t ** 2)
        
        # V = Quality - λ * Risk
        v = quality - (lambda_val * risk)
        
        if v > best_v:
            best_v = v
            best_t = t
        else:
            # Peaked
            break
            
    return best_t, best_v, lambda_val

def main():
    log("GATE 911: HARVEST TIMING AS BCP")
    
    # Budget B here represents "Safety Buffer" or "Financial Resilience"
    # High B = Can afford to take risks -> Low λ
    # Low B = Cannot afford loss -> High λ -> Risk Averse
    
    scenarios = [
        {"name": "Resilient Farm", "budget": 10.0},
        {"name": "Average Farm", "budget": 2.0},
        {"name": "Precarious Farm", "budget": 0.5}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_t = float('inf')
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        t_opt, v, lambda_val = run_harvest_bcp(scen['budget'])
        
        log(f"Lambda (Risk Aversion): {lambda_val:.3f}")
        log(f"Optimal Harvest Time (Days): {t_opt}")
        
        # Monotonicity Check
        # Lower Budget -> Higher Lambda -> Earlier Harvest
        if t_opt < prev_t:
            validation_score += 1
            log("VALID: Harvest is earlier under scarcity (Risk Aversion).")
        else:
            log("INVALID: Harvest time did not decrease.")
            
        prev_t = t_opt
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3282,
        "phase": 182,
        "gate": 911,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3282_harvest_timing.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 911 Complete.")

if __name__ == "__main__":
    main()
