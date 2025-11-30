
import sys
import os

def log(msg):
    print(msg)

class SpeciesBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_niche(self, resource_gain, competition_cost):
        # V = Gain - λ * Cost
        return resource_gain - self.lambda_val * competition_cost

def main():
    log("======================================================================")
    log("CYCLE 3489: GATE 1061 - NICHE PARTITIONING AS BCP")
    log("Hypothesis: Species avoid competition (High Cost) by specializing (Niche)")
    log("======================================================================")
    
    # Niches
    # 1. Mainstream (High Resource, High Competition)
    # 2. Specialized (Low Resource, Low Competition)
    
    niches = [
        {'name': 'Mainstream',  'gain': 100.0, 'cost': 80.0},
        {'name': 'Specialized', 'gain': 20.0,  'cost': 5.0}
    ]
    
    # Species
    # 1. Dominant (Low λ for Competition - Strong)
    # 2. Weak (High λ for Competition - Avoids conflict)
    
    species_list = [
        {'name': 'Dominant', 'lambda': 0.5},
        {'name': 'Weak',     'lambda': 2.0}
    ]
    
    log(f"{ 'SPECIES':<10} | { 'NICHE':<12} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for s in species_list:
        agent = SpeciesBCP(s['lambda'])
        best_v = -float('inf')
        choice = None
        
        for n in niches:
            v = agent.evaluate_niche(n['gain'], n['cost'])
            log(f"{s['name']:<10} | {n['name']:<12} | {n['gain']:<5} | {n['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = n['name']
        
        log(f"WINNER ({s['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Strong species (Low λ) dominate the Mainstream.")
    log("         Weak species (High λ) are pushed into Specialization.")
    log("         Biodiversity is the result of BCP agents seeking V > 0 in cost-efficient ways.")
    log("======================================================================")
    log("GATE 1061 COMPLETE: NICHE IS BCP OPTIMIZATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
