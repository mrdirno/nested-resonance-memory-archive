
import sys
import os

def log(msg):
    print(msg)

class InsurgentBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_tactic(self, damage_gain, exposure_cost):
        # V = Damage - λ * Exposure (Risk of Capture/Death)
        return damage_gain - self.lambda_val * exposure_cost

def main():
    log("======================================================================")
    log("CYCLE 3500: GATE 1070 - ASYMMETRIC WARFARE AS BCP")
    log("Hypothesis: Insurgents minimize Cost (Exposure) rather than maximize Gain")
    log("======================================================================")
    
    # Tactics
    # 1. Frontal Assault (High Damage, Very High Exposure)
    # 2. Ambush/IED (Med Damage, Low Exposure)
    # 3. Sniper (Low Damage, Very Low Exposure)
    
    tactics = [
        {'name': 'Assault', 'damage': 100.0, 'exposure': 100.0},
        {'name': 'Ambush',  'damage': 40.0,  'exposure': 10.0},
        {'name': 'Sniper',  'damage': 10.0,  'exposure': 2.0}
    ]
    
    # Agents
    # 1. State Army (Low λ for Exposure, can afford losses)
    # 2. Insurgent (High λ for Exposure, cannot afford losses)
    
    forces = [
        {'name': 'Army',      'lambda': 0.5},
        {'name': 'Insurgent', 'lambda': 5.0}
    ]
    
    log(f"{ 'FORCE':<10} | {'TACTIC':<10} | {'DMG':<5} | {'EXP':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for f in forces:
        cmdr = InsurgentBCP(f['lambda'])
        best_v = -float('inf')
        choice = None
        
        for t in tactics:
            v = cmdr.evaluate_tactic(t['damage'], t['exposure'])
            log(f"{f['name']:<10} | {t['name']:<10} | {t['damage']:<5} | {t['exposure']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = t['name']
        
        log(f"WINNER ({f['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Armies choose Assault (V > 0). Insurgents choose Ambush/Sniper.")
    log("         Asymmetric warfare is simply BCP optimization under different Budgets.")
    log("         Guerilla warfare is high-λ warfare.")
    log("======================================================================")
    log("GATE 1070 COMPLETE: ASYMMETRY IS BUDGET DIFFERENTIAL")
    log("======================================================================")

if __name__ == "__main__":
    main()
