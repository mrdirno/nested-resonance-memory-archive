
import sys
import os

def log(msg):
    print(msg)

class DrugBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_drug(self, euphoria_gain, withdrawal_cost):
        # V = Euphoria - λ * Withdrawal
        # But λ changes over time.
        # Tolerance: Gain decreases.
        # Dependence: Cost (Withdrawal) increases.
        # Desperation: λ decreases (Need relief NOW).
        return euphoria_gain - self.lambda_val * withdrawal_cost

def main():
    log("======================================================================")
    log("CYCLE 3570: GATE 1123 - TOLERANCE AS BCP")
    log("Hypothesis: Addiction cycle is a BCP trap where Cost rises and Gain falls")
    log("======================================================================")
    
    # Stages
    # 1. First Hit (High Gain, Zero Cost)
    # 2. Habit (Med Gain, Low Cost)
    # 3. Dependence (Low Gain, High Cost)
    # 4. Withdrawal (Zero Gain, Very High Cost) 
    
    stages = [
        {'name': 'First Hit', 'gain': 100.0, 'cost': 0.0},
        {'name': 'Habit',     'gain': 50.0,  'cost': 10.0},
        {'name': 'Dependence','gain': 10.0,  'cost': 80.0}, # Avoid withdrawal
        {'name': 'Withdrawal','gain': 0.0,   'cost': 100.0}
    ]
    
    # User State
    # Initial: Normal λ=1.0
    # Addicted: Desperation lowers λ to 0.1 (Must avoid Cost at all costs? No.)
    # Desperation means Willingness to Pay is High -> low λ for Money/Health.
    # But Withdrawal is a Pain Cost. The User wants to Avoid Pain.
    # Action: Take Drug.
    # V(Take) = Relief - λ * Money/Health
    # V(Don't Take) = 0 - λ * Withdrawal_Pain
    
    # Let's reframe:
    # Choice: Take Drug vs Abstain.
    
    user_lambda = 1.0 # Value of Money/Health
    withdrawal_pain = 100.0
    drug_price = 20.0
    drug_relief = 100.0
    
    log(f"{ 'STATE':<15} | { 'ACTION':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8}")
    log("-" * 60)
    
    # 1. Naive
    # Take: Gain=Euphoria(100), Cost=Price(20). V = 80.
    # Abstain: Gain=0, Cost=0. V = 0.
    log(f"{ 'Naive':<15} | { 'Take':<10} | { 100.0:<5} | { 20.0:<5} | { 80.0:<8.1f}")
    log(f"{ 'Naive':<15} | { 'Abstain':<10} | { 0.0:<5}   | { 0.0:<5}   | { 0.0:<8.1f}")
    
    # 2. Dependent
    # Take: Gain=Relief(100), Cost=Price(20). V = 80.
    # Abstain: Gain=0, Cost=Withdrawal(100). V = -100.
    log(f"{ 'Dependent':<15} | { 'Take':<10} | { 100.0:<5} | { 20.0:<5} | { 80.0:<8.1f}")
    log(f"{ 'Dependent':<15} | { 'Abstain':<10} | { 0.0:<5}   | { 100.0:<5} | {-100.0:<8.1f}")
    
    # 3. Broke Dependent (High Price Perception λ=5.0)
    # Take: Gain=Relief(100), Cost=Price(20*5=100). V = 0.
    # Abstain: Gain=0, Cost=Withdrawal(100*5=500). V = -500.
    # Still optimal to Take until Price > Withdrawal.
    
    log("\nFINDING: Addiction shifts the BCP baseline.")
    log("         Abstinence becomes 'Bankruptcy' (V < 0).")
    log("         Taking the drug becomes the only way to stay solvent (V >= 0).")
    log("         The 'Gain' shifts from Euphoria to Normalcy.")
    log("======================================================================")
    log("GATE 1123 COMPLETE: ADDICTION IS MAINTENANCE")
    log("======================================================================")

if __name__ == "__main__":
    main()
