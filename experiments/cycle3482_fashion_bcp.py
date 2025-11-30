
import sys
import os

def log(msg):
    print(msg)

class FashionBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_trend(self, signal_gain, conformity_cost):
        # V = Signal - λ * Cost
        # Cost = Risk of looking weird (if too early) OR Risk of looking outdated (if too late)
        return signal_gain - self.lambda_val * conformity_cost

def main():
    log("======================================================================")
    log("CYCLE 3482: GATE 1056 - FASHION CYCLES AS BCP")
    log("Hypothesis: Fashion is a signaling game constrained by Cost")
    log("======================================================================")
    
    # Stages
    # 1. Avant-Garde (High Signal, High Risk Cost)
    # 2. Trend (Med Signal, Low Risk Cost)
    # 3. Cliche (Low Signal, High Boredom Cost)
    
    stages = [
        {'name': 'Avant-Garde', 'signal': 10.0, 'cost': 8.0},
        {'name': 'Trend',       'signal': 5.0,  'cost': 1.0},
        {'name': 'Cliche',      'signal': 1.0,  'cost': 5.0}
    ]
    
    # Agents
    # 1. Hipster (Low λ for Risk, values Signal)
    # 2. Normie (High λ for Risk, avoids Cost)
    
    agents = [
        {'name': 'Hipster', 'lambda': 0.5},
        {'name': 'Normie',  'lambda': 2.0}
    ]
    
    log(f"{ 'AGENT':<10} | {'STAGE':<12} | {'SIGNAL':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for a in agents:
        person = FashionBCP(a['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in stages:
            v = person.evaluate_trend(s['signal'], s['cost'])
            log(f"{a['name']:<10} | {s['name']:<12} | {s['signal']:<5} | {s['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({a['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Hipsters adopt Avant-Garde (V > 0 due to low λ).")
    log("         Normies wait for Trend (Cost drops).")
    log("         Fashion cycles occur as Cost shifts from 'Risk' to 'Boredom'.")
    log("======================================================================")
    log("GATE 1056 COMPLETE: FASHION IS SIGNALING BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
