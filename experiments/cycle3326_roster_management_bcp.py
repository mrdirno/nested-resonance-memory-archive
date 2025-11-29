
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3326] {msg}")

def run_roster_bcp(cap_budget):
    k = 1.0
    epsilon = 0.1
    lambda_cap = k / (epsilon + cap_budget)
    
    # Players
    # Star: Wins=10, Cost=50
    # Solid: Wins=5, Cost=10
    # Rookie: Wins=2, Cost=1
    
    players = [
        {"name": "Superstar", "wins": 10.0, "cost": 50.0},
        {"name": "Veteran", "wins": 5.0, "cost": 10.0},
        {"name": "Rookie", "wins": 2.0, "cost": 1.0}
    ]
    
    roster = []
    # Greedy BCP Selection
    # Calculate V per player
    for p in players:
        p['v'] = p['wins'] - (lambda_cap * p['cost'])
        
    players.sort(key=lambda x: x['v'], reverse=True)
    
    # Fill Roster (Slot limit 5? Budget limit Hard?)
    # Let's assume Hard Budget constraint too.
    
    spent = 0
    total_wins = 0
    
    for p in players:
        if p['v'] > 0 and spent + p['cost'] <= cap_budget:
            roster.append(p['name'])
            spent += p['cost']
            total_wins += p['wins']
            
    return roster, spent, lambda_cap

def main():
    log("GATE 945: ROSTER MANAGEMENT AS BCP")
    
    scenarios = [
        {"name": "Big Market (Yankees)", "budget": 200.0},
        {"name": "Small Market (Moneyball)", "budget": 20.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        roster, cost, lam = run_roster_bcp(scen['budget'])
        log(f"Lambda: {lam:.3f}")
        log(f"Roster: {roster}")
        
        if scen['name'] == "Big Market (Yankees)":
            # Should afford Superstar
            if "Superstar" in roster:
                validation_score += 1
                log("VALID: Buying wins at high cost.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Small Market (Moneyball)":
            # B=20. Star costs 50. Cannot afford.
            # Should pick Veteran (10) + Rookie (1) -> Cost 11. Wins 7.
            # λ ~ 0.05. V(Star) = 10 - 2.5 = 7.5. V > 0 but budget constraint kills it.
            if "Superstar" not in roster and "Veteran" in roster:
                validation_score += 1
                log("VALID: Value investing under constraint.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3326,
        "phase": 191,
        "gate": 945,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3326_roster_management.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 945 Complete.")

if __name__ == "__main__":
    main()
