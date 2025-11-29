
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3320] {msg}")

def run_housing_bcp(capital_b, income_stream):
    k = 1.0
    epsilon = 0.1
    # Lambda depends on Capital Stock (for Downpayment) AND Income (for Monthly)
    # Let's use Capital for Upfront pain.
    lambda_cap = k / (epsilon + capital_b)
    
    # Buy Parameters
    downpayment = 20.0
    monthly_buy = 1.0
    equity_gain = 0.5 # Part of monthly that is savings
    
    # Rent Parameters
    downpayment_rent = 0.0
    monthly_rent = 1.5
    
    # V = Net_Value - λ * Pain
    # Let's look at 1-year horizon?
    # Or just the decision moment.
    
    # Constraint Check
    if downpayment > capital_b:
        v_buy = -999.0
    else:
        # V(Buy) = Equity_Gain*12 - λ * Downpayment - λ_inc * (Monthly*12)?
        # Simplified: V = Equity - λ * Cost.
        # Treat Monthly as flow. Treat Downpayment as stock.
        # V_buy = (Equity_Gain * 12) - (lambda_cap * downpayment) - (lambda_cap * monthly_buy * 12)
        # Note: Using same lambda for monthly implies income and capital are fungible.
        v_buy = (equity_gain * 12) - (lambda_cap * (downpayment + monthly_buy * 12))
        
    v_rent = 0.0 - (lambda_cap * (downpayment_rent + monthly_rent * 12))
    
    decision = "BUY" if v_buy > v_rent else "RENT"
    return decision, v_buy, v_rent, lambda_cap

def main():
    log("GATE 940: RENT VS BUY AS BCP")
    
    scenarios = [
        {"name": "Wealthy (Cap=100)", "capital": 100.0},
        {"name": "Middle (Cap=30)", "capital": 30.0},
        {"name": "Poor (Cap=5)", "capital": 5.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        dec, vb, vr, lam = run_housing_bcp(scen['capital'], 0)
        log(f"Lambda: {lam:.3f}")
        log(f"V(Buy): {vb:.2f} | V(Rent): {vr:.2f}")
        log(f"Decision: {dec}")
        
        if scen['name'] == "Wealthy (Cap=100)":
            # Can buy. Equity gain should win.
            if dec == "BUY":
                validation_score += 1
                log("VALID: Wealthy buy assets.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Middle (Cap=30)":
            # Can buy (30 > 20).
            # Downpayment pain: 20 * 0.03 = 0.6.
            # Equity gain: 6.
            # V(Buy) should be positive?
            if dec == "BUY":
                validation_score += 1
                log("VALID: Middle class stretches to buy.")
            else:
                log("INVALID: Renting preferred?")
                
        elif scen['name'] == "Poor (Cap=5)":
            # Cannot buy (5 < 20). Constraint active.
            if dec == "RENT":
                validation_score += 1
                log("VALID: Poor forced to rent.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3320,
        "phase": 190,
        "gate": 940,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3320_rent_vs_buy.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 940 Complete.")

if __name__ == "__main__":
    main()
