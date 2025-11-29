
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3287] {msg}")

def run_review_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    strategies = [
        {"name": "Deep Read", "accuracy": 0.95, "cost": 10.0},
        {"name": "Abstract Scan", "accuracy": 0.70, "cost": 2.0},
        {"name": "Title/Author Scan", "accuracy": 0.55, "cost": 0.1}
    ]
    
    results = []
    for s in strategies:
        # V = Accuracy - λ * Cost
        v = s['accuracy'] - (lambda_val * s['cost'])
        results.append({
            "strategy": s['name'],
            "v": v,
            "acc": s['accuracy'],
            "cost": s['cost']
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 915: PEER REVIEW AS BCP")
    
    # Budget B = Reviewer Time/Energy
    
    # Deep vs Abstract: 0.95-10λ = 0.7-2λ => 0.25 = 8λ => λ = 0.031
    # B ~ 32.
    # Abstract vs Scan: 0.7-2λ = 0.55-0.1λ => 0.15 = 1.9λ => λ = 0.079
    # B ~ 12.
    
    scenarios = [
        {"name": "Sabbatical (Abundance)", "budget": 50.0}, # Expect Deep Read
        {"name": "Tenure Track (Busy)", "budget": 15.0},    # Expect Abstract Scan (Wait, λ=0.066 < 0.079. Should be Abstract)
        {"name": "Deadline Night (Crisis)", "budget": 2.0}  # Expect Scan
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_review_bcp(scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['strategy']} (V={best['v']:.3f})")
        
        if scen['name'] == "Sabbatical (Abundance)":
            if best['strategy'] == "Deep Read":
                validation_score += 1
                log("VALID: Time allows deep review.")
            else:
                log(f"INVALID: Expected Deep Read, got {best['strategy']}")
                
        elif scen['name'] == "Tenure Track (Busy)":
            # B=15 -> λ=0.066
            # Deep V = 0.95 - 0.66 = 0.29
            # Abstract V = 0.70 - 0.132 = 0.568
            # Scan V = 0.55 - 0.006 = 0.544
            # Abstract wins.
            if best['strategy'] == "Abstract Scan":
                validation_score += 1
                log("VALID: Busyness forces heuristics.")
            else:
                 log(f"INVALID: Expected Abstract Scan, got {best['strategy']}")

        elif scen['name'] == "Deadline Night (Crisis)":
            # B=2 -> λ=0.47
            # Deep V = 0.95 - 4.7 = -3.75
            # Abstract V = 0.70 - 0.94 = -0.24
            # Scan V = 0.55 - 0.047 = 0.503
            # Scan wins.
            if best['strategy'] == "Title/Author Scan":
                validation_score += 1
                log("VALID: Crisis forces superficiality.")
            else:
                 log(f"INVALID: Expected Scan, got {best['strategy']}")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3287,
        "phase": 183,
        "gate": 915,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3287_peer_review.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 915 Complete.")

if __name__ == "__main__":
    main()
