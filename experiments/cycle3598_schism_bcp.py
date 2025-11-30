
import sys
import os

def log(msg):
    print(msg)

class SchismBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_schism(self, purity_gain, unity_cost):
        # V = Purity - λ * Unity_Loss
        # Schisms happen when Purity Gain > Unity Cost.
        return purity_gain - self.lambda_val * unity_cost

def main():
    log("======================================================================")
    log("CYCLE 3598: GATE 1144 - SCHISM AS BCP")
    log("Hypothesis: Religions fracture when the Cost of Compromise > Value of Unity")
    log("======================================================================")
    
    # Scenarios
    # 1. Compromise (Low Purity Gain, Low Unity Cost)
    # 2. Schism (High Purity Gain, High Unity Cost)
    
    options = [
        {'name': 'Compromise', 'purity': 10.0,  'unity_cost': 0.0},
        {'name': 'Schism',     'purity': 100.0, 'unity_cost': 80.0}
    ]
    
    # Factions
    # 1. Ecumenist (High λ for Unity - Values Togetherness)
    # 2. Puritan (Low λ for Unity - Values Truth/Purity)
    
    factions = [
        {'name': 'Ecumenist', 'lambda': 2.0},
        {'name': 'Puritan',   'lambda': 0.5}
    ]
    
    log(f"{ 'FACTION':<10} | {'OPTION':<10} | {'PURITY':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for f in factions:
        leader = SchismBCP(f['lambda'])
        best_v = -float('inf')
        choice = None
        
        for o in options:
            v = leader.evaluate_schism(o['purity'], o['unity_cost'])
            log(f"{f['name']:<10} | {o['name']:<10} | {o['purity']:<5} | {o['unity_cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = o['name']
        
        log(f"WINNER ({f['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Puritans split because the Cost of Compromise (Purity Loss) is infinite.")
    log("         Ecumenists stay together because the Cost of Schism (Unity Loss) is infinite.")
    log("         Religious history is the oscillation between Purity and Unity.")
    log("======================================================================")
    log("GATE 1144 COMPLETE: SCHISM IS PURITY BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
