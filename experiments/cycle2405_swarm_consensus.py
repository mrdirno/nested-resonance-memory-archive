"""
Cycle 2405: The Swarm Protocol (Gate 29)
Role: The Economist / Swarm Architect
Responsibility: Implement a distributed market for resource allocation.
Mechanism: Bid/Ask Auction.
"""

import random
import time

class SwarmNode:
    def __init__(self, id, initial_energy, priority):
        self.id = id
        self.energy = initial_energy
        self.priority = priority # 1 (Low) to 10 (Critical)
        self.tasks = []
        
    def needs_energy(self):
        # Threshold: Needs energy if below 100
        return self.energy < 100
        
    def has_excess(self):
        # Threshold: Has excess if above 200
        return self.energy > 200
        
    def bid(self):
        """Generate a Bid for energy."""
        if not self.needs_energy():
            return None
        
        deficit = 100 - self.energy
        # Bid Price depends on Priority and Deficit
        price = self.priority * deficit * 0.1
        return {'node_id': self.id, 'amount': deficit, 'price': price, 'type': 'BID'}
        
    def ask(self):
        """Generate an Ask to sell energy."""
        if not self.has_excess():
            return None
            
        surplus = self.energy - 200
        # Ask Price is inverse to surplus (more surplus = cheaper)
        price = (1.0 / surplus) * 100 
        return {'node_id': self.id, 'amount': surplus, 'price': price, 'type': 'ASK'}
        
    def receive(self, amount):
        self.energy += amount
        
    def give(self, amount):
        self.energy -= amount

class SwarmMarket:
    def __init__(self):
        self.nodes = []
        self.history = []
        
    def add_node(self, node):
        self.nodes.append(node)
        
    def resolve_market(self):
        print("\n--- Market Open ---")
        bids = []
        asks = []
        
        # 1. Gather Orders
        for node in self.nodes:
            b = node.bid()
            if b: bids.append(b)
            
            a = node.ask()
            if a: asks.append(a)
            
        # 2. Sort Orders
        # Highest Bid first
        bids.sort(key=lambda x: x['price'], reverse=True)
        # Lowest Ask first
        asks.sort(key=lambda x: x['price'])
        
        print(f"Bids: {len(bids)}, Asks: {len(asks)}")
        
        # 3. Match
        matches = 0
        while bids and asks:
            best_bid = bids[0]
            best_ask = asks[0]
            
            # Market Clearing Condition
            if best_bid['price'] >= best_ask['price']:
                # Deal!
                amount = min(best_bid['amount'], best_ask['amount'])
                price = (best_bid['price'] + best_ask['price']) / 2 # Midpoint price
                
                buyer = next(n for n in self.nodes if n.id == best_bid['node_id'])
                seller = next(n for n in self.nodes if n.id == best_ask['node_id'])
                
                print(f"MATCH: {buyer.id} buys {amount:.1f} from {seller.id} @ ${price:.2f}")
                
                buyer.receive(amount)
                seller.give(amount)
                
                # Update orders
                best_bid['amount'] -= amount
                best_ask['amount'] -= amount
                
                if best_bid['amount'] <= 0.01: bids.pop(0)
                if best_ask['amount'] <= 0.01: asks.pop(0)
                
                matches += 1
            else:
                print(f"Spread too wide. Bid: {best_bid['price']:.2f}, Ask: {best_ask['price']:.2f}")
                break
                
        return matches

def run_simulation():
    print("Cycle 2405: Swarm Consensus Simulation")
    print("======================================")
    
    market = SwarmMarket()
    
    # Scenario:
    # Node A: Critical Task, Low Energy (Starving)
    market.add_node(SwarmNode("Node-A", initial_energy=50, priority=10))
    
    # Node B: Idle, High Energy (Rich)
    market.add_node(SwarmNode("Node-B", initial_energy=300, priority=1))
    
    # Node C: Normal, Stable
    market.add_node(SwarmNode("Node-C", initial_energy=150, priority=5))
    
    # Run Market
    matches = market.resolve_market()
    
    # Validation
    node_a = market.nodes[0]
    print(f"\nNode-A Final Energy: {node_a.energy}")
    
    if node_a.energy >= 100:
        print("SUCCESS: Critical node received energy via market consensus.")
        return True
    else:
        print("FAIL: Market failed to allocate resources.")
        return False

if __name__ == "__main__":
    run_simulation()