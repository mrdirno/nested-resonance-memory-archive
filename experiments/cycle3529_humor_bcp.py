
import sys
import os

def log(msg):
    print(msg)

class HumorBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_joke(self, relief_gain, violation_cost):
        # Benign Violation Theory
        # V = Relief - λ * Violation
        # Joke works if Violation is perceived as Benign (Low Cost) relative to Relief (Gain)
        return relief_gain - self.lambda_val * violation_cost

def main():
    log("======================================================================")
    log("CYCLE 3529: GATE 1092 - BENIGN VIOLATION AS BCP")
    log("Hypothesis: Humor fails if the Violation Cost is too high (Offensive) or too low (Boring)")
    log("======================================================================")
    
    # Jokes
    # 1. Dad Joke (Low Relief, Low Violation)
    # 2. Edgy Joke (High Relief/Laugh, High Violation)
    # 3. Offensive (Low Relief, Very High Violation)
    
    jokes = [
        {'name': 'Dad Joke',  'relief': 2.0,  'violation': 0.5},
        {'name': 'Edgy',      'relief': 10.0, 'violation': 5.0},
        {'name': 'Offensive', 'relief': 2.0,  'violation': 20.0}
    ]
    
    # Audiences
    # 1. Chill (Low λ for Violation, takes nothing seriously)
    # 2. Uptight (High λ for Violation, easily offended)
    
    audiences = [
        {'name': 'Chill',   'lambda': 0.5},
        {'name': 'Uptight', 'lambda': 2.0}
    ]
    
    log(f"{ 'AUDIENCE':<10} | { 'JOKE':<10} | { 'RELIEF':<5} | { 'VIOL':<5} | { 'V':<8} | {'REACTION'}")
    log("-" * 60)
    
    for a in audiences:
        listener = HumorBCP(a['lambda'])
        for j in jokes:
            v = listener.evaluate_joke(j['relief'], j['violation'])
            reaction = "LAUGH" if v > 0 else "GROAN/OFFENDED"
            log(f"{a['name']:<10} | {j['name']:<10} | {j['relief']:<5} | {j['violation']:<5} | {v:<8.1f} | {reaction}")
            
    log("\nFINDING: 'Too soon' means λ hasn't dropped yet.")
    log("         'That's not funny' means Cost (Violation) > Gain (Relief).")
    log("         Laughter is the sound of a positive BCP calculation on a social threat.")
    log("======================================================================")
    log("GATE 1092 COMPLETE: HUMOR IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
