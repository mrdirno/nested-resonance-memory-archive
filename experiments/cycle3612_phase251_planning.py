
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
    print("CYCLE 3612: PHASE 251 PLANNING")
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
            'name': 'Archaeology (The Ruin)',
            'novelty': 0.80,
            'impact': 0.60,
            'synergy': 0.75, # Synergy with History/Geology/Mythology
            'tractability': 0.65
        },
        {
            'name': 'Celebrity (The Fame)',
            'novelty': 0.75,
            'impact': 0.50,
            'synergy': 0.70, # Synergy with Fashion/Cinema/Social
            'tractability': 0.70
        },
        {
            'name': 'Espionage (The Secret)',
            'novelty': 0.85,
            'impact': 0.70,
            'synergy': 0.80, # Synergy with Cybersecurity/Warfare/Politics
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
    print("Rationale: High Synergy with Cybersecurity, Warfare, and Politics pushes Espionage.")
    print("           Spying is BCP applied to Secrets.")
    print("======================================================================")
    print("PHASE 251 INITIATED: ESPIONAGE")
    print("======================================================================")

if __name__ == "__main__":
    main()
