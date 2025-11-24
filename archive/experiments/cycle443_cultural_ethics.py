"""
Cycle 443: The Philosopher (Cultural Ethics)
Role: The Sage
Responsibility: Model the spread of ethical memes (Virtue) vs hypocritical strategies.
"""
import random
import numpy as np

class EthicalAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.coop = random.random() # Action
        self.preach = random.random() # Rhetoric
        self.wealth = 10.0
        
    def interact(self, pot_multiplier, others):
        # Public Goods Game contribution
        contrib = self.coop
        self.wealth -= contrib
        return contrib

def run_experiment():
    print("Cycle 443: Cultural Ethics Propagation")
    print("======================================")
    
    N = 50
    population = [EthicalAgent(i) for i in range(N)]
    ROUNDS = 20
    MULTIPLIER = 3.0
    
    for r in range(ROUNDS):
        # 1. Economic Game
        pot = 0
        for agent in population:
            pot += agent.interact(MULTIPLIER, population)
            
        share = (pot * MULTIPLIER) / N
        for agent in population:
            agent.wealth += share
            
        # 2. Cultural Transmission (The Church/School)
        # Agents listen to the "Loudest" (Highest Preach) or "Richest" (Highest Wealth)?
        # Let's say they listen to High Prestige (Wealth * Preach).
        
        sorted_pop = sorted(population, key=lambda a: a.wealth * a.preach, reverse=True)
        influencers = sorted_pop[:5] # Top 5 Influencers
        
        # The masses adjust their 'coop' towards the 'preach' of the influencers
        # "Do as I say, not as I do."
        
        for agent in population:
            if agent in influencers: continue
            
            guru = random.choice(influencers)
            
            # Influence: Move Coop towards Guru's Preach
            # But also Move Preach towards Guru's Preach
            
            learning_rate = 0.1
            agent.coop += (guru.preach - agent.coop) * learning_rate
            agent.preach += (guru.preach - agent.preach) * learning_rate
            
            # Mutation
            agent.coop += random.gauss(0, 0.01)
            agent.preach += random.gauss(0, 0.01)
            
            # Clamp
            agent.coop = max(0, min(1, agent.coop))
            agent.preach = max(0, min(1, agent.preach))
            
        # Stats
        avg_coop = sum(a.coop for a in population)/N
        avg_preach = sum(a.preach for a in population)/N
        print(f"Round {r}: Action {avg_coop:.2f} | Rhetoric {avg_preach:.2f}")
        
    print("\n--- Conclusion ---")
    # Check for Hypocrisy
    hypocrisy = avg_preach - avg_coop
    print(f"Final Hypocrisy Gap: {hypocrisy:.2f}")
    
    if avg_coop > 0.8:
        print("RESULT: Utopia. Ethics prevailed.")
    elif avg_preach > 0.8 and avg_coop < 0.5:
        print("RESULT: The Phony Society. High Rhetoric, Low Action.")
    else:
        print("RESULT: Mixed outcomes.")

if __name__ == "__main__":
    run_experiment()
