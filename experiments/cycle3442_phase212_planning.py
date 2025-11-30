
import sys
import os
import random

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock BCP class if not available in this environment for the plan
class BCP_Planner:
    def __init__(self, budget=1.0):
        self.budget = budget
        self.lambda_val = 1.0 / (0.1 + budget)
    
    def evaluate(self, candidate):
        # V = G - lambda * C
        # G = Novelty * Impact * Synergy
        # C = 1 - Tractability
        g = candidate['novelty'] * candidate['impact'] * candidate['synergy']
        c = 1.0 - candidate['tractability']
        v = g - self.lambda_val * c
        return v

def main():
    print("======================================================================")
    print("CYCLE 3442: PHASE 212 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance/Expansion Mode)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'HCI Systems (The Interface)',
            'novelty': 0.85,
            'impact': 0.90,
            'synergy': 0.80, # Connects Replicator to User
            'tractability': 0.75
        },
        {
            'name': 'Quantum Computing II (Deep Dive)',
            'novelty': 0.90,
            'impact': 0.60,
            'synergy': 0.40,
            'tractability': 0.30
        },
        {
            'name': 'Astrophysics (Macro Scale)',
            'novelty': 0.70,
            'impact': 0.50,
            'synergy': 0.30,
            'tractability': 0.60
        },
        {
            'name': 'Cybersecurity (Defensive)',
            'novelty': 0.60,
            'impact': 0.80,
            'synergy': 0.50,
            'tractability': 0.80
        }
    ]
    
    print(f"{'CANDIDATE':<30} | {'GAIN':<6} | {'COST':<6} | {'SCORE (V)':<8}")
    print("-" * 60)
    
    winner = None
    max_v = -float('inf')
    
    for cand in candidates:
        g = cand['novelty'] * cand['impact'] * cand['synergy']
        c = 1.0 - cand['tractability']
        v = planner.evaluate(cand)
        
        print(f"{cand['name']:<30} | {g:.3f}  | {c:.3f}  | {v:+.3f}")
        
        if v > max_v:
            max_v = v
            winner = cand
            
    print("-" * 60)
    print(f"WINNER: {winner['name']}")
    print("Rationale: High Impact/Synergy with Phase 211 (Replicator).")
    print("           The system must now learn to *interact* efficiently.")
    print("======================================================================")
    print("PHASE 212 INITIATED: HCI SYSTEMS")
    print("======================================================================")

if __name__ == "__main__":
    main()
