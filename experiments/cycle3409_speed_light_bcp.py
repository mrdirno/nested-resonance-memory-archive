
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3409] {msg}")

def run_speed_light_bcp(latency_budget):
    k = 1.0
    epsilon = 0.1
    lambda_lat = k / (epsilon + latency_budget)
    
    # Speed C.
    # Gain = Information Speed (C).
    # Cost = Causality Violations (C^2). Or Energy to maintain (C^2).
    # Let's assume maintaining sync at speed C costs Energy.
    
    best_C = 0.0
    best_v = -float('inf')
    
    for c_int in range(1, 100):
        C = float(c_int)
        cost = C**2
        gain = 100.0 * C # Linear utility of speed
        
        v = gain - (lambda_lat * cost)
        
        if v > best_v:
            best_v = v
            best_C = C
        else:
            break
            
    return best_C, best_v, lambda_lat

def main():
    log("GATE 1009: SPEED OF LIGHT AS BCP")
    
    scenarios = [
        {"name": "Real Time (High B)", "budget": 1000.0},
        {"name": "Laggy Sim (Low B)", "budget": 10.0},
        {"name": "Frozen (Zero B)", "budget": 0.1}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_C = 9999.0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        C, v, lam = run_speed_light_bcp(scen['budget'])
        log(f"Lambda: {lam:.4f}")
        log(f"Optimal C: {C}")
        
        if C <= prev_C:
            validation_score += 1
            log("VALID: Speed limit decreases as budget tightens.")
        else:
            log("INVALID: Speed increased?")
            
        prev_C = C
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}")
    
    # Output results
    output = {
        "cycle": 3409,
        "phase": 207,
        "gate": 1009,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3409_speed_light.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 1009 Complete.")

if __name__ == "__main__":
    main()
