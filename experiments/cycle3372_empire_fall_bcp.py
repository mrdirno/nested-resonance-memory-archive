
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3372] {msg}")

def run_empire_fall_bcp(complexity_load):
    # Budget is decreasing.
    # λ = k / (epsilon + B - Load).
    # Load is "Imperial Overstretch".
    # If Load > B, λ -> Infinity (Collapse).
    
    budget = 100.0 # Fixed base resource
    net_budget = budget - complexity_load
    
    if net_budget <= 0:
        lambda_val = 9999.0 # Collapse
        state = "COLLAPSE"
    else:
        k = 1.0
        epsilon = 0.1
        lambda_val = k / (epsilon + net_budget)
        state = "STABLE"
        
    # Maintenance Decision
    # V(Maintain) = Stability_Gain - λ * Maintenance_Cost
    # Stability = 100. Cost = 50.
    
    v_maintain = 100.0 - (lambda_val * 50.0)
    
    if v_maintain < 0:
        decision = "RETREAT" # Abandon provinces
    else:
        decision = "MAINTAIN"
        
    return decision, state, lambda_val

def main():
    log("GATE 981: EMPIRE FALL AS BCP")
    
    scenarios = [
        {"name": "Early Empire (Low Load)", "load": 10.0},
        {"name": "Peak Empire (High Load)", "load": 80.0},
        {"name": "Late Empire (Overload)", "load": 110.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (Load={scen['load']}) ---")
        dec, state, lam = run_empire_fall_bcp(scen['load'])
        log(f"Lambda: {lam:.3f}")
        log(f"State: {state}")
        log(f"Decision: {dec}")
        
        if scen['name'] == "Early Empire (Low Load)":
            # Net B = 90. λ low. Maintain.
            if dec == "MAINTAIN":
                validation_score += 1
                log("VALID: Robust.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Peak Empire (High Load)":
            # Net B = 20. λ = 0.05.
            # V = 100 - 2.5 = 97.5. Maintain.
            # But close to tipping point?
            # If Load=98. Net=2. λ=0.47. V=100-23=77.
            # If Load=99. Net=1. λ=0.9. V=100-45=55.
            # BCP is robust until Net B < 0?
            # V < 0 requires λ > 2.0.
            # 1/(0.1+Net) > 2 => Net < 0.4.
            # So Collapse and Retreat happen almost simultaneously at B ~ Load.
            if dec == "MAINTAIN":
                validation_score += 1
                log("VALID: Struggling but holding.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Late Empire (Overload)":
            # Net B < 0. Collapse.
            if state == "COLLAPSE":
                validation_score += 1
                log("VALID: Budget exhaustion = Collapse.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3372,
        "phase": 200,
        "gate": 981,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3372_empire_fall.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 981 Complete.")

if __name__ == "__main__":
    main()
