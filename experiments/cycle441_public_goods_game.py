"""
Cycle 441: The Commons (Public Goods Game)
Role: The Sociologist
Responsibility: Investigate the stability of cooperation in a population of self-interested agents.
"""
import random
import numpy as np

class SocialAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.wealth = 10.0
        self.cooperation = random.random() # 0=Defector, 1=Altruist
        
    def decide_contribution(self, endowment):
        # Simple: contribute based on tendency
        return endowment * self.cooperation

def run_experiment():
    print("Cycle 441: Public Goods Game")
    print("===========================")
    
    N = 50
    population = [SocialAgent(i) for i in range(N)]
    MULTIPLIER = 3.0 # < N, so Defection is Nash Equilibrium
    ROUNDS = 20
    
    print(f"Population: {N}, Multiplier: {MULTIPLIER}")
    
    avg_coop_history = []
    
    for r in range(ROUNDS):
        # 1. Game Step
        pot = 0
        contributions = []
        
        for agent in population:
            endowment = 1.0 # Daily income
            contrib = agent.decide_contribution(endowment)
            agent.wealth -= contrib
            pot += contrib
            contributions.append(contrib)
            
        # 2. Payout
        pot_value = pot * MULTIPLIER
        share = pot_value / N
        
        for agent in population:
            agent.wealth += share
            
        # 3. Social Learning (Evolution of Strategy)
        # Agents look at a random peer. If peer is richer, adopt their strategy slightly.
        sorted_pop = sorted(population, key=lambda a: a.wealth, reverse=True)
        
        # Simple Replicator Dynamic:
        # Replace worst 10% with copies of best 10% (with mutation)
        num_replace = int(N * 0.1)
        best = sorted_pop[:num_replace]
        worst = sorted_pop[-num_replace:]
        
        for w in worst:
            role_model = random.choice(best)
            w.cooperation = role_model.cooperation + random.gauss(0, 0.05)
            w.cooperation = max(0.0, min(1.0, w.cooperation))
            w.wealth = 10.0 # Reset wealth for next round fairness? 
            # No, wealth accumulates. But for strategy comparison, current wealth matters.
            
        # Stats
        avg_coop = sum(a.cooperation for a in population) / N
        avg_wealth = sum(a.wealth for a in population) / N
        avg_coop_history.append(avg_coop)
        
        print(f"Round {r}: Avg Coop {avg_coop:.2f} | Pot {pot:.1f} -> {pot_value:.1f} | Avg Wealth {avg_wealth:.1f}")

    print("\n--- Conclusion ---")
    start_c = avg_coop_history[0]
    end_c = avg_coop_history[-1]
    print(f"Cooperation: {start_c:.2f} -> {end_c:.2f}")
    
    if end_c < start_c:
        print("RESULT: Tragedy of the Commons. Defectors won.")
    else:
        print("RESULT: Cooperation prevailed (Unexpected without punishment).")

if __name__ == "__main__":
    run_experiment()
