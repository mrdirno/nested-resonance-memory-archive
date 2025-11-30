

import sys
import os

def log(msg):
    print(msg)

class CharacterBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_action(self, plot_gain, character_cost):
        # V = Plot - λ * Character_Integrity
        return plot_gain - self.lambda_val * character_cost

def main():
    log("======================================================================")
    log("CYCLE 3477: GATE 1052 - CHARACTER ARCS AS BCP")
    log("Hypothesis: 'Out of Character' moments happen when Plot Gain > Integrity Cost")
    log("======================================================================")
    
    # Scenario: Hero must kill the Villain
    # Hero Integrity Cost: 50 (Batman Rule: No Killing)
    # Plot Gain: 100 (Save the City)
    
    plot_gain = 100.0
    integrity_cost = 50.0
    
    # Writers
    # 1. Hack (Low value on Integrity, λ=0.5)
    # 2. Purist (High value on Integrity, λ=2.5)
    
    writers = [
        {'name': 'Hack',   'lambda': 0.5},
        {'name': 'Purist', 'lambda': 2.5}
    ]
    
    log(f"{ 'WRITER':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'ACTION'}")
    log("-" * 55)
    
    for w in writers:
        writer = CharacterBCP(w['lambda'])
        v = writer.evaluate_action(plot_gain, integrity_cost)
        action = "KILL" if v > 0 else "SPARE"
        log(f"{w['name']:<10} | {plot_gain:<5} | {integrity_cost:<5} | {v:<8.1f} | {action}")
        
    log("\nFINDING: Bad writing (Deus Ex Machina, Out of Character) is simply")
    log("         rational BCP optimization by a writer with Low Integrity λ.")
    log("         Good writing maintains high λ, forcing creative solutions.")
    log("======================================================================")
    log("GATE 1052 COMPLETE: INTEGRITY IS A COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
