
import sys
import os
import json
import math

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3286] {msg}")

class Experiment:
    def __init__(self, name, cost, power, false_positive_rate):
        self.name = name
        self.cost = cost
        self.power = power
        self.fpr = false_positive_rate

    def info_gain(self):
        # Simplified Info Gain metric: Power / FPR ratio (Signal-to-Noise)
        # Or just (Power - FPR)
        # Let's use a proxy: Quality = Power * (1 - FPR)
        return self.power * (1.0 - self.fpr)

def run_experiment_bcp(experiments, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    results = []
    for e in experiments:
        # V = Quality - λ * Cost
        quality = e.info_gain()
        v = quality - (lambda_val * e.cost)
        results.append({
            "experiment": e.name,
            "v": v,
            "quality": quality,
            "cost": e.cost
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 914: EXPERIMENT SELECTION AS BCP")
    
    # Experiments
    # Gold Standard: High Power, Low FPR, High Cost
    # Quick Study: Med Power, Med FPR, Low Cost
    # P-Hacking: Low Power, High FPR, Zero Cost (Just data mining)
    experiments = [
        Experiment("Gold Standard (RCT)", cost=10.0, power=0.95, false_positive_rate=0.05),
        Experiment("Quick Study (n=20)", cost=2.0, power=0.60, false_positive_rate=0.15),
        Experiment("Data Mining (P-Hack)", cost=0.1, power=0.40, false_positive_rate=0.40) # Quality=0.24
    ]
    
    # Quality:
    # Gold: 0.95 * 0.95 = 0.9025
    # Quick: 0.60 * 0.85 = 0.51
    # P-Hack: 0.40 * 0.60 = 0.24
    
    # Transitions:
    # Gold vs Quick: 0.9 - 10λ = 0.51 - 2λ => 0.39 = 8λ => λ = 0.048
    # B ~ 20.
    # Quick vs P-Hack: 0.51 - 2λ = 0.24 - 0.1λ => 0.27 = 1.9λ => λ = 0.14
    # B ~ 7.
    
    scenarios = [
        {"name": "NIH Grant (Abundance)", "budget": 50.0}, # Expect Gold
        {"name": "Department Funds", "budget": 10.0},      # Expect Quick
        {"name": "Unfunded Student", "budget": 1.0}        # Expect P-Hack
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_experiment_bcp(experiments, scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['experiment']} (V={best['v']:.3f})")
        
        if scen['name'] == "NIH Grant (Abundance)":
            if best['experiment'] == "Gold Standard (RCT)":
                validation_score += 1
                log("VALID: Abundance allows rigorous science.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Department Funds":
            # B=10 -> λ=0.1
            # Gold V = 0.9 - 1.0 = -0.1
            # Quick V = 0.51 - 0.2 = 0.31
            # P-Hack V = 0.24 - 0.01 = 0.23
            # Quick wins.
            if best['experiment'] == "Quick Study (n=20)":
                validation_score += 1
                log("VALID: Normal budget forces compromise (Sample Size).")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Unfunded Student":
            # B=1 -> λ=0.9
            # Gold V = 0.9 - 9 = -8.1
            # Quick V = 0.51 - 1.8 = -1.29
            # P-Hack V = 0.24 - 0.09 = 0.15
            # P-Hack wins.
            if best['experiment'] == "Data Mining (P-Hack)":
                validation_score += 1
                log("VALID: Scarcity incentivizes p-hacking (Survival).")
            else:
                 log("INVALID.")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3286,
        "phase": 183,
        "gate": 914,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3286_experiment_selection.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 914 Complete.")

if __name__ == "__main__":
    main()
