
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3291] {msg}")

class Material:
    def __init__(self, name, quality, cost):
        self.name = name
        self.quality = quality
        self.cost = cost
        
    def __repr__(self):
        return f"{self.name}(Q={self.quality}, C={self.cost})"

def run_material_bcp(materials, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    results = []
    for m in materials:
        v = m.quality - (lambda_val * m.cost)
        results.append({
            "material": m.name,
            "v": v,
            "quality": m.quality,
            "cost": m.cost
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 918: MATERIAL SELECTION AS BCP")
    
    # Materials
    materials = [
        Material("Steel/Concrete", 10.0, 10.0),
        Material("Wood Frame", 6.0, 4.0),
        Material("Mud Brick", 3.0, 1.0)
    ]
    
    # Steel vs Wood: 10-10λ = 6-4λ => 4=6λ => λ=0.66. B~1.4.
    # Wood vs Mud: 6-4λ = 3-1λ => 3=3λ => λ=1.0. B~0.9.
    
    # Ranges:
    # B > 1.4: Steel
    # 0.9 < B < 1.4: Wood
    # B < 0.9: Mud
    
    scenarios = [
        {"name": "Skyscraper (High B)", "budget": 10.0}, # Expect Steel
        {"name": "Suburban House (Med B)", "budget": 1.0}, # Expect Wood
        {"name": "Rural Shelter (Low B)", "budget": 0.5}   # Expect Mud
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_material_bcp(materials, scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['material']} (V={best['v']:.3f})")
        
        expected = ""
        if scen['name'] == "Skyscraper (High B)": expected = "Steel/Concrete"
        elif scen['name'] == "Suburban House (Med B)": expected = "Wood Frame"
        elif scen['name'] == "Rural Shelter (Low B)": expected = "Mud Brick"
        
        if best['material'] == expected:
            validation_score += 1
            log(f"VALID: Matches expectation ({expected})")
        else:
            log(f"INVALID: Expected {expected}, got {best['material']}")
            
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3291,
        "phase": 184,
        "gate": 918,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3291_material_selection.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 918 Complete.")

if __name__ == "__main__":
    main()
