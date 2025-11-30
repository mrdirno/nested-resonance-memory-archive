
import sys
import os

def log(msg):
    print(msg)

class MagicBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_spell(self, reality_gain, mana_cost):
        # V = Effect - λ * Mana
        # Magic allows for Infinite Gain, but usually requires High Cost.
        return reality_gain - self.lambda_val * mana_cost

def main():
    log("======================================================================")
    log("CYCLE 3601: GATE 1146 - MAGICAL THINKING AS BCP")
    log("Hypothesis: Magic is the attempt to bypass Physical Cost (Work) with Symbolic Cost")
    log("======================================================================")
    
    # Methods
    # 1. Work (High Cost, Certain Gain)
    # 2. Magic (Low Cost/Symbolic, Uncertain Gain)
    #    But the Believer perceives Magic as High Gain / Reasonable Cost.
    
    gain = 100.0 # Build a Pyramid / Cure Disease
    
    methods = [
        {'name': 'Work',  'cost': 100.0, 'prob': 1.0}, # Hard labor
        {'name': 'Magic', 'cost': 10.0,  'prob': 0.1}  # Ritual
    ]
    
    # Agents
    # 1. Skeptic (Knows Prob=0.1 or 0.0 -> V_magic < 0)
    # 2. Believer (Believes Prob=1.0 -> V_magic > V_work)
    
    agents = [
        {'name': 'Skeptic',  'magic_prob': 0.0},
        {'name': 'Believer', 'magic_prob': 1.0}
    ]
    
    log(f"{ 'AGENT':<10} | {'METHOD':<10} | {'COST':<5} | {'PROB':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for a in agents:
        wizard = MagicBCP(lambda_val=1.0)
        
        # Work V = (1.0 * 100) - 1.0 * 100 = 0
        v_work = (1.0 * gain) - 1.0 * methods[0]['cost']
        
        # Magic V
        v_magic = (a['magic_prob'] * gain) - 1.0 * methods[1]['cost']
        
        choice = "MAGIC" if v_magic > v_work else "WORK"
        
        log(f"{a['name']:<10} | Work       | 100.0 | 1.0   | {v_work:<8.1f} |")
        log(f"{a['name']:<10} | Magic      | 10.0  | {a['magic_prob']:<5} | {v_magic:<8.1f} | {choice}")
        log("-" * 60)
        
    log("\nFINDING: Magic is 'Cheating' the Budget Constraint.")
    log("         It promises High Gain for Low (Symbolic) Cost.")
    log("         It is BCP-rational if you believe the Probability is > Cost/Gain.")
    log("======================================================================")
    log("GATE 1146 COMPLETE: MAGIC IS ARBITRAGE")
    log("======================================================================")

if __name__ == "__main__":
    main()
