
import sys
import os
import random
import json
from datetime import datetime

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3269] {msg}")

def calculate_bcp_score(candidate, budget_b):
    """
    Calculate BCP score for a research candidate.
    V = Gain - lambda(B) * Cost
    """
    # Lambda function: k/(epsilon + B)
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    gain = candidate['novelty'] * candidate['impact']
    cost = candidate['difficulty']
    
    score = gain - (lambda_val * cost)
    return score, lambda_val

def main():
    log("PHASE 180 PLANNING INITIATED")
    
    # Current Research Budget (simulated based on recent success)
    # High success in Phase 179 (Education) -> Abundance
    current_budget = 3.5 
    log(f"Current Research Budget B = {current_budget}")
    
    candidates = [
        {
            "name": "Healthcare AI",
            "novelty": 0.85,    # High novelty in applying BCP to triage
            "impact": 0.95,     # Critical impact
            "difficulty": 0.60  # High complexity/regulation
        },
        {
            "name": "Legal AI",
            "novelty": 0.75,
            "impact": 0.80,
            "difficulty": 0.50  # Moderate complexity
        },
        {
            "name": "Agricultural AI",
            "novelty": 0.70,
            "impact": 0.85,
            "difficulty": 0.40  # Physical constraints
        },
        {
            "name": "Entertainment AI",
            "novelty": 0.60,
            "impact": 0.50,
            "difficulty": 0.30  # Low risk
        }
    ]
    
    log("Evaluating Candidates via BCP...")
    results = []
    
    for cand in candidates:
        score, lambda_val = calculate_bcp_score(cand, current_budget)
        cand['score'] = score
        cand['lambda'] = lambda_val
        results.append(cand)
        log(f"  Candidate: {cand['name']:<15} | Gain: {cand['novelty']*cand['impact']:.3f} | Cost: {cand['difficulty']:.2f} | V: {score:.4f}")
        
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    winner = results[0]
    
    log(f"WINNER: {winner['name']} (Score: {winner['score']:.4f})")
    
    # Output result
    output = {
        "cycle": 3269,
        "phase": 180,
        "winner": winner['name'],
        "rationale": "Highest BCP Score under current budget abundance",
        "budget": current_budget,
        "candidates": results
    }
    
    results_dir = "data/results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    with open(f"{results_dir}/cycle3269_phase180_planning.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Planning Complete. Proceeding to Phase 180.")

if __name__ == "__main__":
    main()
