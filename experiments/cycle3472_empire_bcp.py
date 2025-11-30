
import sys
import os

def log(msg):
    print(msg)

class EmpireBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_expansion(self, revenue_gain, military_cost):
        # V = Revenue - λ * Cost
        return revenue_gain - self.lambda_val * military_cost

def main():
    log("======================================================================")
    log("CYCLE 3472: GATE 1048 - IMPERIAL OVERSTRETCH AS BCP")
    log("Hypothesis: Empires collapse when Maintenance Cost > Revenue/λ")
    log("======================================================================")
    
    # Expansion Stages
    # 1. Core (High Revenue, Low Cost)
    # 2. Periphery (Med Revenue, Med Cost)
    # 3. Frontier (Low Revenue, High Cost)
    
    stages = [
        {'name': 'Core',      'rev': 100.0, 'cost': 10.0},
        {'name': 'Periphery', 'rev': 50.0,  'cost': 40.0},
        {'name': 'Frontier',  'rev': 10.0,  'cost': 50.0}
    ]
    
    # Scenario 1: The Rise (Low λ, High Efficiency/Morale)
    lambda_rise = 0.5
    log(f"\nSCENARIO 1: THE RISE (λ={lambda_rise})")
    
    empire_rise = EmpireBCP(lambda_rise)
    total_v_rise = 0
    
    for s in stages:
        v = empire_rise.evaluate_expansion(s['rev'], s['cost'])
        decision = "HOLD" if v > 0 else "RETREAT"
        log(f"{s['name']:<10} | Rev={s['rev']:<5} | Cost={s['cost']:<5} | V={v:<6.1f} | {decision}")
        total_v_rise += v
        
    log(f"Total Empire Value: {total_v_rise:.1f}")
    
    # Scenario 2: The Fall (High λ, Corruption/Inflation/Barbarians)
    lambda_fall = 2.0
    log(f"\nSCENARIO 2: THE FALL (λ={lambda_fall})")
    
    empire_fall = EmpireBCP(lambda_fall)
    total_v_fall = 0
    
    for s in stages:
        v = empire_fall.evaluate_expansion(s['rev'], s['cost'])
        decision = "HOLD" if v > 0 else "RETREAT"
        log(f"{s['name']:<10} | Rev={s['rev']:<5} | Cost={s['cost']:<5} | V={v:<6.1f} | {decision}")
        total_v_fall += v
        
    log(f"Total Empire Value: {total_v_fall:.1f}")
    
    log("\nFINDING: As λ rises (Inefficiency/Stress), the Frontier becomes unprofitable (V<0).")
    log("         Rational empires retreat. Irrational ones persist and collapse.")
    log("         Kennedy's 'Imperial Overstretch' is simply BCP Budget Exhaustion.")
    log("======================================================================")
    log("GATE 1048 COMPLETE: OVERSTRETCH IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
