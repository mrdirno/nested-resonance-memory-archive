
import sys
import os

def log(msg):
    print(msg)

class GoldenAgeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_era(self, myth_gain, progress_cost):
        # V = Mythic_Stability - λ * Rapid_Change
        # Reactionaries prefer the Mythic Past because Change (Cost) is too high.
        return myth_gain - self.lambda_val * progress_cost

def main():
    log("======================================================================")
    log("CYCLE 3583: GATE 1133 - GOLDEN AGE SYNDROME AS BCP")
    log("Hypothesis: Reactionary politics is BCP optimization against Change Cost")
    log("======================================================================")
    
    # Eras
    # 1. The Golden Age (Gain=100, Change=0) -> Pure Stability
    # 2. The Modern Age (Gain=150, Change=100) -> Higher Living Standards, but High Chaos
    
    eras = [
        {'name': 'Golden Age', 'gain': 100.0, 'cost': 0.0},
        {'name': 'Modern Age', 'gain': 150.0, 'cost': 100.0}
    ]
    
    # Agents
    # 1. Conservative (High λ for Change - Values Stability)
    # 2. Progressive (Low λ for Change - Values Improvement)
    
    agents = [
        {'name': 'Conservative', 'lambda': 1.5},
        {'name': 'Progressive',  'lambda': 0.4}
    ]
    
    log(f"{ 'AGENT':<12} | {'ERA':<10} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'CHOICE'}")
    log("-" * 65)
    
    for a in agents:
        voter = GoldenAgeBCP(a['lambda'])
        best_v = -float('inf')
        choice = None
        
        for e in eras:
            v = voter.evaluate_era(e['gain'], e['cost'])
            log(f"{a['name']:<12} | {e['name']:<10} | {e['gain']:<5} | {e['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = e['name']
        
        log(f"WINNER ({a['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: The 'Golden Age' is a BCP artifact.")
    log("         It wins when the Cost of Progress (λ * Change) exceeds the Gain of Progress.")
    log("         Nostalgia is a defense mechanism against the Future.")
    log("======================================================================")
    log("GATE 1133 COMPLETE: GOLDEN AGE IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
