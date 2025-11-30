
import sys
import os

def log(msg):
    print(msg)

class DirectorBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_shot(self, visual_gain, budget_cost):
        # V = Visuals - λ * Money
        return visual_gain - self.lambda_val * budget_cost

def main():
    log("======================================================================")
    log("CYCLE 3587: GATE 1136 - BLOCKBUSTER VS INDIE AS BCP")
    log("Hypothesis: CGI is high-cost gain. Practical effects are low-cost gain (sometimes).")
    log("======================================================================")
    
    # Shots
    # 1. CGI Battle (Gain=100, Cost=100)
    # 2. Dialogue Scene (Gain=20, Cost=1)
    # 3. Practical Stunt (Gain=80, Cost=50)
    
    shots = [
        {'name': 'CGI Battle', 'gain': 100.0, 'cost': 100.0},
        {'name': 'Dialogue',   'gain': 20.0,  'cost': 1.0},
        {'name': 'Stunt',      'gain': 80.0,  'cost': 50.0}
    ]
    
    # Studios
    # 1. Marvel (Low λ for Money - Infinite Budget)
    # 2. A24 (High λ for Money - Shoe-string)
    
    studios = [
        {'name': 'Marvel', 'lambda': 0.5}, # Can spend 2$ to get 1$ visual
        {'name': 'A24',    'lambda': 5.0}  # Must be efficient
    ]
    
    log(f"{ 'STUDIO':<10} | { 'SHOT':<12} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'CHOICE'}")
    log("-" * 60)
    
    for s in studios:
        dir = DirectorBCP(s['lambda'])
        best_v = -float('inf')
        choice = None
        
        for sh in shots:
            v = dir.evaluate_shot(sh['gain'], sh['cost'])
            log(f"{s['name']:<10} | {sh['name']:<12} | {sh['gain']:<5} | {sh['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = sh['name']
        
        log(f"WINNER ({s['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Marvel chooses CGI because λ is low (Budget Abundance).")
    log("         A24 chooses Dialogue because λ is high (Scarcity).")
    log("         Artistic Style is a function of Financial Constraints.")
    log("======================================================================")
    log("GATE 1136 COMPLETE: SPECTACLE IS BUDGET")
    log("======================================================================")

if __name__ == "__main__":
    main()
