
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
    print("CYCLE 3596: PHASE 247 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Sports (The Game)',
            'novelty': 0.70,
            'impact': 0.50,
            'synergy': 0.50,
            'tractability': 0.80
        },
        {
            'name': 'Bureaucracy (The Form)',
            'novelty': 0.65,
            'impact': 0.85,
            'synergy': 0.80, # Synergy with Law/Logistics/Organization
            'tractability': 0.70
        },
        {
            'name': 'Cryptocurrency (The Hash)',
            'novelty': 0.85,
            'impact': 0.70,
            'synergy': 0.60,
            'tractability': 0.65
        },
        {
            'name': 'Religion (The Institution)',
            'novelty': 0.75,
            'impact': 0.80,
            'synergy': 0.85, # Synergy with Theology/Ethics/Ritual
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
    print("Rationale: High Synergy with Theology, Ethics, and Ritual pushes Religion.")
    print("           Religion is BCP institutionalized over millennia.")
    print("======================================================================")
    print("PHASE 247 INITIATED: RELIGION")
    print("======================================================================")

if __name__ == "__main__":
    main()
