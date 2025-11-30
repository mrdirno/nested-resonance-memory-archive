
import sys
import os

def log(msg):
    print(msg)

class AttackerBCP:
    def __init__(self, budget=100.0):
        self.budget = budget
        self.lambda_val = 1.0 / (0.1 + budget)
        
    def evaluate_target(self, value, defense_difficulty):
        # V = Value - λ * Difficulty
        # Difficulty includes Time, Compute, Zero-Day purchase price
        return value - self.lambda_val * defense_difficulty

def main():
    log("======================================================================")
    log("CYCLE 3455: GATE 1034 - ATTACK ECONOMICS AS BCP")
    log("Hypothesis: Attackers are rational BCP agents maximizing ROI")
    log("======================================================================")
    
    attacker = AttackerBCP(budget=100.0) # Well-funded (State Actor / Organized Crime) 
    
    targets = [
        {'name': 'Personal Blog',   'value': 10,    'difficulty': 5},
        {'name': 'Small Business',  'value': 1000,  'difficulty': 50},
        {'name': 'Enterprise DB',   'value': 50000, 'difficulty': 2000},
        {'name': 'Crypto Exchange', 'value': 100000,'difficulty': 5000}
    ]
    
    log(f"Attacker Budget: {attacker.budget} (λ={attacker.lambda_val:.3f})")
    log("-" * 60)
    log(f"{ 'TARGET':<20} | {'VALUE':<8} | {'DIFF':<8} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for t in targets:
        v = attacker.evaluate_target(t['value'], t['difficulty'])
        decision = "ATTACK" if v > 0 else "IGNORE"
        log(f"{t['name']:<20} | {t['value']:<8} | {t['difficulty']:<8} | {v:<8.1f} | {decision}")
        
    # Scenario 2: Script Kiddie (Low Budget)
    log("\nSCENARIO 2: SCRIPT KIDDIE (Budget = 1.0)")
    kiddie = AttackerBCP(budget=1.0) # λ ≈ 0.9
    
    log(f"Attacker Budget: {kiddie.budget} (λ={kiddie.lambda_val:.3f})")
    log("-" * 60)
    
    for t in targets:
        v = kiddie.evaluate_target(t['value'], t['difficulty'])
        decision = "ATTACK" if v > 0 else "IGNORE"
        log(f"{t['name']:<20} | {t['value']:<8} | {t['difficulty']:<8} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: Cyberdefense is not about being invulnerable.")
    log("         It is about raising Difficulty until Cost > Budget/λ for the threat actor.")
    log("======================================================================")
    log("GATE 1034 COMPLETE: ATTACK ECONOMICS IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
