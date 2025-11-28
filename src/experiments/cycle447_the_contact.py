"""
Cycle 447: The Contact (Multi-Civilization Interaction)
Role: The Diplomat
Responsibility: Simulate the collision of two distinct cultures/species.
"""
import random
import numpy as np

class ContactAgent:
    def __init__(self, agent_id, tribe):
        self.id = agent_id
        self.tribe = tribe
        self.wealth = 10.0
        
        if tribe == "MERCHANT":
            self.skill = 0.9
            self.coop = 0.1 # Defector
        else: # MONK
            self.skill = 0.2
            self.coop = 0.9 # Altruist
            
    def interact(self):
        # Contribution = coop * skill (Capacity to give)
        # Cost = coop * skill
        return self.coop * self.skill

def run_experiment():
    print("Cycle 447: First Contact Simulation")
    print("===================================")
    
    pop_A = [ContactAgent(i, "MERCHANT") for i in range(25)]
    pop_B = [ContactAgent(i+25, "MONK") for i in range(25)]
    population = pop_A + pop_B
    
    ROUNDS = 20
    MULTIPLIER = 3.0
    
    print(f"Initial: {len(pop_A)} Merchants, {len(pop_B)} Monks.")
    
    for r in range(ROUNDS):
        pot = 0
        
        # 1. Contribution
        for agent in population:
            contrib = agent.interact()
            agent.wealth -= contrib
            pot += contrib
            
        # 2. Distribution (Global Economy)
        total_value = pot * MULTIPLIER
        share = total_value / len(population)
        
        for agent in population:
            agent.wealth += share
            
        # 3. Migration/Conversion (Replicator Dynamic)
        # Agents switch to the Tribe that is wealthier on average?
        # Or just pure survival (Wealth < 0 -> Death)?
        # Let's use "Conversion". Poor agents join the Rich tribe.
        
        # Calculate Avg Wealth per Tribe
        wealth_A = [a.wealth for a in population if a.tribe == "MERCHANT"]
        wealth_B = [a.wealth for a in population if a.tribe == "MONK"]
        
        avg_A = sum(wealth_A)/len(wealth_A) if wealth_A else 0
        avg_B = sum(wealth_B)/len(wealth_B) if wealth_B else 0
        
        # If diff is large, 10% of poor tribe converts
        if avg_A > avg_B + 5.0:
            # A is richer. Convert B -> A
            candidates = [a for a in population if a.tribe == "MONK"]
            num_convert = int(len(candidates) * 0.1)
            for i in range(num_convert):
                candidates[i].tribe = "MERCHANT"
                candidates[i].skill = 0.9
                candidates[i].coop = 0.1
        elif avg_B > avg_A + 5.0:
            # B is richer. Convert A -> B
            candidates = [a for a in population if a.tribe == "MERCHANT"]
            num_convert = int(len(candidates) * 0.1)
            for i in range(num_convert):
                candidates[i].tribe = "MONK"
                candidates[i].skill = 0.2
                candidates[i].coop = 0.9
                
        # Stats
        count_A = sum(1 for a in population if a.tribe == "MERCHANT")
        count_B = sum(1 for a in population if a.tribe == "MONK")
        
        print(f"Round {r}: Merchants {count_A} ({avg_A:.1f}) | Monks {count_B} ({avg_B:.1f})")
        
        if count_A == 0 or count_B == 0:
            print("Assimilation Complete.")
            break

    print("\n--- Conclusion ---")
    if count_A > count_B:
        print("RESULT: The Merchants assimilated the Monks. Efficiency > Virtue.")
    else:
        print("RESULT: The Monks assimilated the Merchants. Virtue > Efficiency.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
