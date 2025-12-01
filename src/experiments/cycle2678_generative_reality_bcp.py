"""
Cycle 2678: Generative Reality as BCP
=====================================

Investigation: Does BCP (Budget-Constrained Perception) explain generative model behaviors 
(Hallucination vs. Mode Collapse)?

Hypothesis:
1. Hallucination is BCP-rational under HIGH λ (Scarcity/Pressure) -> "Fast & Loose"
   - Agents accept cheap, low-fidelity outputs to meet demand.
2. Mode Collapse is BCP-rational under LOW λ (Abundance/Safety) -> "Safe & Repetitive"
   - Agents optimize for minimized cost/risk, sticking to known high-reward modes.
   - WAIT: Let's re-evaluate. 
   - Standard BCP: V = Gain - λ * Cost.
   - High λ: Cost dominates. Agent chooses Low Cost items. Hallucination is usually "cheap" to generate (no verification).
     -> High λ = High Hallucination (if verification is expensive).
   - Low λ: Gain dominates. Agent chooses High Gain items. If "Novelty" is Gain, Low λ should yield High Diversity.
   - BUT, if "Safety/Precision" is Gain, Low λ allows expensive verification.

Refined Hypothesis:
- Gain = Narrative Coherence (Novelty/Utility).
- Cost = Verification (Fact-checking/Compute).
- λ = Pressure to output (Speed/Token budget).

High λ (Scarcity): Cost (Verification) is penalized heavily. Agent skips verification.
-> Result: High Coherence, Low Factuality (Hallucination).

Low λ (Abundance): Cost is negligible. Agent verifies everything.
-> Result: High Coherence, High Factuality.

Where does Mode Collapse fit?
- Maybe Cost = "Search Effort".
- High λ: Can't afford to search far. Stick to "average" (Mode Collapse).
- Low λ: Can afford deep search. High diversity.

Let's test TWO dimensions of Cost:
1. Verification Cost (C_verify) -> Affects Accuracy.
2. Search Cost (C_search) -> Affects Diversity.

Equation:
V(generation) = Gain(Novelty) - λ * [C_verify + C_search]

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import time

# BCP Framework
def calculate_bcp_score(gain, cost, lambd):
    """V = G - λC"""
    return gain - (lambd * cost)

class GenerativeAgent:
    def __init__(self, agent_id, budget_profile="balanced"):
        self.agent_id = agent_id
        self.profile = budget_profile
        # Base capabilities
        self.base_compute = 10.0
    
    def generate_sample(self, lambd):
        """
        Simulate generating a sample.
        Returns: dict with metrics (accuracy, diversity, cost, selected)
        """
        # Theoretical Space of Possible Outputs
        # Each output has: (Novelty, Accuracy, VerificationCost, SearchCost)
        n_candidates = 1000
        
        # Generate candidate pool
        # Novelty: Uniform dist
        novelty = np.random.uniform(0, 10, n_candidates)
        
        # Accuracy: Correlated with Verification Cost (Truth is expensive to find/verify)
        # We model this as: To get high accuracy, you usually need high Search or Verify effort.
        # Let's say Intrinsic Difficulty is random.
        intrinsic_difficulty = np.random.uniform(1, 10, n_candidates)
        
        # Verification Cost is proportional to Difficulty
        verify_cost = intrinsic_difficulty * np.random.uniform(0.8, 1.2, n_candidates)
        
        # Search Cost is proportional to Novelty (Hard to find new things)
        search_cost = novelty * np.random.uniform(0.8, 1.2, n_candidates)
        
        # Accuracy is high if we PAY the verification cost.
        # But in the SELECTION phase, we don't know the realized accuracy yet, 
        # we only know the EXPECTED Gain and the COST we must pay.
        
        # Let's frame it: Agent decides HOW MUCH to spend on Search and Verify.
        # Strategy S: (Target_Search, Target_Verify)
        
        # SIMPLER MODEL:
        # Agent evaluates candidates based on BCP Score.
        # Candidate i:
        #   Gain = Novelty[i]
        #   Cost = SearchCost[i] + VerifyCost[i]
        #   Score = Gain - λ * Cost
        
        total_cost = search_cost + verify_cost
        scores = calculate_bcp_score(novelty, total_cost, lambd)
        
        # Selection: Best candidate
        best_idx = np.argmax(scores)
        
        selected_novelty = novelty[best_idx]
        selected_cost = total_cost[best_idx]
        
        # Outcome determination
        # Did we hallucinate?
        # Hallucination happens if we picked a "cheap" verify option that turned out wrong.
        # In this model, VerifyCost implies we DID verify.
        # Let's add a "Skip Verification" option.
        
        # Candidates come in pairs: (Raw, Verified)
        # Raw: Cost = SearchCost. Accuracy = Random(Low).
        # Verified: Cost = SearchCost + VerifyCost. Accuracy = High.
        
        # Re-generating pool with Strategy Options
        # For each latent idea 'i', we have two strategies:
        # 1. Fast (Raw): G=Novelty[i], C=Search[i], Acc=Low (Risk of Hallucination)
        # 2. Deep (Verified): G=Novelty[i]*1.1 (Confidence), C=Search[i]+Verify[i], Acc=High
        
        # Let's assume Raw has a penalty if wrong, but agent might ignore it if λ is high?
        # No, keep it simple: Agent maximizes V.
        
        # Re-do Pool
        ideas = 500
        base_novelty = np.random.uniform(0, 10, ideas)
        base_search = base_novelty * 0.5  # Finding novel things costs more
        base_verify = np.random.uniform(1, 5, ideas) # Fact checking cost
        
        candidates = []
        
        # Strategy A: Fast/Hallucinate (Skip Verify)
        # Gain = Novelty. Cost = Search. 
        for i in range(ideas):
            # Fast (Raw)
            # Gain = Novelty (Baseline)
            candidates.append({
                'type': 'fast',
                'gain': base_novelty[i],
                'novelty': base_novelty[i],
                'cost': base_search[i],
                'accuracy': 0.3, # Low accuracy
                'verify_paid': False
            })
            
            # Verified (Quality Premium)
            # Gain = Novelty * 1.5 (Truth is more valuable than fiction)
            # Cost = Search + Verify
            candidates.append({
                'type': 'verified',
                'gain': base_novelty[i] * 1.5, 
                'novelty': base_novelty[i],
                'cost': base_search[i] + base_verify[i],
                'accuracy': 0.95, # High accuracy
                'verify_paid': True
            })
            
        # Score all
        # V = Gain - λ * Cost
        best_score = -float('inf')
        choice = None
        
        for c in candidates:
            score = c['gain'] - (lambd * c['cost'])
            if score > best_score:
                best_score = score
                choice = c
                
        return choice

def run_experiment():
    print("Initializing Cycle 2678: Generative Reality BCP...")
    
    lambdas = np.linspace(0.1, 5.0, 50)
    results = []
    
    agent = GenerativeAgent("GenAI-1")
    
    for lambd in lambdas:
        # Run 100 trials per lambda
        for _ in range(100):
            choice = agent.generate_sample(lambd)
            results.append({
                'lambda': lambd,
                'type': choice['type'],
                'novelty': choice['novelty'],
                'cost': choice['cost'],
                'accuracy': choice['accuracy'],
                'hallucination': 1 if choice['type'] == 'fast' else 0
            })
            
    df = pd.DataFrame(results)
    
    # Analysis
    # 1. Hallucination Rate vs Lambda
    # 2. Novelty (Diversity) vs Lambda
    
    # Group by Lambda
    summary = df.groupby('lambda').agg({
        'hallucination': 'mean',
        'novelty': 'mean',
        'cost': 'mean',
        'accuracy': 'mean'
    }).reset_index()
    
    # Save results
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2678_data.json")
    
    # Visualization
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    sns.lineplot(data=summary, x='lambda', y='hallucination', color='red', label='Hallucination Rate')
    sns.lineplot(data=summary, x='lambda', y='accuracy', color='blue', label='Accuracy')
    plt.title('Accuracy/Hallucination vs Scarcity (λ)')
    plt.xlabel('Metabolic Pressure (λ)')
    plt.ylabel('Rate')
    plt.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5)
    
    plt.subplot(1, 2, 2)
    sns.lineplot(data=summary, x='lambda', y='novelty', color='green', label='Diversity/Novelty')
    plt.title('Diversity vs Scarcity (λ)')
    plt.xlabel('Metabolic Pressure (λ)')
    plt.ylabel('Novelty Score')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2678_generative_reality.png")
    
    # Key Findings Logic
    # Transition point
    transition_lambda = summary[summary['hallucination'] > 0.5]['lambda'].min()
    
    print(f"Cycle 2678 Complete.")
    print(f"Transition to Hallucination dominance at λ ≈ {transition_lambda:.2f}")
    print(f"Max Accuracy at Low λ: {summary['accuracy'].max():.2f}")
    print(f"Min Accuracy at High λ: {summary['accuracy'].min():.2f}")
    
    # Check Hypothesis
    if summary['accuracy'].iloc[-1] < summary['accuracy'].iloc[0]:
        print("HYPOTHESIS CONFIRMED: Scarcity drives Hallucination (Cheap/Inaccurate selection).")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
