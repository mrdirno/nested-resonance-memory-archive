
import sys
import os
import random
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3275] {msg}")

class Document:
    def __init__(self, id, relevance_prob, impact):
        self.id = id
        self.prob = relevance_prob
        self.impact = impact
        
    def __repr__(self):
        return f"D{self.id}(P={self.prob:.2f}, I={self.impact:.2f})"

def run_discovery_bcp(docs, budget_b, review_cost_per_doc):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    reviewed_docs = []
    total_cost = 0
    
    # Calculate V for all docs
    scored_docs = []
    for d in docs:
        # Gain = Prob * Impact
        gain = d.prob * d.impact
        v = gain - (lambda_val * review_cost_per_doc)
        scored_docs.append((d, v))
    
    # Sort by V
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    # Review until V < 0 or Budget Exhausted (Soft constraint: V < 0 stops us)
    # In BCP, V < 0 means "Not worth doing".
    
    for d, v in scored_docs:
        if v > 0:
            if total_cost + review_cost_per_doc <= budget_b: # Hard budget check too
                reviewed_docs.append(d)
                total_cost += review_cost_per_doc
            else:
                break # Budget exhausted
        else:
            break # Not worth reviewing
            
    return reviewed_docs, lambda_val

def main():
    log("GATE 905: LEGAL DISCOVERY AS BCP")
    
    # Generate Corpus
    # 100 Docs
    # 10 "Smoking Guns" (High Prob, High Impact)
    # 90 Noise (Low Prob)
    docs = []
    for i in range(10):
        docs.append(Document(i, 0.9, 10.0)) # Smoking Gun
    for i in range(90):
        docs.append(Document(10+i, 0.1, 1.0)) # Noise
        
    # Scenarios
    # 1. Manual Review (Cost = 1.0)
    # 2. TAR (Cost = 0.1)
    
    scenarios = [
        {"name": "Manual Review (Abundance)", "budget": 50.0, "cost": 1.0},
        {"name": "Manual Review (Scarcity)", "budget": 5.0, "cost": 1.0},
        {"name": "TAR (Scarcity)", "budget": 5.0, "cost": 0.1}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}, C={scen['cost']}) ---")
        reviewed, lambda_val = run_discovery_bcp(docs, scen['budget'], scen['cost'])
        
        count = len(reviewed)
        smoking_guns = sum(1 for d in reviewed if d.impact == 10.0)
        
        log(f"Reviewed: {count}/100")
        log(f"Smoking Guns Found: {smoking_guns}/10")
        log(f"Lambda: {lambda_val:.3f}")
        
        # Validation
        if scen['name'] == "Manual Review (Abundance)":
            # Should get all smoking guns + some noise
            if smoking_guns == 10:
                validation_score += 1
                log("VALID: High budget finds truth.")
            else:
                log("INVALID: Missed smoking guns.")
                
        elif scen['name'] == "Manual Review (Scarcity)":
            # Budget 5.0, Cost 1.0 -> Max 5 docs.
            # Should find 5 smoking guns (highest V).
            if count == 5 and smoking_guns == 5:
                validation_score += 1
                log("VALID: Triage works (Top 5 found).")
            else:
                log(f"INVALID: Reviewed {count}, Found {smoking_guns}")
                
        elif scen['name'] == "TAR (Scarcity)":
            # Budget 5.0, Cost 0.1 -> Max 50 docs.
            # Should find all 10 smoking guns + 40 noise.
            if smoking_guns == 10:
                validation_score += 1
                log("VALID: TAR enables full recall under scarcity.")
            else:
                 log("INVALID: TAR failed.")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3275,
        "phase": 181,
        "gate": 905,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3275_legal_discovery.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 905 Complete.")

if __name__ == "__main__":
    main()
