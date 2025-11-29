
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3321] {msg}")

def run_location_bcp(income):
    # Budget
    k = 1.0
    epsilon = 0.1
    lambda_money = k / (epsilon + income)
    
    # Value of Time (VOT) ~ Income / Time_Available?
    # Let's assume VOT scales linearly with Income.
    # VOT = Income / 200 (Hours per month).
    vot = income / 200.0
    
    # City
    rent_c = 2000.0
    time_c = 10.0 # hours/month
    cost_c = rent_c + (time_c * vot)
    v_city = - (lambda_money * cost_c)
    
    # Suburb
    rent_s = 1000.0
    time_s = 60.0 # hours/month
    cost_s = rent_s + (time_s * vot)
    v_suburb = - (lambda_money * cost_s)
    
    decision = "CITY" if v_city > v_suburb else "SUBURB"
    return decision, v_city, v_suburb

def main():
    log("GATE 941: LOCATION CHOICE AS BCP")
    
    scenarios = [
        {"name": "High Income ($10k)", "income": 10000.0},
        {"name": "Low Income ($2k)", "income": 2000.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        dec, vc, vs = run_location_bcp(scen['income'])
        log(f"V(City): {vc:.4f} | V(Suburb): {vs:.4f}")
        log(f"Decision: {dec}")
        
        if scen['name'] == "High Income ($10k)":
            # VOT = 50. City Cost = 2000 + 500 = 2500.
            # Suburb Cost = 1000 + 3000 = 4000.
            # City wins.
            if dec == "CITY":
                validation_score += 1
                log("VALID: Rich prefer time savings.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Low Income ($2k)":
            # VOT = 10. City Cost = 2000 + 100 = 2100.
            # Suburb Cost = 1000 + 600 = 1600.
            # Suburb wins.
            if dec == "SUBURB":
                validation_score += 1
                log("VALID: Poor prefer money savings.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3321,
        "phase": 190,
        "gate": 941,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3321_location_choice.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 941 Complete.")

if __name__ == "__main__":
    main()
