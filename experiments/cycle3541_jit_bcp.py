
import sys
import os

def log(msg):
    print(msg)

class SupplyChainBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_strategy(self, efficiency_gain, resilience_cost):
        # V = Efficiency - λ * Risk_of_Failure
        # JIT (Just In Time): High Efficiency, High Risk (Low Resilience)
        # JIC (Just In Case): Low Efficiency (Warehousing Cost), Low Risk (High Resilience)
        
        # Wait, Efficiency Gain = Cost Savings.
        # Resilience Cost = Warehousing + Redundancy.
        # But Risk is a Probability * Impact Cost.
        
        # Let's model it as:
        # V = (Profit_Margin) - λ * (Inventory_Cost + Stockout_Risk)
        
        # JIT: High Profit (Low Inventory), High Stockout Risk
        # JIC: Low Profit (High Inventory), Low Stockout Risk
        
        # Efficiency Gain is implicit in the Profit Margin.
        pass

def main():
    log("======================================================================")
    log("CYCLE 3541: GATE 1101 - JIT VS JIC AS BCP")
    log("Hypothesis: JIT is optimal only when Supply Chain Reliability (λ) is High (Low Risk)")
    log("======================================================================")
    
    # Strategies
    # 1. JIT (Lean): Inventory Cost = 10, Risk Cost = 50 (if shock happens)
    # 2. JIC (Resilient): Inventory Cost = 40, Risk Cost = 5
    
    strategies = [
        {'name': 'JIT (Lean)',      'inv_cost': 10.0, 'risk_cost': 50.0},
        {'name': 'JIC (Resilient)', 'inv_cost': 40.0, 'risk_cost': 5.0}
    ]
    
    # Conditions (λ = Probability of Shock * Magnitude)
    # 1. Stable Era (Low λ for Risk)
    # 2. Turbulent Era (High λ for Risk)
    
    # Wait, λ is metabolic pressure.
    # In Stable Era, Risk is perceived as Low Cost.
    # In Turbulent Era, Risk is perceived as High Cost.
    
    conditions = [
        {'name': 'Stable',    'lambda': 0.2}, # Low worry about risk
        {'name': 'Turbulent', 'lambda': 2.0}  # High worry about risk
    ]
    
    base_gain = 100.0
    
    log(f"{ 'ERA':<10} | { 'STRATEGY':<15} | { 'INV':<5} | { 'RISK':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    class LogisticsBCP:
        def __init__(self, lambda_val):
            self.lambda_val = lambda_val
            
        def evaluate(self, gain, inv_cost, risk_cost):
            # V = Gain - (Inv_Cost + λ * Risk_Cost)
            # Actually, Inv_Cost is certain. Risk_Cost is probabilistic (λ scales it).
            return gain - (inv_cost + self.lambda_val * risk_cost)
            
    for c in conditions:
        mgr = LogisticsBCP(c['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in strategies:
            v = mgr.evaluate(base_gain, s['inv_cost'], s['risk_cost'])
            log(f"{c['name']:<10} | {s['name']:<15} | {s['inv_cost']:<5} | {s['risk_cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({c['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: JIT is optimal in Stable Eras (Cost of Inventory > Risk).")
    log("         JIC is optimal in Turbulent Eras (Risk > Cost of Inventory).")
    log("         The Supply Chain Crisis was a global λ-shock.")
    log("======================================================================")
    log("GATE 1101 COMPLETE: LOGISTICS IS RISK BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
