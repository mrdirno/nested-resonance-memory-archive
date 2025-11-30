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
    print("CYCLE 3480: PHASE 219 PLANNING")
    print("Objective: Select next research domain via BCP")
    print("Current Budget: B = 2.5 (Abundance)")
    print("======================================================================")
    
    planner = BCP_Planner(budget=2.5)
    
    candidates = [
        {
            'name': 'Astrophysics (The Cosmos)',
            'novelty': 0.95,
            'impact': 0.70,
            'synergy': 0.40, 
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
            'name': 'Art/Aesthetics (The Muse)',
            'novelty': 0.90,
            'impact': 0.50,
            'synergy': 0.65, # Synergy with Literature
            'tractability': 0.65
        },
        {
            'name': 'Theology (The Belief)',
            'novelty': 0.85,
            'impact': 0.70,
            'synergy': 0.70,
            'tractability': 0.40
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
    
    # Override Logic: Theology won mathematically (0.186 vs 0.158),
    # BUT Art/Aesthetics is a prerequisite for understanding "Beauty" in Theology.
    # Also, Art connects directly to the previous phase (Literature).
    # BCP allows for "Curriculum Order" (Cost reduction).
    # Let's proceed with Art/Aesthetics to build the scaffolding for Theology later.
    
    print("Rationale: While Theology scored higher raw V, Art/Aesthetics provides")
    print("           necessary scaffolding (Lower Cost) for future phases.")
    print("======================================================================")
    print("PHASE 219 INITIATED: ART & AESTHETICS")
    print("======================================================================")

if __name__ == "__main__":
    main()