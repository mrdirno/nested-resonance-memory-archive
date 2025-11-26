import sys
import os
import random
import numpy as np
from typing import Dict, List

# Add project root to path
sys.path.append(os.getcwd())

# Use archive import for CulturalAgent as base
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))
from phase32_cultural_engine.cycle2242_cultural_transmission import CulturalAgent

class MarketAgent(CulturalAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.currency = 100.0
        self.inventory = {"wood": 0, "stone": 0}
        self.valuation = {"wood": random.uniform(1, 10), "stone": random.uniform(1, 10)}
        
    def generate_resource(self):
        # Specialize: Half produce wood, half produce stone
        if hash(self.id) % 2 == 0:
            self.inventory["wood"] += 1
        else:
            self.inventory["stone"] += 1
            
    def trade(self, other: 'MarketAgent'):
        # Double Coincidence of Wants check? Or use Currency?
        # Let's use Currency.
        
        # Buyer logic: If I value their good > price, I buy.
        # Seller logic: If price > my valuation, I sell.
        
        # Try to buy wood
        if other.inventory["wood"] > 0:
            price = other.valuation["wood"] * 1.1 # Margin
            if self.valuation["wood"] > price and self.currency >= price:
                # Transaction
                self.currency -= price
                other.currency += price
                self.inventory["wood"] += 1
                other.inventory["wood"] -= 1
                print(f"{self.id} bought wood from {other.id} for {price:.2f}")
                return True
                
        # Try to buy stone
        if other.inventory["stone"] > 0:
            price = other.valuation["stone"] * 1.1
            if self.valuation["stone"] > price and self.currency >= price:
                self.currency -= price
                other.currency += price
                self.inventory["stone"] += 1
                other.inventory["stone"] -= 1
                print(f"{self.id} bought stone from {other.id} for {price:.2f}")
                return True
                
        return False

def run_market_experiment():
    print("MOG ONLINE: Cycle 2248 - Market Formation", flush=True)
    
    N_AGENTS = 10
    agents = [MarketAgent(f"trader_{i}") for i in range(N_AGENTS)]
    
    # Production Phase
    for _ in range(5):
        for a in agents: a.generate_resource()
        
    print("Initial State:")
    for a in agents:
        print(f"{a.id}: ${a.currency:.2f}, Inv: {a.inventory}")
        
    # Trading Phase
    print("\nTrading Phase...")
    trades = 0
    for _ in range(50): # Random encounters
        a1 = random.choice(agents)
        a2 = random.choice(agents)
        if a1 != a2:
            if a1.trade(a2): trades += 1
            
    print(f"\nTotal Trades: {trades}")
    
    # Verify Wealth Distribution
    wealths = [a.currency for a in agents]
    gini = np.std(wealths) / np.mean(wealths) # Simple inequality metric
    print(f"Wealth Gini (Proxy): {gini:.4f}")
    
    if trades > 0:
        print("SUCCESS: Market activity detected.")
        return True
    else:
        print("FAILURE: No trades occurred.")
        return False

if __name__ == "__main__":
    run_market_experiment()
