
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3306] {msg}")

class Load:
    def __init__(self, name, utility, mw):
        self.name = name
        self.utility = utility # Value of Lost Load per MW
        self.mw = mw
        self.status = "ON"
        
    def __repr__(self):
        return f"{self.name}(Util={self.utility})"

def run_dr_bcp(loads, price_lambda):
    shed_mw = 0.0
    
    for load in loads:
        # V = Utility - Cost
        # Cost = Price
        v = load.utility - price_lambda
        
        if v < 0:
            load.status = "OFF"
            shed_mw += load.mw
        else:
            load.status = "ON"
            
    return shed_mw

def main():
    log("GATE 930: DEMAND RESPONSE AS BCP")
    
    loads = [
        Load("Pool Pump", 10.0, 1.0),
        Load("EV Charger", 50.0, 5.0),
        Load("Home AC", 200.0, 2.0),
        Load("Hospital", 10000.0, 5.0)
    ]
    
    scenarios = [
        {"name": "Normal ($5/MWh)", "price": 5.0},
        {"name": "Peak ($100/MWh)", "price": 100.0},
        {"name": "Scarcity ($1000/MWh)", "price": 1000.0}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (Price={scen['price']}) ---")
        shed = run_dr_bcp(loads, scen['price'])
        
        log(f"Shed Load: {shed} MW")
        for l in loads:
            log(f"  {l.name}: {l.status}")
            
        if scen['name'] == "Normal ($5/MWh)":
            # All On (Lowest utility is 10 > 5)
            if shed == 0:
                validation_score += 1
                log("VALID: Cheap energy serves all needs.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Peak ($100/MWh)":
            # Pool(10), EV(50) OFF. AC(200), Hosp(10000) ON.
            if loads[0].status == "OFF" and loads[1].status == "OFF" and loads[2].status == "ON":
                validation_score += 1
                log("VALID: Flexible loads shed.")
            else:
                log("INVALID.")
                
        elif scen['name'] == "Scarcity ($1000/MWh)":
            # AC(200) OFF. Only Hospital ON.
            if loads[2].status == "OFF" and loads[3].status == "ON":
                validation_score += 1
                log("VALID: Deep triage. Comfort sacrificed for critical.")
            else:
                log("INVALID.")
                
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3306,
        "phase": 187,
        "gate": 930,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3306_demand_response.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 930 Complete.")

if __name__ == "__main__":
    main()
