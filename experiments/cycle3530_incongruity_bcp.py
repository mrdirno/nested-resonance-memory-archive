
import sys
import os

def log(msg):
    print(msg)

class IncongruityBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_setup(self, surprise_gain, processing_cost):
        # V = Surprise - λ * Processing
        # If the punchline is too obscure (High Processing), V < 0 (Didn't get it).
        return surprise_gain - self.lambda_val * processing_cost

def main():
    log("======================================================================")
    log("CYCLE 3530: GATE 1093 - INCONGRUITY RESOLUTION AS BCP")
    log("Hypothesis: Jokes fail if the Cognitive Load (Cost) of resolution is too high")
    log("======================================================================")
    
    # Joke Complexity
    # 1. Slapstick (High Surprise, Low Processing)
    # 2. Wordplay (Med Surprise, Med Processing)
    # 3. Abstract/Meta (Med Surprise, High Processing)
    
    jokes = [
        {'name': 'Slapstick', 'surprise': 10.0, 'process': 1.0},
        {'name': 'Wordplay',  'surprise': 8.0,  'process': 4.0},
        {'name': 'Meta',      'surprise': 8.0,  'process': 10.0}
    ]
    
    # Audiences
    # 1. Drunk (High λ for Processing - Cognitive Impairment)
    # 2. Sober (Low λ for Processing)
    
    audiences = [
        {'name': 'Drunk', 'lambda': 2.0},
        {'name': 'Sober', 'lambda': 0.5}
    ]
    
    log(f"{ 'AUDIENCE':<10} | { 'JOKE':<10} | { 'SURP':<5} | { 'PROC':<5} | { 'V':<8} | {'REACTION'}")
    log("-" * 60)
    
    for a in audiences:
        listener = IncongruityBCP(a['lambda'])
        for j in jokes:
            v = listener.evaluate_setup(j['surprise'], j['process'])
            reaction = "LAUGH" if v > 0 else "HUH?"
            log(f"{a['name']:<10} | {j['name']:<10} | {j['surprise']:<5} | {j['process']:<5} | {v:<8.1f} | {reaction}")
            
    log("\nFINDING: Drunks prefer Slapstick because their Processing Budget is low (High λ).")
    log("         Intellectual humor requires a surplus of Cognitive Budget.")
    log("         A joke is an efficiency test for the brain.")
    log("======================================================================")
    log("GATE 1093 COMPLETE: INCONGRUITY IS COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
