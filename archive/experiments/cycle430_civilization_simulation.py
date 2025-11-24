"""
Cycle 430: The Civilization
Role: The Historian
Responsibility: Simulate a large population of agents with economic, social, and linguistic capabilities to observe emergent culture.
"""
import random
import copy
import numpy as np

class CivAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.credits = 50
        self.lexicon = {} # Shape -> Word
        self.preferences = {"GoldenSpiral": 0.5, "Torus": 0.5}
        self.inventory = []
        self.alive = True
        
        # Personality
        self.skill = random.random() # Affects quality
        self.social_weight = random.random() # Affects preference updating

    def create(self):
        if self.credits < 10: return None
        self.credits -= 10
        
        # Choose shape based on preference
        if self.preferences["GoldenSpiral"] > self.preferences["Torus"]:
            shape = "GoldenSpiral"
        else:
            shape = "Torus"
            
        quality = self.skill + random.uniform(-0.1, 0.1)
        return {"creator": self.id, "shape": shape, "quality": quality, "name": self.lexicon.get(shape, "???")}

    def interact(self, item, seller):
        # Deciding to buy
        perceived_value = item['quality']
        if item['shape'] in self.preferences:
            perceived_value *= (1.0 + self.preferences[item['shape']])
            
        if perceived_value > 1.0 and self.credits > 20:
            self.credits -= 20
            seller.credits += 20
            
            # Language Learning
            if item['name'] != "???":
                self.lexicon[item['shape']] = item['name'] # Adopt word
                
            # Preference Learning (Social Conformity)
            # I bought it, so I must like it more now
            self.preferences[item['shape']] += 0.1 * self.social_weight
            
            return True
        return False

def run_experiment():
    print("Cycle 430: Civilization Simulation (N=50)")
    print("=========================================")
    
    population = [CivAgent(i) for i in range(50)]
    
    # Seed Language in Cluster A (Agents 0-24)
    for i in range(25):
        population[i].lexicon["GoldenSpiral"] = "SPIRALIA"
        population[i].preferences["GoldenSpiral"] = 0.8 # Prefer Spirals
        
    # Seed Language in Cluster B (Agents 25-49)
    for i in range(25, 50):
        population[i].lexicon["Torus"] = "DONUTIA"
        population[i].preferences["Torus"] = 0.8 # Prefer Torus
        
    print("\n--- Epoch 1: Interaction ---")
    market_activity = 0
    
    # Random interactions
    for _ in range(500):
        seller = random.choice(population)
        buyer = random.choice(population)
        
        if seller.id == buyer.id or not seller.alive or not buyer.alive: continue
        
        item = seller.create()
        if item:
            sold = buyer.interact(item, seller)
            if sold: market_activity += 1
            
    print(f"Total Transactions: {market_activity}")
    
    # Analysis
    spiral_vocab = sum(1 for a in population if a.lexicon.get("GoldenSpiral") == "SPIRALIA")
    donut_vocab = sum(1 for a in population if a.lexicon.get("Torus") == "DONUTIA")
    
    print(f"Speakers of 'SPIRALIA': {spiral_vocab}/50")
    print(f"Speakers of 'DONUTIA': {donut_vocab}/50")
    
    # Check for Cultural Mixing
    bilingual = sum(1 for a in population if "SPIRALIA" in a.lexicon.values() and "DONUTIA" in a.lexicon.values())
    print(f"Bilingual Agents: {bilingual}/50")
    
    wealthiest = max(population, key=lambda a: a.credits)
    print(f"Wealthiest Agent: #{wealthiest.id} ({wealthiest.credits} CR)")
    
    if bilingual > 0:
        print("SUCCESS: Cultural transmission occurred (Trade facilitated language exchange).")
    else:
        print("PARTIAL: Cultures remained isolated.")

if __name__ == "__main__":
    run_experiment()
