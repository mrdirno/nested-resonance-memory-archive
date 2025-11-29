
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3332] {msg}")

def run_risk_bcp(budget_mass):
    k = 1.0
    epsilon = 0.1
    lambda_mass = k / (epsilon + budget_mass)
    
    # Risk vs Payload
    # Option A: Single String. Payload 100%. Risk 50%.
    # Option B: Redundant. Payload 80%. Risk 10%.
    # Cost of Risk = Failure.
    # V = Payload * (1 - Risk) - (Payload if Fail?)
    # Or V = Expected Payload.
    # Exp(A) = 1.0 * 0.5 = 0.5.
    # Exp(B) = 0.8 * 0.9 = 0.72.
    # B always wins on Expectation?
    # But BCP adds λ * Cost (Mass).
    # If Mass is tight, maybe we can't afford Redundancy Mass (20%).
    # V = Payload_Value - λ * Mass.
    # If Mass Budget is fixed, we just maximize Utility within Budget.
    # Let's say Mission requires min Payload X.
    # If Budget < X/0.8, we CANNOT pick B.
    # Forced to pick A (Single String) or nothing.
    
    required_payload = 1.0
    mass_A = 1.0 # Just payload
    mass_B = 1.25 # Payload + Redundancy (1.25 * 0.8 = 1)
    
    # If Budget < 1.25, must pick A.
    # If Budget > 1.25, pick B (higher success rate).
    
    if budget_mass >= mass_B:
        decision = "REDUNDANT"
    elif budget_mass >= mass_A:
        decision = "SINGLE_STRING"
    else:
        decision = "ABORT"
        
    return decision

def main():
    log("GATE 950: RISK MANAGEMENT AS BCP")
    
    scenarios = [
        {"name": "Flagship (High Budget)", "budget": 5.0},
        {"name": "CubeSat (Low Budget)", "budget": 1.1},
        {"name": "Impossible", "budget": 0.5}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        dec = run_risk_bcp(scen['budget'])
        log(f"Decision: {dec}")
        
        if scen['name'] == "Flagship (High Budget)":
            if dec == "REDUNDANT":
                validation_score += 1
                log("VALID: Redundancy affordable.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "CubeSat (Low Budget)":
            if dec == "SINGLE_STRING":
                validation_score += 1
                log("VALID: Risk accepted due to mass constraints.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}") # Last one doesn't count
    
    # Output results
    output = {
        "cycle": 3332,
        "phase": 192,
        "gate": 950,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3332_risk_management.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 950 Complete.")

if __name__ == "__main__":
    main()
