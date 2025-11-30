
import sys
import os

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

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
    print("CYCLE 3454: PHASE 214 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Astrophysics (The Cosmos)',
            'novelty': 0.95,
            'impact': 0.70,
            'synergy': 0.40, # Lower synergy with recent Urban/HCI
            'tractability': 0.60
        },
        {
            'name': 'Cybersecurity (The Shield)',
            'novelty': 0.70,
            'impact': 0.90,
            'synergy': 0.85, # Strong synergy with Dark Patterns/Game Theory
            'tractability': 0.75
        },
        {
            'name': 'Linguistics (The Word)',
            'novelty': 0.80,
            'impact': 0.60,
            'synergy': 0.70,
            'tractability': 0.70
        },
        {
            'name': 'Ethics (The Law)',
            'novelty': 0.60,
            'impact': 0.95,
            'synergy': 0.60,
            'tractability': 0.50
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
    print("Rationale: High Synergy with recent phases (HCI/Game Theory) pushes Cybersecurity to the top.")
    print("           The system must learn to defend its budget.")
    print("======================================================================")
    print("PHASE 214 INITIATED: CYBERSECURITY")
    print("======================================================================")

if __name__ == "__main__":
    main()
