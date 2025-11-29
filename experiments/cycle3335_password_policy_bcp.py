
import sys
import os
import json
import math

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3335] {msg}")

def run_password_bcp(threat_budget):
    k = 1.0
    epsilon = 0.1
    # If Threat Budget is High, λ is Low?
    # No, λ = Pain of Breach.
    # If Threat Budget is High, Breach Prob is High.
    # λ scales with Risk.
    # Risk = Prob * Impact.
    # Let's say λ_risk = 1 / (0.1 + 1/Threat).
    # Or simply λ_risk scales with Threat Level.
    
    lambda_risk = threat_budget # Higher threat -> Higher λ
    
    # Policies
    # 123456: Entropy 10. Cost 0.
    # CorrectHorse: Entropy 40. Cost 5.
    # 8X#v9$zL: Entropy 60. Cost 20 (Memory).
    
    policies = [
        {"name": "Weak (123456)", "entropy": 10.0, "cost": 0.0},
        {"name": "Passphrase (CorrectHorse)", "entropy": 40.0, "cost": 5.0},
        {"name": "Complex (8X#v9$zL)", "entropy": 60.0, "cost": 20.0}
    ]
    
    # V = Security - Cost?
    # Security = 1 - P(Breach).
    # P(Breach) = exp(-Entropy / Threat).
    # V = (1 - P(Breach)) * Impact - Cost.
    # Impact = 1000.
    
    impact = 1000.0
    
    results = []
    for p in policies:
        prob_breach = math.exp(-p['entropy'] / threat_budget)
        security_val = (1.0 - prob_breach) * impact
        
        v = security_val - p['cost'] # Cost is effort.
        
        results.append({
            "policy": p['name'],
            "v": v,
            "prob": prob_breach
        })
        
    results.sort(key=lambda x: x['v'], reverse=True)
    return results

def main():
    log("GATE 952: PASSWORD POLICY AS BCP")
    
    scenarios = [
        {"name": "Low Threat (Casual)", "threat": 5.0},
        {"name": "Med Threat (Banking)", "threat": 20.0},
        {"name": "High Threat (State Actor)", "threat": 100.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (Threat={scen['threat']}) ---")
        results = run_password_bcp(scen['threat'])
        
        best = results[0]
        log(f"Selected: {best['policy']} (V={best['v']:.2f})")
        
        if scen['name'] == "Low Threat (Casual)":
            # Threat=5. 
            # Weak: P=exp(-2)=0.13. Val=870. V=870.
            # Passphrase: P=exp(-8)=0. Val=1000. V=995.
            # Complex: P=0. Val=1000. V=980.
            # Passphrase wins. (Good security, low cost).
            if best['policy'] == "Passphrase (CorrectHorse)":
                validation_score += 1
                log("VALID: Good enough security.")
            elif best['policy'] == "Weak (123456)":
                # Maybe valid for casual?
                pass
            else:
                log("INVALID.")
                
        elif scen['name'] == "Med Threat (Banking)":
            # Threat=20.
            # Weak: P=exp(-0.5)=0.6. Val=400. V=400.
            # Passphrase: P=exp(-2)=0.13. Val=870. V=865.
            # Complex: P=exp(-3)=0.05. Val=950. V=930.
            # Complex wins.
            if best['policy'] == "Complex (8X#v9$zL)":
                validation_score += 1
                log("VALID: High risk requires high entropy.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "High Threat (State Actor)":
            # Threat=100.
            # Weak: P=0.9. V=100.
            # Pass: P=0.67. V=330.
            # Comp: P=0.54. V=460-20=440.
            # Complex still wins.
            if best['policy'] == "Complex (8X#v9$zL)":
                validation_score += 1
                log("VALID: Max security.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3335,
        "phase": 193,
        "gate": 952,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3335_password_policy.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 952 Complete.")

if __name__ == "__main__":
    main()
