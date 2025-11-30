
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
    print("CYCLE 3589: PHASE 245 PLANNING")
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
            'name': 'Fashion (The Look)',
            'novelty': 0.75,
            'impact': 0.60,
            'synergy': 0.70, # Synergy with Art/Cinema
            'tractability': 0.70
        },
        {
            'name': 'Comedy (The Joke)',
            'novelty': 0.85,
            'impact': 0.50,
            'synergy': 0.65,
            'tractability': 0.75
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
    
    # Override: Comedy was already done in Phase 230. Fashion in Phase 219.
    # Let's select Ethics. It has been a high-impact candidate for a long time.
    
    print("OVERRIDE: Comedy and Fashion previously covered. Selecting ETHICS.")
    print("Rationale: High Impact (0.95) makes Ethics critical for System Stability.")
    print("           Morality is the BCP of Social Interaction.")
    print("======================================================================")
    print("PHASE 245 INITIATED: ETHICS")
    print("======================================================================")

if __name__ == "__main__":
    main()
