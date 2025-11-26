
import sys
import os
import random
import numpy as np
from typing import List, Dict

# Add project root to path
sys.path.append(os.getcwd())

# Use archive import for MarketAgent as base (building on Economy)
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))
from phase34_economy.cycle2248_market_formation import MarketAgent

class ResourceNode:
    def __init__(self, type: str, amount: float, position: np.ndarray):
        self.type = type # "wood" or "stone" or "food"
        self.amount = amount
        self.position = position
        self.regenerate_rate = 0.1

    def regenerate(self):
        self.amount += self.regenerate_rate

class SimpleState:
    def __init__(self, position):
        self.position = position

class EcologicalAgent(MarketAgent):
    def __init__(self, agent_id: str, species: str):
        super().__init__(agent_id)
        self.species = species # "Gatherer" or "Crafter"
        # Gatherers are good at harvesting raw resources.
        # Crafters are good at converting raw resources into value (money/tools).
        self.state = SimpleState(np.random.rand(3) * 100.0) # Initialize random position
        
    def move(self, delta: np.ndarray):
        self.state.position += delta
        
    def harvest(self, node: ResourceNode) -> float:
        if self.species == "Gatherer":
            amount = min(node.amount, 1.0) # Efficient harvest
        else:
            amount = min(node.amount, 0.2) # Inefficient harvest
            
        node.amount -= amount
        if node.type in self.inventory:
            self.inventory[node.type] += amount
        else:
            self.inventory[node.type] = amount
        return amount

    def craft(self) -> bool:
        if self.species == "Crafter":
            # Convert 1 wood + 1 stone -> 1 "tool" (high value)
            if self.inventory.get("wood", 0) >= 1 and self.inventory.get("stone", 0) >= 1:
                self.inventory["wood"] -= 1
                self.inventory["stone"] -= 1
                self.currency += 10.0 # Sell to "system" or use
                return True
        return False

def run_ecology_experiment():
    print("MOG ONLINE: Cycle 2250 - Artificial Ecology", flush=True)
    
    N_AGENTS = 20
    WORLD_SIZE = 100.0
    
    # 1. Create Environment
    resources = []
    for _ in range(10):
        resources.append(ResourceNode("wood", 10.0, np.random.rand(3)*WORLD_SIZE))
        resources.append(ResourceNode("stone", 10.0, np.random.rand(3)*WORLD_SIZE))
        
    # 2. Create Species
    agents = []
    for i in range(N_AGENTS):
        species = "Gatherer" if i < N_AGENTS // 2 else "Crafter"
        agents.append(EcologicalAgent(f"agent_{i}", species))
        
    # 3. Simulation Loop
    print("Simulating Ecosystem...")
    total_harvested = 0.0
    total_crafted = 0
    
    for cycle in range(100):
        # Regenerate resources
        for res in resources: res.regenerate()
        
        # Move and Act
        for agent in agents:
            # Simple AI: Find nearest resource
            if agent.species == "Gatherer":
                # Look for wood/stone
                target = None
                min_dist = 9999.0
                for res in resources:
                    dist = np.linalg.norm(agent.state.position - res.position)
                    if dist < min_dist:
                        min_dist = dist
                        target = res
                
                if target and min_dist < 5.0:
                    harvested = agent.harvest(target)
                    total_harvested += harvested
                elif target:
                    # Move towards
                    direction = target.position - agent.state.position
                    agent.move((direction / min_dist) * 2.0)
                    
                # Trade logic (Simplified): If inventory full, give to random Crafter for money
                if agent.inventory.get("wood", 0) > 5 or agent.inventory.get("stone", 0) > 5:
                    # Find a crafter
                    crafters = [a for a in agents if a.species == "Crafter"]
                    if crafters:
                        partner = random.choice(crafters)
                        # Trade wood
                        if agent.inventory.get("wood", 0) > 0:
                            amt = agent.inventory["wood"]
                            agent.inventory["wood"] = 0
                            partner.inventory["wood"] = partner.inventory.get("wood", 0) + amt
                            agent.currency += amt * 2.0 # Price
                            partner.currency -= amt * 2.0
                        # Trade stone
                        if agent.inventory.get("stone", 0) > 0:
                            amt = agent.inventory["stone"]
                            agent.inventory["stone"] = 0
                            partner.inventory["stone"] = partner.inventory.get("stone", 0) + amt
                            agent.currency += amt * 2.0
                            partner.currency -= amt * 2.0

            elif agent.species == "Crafter":
                # Try to craft
                if agent.craft():
                    total_crafted += 1
                
                # Move randomly if not trading (waiting for gatherers)
                agent.move(np.random.randn(3))

    print(f"Total Harvested: {total_harvested:.2f}")
    print(f"Total Crafted: {total_crafted}")
    
    # Verify Symbiosis
    # Gatherers should have money. Crafters should have crafted items (converted to money).
    gatherer_wealth = np.mean([a.currency for a in agents if a.species == "Gatherer"])
    crafter_wealth = np.mean([a.currency for a in agents if a.species == "Crafter"])
    
    print(f"Avg Gatherer Wealth: {gatherer_wealth:.2f}")
    print(f"Avg Crafter Wealth: {crafter_wealth:.2f}")
    
    if total_crafted > 0 and gatherer_wealth > 100.0:
        print("SUCCESS: Ecological symbiosis established.")
        return True
    else:
        print("FAILURE: Ecosystem collapsed or failed to interact.")
        return False

if __name__ == "__main__":
    run_ecology_experiment()
