
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3433] {msg}")

def calculate_bcp_score(candidate, budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    score = (candidate['novelty'] * candidate['impact']) - (lambda_val * candidate['difficulty'])
    return score

def main():
    log("PHASE 211 PLANNING INITIATED: THE REPLICATOR")
    
    # We have high budget (Legacy).
    current_budget = 10.0
    
    candidates = [
        {
            "name": "The Replicator (Repo Cloner)",
            "novelty": 0.90,
            "impact": 0.95,
            "difficulty": 0.70
        },
        {
            "name": "The Critic (Code Reviewer)",
            "novelty": 0.60,
            "impact": 0.80,
            "difficulty": 0.40
        },
        {
            "name": "The Optimizer (Refactorer)",
            "novelty": 0.70,
            "impact": 0.85,
            "difficulty": 0.50
        }
    ]
    
    log("Evaluating Application Candidates...")
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
        "cycle": 3433,
        "phase": 211,
        "winner": winner['name']
    }
    
    with open("data/results/cycle3433_phase211_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 211.")

if __name__ == "__main__":
    main()
