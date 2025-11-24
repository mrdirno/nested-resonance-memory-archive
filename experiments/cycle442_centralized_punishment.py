"""
Cycle 442: The Leviathan (Centralized Punishment)
Role: The Governor
Responsibility: Restore order to the Commons via centralized enforcement.
"""
import random
import numpy as np

class SocialAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.wealth = 10.0
        self.cooperation = random.random()
        
    def decide_contribution(self, endowment):
        return endowment * self.cooperation

class Government:
    def __init__(self, tax_rate=0.1, fine_amount=2.0, detection_rate=1.0):
        self.tax_rate = tax_rate
        self.fine_amount = fine_amount
        self.detection_rate = detection_rate
        self.treasury = 0.0
        
    def tax(self, agent):
        tax = agent.wealth * self.tax_rate
        agent.wealth -= tax
        self.treasury += tax
        
    def punish(self, agent, contribution, endowment):
        # Defector definition: Contributes less than 50%
        if contribution < (endowment * 0.5):
            if random.random() < self.detection_rate:
                agent.wealth -= self.fine_amount
                self.treasury += self.fine_amount # Fines go to state

def run_experiment():
    print("Cycle 442: The Leviathan")
    print("========================'")
    
    N = 50
    population = [SocialAgent(i) for i in range(N)]
    gov = Government(tax_rate=0.05, fine_amount=2.0) # 5% tax, massive fine
    
    MULTIPLIER = 3.0
    ROUNDS = 20
    
    avg_coop_history = []
    
    for r in range(ROUNDS):
        pot = 0
        
        # 1. Production & Contribution
        for agent in population:
            endowment = 1.0
            contrib = agent.decide_contribution(endowment)
            agent.wealth -= contrib
            pot += contrib
            
            # Government Intervention
            gov.tax(agent)
            gov.punish(agent, contrib, endowment)
            
        # 2. Payout
        pot_value = pot * MULTIPLIER
        share = pot_value / N
        for agent in population:
            agent.wealth += share
            
        # 3. Evolution
        sorted_pop = sorted(population, key=lambda a: a.wealth, reverse=True)
        num_replace = int(N * 0.1)
        best = sorted_pop[:num_replace]
        worst = sorted_pop[-num_replace:]
        
        for w in worst:
            role_model = random.choice(best)
            w.cooperation = role_model.cooperation + random.gauss(0, 0.05)
            w.cooperation = max(0.0, min(1.0, w.cooperation))
            w.wealth = 10.0 
            
        avg_coop = sum(a.cooperation for a in population) / N
        avg_coop_history.append(avg_coop)
        
        print(f"Round {r}: Avg Coop {avg_coop:.2f} | Treasury {gov.treasury:.1f}")

    print("\n--- Conclusion ---")
    start_c = avg_coop_history[0]
    end_c = avg_coop_history[-1]
    print(f"Cooperation: {start_c:.2f} -> {end_c:.2f}")
    
    if end_c > start_c and end_c > 0.8:
        print("RESULT: Order Restored. The Leviathan enforced cooperation.")
    else:
        print("RESULT: Failed to stabilize cooperation.")

if __name__ == "__main__":
    run_experiment()
