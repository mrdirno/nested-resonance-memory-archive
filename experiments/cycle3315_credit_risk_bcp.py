
import sys
import os
import json
import random

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3315] {msg}")

class Borrower:
    def __init__(self, id, income, stability):
        self.id = id
        self.income = income
        self.stability = stability # 0 to 1
        # λ of Borrower: 1 / Income
        self.lambda_bor = 1.0 / (0.1 + income)
        
    def will_default(self, loan_payment):
        # V(Repay) = Credit_Score_Benefit - λ * Payment
        # V(Default) = -Stigma - λ * 0
        # Default if V(Repay) < V(Default)
        # Credit Benefit = 100. Stigma = 50.
        # 100 - λ * Payment < -50 => 150 < λ * Payment.
        
        threshold = 150.0
        pain = self.lambda_bor * loan_payment
        
        # Also random shock
        shock = random.uniform(0, 1)
        if shock > self.stability:
            return True
            
        if pain > threshold:
            return True
            
        return False

def run_credit_bcp(borrowers, interest_rate):
    loan_amt = 1000.0
    payment = loan_amt * (1.0 + interest_rate)
    
    defaults = 0
    for b in borrowers:
        if b.will_default(payment):
            defaults += 1
            
    return defaults

def main():
    log("GATE 937: CREDIT RISK AS BCP")
    
    # Generate Borrowers
    borrowers = []
    for i in range(100):
        # Income: 1 to 10 (Low to High)
        inc = random.uniform(1, 10)
        # Stability: 0.8 to 1.0
        stab = random.uniform(0.8, 1.0)
        borrowers.append(Borrower(i, inc, stab))
        
    scenarios = [
        {"name": "Low Rate (5%)", "rate": 0.05},
        {"name": "High Rate (20%)", "rate": 0.20},
        {"name": "Predatory (100%)", "rate": 1.00}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_def = -1
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} ---")
        defs = run_credit_bcp(borrowers, scen['rate'])
        log(f"Defaults: {defs}/100")
        
        if prev_def == -1:
            pass
        elif defs >= prev_def:
            validation_score += 1
            log("VALID: Defaults increase with rate (Payment pain).")
        else:
            log("INVALID: Defaults decreased?")
            
        prev_def = defs
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}")
    
    # Output results
    output = {
        "cycle": 3315,
        "phase": 189,
        "gate": 937,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3315_credit_risk.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 937 Complete.")

if __name__ == "__main__":
    main()
