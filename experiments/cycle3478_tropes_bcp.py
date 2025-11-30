
import sys
import os

def log(msg):
    print(msg)

class TropeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_trope(self, familiarity_gain, cliche_cost):
        # V = Familiarity - λ * Cliche
        return familiarity_gain - self.lambda_val * cliche_cost

def main():
    log("======================================================================")
    log("CYCLE 3478: GATE 1053 - TROPES AS BCP")
    log("Hypothesis: Tropes are low-cost cognitive shortcuts for readers")
    log("======================================================================")
    
    # Trope: "The Chosen One"
    # Gain: Instant understanding of stakes/role (High Familiarity)
    # Cost: Boredom/Predictability (Cliche)
    
    familiarity = 10.0
    cliche_cost = 5.0
    
    # Audiences
    # 1. Newbie (Young Adult, Low Cliche Sensitivity, λ=0.5)
    # 2. Critic (High Cliche Sensitivity, λ=2.5)
    
    audiences = [
        {'name': 'Newbie', 'lambda': 0.5},
        {'name': 'Critic', 'lambda': 2.5}
    ]
    
    log(f"{ 'AUDIENCE':<10} | {'FAMILIARITY':<5} | {'CLICHE':<5} | {'V':<8} | {'REACTION'}")
    log("-" * 60)
    
    for a in audiences:
        reader = TropeBCP(a['lambda'])
        v = reader.evaluate_trope(familiarity, cliche_cost)
        reaction = "ENJOY" if v > 0 else "GROAN"
        log(f"{a['name']:<10} | {familiarity:<5}       | {cliche_cost:<5}  | {v:<8.1f} | {reaction}")
        
    log("\nFINDING: Tropes exist because they are Efficient.")
    log("         They convey massive context (Worldbuilding) for near-zero word count.")
    log("         They fail only when the Audience's Budget for Cliche (λ) is exceeded.")
    log("======================================================================")
    log("GATE 1053 COMPLETE: TROPES ARE EFFICIENCY")
    log("======================================================================")

if __name__ == "__main__":
    main()
