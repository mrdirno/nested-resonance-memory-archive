
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3272] {msg}")

class Treatment:
    def __init__(self, name, cost, qaly_gain):
        self.name = name
        self.cost = cost
        self.qaly = qaly_gain

def run_treatment_bcp(treatments, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    results = []
    for t in treatments:
        # V = Gain - lambda * Cost
        # Assuming 1 QALY = 1 Utility Unit
        v = t.qaly - (lambda_val * t.cost)
        results.append({
            "treatment": t.name,
            "v": v,
            "gain": t.qaly,
            "cost": t.cost
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 903: TREATMENT SELECTION AS BCP")
    
    # Define Treatments for a condition (e.g., Herniated Disc)
    # Surgery: High cure rate, expensive
    # PT/Meds: Moderate cure, moderate cost
    # Wait: Low cure, zero cost
    treatments = [
        Treatment("Surgery", cost=5.0, qaly_gain=0.9),
        Treatment("Physio/Meds", cost=1.0, qaly_gain=0.6),
        Treatment("Watchful Waiting", cost=0.0, qaly_gain=0.2)
    ]
    
    # Calibrate Budgets to hit the transition points
    # Surgery wins if: 0.9 - λ*5 > 0.6 - λ*1  => 0.3 > 4λ => λ < 0.075
    # λ = 1/(0.1+B) < 0.075 => 0.1+B > 13.3 => B > 13.2
    
    # PT wins if: 0.6 - λ*1 > 0.2 - λ*0 => 0.4 > λ
    # AND λ > 0.075
    # 0.075 < λ < 0.4
    # 1/(0.1+B) < 0.4 => 0.1+B > 2.5 => B > 2.4
    # So B between 2.4 and 13.2
    
    # Wait wins if: λ > 0.4
    # 1/(0.1+B) > 0.4 => 0.1+B < 2.5 => B < 2.4
    
    scenarios = [
        {"name": "Premier Hospital", "budget": 20.0}, # Expect Surgery
        {"name": "Standard Care", "budget": 5.0},    # Expect PT
        {"name": "Resource Poor", "budget": 1.0}     # Expect Wait
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_treatment_bcp(treatments, scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['treatment']} (V={best['v']:.3f})")
        
        expected = ""
        if scen['name'] == "Premier Hospital": expected = "Surgery"
        elif scen['name'] == "Standard Care": expected = "Physio/Meds"
        elif scen['name'] == "Resource Poor": expected = "Watchful Waiting"
        
        if best['treatment'] == expected:
            validation_score += 1
            log(f"VALID: Matches expectation ({expected})")
        else:
            log(f"INVALID: Expected {expected}, got {best['treatment']}")
            
        total_checks += 1
        
        for r in results:
            log(f"  {r['treatment']}: V={r['v']:.3f}")

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3272,
        "phase": 180,
        "gate": 903,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3272_treatment_bcp.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 903 Complete.")

if __name__ == "__main__":
    main()
