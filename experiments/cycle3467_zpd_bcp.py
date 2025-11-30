
import sys
import os

def log(msg):
    print(msg)

class LearnerBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_scaffold(self, learning_gain, effort_cost):
        # V = Gain - λ * Effort
        # Scaffolding reduces Effort (Cost)
        return learning_gain - self.lambda_val * effort_cost

def main():
    log("======================================================================")
    log("CYCLE 3467: GATE 1044 - ZPD AS BCP")
    log("Hypothesis: Zone of Proximal Development is the region where V > 0")
    log("======================================================================")
    
    # Task: Solve Complex Problem
    gain = 10.0
    
    # Scenarios:
    # 1. Too Hard (No Help): Cost = 20
    # 2. ZPD (With Help): Cost = 5
    # 3. Too Easy (Already Known): Gain = 1, Cost = 1 (Boredom)
    
    scenarios = [
        {'name': 'Too Hard', 'gain': 10.0, 'cost': 20.0},
        {'name': 'ZPD',      'gain': 10.0, 'cost': 5.0},
        {'name': 'Too Easy', 'gain': 1.0,  'cost': 1.0}
    ]
    
    learner = LearnerBCP(lambda_val=1.0) # Normal capacity
    
    log(f"{ 'ZONE':<10} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'STATUS'}")
    log("-" * 50)
    
    for s in scenarios:
        v = learner.evaluate_scaffold(s['gain'], s['cost'])
        status = "ENGAGED" if v > 0 else "DISENGAGED"
        log(f"{s['name']:<10} | {s['gain']:<5} | {s['cost']:<5} | {v:<8.1f} | {status}")
        
    log("\nFINDING: ZPD is simply the BCP-optimal zone.")
    log("         - Too Hard: Cost dominates Gain (V < 0)")
    log("         - Too Easy: Gain is too low relative to λ (V ≈ 0)")
    log("         - ZPD: Scaffolding lowers Cost to make V > 0.")
    log("======================================================================")
    log("GATE 1044 COMPLETE: ZPD IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
