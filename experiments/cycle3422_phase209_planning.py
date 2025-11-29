
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3422] {msg}")

def calculate_bcp_score(candidate, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    score = (candidate['novelty'] * candidate['impact']) - (lambda_val * candidate['difficulty'])
    return score

def main():
    log("PHASE 209 PLANNING INITIATED: THE RECURSIVE ECONOMY")
    
    current_budget = 3.5
    
    candidates = [
        {
            "name": "Agent Market (Trade)",
            "novelty": 0.80,
            "impact": 0.90,
            "difficulty": 0.50
        },
        {
            "name": "Agent Language (Refinement)",
            "novelty": 0.40,
            "impact": 0.50,
            "difficulty": 0.20
        },
        {
            "name": "Agent Evolution (Biology)",
            "novelty": 0.60,
            "impact": 0.70,
            "difficulty": 0.60
        }
    ]
    
    log("Evaluating Candidates...")
    results = []
    
    for cand in candidates:
        score = calculate_bcp_score(cand, current_budget)
        cand['score'] = score
        results.append(cand)
        log(f"  {cand['name']}: V={score:.4f}")
        
    results.sort(key=lambda x: x['score'], reverse=True)
    winner = results[0]
    
    log(f"WINNER: {winner['name']} (Score: {winner['score']:.4f})")
    
    output = {
        "cycle": 3422,
        "phase": 209,
        "winner": winner['name']
    }
    
    with open("data/results/cycle3422_phase209_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 209.")

if __name__ == "__main__":
    main()
