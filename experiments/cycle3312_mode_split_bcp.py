
import sys
import os
import json
import random

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3312] {msg}")

def run_mode_split_bcp(agents, uber_cost, bus_time):
    uber_time = 20.0
    bus_cost = 2.0
    
    uber_count = 0
    bus_count = 0
    
    for a in agents:
        # V = -Time - λ * Cost
        v_uber = -uber_time - (a['lambda'] * uber_cost)
        v_bus = -bus_time - (a['lambda'] * bus_cost)
        
        if v_uber > v_bus:
            uber_count += 1
        else:
            bus_count += 1
            
    return uber_count, bus_count

def main():
    log("GATE 935: MODE SPLIT AS BCP")
    
    agents = []
    for i in range(100):
        b = random.uniform(1, 100)
        agents.append({'lambda': 1.0/(0.1+b)})
        
    scenarios = [
        {"name": "Baseline", "u_cost": 20.0, "b_time": 60.0},
        {"name": "Bus Priority (Faster Bus)", "u_cost": 20.0, "b_time": 40.0},
        {"name": "Uber Surge (Expensive Car)", "u_cost": 50.0, "b_time": 60.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_bus = -1
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        u, b = run_mode_split_bcp(agents, scen['u_cost'], scen['b_time'])
        log(f"Uber: {u}, Bus: {b}")
        
        if prev_bus == -1:
            pass
        elif b > prev_bus:
            validation_score += 1
            log("VALID: Bus share increased as relative value improved.")
        else:
            log("INVALID: Bus share stagnated/dropped.")
            
        prev_bus = b
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}")
    
    # Output results
    output = {
        "cycle": 3312,
        "phase": 188,
        "gate": 935,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3312_mode_split.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 935 Complete.")

if __name__ == "__main__":
    main()
