
import sys
import os

def log(msg):
    print(msg)

class DesirePathBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_path(self, distance_cost, mud_cost):
        # V = 0 - λ * (Distance + Mud)
        return -self.lambda_val * (distance_cost + mud_cost)

def main():
    log("======================================================================")
    log("CYCLE 3496: GATE 1067 - DESIRE PATHS AS BCP")
    log("Hypothesis: Desire Paths emerge when Paved Cost > Dirt Cost")
    log("======================================================================")
    
    # Paths
    # 1. Paved (Long, Clean)
    # 2. Desire (Short, Muddy)
    
    paths = [
        {'name': 'Paved',  'dist': 20.0, 'mud': 0.0},
        {'name': 'Desire', 'dist': 10.0, 'mud': 5.0}
    ]
    
    # Conditions
    # 1. Sunny (Mud Cost is Low)
    # 2. Rainy (Mud Cost is High)
    
    conditions = [
        {'name': 'Sunny', 'mud_mult': 0.5},
        {'name': 'Rainy', 'mud_mult': 3.0}
    ]
    
    walker = DesirePathBCP(lambda_val=1.0)
    
    log(f"{ 'CONDITION':<10} | { 'PATH':<10} | { 'DIST':<5} | { 'MUD':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for c in conditions:
        best_v = -float('inf')
        choice = None
        for p in paths:
            eff_mud = p['mud'] * c['mud_mult']
            v = walker.evaluate_path(p['dist'], eff_mud)
            log(f"{c['name']:<10} | {p['name']:<10} | {p['dist']:<5} | {eff_mud:<5.1f} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = p['name']
        
        log(f"WINNER ({c['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Desire paths are BCP optimizations of the physical environment.")
    log("         They represent the user voting with their feet against the Architect's BCP model.")
    log("======================================================================")
    log("GATE 1067 COMPLETE: DESIRE PATHS ARE VOTES")
    log("======================================================================")

if __name__ == "__main__":
    main()
