
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3363] {msg}")

def run_meta_bcp(budget_cards):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_cards)
    
    # Meta Game (e.g. Hearthstone/Magic)
    # Tier 1 Deck: Win Rate 60%. Cost 10000 Dust.
    # Budget Deck: Win Rate 50%. Cost 1000 Dust. 
    
    # V = WinRate - λ * Cost. 
    # WinRate in Utility units (1% = 10 Util).
    # Tier 1: 600 Util.
    # Budget: 500 Util.
    
    decks = [
        {"name": "Tier 1 (Meta)", "util": 600.0, "cost": 10000.0},
        {"name": "Budget Aggro", "util": 500.0, "cost": 1000.0}
    ]
    
    results = []
    for d in decks:
        # Hard constraint check?
        if d['cost'] > budget_cards:
            v = -9999.0
        else:
            v = d['util'] - (lambda_val * d['cost'])
            
        results.append({
            "deck": d['name'],
            "v": v
        })
        
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 974: META GAME AS BCP")
    
    scenarios = [
        {"name": "Pro Player (Full Collection)", "budget": 100000.0},
        {"name": "F2P Grinder", "budget": 2000.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        results, lam = run_meta_bcp(scen['budget'])
        
        best = results[0]
        log(f"Selected: {best['deck']} (V={best['v']:.2f})")
        
        if scen['name'] == "Pro Player (Full Collection)":
            # Affords both. Tier 1 Utility > Budget Utility.
            # λ is tiny. Cost irrelevant.
            if best['deck'] == "Tier 1 (Meta)":
                validation_score += 1
                log("VALID: Pro plays to win.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "F2P Grinder":
            # Budget 2000. Tier 1 Cost 10000.
            # Tier 1 impossible.
            if best['deck'] == "Budget Aggro":
                validation_score += 1
                log("VALID: F2P forced to Budget Aggro.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3363,
        "phase": 198,
        "gate": 974,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3363_meta_game.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 974 Complete.")

if __name__ == "__main__":
    main()
