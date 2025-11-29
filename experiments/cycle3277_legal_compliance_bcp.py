
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3277] {msg}")

def run_compliance_bcp(compliance_cost, p_caught, penalty, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # V(Comply)
    # If Cost > Budget, we effectively CANNOT comply without going bust.
    # We model this as a massive penalty (Bankruptcy) or infinite lambda?
    # Standard BCP: V = -λ * Cost.
    v_comply = -(lambda_val * compliance_cost)
    
    # V(Violate)
    # Expected Penalty = P * Penalty
    v_violate = -(lambda_val * p_caught * penalty)
    
    # Decision
    # Note: If Cost > Budget, V_comply drops off a cliff in reality (bankruptcy).
    # But simple BCP just compares the values. 
    # Let's add a "Bankruptcy Constraint": If Cost > B, V_comply = -Infinity.
    
    if compliance_cost > budget_b:
        v_comply = -999999.0 # Forced violation
        log("  (Bankruptcy Constraint Active)")
        
    decision = "COMPLY" if v_comply > v_violate else "VIOLATE"
    
    return decision, v_comply, v_violate, lambda_val

def main():
    log("GATE 907: REGULATORY COMPLIANCE AS BCP")
    
    # Regulation Parameters
    compliance_cost = 10.0
    p_caught = 0.5
    penalty = 50.0
    
    # Expected Penalty = 0.5 * 50 = 25.0
    # Compliance Cost = 10.0
    # Rational Choice (Risk Neutral): 10 < 25 -> Comply.
    
    scenarios = [
        {"name": "Large Corp", "budget": 100.0},
        {"name": "Small Biz", "budget": 12.0},
        {"name": "Micro Biz (Insolvent)", "budget": 5.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        decision, v_comply, v_violate, lambda_val = run_compliance_bcp(
            compliance_cost, p_caught, penalty, scen['budget']
        )
        
        log(f"Lambda: {lambda_val:.3f}")
        log(f"V(Comply): {v_comply:.2f} | V(Violate): {v_violate:.2f}")
        log(f"Decision: {decision}")
        
        # Validation
        if scen['name'] == "Large Corp":
            if decision == "COMPLY":
                validation_score += 1
                log("VALID: Corp complies (Rational).")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Small Biz":
            # B=12 > Cost=10. Can comply.
            # V(C) = -λ*10. V(V) = -λ*25.
            # Should comply.
            if decision == "COMPLY":
                validation_score += 1
                log("VALID: Small Biz complies (Struggling but legal).")
            else:
                log("INVALID.")

        elif scen['name'] == "Micro Biz (Insolvent)":
            # B=5 < Cost=10. Bankruptcy Constraint.
            # Forced Violation.
            if decision == "VIOLATE":
                validation_score += 1
                log("VALID: Micro Biz forced to violate (Involuntary).")
            else:
                 log("INVALID.")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3277,
        "phase": 181,
        "gate": 907,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3277_legal_compliance.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 907 Complete.")

if __name__ == "__main__":
    main()
