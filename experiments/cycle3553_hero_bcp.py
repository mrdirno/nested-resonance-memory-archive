
import sys
import os

def log(msg):
    print(msg)

class HeroBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_quest(self, boon_gain, ordeal_cost):
        # V = Boon - λ * Ordeal
        # Campbell's Hero's Journey:
        # 1. Departure (Cost of Leaving)
        # 2. Initiation (Ordeal Cost)
        # 3. Return (Gain of Boon)
        return boon_gain - self.lambda_val * ordeal_cost

def main():
    log("======================================================================")
    log("CYCLE 3553: GATE 1110 - HERO'S JOURNEY AS BCP")
    log("Hypothesis: Myths are BCP templates for handling High-Cost transitions")
    log("======================================================================")
    
    # The Quest
    boon = 100.0 # The Elixir / Wisdom / Safety
    ordeal = 80.0 # Facing the Dragon / Death
    
    # Agents
    # 1. Hero (Low λ for Risk/Ordeal - often aided by Supernatural Help/Mentor)
    # 2. Refuser (High λ - "Refusal of the Call")
    
    agents = [
        {'name': 'Hero',    'lambda': 0.8},
        {'name': 'Refuser', 'lambda': 1.5}
    ]
    
    log(f"{ 'AGENT':<10} | { 'BOON':<5} | { 'ORDEAL':<6} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for a in agents:
        person = HeroBCP(a['lambda'])
        v = person.evaluate_quest(boon, ordeal)
        decision = "ACCEPT" if v > 0 else "REFUSE"
        log(f"{a['name']:<10} | {boon:<5} | {ordeal:<6} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: The 'Mentor' archetype exists to lower λ (reduce perceived Cost/Risk).")
    log("         The 'Belly of the Whale' is the point of Maximum Cost.")
    log("         Myth teaches us that High Cost yields High Gain.")
    log("======================================================================")
    log("GATE 1110 COMPLETE: MYTH IS BCP TRAINING")
    log("======================================================================")

if __name__ == "__main__":
    main()
