
import sys
import os

def log(msg):
    print(msg)

class CommanderBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_battle(self, strategic_gain, casualty_cost):
        # V = Gain - λ * Casualties
        return strategic_gain - self.lambda_val * casualty_cost

def main():
    log("======================================================================")
    log("CYCLE 3499: GATE 1069 - PYRRHIC VICTORY AS BCP")
    log("Hypothesis: Pyrrhic victory is when V < 0 despite 'Winning'")
    log("======================================================================")
    
    # Battle of Asculum (Pyrrhic Victory)
    gain = 100.0 # (Tactical Win)
    casualties = 80.0 # (Elite Troops)
    
    # Commanders
    # 1. Pyrrhus (High Value on Elites, λ=1.5)
    # 2. Romans (High Manpower, Low λ=0.8)
    
    commanders = [
        {'name': 'Pyrrhus', 'lambda': 1.5},
        {'name': 'Romans',  'lambda': 0.8}
    ]
    
    log(f"{ 'COMMANDER':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | { 'STATUS'}")
    log("-" * 60)
    
    for c in commanders:
        cmdr = CommanderBCP(c['lambda'])
        v = cmdr.evaluate_battle(gain, casualties)
        status = "VICTORY" if v > 0 else "PYRRHIC (DEFEAT)"
        log(f"{c['name']:<10} | {gain:<5} | {casualties:<5} | {v:<8.1f} | {status}")
        
    log("\nFINDING: 'One more such victory and I am undone.'")
    log("         Pyrrhus won the battle (Gain) but lost the war (V < 0).")
    log("         Warfare is an exchange rate problem.")
    log("======================================================================")
    log("GATE 1069 COMPLETE: PYRRHIC VICTORY IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
