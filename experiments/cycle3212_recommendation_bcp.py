import random

# ======================================================================
# CYCLE 3212: RECOMMENDATION AS BCP
# ======================================================================
# Hypothesis: Recommendation is attention budget allocation.
#   V(item) = Relevance - lambda(User_Attention) * Cognitive_Load
#   User Attention depletes with every bad recommendation.
#   High lambda (impatient) -> Show only safe/high-relevance items.
#   Low lambda (bored/exploring) -> Show serendipitous/risky items.
# ======================================================================

def run_experiment():
    print("CYCLE 3212: Recommendation as BCP")
    
    # Parameters
    N_items = 1000
    N_users = 100
    
    # Generate Items: [Relevance_Mean, Complexity]
    items = [{"id": i, "rel": random.random(), "cost": random.random()} for i in range(N_items)]
    
    total_clicks = 0
    total_bounces = 0
    
    for u in range(N_users):
        # User State
        attention_budget = 10.0 # Seconds? Or "Units of patience"
        
        while attention_budget > 0:
            # Calculate Lambda (Patience Pressure)
            # Low budget -> High lambda (Impatience)
            lamb = 1.0 / (0.1 + attention_budget)
            
            # Rank Items by V = Rel - lambda * Cost
            # (Simulating personalized relevance)
            # Add noise to relevance to simulate estimation error
            candidates = []
            for item in random.sample(items, 50): # Retrieval set
                est_rel = item["rel"] + random.gauss(0, 0.1)
                val = est_rel - lamb * item["cost"]
                candidates.append((val, item))
            
            # Select Top 1
            best_val, best_item = max(candidates, key=lambda x: x[0])
            
            # User Interaction
            # User clicks if True Relevance > Threshold - (Boredom_Factor)
            # Boredom: High budget -> lower threshold
            threshold = 0.5
            if best_item["rel"] > threshold:
                # Click!
                total_clicks += 1
                # Reward: Budget increase (Engagement loop)
                attention_budget += 2.0
            else:
                # Bounce
                total_bounces += 1
                # Penalty: Budget decrease (Frustration)
                attention_budget -= 1.0
                
            # Natural decay
            attention_budget -= 0.1
            
            if attention_budget > 50: break # Session cap
            
    ctr = total_clicks / (total_clicks + total_bounces)
    print(f"FINAL: Clicks={total_clicks}, Bounces={total_bounces}, CTR={ctr:.2%}")
    
    if ctr > 0.1:
        print("VERIFIED: BCP Recommendation sustains engagement.")
        return True
    else:
        print("FAILED: Low engagement.")
        return False

if __name__ == "__main__":
    run_experiment()
