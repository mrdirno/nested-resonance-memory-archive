
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3336] {msg}")

def run_surveillance_bcp(crime_rate, privacy_cost):
    # V = Safety_Gain - λ * Privacy_Loss
    # Safety Gain scales with Crime Rate.
    
    gain = crime_rate * 10.0 # Reduction in crime
    
    # Lambda is public tolerance for surveillance?
    # Let's assume λ=1.
    
    v = gain - privacy_cost
    
    decision = "INSTALL" if v > 0 else "REJECT"
    return decision, v

def main():
    log("GATE 953: SURVEILLANCE AS BCP")
    
    scenarios = [
        {"name": "High Crime Area", "crime": 10.0, "privacy": 50.0},
        {"name": "Safe Suburb", "crime": 1.0, "privacy": 50.0},
        {"name": "Totalitarian State", "crime": 10.0, "privacy": 0.0} # Privacy valued at 0
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        dec, v = run_surveillance_bcp(scen['crime'], scen['privacy'])
        log(f"Decision: {dec} (V={v:.2f})")
        
        if scen['name'] == "High Crime Area":
            # Gain 100. Cost 50. Install.
            if dec == "INSTALL":
                validation_score += 1
                log("VALID: Safety outweighs privacy.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Safe Suburb":
            # Gain 10. Cost 50. Reject.
            if dec == "REJECT":
                validation_score += 1
                log("VALID: Privacy outweighs minor safety gain.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Totalitarian State":
            # Gain 100. Cost 0. Install.
            if dec == "INSTALL":
                validation_score += 1
                log("VALID: No privacy cost = Max surveillance.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3336,
        "phase": 193,
        "gate": 953,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3336_surveillance.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 953 Complete.")

if __name__ == "__main__":
    main()
