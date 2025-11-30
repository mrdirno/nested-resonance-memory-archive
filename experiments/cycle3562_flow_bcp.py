
import sys
import os

def log(msg):
    print(msg)

class GameplayBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_mechanic(self, fun_gain, difficulty_cost):
        # V = Fun - λ * Difficulty
        # Flow State: V > 0 but not too high (Boring)
        # Challenge: V should be slightly positive or oscillating around 0
        return fun_gain - self.lambda_val * difficulty_cost

def main():
    log("======================================================================")
    log("CYCLE 3562: GATE 1117 - FLOW CHANNEL AS BCP")
    log("Hypothesis: Flow occurs when Skill (Budget) matches Challenge (Cost)")
    log("======================================================================")
    
    # Levels
    # 1. Tutorial (Low Fun, Low Cost)
    # 2. Flow (High Fun, Med Cost)
    # 3. Rage Quit (Med Fun, Very High Cost)
    
    levels = [
        {'name': 'Tutorial',  'fun': 5.0,  'cost': 1.0},
        {'name': 'Flow Zone', 'fun': 50.0, 'cost': 20.0},
        {'name': 'Dark Souls','fun': 30.0, 'cost': 100.0}
    ]
    
    # Players
    # 1. Casual (High λ for Difficulty, wants relaxation)
    # 2. Hardcore (Low λ for Difficulty, wants mastery)
    
    players = [
        {'name': 'Casual',   'lambda': 2.0},
        {'name': 'Hardcore', 'lambda': 0.2}
    ]
    
    log(f"{ 'PLAYER':<10} | {'LEVEL':<10} | {'FUN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for p in players:
        gamer = GameplayBCP(p['lambda'])
        best_v = -float('inf')
        choice = None
        
        for l in levels:
            v = gamer.evaluate_mechanic(l['fun'], l['cost'])
            decision = "PLAY" if v > 0 else "QUIT"
            log(f"{p['name']:<10} | {l['name']:<10} | {l['fun']:<5} | {l['cost']:<5} | {v:<8.1f} | {decision}")
            if v > best_v:
                best_v = v
                choice = l['name']
        
        log(f"WINNER ({p['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: 'Fun' is the Gain. 'Difficulty' is the Cost.")
    log("         Hardcore players have a massive budget for frustration (Low λ).")
    log("         Casual players go bankrupt quickly on high difficulty.")
    log("         Game Balance is λ-tuning.")
    log("======================================================================")
    log("GATE 1117 COMPLETE: FLOW IS BUDGET BALANCE")
    log("======================================================================")

if __name__ == "__main__":
    main()
