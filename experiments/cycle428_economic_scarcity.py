"""
Cycle 428: The Economy
Role: The Economist
Responsibility: Introduce scarcity and value exchange to drive efficient evolution.
"""
import random
import copy

class EconomicAgent:
    def __init__(self, agent_id, initial_credits=100):
        self.id = agent_id
        self.credits = initial_credits
        self.inventory = []
        self.cost_per_creation = 10
        self.price_per_sale = 20
        self.alive = True
        
        # Strategy: 0.0 = Random, 1.0 = Perfect Market Fit
        self.strategy_quality = random.random()

    def create(self):
        if not self.alive: return None
        
        if self.credits < self.cost_per_creation:
            print(f"[Agent {self.id}] BANKRUPT! Cannot create.")
            self.alive = False
            return None
            
        self.credits -= self.cost_per_creation
        
        # Simulate creation quality based on strategy
        quality = self.strategy_quality + random.uniform(-0.1, 0.1)
        product = {"creator": self.id, "quality": quality}
        
        print(f"[Agent {self.id}] Created Product (Qual: {quality:.2f}) | Credits: {self.credits}")
        return product

    def evaluate_and_buy(self, product):
        if not self.alive: return False
        
        # Market Logic: Buy if quality > 0.5 (simulating "good" design)
        if product['quality'] > 0.5:
            return True
        return False

    def receive_payment(self):
        self.credits += self.price_per_sale
        print(f"[Agent {self.id}] Made a Sale! (+{self.price_per_sale}) | Credits: {self.credits}")

def run_experiment():
    print("Cycle 428: Economic Scarcity Test")
    print("=================================")
    
    # 1. Initialize Market
    # Agent A: Smart (High Quality)
    # Agent B: Dumb (Low Quality)
    agent_a = EconomicAgent("A", initial_credits=50)
    agent_a.strategy_quality = 0.8 
    
    agent_b = EconomicAgent("B", initial_credits=50)
    agent_b.strategy_quality = 0.2
    
    agents = [agent_a, agent_b]
    market = [] # List of products on sale
    
    # 2. Run Simulation Steps
    for step in range(10):
        print(f"\n--- Market Step {step+1} ---")
        
        # Production Phase
        for agent in agents:
            item = agent.create()
            if item:
                market.append(item)
                
        # Consumption Phase (Consumer is the 'World' or other agents)
        # Here, we simulate a "Market God" that buys good stuff
        for item in list(market):
            if item['quality'] > 0.5:
                print(f"[MARKET] Sold product from Agent {item['creator']}")
                # Pay the creator
                creator = next(a for a in agents if a.id == item['creator'])
                creator.receive_payment()
                market.remove(item) # Sold
            else:
                print(f"[MARKET] Rejected product from Agent {item['creator']} (Low Quality)")
                # Item stays in market (unsold inventory cost? maybe later)
                market.remove(item) # Perishable goods for now
                
        # Check Status
        if not agent_a.alive and not agent_b.alive:
            print("Market Collapse.")
            break

    print("\n--- Final Status ---")
    print(f"Agent A (High Skill): {agent_a.credits} Credits | Alive: {agent_a.alive}")
    print(f"Agent B (Low Skill): {agent_b.credits} Credits | Alive: {agent_b.alive}")
    
    if agent_a.alive and agent_a.credits > 50 and not agent_b.alive:
        print("SUCCESS: Natural Selection worked. Competent agent thrived, incompetent went bankrupt.")
    else:
        print("FAIL: Economic pressure did not sort agents correctly.")

if __name__ == "__main__":
    run_experiment()
