
import sys
import os

def log(msg):
    print(msg)

class EmployeeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_email(self, verify_cost, trust_cost, risk_loss):
        # Option A: Verify
        # Gain = 0 (Avoid risk), Cost = verify_cost
        v_verify = 0 - self.lambda_val * verify_cost
        
        # Option B: Trust (Click Link)
        # Gain = 0, Cost = trust_cost + Prob(Phish)*Risk
        # Assume Phish Probability = 0.1
        expected_loss = 0.1 * risk_loss
        # But users often underestimate risk or discount it.
        # Let's say they feel the Immediate Cost of clicking is low.
        v_trust = 0 - self.lambda_val * trust_cost - expected_loss
        
        return v_verify, v_trust

def main():
    log("======================================================================")
    log("CYCLE 3457: GATE 1036 - PHISHING AS BCP")
    log("Hypothesis: High λ (Busyness) forces users to skip Verification")
    log("======================================================================")
    
    verify_cost = 20.0 # Call sender, check URL carefully
    trust_cost = 1.0   # Click link
    risk_loss = 1000.0 # Compromise cost (often externalized to company)
    
    # But wait, the employee often doesn't bear the full risk loss.
    # Let's assume they bear a "Reputation Cost" of 50.
    perceived_risk = 50.0
    
    lambdas = [0.1, 1.0, 5.0] # Relaxed, Normal, Rushed
    
    log(f"{ 'STATE (λ)':<10} | {'V(VERIFY)':<10} | {'V(TRUST)':<10} | {'ACTION'}")
    log("-" * 50)
    
    for lam in lambdas:
        employee = EmployeeBCP(lambda_val=lam)
        
        # V_verify = -λ * 20
        # V_trust = -λ * 1 - (0.1 * 50) = -λ - 5
        
        v_v, v_t = employee.evaluate_email(verify_cost, trust_cost, perceived_risk)
        
        action = "VERIFY" if v_v > v_t else "CLICK (PHISHED)"
        log(f"{lam:<10} | {v_v:+.2f}      | {v_t:+.2f}      | {action}")
        
    log("\nFINDING: As λ increases (Busyness), V(Verify) drops faster than V(Trust).")
    log("         Eventually, the Cost of Verification exceeds the Perceived Risk.")
    log("         Phishing exploits the Cognitive Budget.")
    log("======================================================================")
    log("GATE 1036 COMPLETE: PHISHING EXPLOITS HIGH λ")
    log("======================================================================")

if __name__ == "__main__":
    main()
