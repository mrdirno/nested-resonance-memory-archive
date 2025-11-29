
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3337] {msg}")

def run_access_bcp(threat_level):
    k = 1.0
    epsilon = 0.1
    lambda_risk = k / (epsilon + (1.0/threat_level)) 
    # If Threat is high, 1/Threat is low. λ is High.
    # Wait. Threat High -> Risk Expensive.
    # Cost of Openness = Threat * Impact.
    # V = Convenience - λ * Risk.
    # If Threat is High, Risk is High.
    # V < 0 -> Restrict Access.
    
    policies = [
        {"name": "Open", "conv": 100.0, "risk": 50.0},
        {"name": "Restricted", "conv": 20.0, "risk": 5.0}
    ]
    
    # Assume λ=1. Just compare V.
    # But Risk scales with Threat Level.
    
    results = []
    for p in policies:
        risk_val = p['risk'] * threat_level
        v = p['conv'] - risk_val
        results.append({
            "policy": p['name'],
            "v": v
        })
        
    results.sort(key=lambda x: x['v'], reverse=True)
    return results

def main():
    log("GATE 954: ACCESS CONTROL AS BCP")
    
    scenarios = [
        {"name": "Public Library (Low Threat)", "threat": 0.1},
        {"name": "Nuclear Silo (High Threat)", "threat": 100.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        results = run_access_bcp(scen['threat'])
        
        best = results[0]
        log(f"Selected: {best['policy']} (V={best['v']:.2f})")
        
        if scen['name'] == "Public Library (Low Threat)":
            # Risk low. Openness high.
            if best['policy'] == "Open":
                validation_score += 1
                log("VALID: Open access for public goods.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Nuclear Silo (High Threat)":
            # Risk huge. Restrict.
            if best['policy'] == "Restricted":
                validation_score += 1
                log("VALID: Restricted access for critical assets.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3337,
        "phase": 193,
        "gate": 954,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3337_access_control.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 954 Complete.")

if __name__ == "__main__":
    main()
