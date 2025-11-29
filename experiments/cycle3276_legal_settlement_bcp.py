
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3276] {msg}")

def run_settlement_bcp(p_win, award, cost, offer, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # V(Trial)
    expected_gain = p_win * award
    v_trial = expected_gain - (lambda_val * cost)
    
    # V(Settle)
    # Gain is Offer. Cost is ~0 (negotiation cost assumed paid).
    v_settle = offer
    
    decision = "TRIAL" if v_trial > v_settle else "SETTLE"
    
    return decision, v_trial, v_settle, lambda_val

def main():
    log("GATE 906: SETTLEMENT VS TRIAL AS BCP")
    
    # Case Parameters
    p_win = 0.8
    award = 100.0
    cost = 20.0
    offer = 50.0
    
    # Expected Value of Trial = 0.8 * 100 = 80.0
    # Cost = 20.0
    # Offer = 50.0
    # Risk Neutral (λ=0): 80 > 50 -> Trial
    
    # Break-even: 80 - λ*20 = 50 => 30 = 20λ => λ = 1.5
    # λ = 1/(0.1+B) = 1.5 => 0.1+B = 0.66 => B = 0.56
    
    scenarios = [
        {"name": "Deep Pockets (Corp)", "budget": 100.0},
        {"name": "Middle Class (Individual)", "budget": 2.0},
        {"name": "Indigent (No Funds)", "budget": 0.1}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        decision, v_trial, v_settle, lambda_val = run_settlement_bcp(
            p_win, award, cost, offer, scen['budget']
        )
        
        log(f"Lambda: {lambda_val:.3f}")
        log(f"V(Trial): {v_trial:.2f} | V(Settle): {v_settle:.2f}")
        log(f"Decision: {decision}")
        
        # Validation
        if scen['name'] == "Deep Pockets (Corp)":
            # λ ~ 0.01. V(T) ~ 80 - 0.2 = 79.8 > 50. Trial.
            if decision == "TRIAL":
                validation_score += 1
                log("VALID: Wealthy plaintiff pursues justice.")
            else:
                log("INVALID: Should have chosen Trial.")
                
        elif scen['name'] == "Middle Class (Individual)":
            # λ ~ 1/(2.1) = 0.47. V(T) = 80 - 9.4 = 70.6 > 50. Trial.
            # Wait, my break-even calc above was B=0.56. So B=2.0 is still Trial territory.
            if decision == "TRIAL":
                validation_score += 1
                log("VALID: Moderate budget still fights strong case.")
            else:
                 log("INVALID: Should have chosen Trial.")

        elif scen['name'] == "Indigent (No Funds)":
            # λ ~ 1/(0.2) = 5.0. V(T) = 80 - 100 = -20. V(Settle) = 50.
            # Settle.
            if decision == "SETTLE":
                validation_score += 1
                log("VALID: Poor plaintiff forced to settle (coerced).")
            else:
                 log("INVALID: Should have settled.")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3276,
        "phase": 181,
        "gate": 906,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3276_legal_settlement.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 906 Complete.")

if __name__ == "__main__":
    main()
