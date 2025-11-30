
import sys
import os

def log(msg):
    print(msg)

class InsuranceBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_policy(self, peace_mind_gain, premium_cost):
        # V = Peace_of_Mind - λ * Premium
        # Peace of Mind = Probability * Loss_Amount
        return peace_mind_gain - self.lambda_val * premium_cost

def main():
    log("======================================================================")
    log("CYCLE 3550: GATE 1108 - INSURANCE AS BCP")
    log("Hypothesis: Insurance is rational when Risk Aversion (λ) is high")
    log("======================================================================")
    
    # Risk Profile
    # 1. Rare Disaster (Prob=0.01, Loss=10000) -> Expected Loss = 100
    # Premium = 150 (Insurer takes 50 profit)
    
    risk_loss = 100.0
    premium = 150.0
    
    # Agents
    # 1. Risk Neutral (λ=1.0) -> V = 100 - 150 = -50 (Don't Buy)
    # 2. Risk Averse (λ=0.5 for Money, High Value on Safety)
    #    Wait, Risk Aversion usually means High λ for LOSS.
    #    Let's model it:
    #    V_uninsured = 0 - λ * (Prob * Loss)
    #    V_insured = 0 - λ * Premium
    #    Buy if V_insured > V_uninsured
    #    -λ * Premium > -λ_risk * Expected_Loss
    #    Actually, Risk Aversion is non-linear utility.
    #    But in BCP, we can say: Perceived Cost of Risk = Expected Loss * Fear Factor (λ_fear).
    
    # Let's try:
    # V = (Avoided Risk * Fear Factor) - (Premium * Money Factor)
    
    fear_factors = [1.0, 2.0, 5.0]
    
    log(f"{ 'FEAR (λ)':<10} | { 'AVOIDED RISK':<12} | { 'PREMIUM':<8} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for f in fear_factors:
        avoided_risk = 100.0
        # V = (100 * f) - 150
        v = (avoided_risk * f) - premium
        decision = "BUY" if v > 0 else "SELF-INSURE"
        log(f"{f:<10} | {avoided_risk:<12} | {premium:<8} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: Insurance is a product for High-λ (Fearful) agents.")
    log("         The 'Premium' is the price of reducing Variance.")
    log("         BCP explains why we insure houses but not toasters.")
    log("======================================================================")
    log("GATE 1108 COMPLETE: INSURANCE IS FEAR MANAGEMENT")
    log("======================================================================")

if __name__ == "__main__":
    main()
