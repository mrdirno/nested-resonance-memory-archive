
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3302] {msg}")

def run_ad_bcp(l_money, l_time, price, duration):
    v_pay = -(l_money * price)
    v_watch = -(l_time * duration)
    
    decision = "PAY" if v_pay > v_watch else "WATCH_AD"
    return decision, v_pay, v_watch

def main():
    log("GATE 927: AD TOLERANCE AS BCP")
    
    price = 1.0 # Dollar
    duration = 30.0 # Seconds (Time unit)
    # Scale duration to "Monetary Equivalent"? 
    # Or just keep λ units consistent.
    # If λ_time = 1.0, then 1 sec = 1 unit of pain.
    # If λ_money = 1.0, then $1 = 1 unit of pain.
    
    scenarios = [
        {"name": "Rich & Busy", "l_money": 0.1, "l_time": 1.0},
        {"name": "Poor & Idle", "l_money": 10.0, "l_time": 0.01},
        {"name": "Poor & Busy (Worst Case)", "l_money": 10.0, "l_time": 1.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        dec, vp, vw = run_ad_bcp(scen['l_money'], scen['l_time'], price, duration)
        log(f"V(Pay): {vp:.2f} | V(Watch): {vw:.2f}")
        log(f"Decision: {dec}")
        
        if scen['name'] == "Rich & Busy":
            if dec == "PAY":
                validation_score += 1
                log("VALID: Time is money.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Poor & Idle":
            if dec == "WATCH_AD":
                validation_score += 1
                log("VALID: Money is time.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Poor & Busy (Worst Case)":
            # V(Pay)=-10. V(Watch)=-30.
            # Pay is "less bad".
            # But maybe they churn? V < Threshold.
            # Assuming they MUST consume content.
            if dec == "PAY":
                log("VALID: Forced to pay (Time is too scarce).")
                validation_score += 1
            else:
                # If V(Watch) > V(Pay), they watch.
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3302,
        "phase": 186,
        "gate": 927,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3302_ad_tolerance.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 927 Complete.")

if __name__ == "__main__":
    main()
