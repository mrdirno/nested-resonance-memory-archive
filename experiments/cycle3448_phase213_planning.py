
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
    print("CYCLE 3448: PHASE 213 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Urban Dynamics (The City)',
            'novelty': 0.80,
            'impact': 0.85,
            'synergy': 0.90, # Unifies Social, Economic, Physical, Transport
            'tractability': 0.70
        },
        {
            'name': 'Cybersecurity (Defensive)',
            'novelty': 0.60,
            'impact': 0.90,
            'synergy': 0.50,
            'tractability': 0.80
        },
        {
            'name': 'Astrophysics (Cosmic BCP)',
            'novelty': 0.95,
            'impact': 0.40,
            'synergy': 0.30,
            'tractability': 0.50
        },
        {
            'name': 'Linguistics (Language Evolution)',
            'novelty': 0.75,
            'impact': 0.60,
            'synergy': 0.70,
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
    print("Rationale: Urban Dynamics allows us to UNIFY multiple previous phases")
    print("           (Transport, Energy, Social, Economic) into a single spatial model.")
    print("======================================================================")
    print("PHASE 213 INITIATED: URBAN DYNAMICS")
    print("======================================================================")

if __name__ == "__main__":
    main()
