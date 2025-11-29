
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3316] {msg}")

def solve_savings(income):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + income)
    gamma = 1.0 / (1.0 + lambda_val)
    
    # Maximize ln(C) + gamma * ln(Income - C)
    # d/dC = 1/C - gamma/(I-C) = 0
    # I-C = gamma * C
    # I = C(1+gamma)
    # C* = I / (1+gamma)
    # Savings S = I - C* = I - I/(1+gamma) = I * (1 - 1/(1+gamma)) = I * (gamma/(1+gamma))
    # Savings Rate = S/I = gamma / (1+gamma)
    
    savings_rate = gamma / (1.0 + gamma)
    return savings_rate, lambda_val

def main():
    log("GATE 938: SAVINGS RATE AS BCP")
    
    scenarios = [
        {"name": "Poverty (I=1)", "income": 1.0},
        {"name": "Middle (I=10)", "income": 10.0},
        {"name": "Wealthy (I=100)", "income": 100.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_rate = -1.0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        rate, lam = solve_savings(scen['income'])
        log(f"Lambda: {lam:.3f}")
        log(f"Savings Rate: {rate:.3f}")
        
        if prev_rate == -1.0:
            pass
        elif rate >= prev_rate:
            validation_score += 1
            log("VALID: Savings rate increases with income.")
        else:
            log("INVALID: Savings rate decreased.")
            
        prev_rate = rate
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}")
    
    # Output results
    output = {
        "cycle": 3316,
        "phase": 189,
        "gate": 938,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3316_savings_rate.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 938 Complete.")

if __name__ == "__main__":
    main()
