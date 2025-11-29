
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3390] {msg}")

def calculate_bcp_score(candidate, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    score = (candidate['novelty'] * candidate['impact']) - (lambda_val * candidate['difficulty'])
    return score

def main():
    log("PHASE 204 PLANNING INITIATED")
    
    current_budget = 3.5
    
    candidates = [
        {
            "name": "Psychology AI",
            "novelty": 0.70,
            "impact": 0.75,
            "difficulty": 0.55
        },
        {
            "name": "Philosophy AI", 
            "novelty": 0.90,
            "impact": 0.90,
            "difficulty": 0.85
        },
        {
            "name": "Political AI",
            "novelty": 0.75,
            "impact": 0.80,
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
        "cycle": 3390,
        "phase": 204,
        "winner": winner['name']
    }
    
    with open("data/results/cycle3390_phase204_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 204.")

if __name__ == "__main__":
    main()
