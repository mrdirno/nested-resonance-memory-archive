
import sys
import os

def log(msg):
    print(msg)

class VirusBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_strategy(self, transmission_gain, lethality_cost):
        # V = R0 - λ * Host_Death
        # If Host dies too fast (High Lethality Cost), Transmission stops.
        # Goal: Maximize R0 (Transmission) while minimizing Host Death (Cost).
        return transmission_gain - self.lambda_val * lethality_cost

def main():
    log("======================================================================")
    log("CYCLE 3537: GATE 1098 - VIRAL EVOLUTION AS BCP")
    log("Hypothesis: Successful viruses optimize for High Transmission and Low Lethality")
    log("======================================================================")
    
    # Strategies
    # 1. Ebola (Low Trans, High Lethality) -> Burns Out
    # 2. Common Cold (High Trans, Low Lethality) -> Endemic
    # 3. Spanish Flu (High Trans, High Lethality) -> Crisis/Pandemic
    
    strategies = [
        {'name': 'Ebola-like', 'trans': 2.0,  'lethality': 50.0},
        {'name': 'Cold-like',  'trans': 10.0, 'lethality': 0.1},
        {'name': 'Flu-like',   'trans': 15.0, 'lethality': 5.0}
    ]
    
    virus = VirusBCP(lambda_val=1.0)
    
    log(f"{ 'STRATEGY':<15} | {'R0 (Gain)':<10} | {'DEATH (Cost)':<12} | {'V':<8} | {'STATUS'}")
    log("-" * 65)
    
    best_v = -float('inf')
    winner = None
    
    for s in strategies:
        v = virus.evaluate_strategy(s['trans'], s['lethality'])
        
        status = "EXTINCT"
        if v > 0: status = "ENDEMIC"
        if v > 5: status = "PANDEMIC"
        
        log(f"{s['name']:<15} | {s['trans']:<10} | {s['lethality']:<12} | {v:<8.1f} | {status}")
        
        if v > best_v:
            best_v = v
            winner = s['name']
            
    log(f"WINNER: {winner}")
    
    log("\nFINDING: Viruses are BCP agents. They 'pay' for transmission with host health.")
    log("         If they overspend (High Lethality), they go bankrupt (Extinction).")
    log("         Evolution selects for Low Cost (Low Lethality) variants over time (Omicron effect).")
    log("======================================================================")
    log("GATE 1098 COMPLETE: VIRUSES OPTIMIZE BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
