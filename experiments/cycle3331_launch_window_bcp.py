
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3331] {msg}")

def run_launch_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Launch Window (Delay vs dV)
    # Wait 0 months: dV penalty 2000 m/s.
    # Wait 6 months: dV penalty 500 m/s.
    # Wait 26 months: dV penalty 0 m/s (Hohmann).
    
    # V = -(Penalty_dV) - (λ * Delay_Cost)
    # Delay Cost in m/s equivalent?
    # If Budget is "Patience/Funding", then λ converts Time to "Pain".
    # 1 Month = 100 m/s penalty equivalent?
    
    options = [
        {"name": "Launch Now (Off-Hohmann)", "dv_pen": 2000.0, "delay": 0.0},
        {"name": "Wait 6mo (Intermediate)", "dv_pen": 500.0, "delay": 6.0},
        {"name": "Wait 26mo (Optimal)", "dv_pen": 0.0, "delay": 26.0}
    ]
    
    results = []
    for o in options:
        # Pain of Delay scaled by λ
        # Assume 1 month delay = 100 units of dV pain at λ=1.
        # V = -dV - λ * (Delay * 100)
        v = -o['dv_pen'] - (lambda_val * o['delay'] * 100.0)
        results.append({
            "option": o['name'],
            "v": v
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 949: LAUNCH WINDOW AS BCP")
    
    # Budget B = Program Patience / Funding Runway
    scenarios = [
        {"name": "Long Term (NASA)", "budget": 100.0},
        {"name": "Start-up (Burn Rate)", "budget": 2.0},
        {"name": "War (Panic)", "budget": 0.1}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lam = run_launch_bcp(scen['budget'])
        log(f"Lambda: {lam:.3f}")
        
        best = results[0]
        log(f"Selected: {best['option']} (V={best['v']:.2f})")
        
        if scen['name'] == "Long Term (NASA)":
            # B=100 -> λ=0.01. Delay is cheap.
            # Now: -2000. Wait 26mo: -0 - 0.01*2600 = -26.
            # Wait wins.
            if best['option'] == "Wait 26mo (Optimal)":
                validation_score += 1
                log("VALID: Patience allows optimal physics.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Start-up (Burn Rate)":
            # B=2 -> λ=0.47.
            # Now: -2000.
            # Wait 6mo: -500 - 0.47*600 = -782.
            # Wait 26mo: -0 - 0.47*2600 = -1222.
            # Wait 6mo wins (Intermediate).
            if best['option'] == "Wait 6mo (Intermediate)":
                validation_score += 1
                log("VALID: Tradeoff between fuel and burn rate.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "War (Panic)":
            # B=0.1 -> λ=5.0.
            # Now: -2000.
            # Wait 6mo: -500 - 3000 = -3500.
            # Launch NOW.
            if best['option'] == "Launch Now (Off-Hohmann)":
                validation_score += 1
                log("VALID: Panic overrides physics (Brute force).")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3331,
        "phase": 192,
        "gate": 949,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3331_launch_window.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 949 Complete.")

if __name__ == "__main__":
    main()
