
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
    print("CYCLE 3511: PHASE 226 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Astrophysics (The Cosmos)',
            'novelty': 0.95,
            'impact': 0.70,
            'synergy': 0.45, # Increasing synergy with Physics/Chemistry
            'tractability': 0.60
        },
        {
            'name': 'Ethics (The Law)',
            'novelty': 0.60,
            'impact': 0.95,
            'synergy': 0.60,
            'tractability': 0.50
        },
        {
            'name': 'Geology (The Earth)',
            'novelty': 0.80,
            'impact': 0.60,
            'synergy': 0.70, # Synergy with Chemistry/Ecology
            'tractability': 0.65
        },
        {
            'name': 'Sports (The Game)',
            'novelty': 0.70,
            'impact': 0.50,
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
    print("Rationale: Geology builds directly on Chemistry (Minerals) and Ecology (Habitats).")
    print("           The Earth is the budget constraint for Life.")
    print("======================================================================")
    print("PHASE 226 INITIATED: GEOLOGY")
    print("======================================================================")

if __name__ == "__main__":
    main()
