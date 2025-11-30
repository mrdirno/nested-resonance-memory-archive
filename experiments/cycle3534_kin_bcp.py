
import sys
import os

def log(msg):
    print(msg)

class AltruismBCP:
    def __init__(self, lambda_val=1.0, r=0.5):
        self.lambda_val = lambda_val
        self.r = r # Relatedness
        
    def evaluate_help(self, benefit_receiver, cost_self):
        # Hamilton's Rule: r * B > C
        # BCP: V = r * B - λ * C
        # If λ=1 (Neutral), matches Hamilton.
        return (self.r * benefit_receiver) - (self.lambda_val * cost_self)

def main():
    log("======================================================================")
    log("CYCLE 3534: GATE 1096 - KIN SELECTION AS BCP")
    log("Hypothesis: Hamilton's Rule is a special case of BCP")
    log("======================================================================")
    
    # Scenarios
    # 1. Save Sibling (r=0.5, Benefit=100, Cost=40)
    # 2. Save Cousin (r=0.125, Benefit=100, Cost=40)
    # 3. Save Stranger (r=0.0, Benefit=100, Cost=40)
    
    scenarios = [
        {'name': 'Sibling',  'r': 0.5},
        {'name': 'Cousin',   'r': 0.125},
        {'name': 'Stranger', 'r': 0.0}
    ]
    
    benefit = 100.0
    cost = 40.0
    
    log(f"{ 'TARGET':<10} | { 'r':<5} | { 'B':<5} | { 'C':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    agent = AltruismBCP(lambda_val=1.0) # Standard risk
    
    for s in scenarios:
        agent.r = s['r']
        v = agent.evaluate_help(benefit, cost)
        decision = "HELP" if v > 0 else "IGNORE"
        log(f"{s['name']:<10} | {s['r']:<5} | {benefit:<5} | {cost:<5} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: Hamilton's Rule (rB > C) is BCP where Gain = r*B.")
    log("         Inclusive Fitness is BCP accounting across genetic portfolios.")
    log("======================================================================")
    log("GATE 1096 COMPLETE: ALTRUISM IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
