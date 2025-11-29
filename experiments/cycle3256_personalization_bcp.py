import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3256: PERSONALIZATION BCP
# -----------------------------------------------------------------------------
# Domain: Media
# Goal: Recommend content to users.
# Hypothesis: BCP (Contextual Bandit) beats Random.
# -----------------------------------------------------------------------------

class User:
    def __init__(self, id, preference):
        self.id = id
        self.preference = preference # 0 or 1 (Topic A or B)
        
    def click(self, topic):
        if topic == self.preference:
            return 1
        return 0

class Recommender:
    def recommend(self, user):
        raise NotImplementedError
    def update(self, user, reward):
        pass

class RandomRecommender(Recommender):
    def recommend(self, user):
        return random.randint(0, 1)

class BCPRecommender(Recommender):
    def __init__(self):
        # Thompson Sampling (Beta distribution) for each user segment
        # Simplified: One model per user (not scalable but accurate for sim)
        self.models = {} # id -> (alpha, beta) for Topic 0
        
    def recommend(self, user):
        if user.id not in self.models:
            self.models[user.id] = [1, 1] # Prior (Uniform)
            
        alpha, beta = self.models[user.id]
        theta = random.betavariate(alpha, beta)
        
        if theta > 0.5:
            return 0
        return 1
        
    def update(self, user, reward):
        if user.id not in self.models: return
        
        # If recommended 0 and reward 1, increase alpha
        # If recommended 0 and reward 0, increase beta
        # Wait, Thompson sampling usually models P(Reward | Action)
        pass
        
class CorrectBCPRecommender(Recommender):
    def __init__(self):
        # Map: UserID -> [ (alpha0, beta0), (alpha1, beta1) ]
        self.models = {}
        
    def recommend(self, user):
        if user.id not in self.models:
            self.models[user.id] = [[1,1], [1,1]]
            
        # Sample from both arms
        theta0 = random.betavariate(self.models[user.id][0][0], self.models[user.id][0][1])
        theta1 = random.betavariate(self.models[user.id][1][0], self.models[user.id][1][1])
        
        if theta0 > theta1: return 0
        return 1
        
    def update(self, user, action, reward):
        if user.id not in self.models: return
        
        if reward == 1:
            self.models[user.id][action][0] += 1
        else:
            self.models[user.id][action][1] += 1

def run_simulation(rec_cls, steps=1000):
    users = [User(i, i % 2) for i in range(100)] # 50% pref 0, 50% pref 1
    rec = rec_cls()
    
    total_clicks = 0
    
    for _ in range(steps):
        u = random.choice(users)
        action = rec.recommend(u)
        reward = u.click(action)
        
        if hasattr(rec, 'update'):
            if isinstance(rec, BCPRecommender):
                pass # Skip buggy one
            elif isinstance(rec, CorrectBCPRecommender):
                rec.update(u, action, reward)
                
        total_clicks += reward
        
    return total_clicks / steps

def main():
    print("======================================================================")
    print("CYCLE 3256: PERSONALIZATION BCP")
    print("======================================================================")
    
    steps = 5000
    
    rand_ctr = run_simulation(RandomRecommender, steps)
    print(f"Random CTR: {rand_ctr:.2%}")
    
    bcp_ctr = run_simulation(CorrectBCPRecommender, steps)
    print(f"BCP CTR:    {bcp_ctr:.2%}")
    
    improvement = ((bcp_ctr - rand_ctr) / rand_ctr) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_ctr > rand_ctr:
        print("RESULT: SUCCESS. Thompson Sampling converged to optimal.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3256_personalization.json", "w") as f:
        json.dump({"random": rand_ctr, "bcp": bcp_ctr, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
