
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
        g = candidate['novelty'] * candidate['impact'] * candidate['synergy']
        c = 1.0 - candidate['tractability']
        v = g - self.lambda_val * c
        return v

def main():
    print("======================================================================")
    print("CYCLE 3569: PHASE 240 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Ethics (The Law)',
            'novelty': 0.60,
            'impact': 0.95,
            'synergy': 0.60,
            'tractability': 0.50
        },
        {
            'name': 'Sports (The Game)',
            'novelty': 0.70,
            'impact': 0.50,
            'synergy': 0.50,
            'tractability': 0.80
        },
        {
            'name': 'Cinema (The Screen)',
            'novelty': 0.75,
            'impact': 0.70,
            'synergy': 0.70, # Synergy with Literature/Game Design
            'tractability': 0.65
        },
        {
            'name': 'Addiction (The Hook)',
            'novelty': 0.80,
            'impact': 0.80,
            'synergy': 0.85, # Synergy with Game Design/Medicine/HCI
            'tractability': 0.60
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
    print("Rationale: High Synergy with Game Design, Medicine, and HCI pushes Addiction.")
    print("           Addiction is BCP Optimization run amok.")
    print("======================================================================")
    print("PHASE 240 INITIATED: ADDICTION")
    print("======================================================================")

if __name__ == "__main__":
    main()
