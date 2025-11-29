
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3271] {msg}")

def kl_divergence(p, q):
    """
    Calculate KL Divergence between two Bernoulli distributions.
    p = posterior, q = prior
    """
    # Avoid log(0)
    epsilon = 1e-9
    p = max(epsilon, min(1-epsilon, p))
    q = max(epsilon, min(1-epsilon, q))
    
    return p * math.log(p/q) + (1-p) * math.log((1-p)/(1-q))

class DiagnosticTest:
    def __init__(self, name, cost, sensitivity, specificity):
        self.name = name
        self.cost = cost
        self.sens = sensitivity
        self.spec = specificity

    def expected_info_gain(self, prior_prob):
        """
        Calculate Expected Information Gain (KL Divergence)
        """
        # Prob of positive result: P(+) = P(+|D)P(D) + P(+|~D)P(~D)
        p_pos = self.sens * prior_prob + (1 - self.spec) * (1 - prior_prob)
        
        # Posterior if positive: P(D|+) = P(+|D)P(D) / P(+)
        post_pos = (self.sens * prior_prob) / p_pos
        
        # Posterior if negative: P(D|-) = P(-|D)P(D) / P(-)
        # P(-) = 1 - P(+)
        # P(-|D) = 1 - sens
        p_neg = 1 - p_pos
        post_neg = ((1 - self.sens) * prior_prob) / p_neg
        
        # Expected KL = P(+) * KL(post_pos || prior) + P(-) * KL(post_neg || prior)
        kl_pos = kl_divergence(post_pos, prior_prob)
        kl_neg = kl_divergence(post_neg, prior_prob)
        
        eig = p_pos * kl_pos + p_neg * kl_neg
        return eig

def run_diagnostic_bcp(tests, budget_b, prior):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    results = []
    for t in tests:
        eig = t.expected_info_gain(prior)
        # Gain is Info Gain, Cost is Resource Cost
        # We need to scale Info Gain to be comparable to Cost, or assume units match (Utils)
        # Let's assume 1 bit of info ~ 1 unit of utility for this simulation
        v = eig - (lambda_val * t.cost)
        results.append({
            "test": t.name,
            "gain": eig,
            "cost": t.cost,
            "v": v
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 902: DIAGNOSTIC PATH AS BCP")
    
    # Define Tests
    # MRI: High Cost, High Accuracy (High Gain)
    # X-Ray: Low Cost, Med Accuracy
    # Physical: Zero Cost, Low Accuracy
    tests = [
        DiagnosticTest("MRI Scan", cost=1.0, sensitivity=0.95, specificity=0.95),
        DiagnosticTest("X-Ray", cost=0.1, sensitivity=0.70, specificity=0.80),
        DiagnosticTest("Physical Exam", cost=0.01, sensitivity=0.60, specificity=0.60)
    ]
    
    prior_probability = 0.5 # Maximum entropy start
    
    scenarios = [
        {"name": "Rich Hospital (Abundance)", "budget": 10.0},
        {"name": "Rural Clinic (Scarcity)", "budget": 0.5},
        {"name": "Battlefield (Crisis)", "budget": 0.05}
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_diagnostic_bcp(tests, scen['budget'], prior_probability)
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['test']} (V={best['v']:.3f}, G={best['gain']:.3f}, C={best['cost']:.2f})")
        
        # Validation Logic
        if scen['name'] == "Rich Hospital":
            # Expect MRI
            if best['test'] == "MRI Scan":
                validation_score += 1
                log("VALID: Expensive test selected under abundance.")
            else:
                log(f"INVALID: Expected MRI, got {best['test']}")
        
        elif scen['name'] == "Rural Clinic":
            # Expect X-Ray (MRI too expensive)
            # MRI cost=1.0, lambda ~ 1/0.6 = 1.6. Cost penalty = 1.6. Gain ~ 0.6. V < 0.
            # X-Ray cost=0.1, penalty = 0.16. Gain ~ 0.2. V > 0.
            if best['test'] == "X-Ray":
                validation_score += 1
                log("VALID: Cost-effective test selected under scarcity.")
            else:
                 log(f"INVALID: Expected X-Ray, got {best['test']}")

        elif scen['name'] == "Battlefield":
            # Expect Physical or None
            if best['test'] == "Physical Exam":
                validation_score += 1
                log("VALID: Cheap test selected under crisis.")
            else:
                 log(f"INVALID: Expected Physical, got {best['test']}")
                 
        total_checks += 1
        
        # Print full ranking
        for r in results:
            log(f"  {r['test']}: V={r['v']:.3f}")

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3271,
        "phase": 180,
        "gate": 902,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3271_diagnostic_path.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 902 Complete.")

if __name__ == "__main__":
    main()
