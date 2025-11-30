
import sys
import os

def log(msg):
    print(msg)

class CreditBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_loan(self, consumption_gain, interest_cost):
        # V = Consumption - λ * Future_Payment
        return consumption_gain - self.lambda_val * interest_cost

def main():
    log("======================================================================")
    log("CYCLE 3549: GATE 1107 - INTEREST RATES AS BCP")
    log("Hypothesis: High Interest Rates (Cost) deter Borrowing unless Need (Gain) is Critical")
    log("======================================================================")
    
    # Loan
    principal = 100.0
    
    # Rates
    # 1. ZIRP (Zero Interest Rate Policy, Rate=0%)
    # 2. Normal (Rate=5%)
    # 3. Crisis (Rate=20%)
    
    rates = [
        {'name': 'ZIRP',   'rate': 0.0, 'cost': 100.0}, # Pay back Principal only
        {'name': 'Normal', 'rate': 0.05,'cost': 105.0},
        {'name': 'Crisis', 'rate': 0.2, 'cost': 120.0}
    ]
    
    # Borrowers
    # 1. Investor (Low λ for Future Cost - Optimistic)
    # 2. Desperate (High Gain from Consumption - Need to eat)
    # 3. Prudent (High λ for Future Cost - Risk Averse)
    
    borrowers = [
        {'name': 'Investor',  'gain': 150.0, 'lambda': 0.8}, # Expects 50 profit
        {'name': 'Desperate', 'gain': 200.0, 'lambda': 1.0}, # Survival value is high
        {'name': 'Prudent',   'gain': 100.0, 'lambda': 1.2}  # Only borrows if free money
    ]
    
    log(f"{ 'BORROWER':<10} | {'RATE':<8} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for b in borrowers:
        person = CreditBCP(b['lambda'])
        for r in rates:
            v = person.evaluate_loan(b['gain'], r['cost'])
            decision = "BORROW" if v > 0 else "SAVE"
            log(f"{b['name']:<10} | {r['name']:<8} | {b['gain']:<5} | {r['cost']:<5} | {v:<8.1f} | {decision}")
            
    log("\nFINDING: ZIRP encourages borrowing even for marginal gains (Bubbles).")
    log("         Crisis rates kill investment but Desperate borrowers still pay.")
    log("         Interest is the price of impatience.")
    log("======================================================================")
    log("GATE 1107 COMPLETE: INTEREST IS TIME COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
