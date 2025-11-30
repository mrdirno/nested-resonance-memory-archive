
import sys
import os

def log(msg):
    print(msg)

class EditorBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_story(self, interest_gain, reporting_cost):
        # V = Interest - λ * Cost
        return interest_gain - self.lambda_val * reporting_cost

def main():
    log("======================================================================")
    log("CYCLE 3557: GATE 1113 - EDITORIAL SELECTION AS BCP")
    log("Hypothesis: The Front Page is a Budget Allocation of Attention")
    log("======================================================================")
    
    # Stories
    # 1. Dog Bites Man (Low Interest, Low Cost)
    # 2. Man Bites Dog (High Interest, Low Cost - Viral)
    # 3. Corruption Scandal (High Interest, High Cost - Legal/Time)
    # 4. Policy Analysis (Low Interest, High Cost - Boring/Deep)
    
    stories = [
        {'name': 'Dog Bites Man', 'gain': 1.0,  'cost': 1.0},
        {'name': 'Man Bites Dog', 'gain': 100.0,'cost': 1.0},
        {'name': 'Scandal',       'gain': 80.0, 'cost': 60.0},
        {'name': 'Policy Deep',   'gain': 10.0, 'cost': 40.0}
    ]
    
    # Editors
    # 1. Tabloid (High λ for Cost, needs quick hits)
    # 2. Prestige Paper (Low λ for Cost, values reputation)
    
    editors = [
        {'name': 'Tabloid',  'lambda': 1.5},
        {'name': 'Prestige', 'lambda': 0.5}
    ]
    
    log(f"{ 'EDITOR':<10} | {'STORY':<15} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 70)
    
    for e in editors:
        ed = EditorBCP(e['lambda'])
        for s in stories:
            v = ed.evaluate_story(s['gain'], s['cost'])
            decision = "PUBLISH" if v > 0 else "SPIKE"
            log(f"{e['name']:<10} | {s['name']:<15} | {s['gain']:<5} | {s['cost']:<5} | {v:<8.1f} | {decision}")
            
    log("\nFINDING: 'Man Bites Dog' is universally optimal (High Gain, Low Cost).")
    log("         Tabloids spike 'Scandal' because Cost (60*1.5 = 90) > Gain (80).")
    log("         Prestige papers publish 'Scandal' because Gain (80) > Cost (30).")
    log("         Investigative journalism is a luxury good (Low λ).")
    log("======================================================================")
    log("GATE 1113 COMPLETE: NEWS IS A COMMODITY")
    log("======================================================================")

if __name__ == "__main__":
    main()
