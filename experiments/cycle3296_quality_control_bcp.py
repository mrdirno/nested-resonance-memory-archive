
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3296] {msg}")

def run_quality_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Discount Factor gamma = 1/(1+λ)
    gamma = 1.0 / (1.0 + lambda_val)
    
    # Speed S in [1, 10]
    # Revenue = S * 10 (More speed, more sales now)
    # Defect Rate = 0.01 * S^2
    # Future Cost per Defect = 100 (Warranty/Reputation)
    
    best_s = 0
    best_v = -float('inf')
    
    for s in range(1, 11):
        revenue = s * 10.0
        defects = 0.01 * (s ** 2)
        future_cost = defects * 100.0
        
        # V = Revenue - PV(Future Cost)
        # PV = Future * gamma
        # Note: λ usually penalizes CURRENT cost.
        # But λ also sets the time preference.
        # We assume 'Budget Pressure' means we need money NOW.
        
        v = revenue - (future_cost * gamma)
        
        if v > best_v:
            best_v = v
            best_s = s
            
    return best_s, best_v, lambda_val, gamma

def main():
    log("GATE 922: QUALITY VS SPEED AS BCP")
    
    # Scenario:
    # High Budget -> Low λ -> Gamma ~ 1 -> Future cost fully felt -> Low Speed/High Quality.
    # Low Budget -> High λ -> Gamma ~ 0 -> Future cost ignored -> High Speed/Low Quality.
    
    scenarios = [
        {"name": "Established Brand (High B)", "budget": 10.0}, # Expect Low Speed/High Quality
        {"name": "Struggling Startup (Low B)", "budget": 0.5},  # Expect High Speed/Bugs
        {"name": "Desperate (Crisis)", "budget": 0.01}          # Expect Max Speed
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_s = -1
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        s_opt, v, lambda_val, gamma = run_quality_bcp(scen['budget'])
        
        log(f"Lambda: {lambda_val:.3f} | Gamma (Patience): {gamma:.3f}")
        log(f"Optimal Speed: {s_opt}")
        
        # Monotonicity Check
        # As B drops, Speed should INCREASE (sacrificing quality for cash).
        if prev_s == -1:
            pass
        elif s_opt >= prev_s:
            validation_score += 1
            log("VALID: Speed increased/maintained as budget tightened (Future discounted).")
        else:
            log("INVALID: Speed decreased.")
            
        prev_s = s_opt
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}")
    
    # Output results
    output = {
        "cycle": 3296,
        "phase": 185,
        "gate": 922,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3296_quality_control.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 922 Complete.")

if __name__ == "__main__":
    main()
