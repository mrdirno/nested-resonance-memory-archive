import sys
import os

def log(msg):
    print(msg)

class PolitenessBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_politeness(self, social_gain, effort_cost):
        # V = Social_Harmony - λ * Effort (Repression of True Self)
        # "Politeness" is a tax we pay for social access.
        return social_gain - self.lambda_val * effort_cost

def main():
    log("======================================================================")
    log("CYCLE 3594: GATE 1141 - POLITENESS AS BCP")
    log("Hypothesis: Manners reduce Social Friction (Cost) but require Effort")
    log("======================================================================")
    
    # Interactions
    # 1. Rude (Low Gain, Low Cost) -> Efficient but Lonely
    # 2. Polite (High Gain, Med Cost) -> Standard
    # 3. Sycophantic (High Gain, High Cost) -> Fake
    
    interactions = [
        {'name': 'Rude',       'gain': 0.0,  'cost': 0.0},
        {'name': 'Polite',     'gain': 10.0, 'cost': 5.0},
        {'name': 'Sycophant',  'gain': 12.0, 'cost': 15.0}
    ]
    
    # Agents
    # 1. Diplomat (Low λ for Effort - Values Harmony)
    # 2. Curmudgeon (High λ for Effort - Values Authenticity/Laziness)
    
    agents = [
        {'name': 'Diplomat',   'lambda': 0.5},
        {'name': 'Curmudgeon', 'lambda': 2.5}
    ]
    
    log(f"{ 'AGENT':<12} | { 'STYLE':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'CHOICE'}")
    log("------------------------------------------------------------")
    
    for a in agents:
        person = PolitenessBCP(a['lambda'])
        best_v = -float('inf')
        choice = None
        
        for i in interactions:
            v = person.evaluate_politeness(i['gain'], i['cost'])
            log(f"{a['name']:<12} | {i['name']:<10} | {i['gain']:<5} | {i['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = i['name']
        
        log(f"WINNER ({a['name']}): {choice}")
        log("------------------------------------------------------------")
        
    log("\nFINDING: Diplomats choose Politeness (V > 0).")
    log("         Curmudgeons choose Rudeness (V=0 is better than V<0).")
    log("         'Fake Nice' occurs when the Social Gain is high enough to pay the Cost.")
    log("======================================================================")
    log("GATE 1141 COMPLETE: MANNERS ARE SOCIAL TAX")
    log("======================================================================")

if __name__ == "__main__":
    main()