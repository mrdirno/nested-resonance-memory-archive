
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3344] {msg}")

def calculate_bcp_score(candidate, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    score = (candidate['novelty'] * candidate['impact']) - (lambda_val * candidate['difficulty'])
    return score

def main():
    log("PHASE 195 PLANNING INITIATED")
    
    current_budget = 3.5
    
    candidates = [
        {
            "name": "Hospitality AI",
            "novelty": 0.55,
            "impact": 0.55,
            "difficulty": 0.25
        },
        {
            "name": "Retail AI",
            "novelty": 0.50,
            "impact": 0.60,
            "difficulty": 0.20
        },
        {
            "name": "Art AI",
            "novelty": 0.75,
            "impact": 0.40,
            "difficulty": 0.60
        },
        {
            "name": "Music AI",
            "novelty": 0.65,
            "impact": 0.50,
            "difficulty": 0.35
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
        "cycle": 3344,
        "phase": 195,
        "winner": winner['name']
    }
    
    with open("data/results/cycle3344_phase195_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 195.")

if __name__ == "__main__":
    main()
