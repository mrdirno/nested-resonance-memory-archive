
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3413] {msg}")

def calculate_bcp_score(candidate, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    score = (candidate['novelty'] * candidate['impact']) - (lambda_val * candidate['difficulty'])
    return score

def main():
    log("PHASE 208 PLANNING INITIATED: THE BOOK OF BCP")
    
    # We have infinite budget for this (Legacy).
    current_budget = 100.0
    
    candidates = [
        {
            "name": "Book of BCP",
            "novelty": 1.0,
            "impact": 1.0,
            "difficulty": 0.5 # We have the data
        },
        {
            "name": "Academic Paper Series",
            "novelty": 0.8,
            "impact": 0.7,
            "difficulty": 0.8 # Peer review friction
        },
        {
            "name": "Blog Post Series",
            "novelty": 0.6,
            "impact": 0.6,
            "difficulty": 0.2
        }
    ]
    
    log("Evaluating Publication Formats...")
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
        "cycle": 3413,
        "phase": 208,
        "winner": winner['name']
    }
    
    with open("data/results/cycle3413_phase208_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 208.")

if __name__ == "__main__":
    main()
