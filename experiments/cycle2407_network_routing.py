"""
Cycle 2407: The Network Effect (Gate 31)
Role: The Network Engineer
Responsibility: Implement routing logic where energy transfer incurs loss based on distance.
Constraint: Nodes have a maximum connection range. Transfers must hop through intermediate nodes.
"""

import math
import heapq

class NetworkNode:
    def __init__(self, id, x, y, energy=0):
        self.id = id
        self.x = x
        self.y = y
        self.energy = energy
        self.neighbors = [] # List of (neighbor_node, distance)

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class SmartGrid:
    def __init__(self, loss_coefficient=0.01, max_range=15.0):
        self.nodes = {}
        self.loss_coefficient = loss_coefficient # Loss per unit distance
        self.max_range = max_range
        
    def add_node(self, node):
        self.nodes[node.id] = node
        
    def build_topology(self):
        """Connect nodes within max_range."""
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                n1 = node_list[i]
                n2 = node_list[j]
                dist = n1.distance_to(n2)
                
                if dist <= self.max_range:
                    n1.neighbors.append((n2, dist))
                    n2.neighbors.append((n1, dist))
                    
    def find_route(self, start_id, end_id):
        """Dijkstra's Algorithm to find path with minimum distance."""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None, float('inf')
            
        # Priority Queue: (total_distance, current_node_id, path)
        pq = [(0, start_id, [start_id])]
        visited = set()
        # To properly implement Dijkstra, we need to track min cost to node
        min_costs = {start_id: 0}
        
        final_path = None
        final_cost = float('inf')
        
        while pq:
            cost, current_id, path = heapq.heappop(pq)
            
            if current_id == end_id:
                if cost < final_cost:
                    final_cost = cost
                    final_path = path
                continue
            
            if cost > min_costs.get(current_id, float('inf')):
                continue
            
            current_node = self.nodes[current_id]
            for neighbor, dist in current_node.neighbors:
                new_cost = cost + dist
                if new_cost < min_costs.get(neighbor.id, float('inf')):
                    min_costs[neighbor.id] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor.id, path + [neighbor.id]))
                    
        return final_path, final_cost

    def transfer_energy(self, start_id, end_id, amount):
        path, distance = self.find_route(start_id, end_id)
        
        if not path:
            print(f"FAIL: No path from {start_id} to {end_id}.")
            return False
            
        loss = distance * self.loss_coefficient * amount
        net_received = amount - loss
        
        print(f"Transfer: {start_id} -> {end_id}")
        print(f"  Path: {' -> '.join(path)}")
        print(f"  Distance: {distance:.2f}")
        print(f"  Sent: {amount}")
        print(f"  Loss: {loss:.2f} ({loss/amount*100:.1f}%)")
        print(f"  Received: {net_received:.2f}")
        
        if net_received <= 0:
            print("FAIL: Energy dissipated completely before arrival.")
            return False
            
        # Execute Transfer
        self.nodes[start_id].energy -= amount
        self.nodes[end_id].energy += net_received
        return True

def run_simulation():
    print("Cycle 2407: Network Routing Simulation")
    print("======================================")
    
    # 1. Setup Grid
    # Loss = 1% per unit distance
    # Max Range = 15 units
    grid = SmartGrid(loss_coefficient=0.01, max_range=15.0)
    
    # 2. Create Nodes (Linear Chain for testing)
    # A(0,0) --10--> B(10,0) --10--> C(20,0) --10--> D(30,0)
    # Direct A->D is 30 units (Out of range 15)
    # Must route A->B->C->D
    
    grid.add_node(NetworkNode("A", 0, 0, energy=1000))
    grid.add_node(NetworkNode("B", 10, 0))
    grid.add_node(NetworkNode("C", 20, 0))
    grid.add_node(NetworkNode("D", 30, 0))
    
    grid.build_topology()
    
    # 3. Execute Transfer
    print("[1] Attempting Transfer A -> D (Distance 30, Multi-hop)...")
    success = grid.transfer_energy("A", "D", 100)
    
    # Validation
    final_d = grid.nodes["D"].energy
    # Expected Distance = 30
    # Expected Loss = 30 * 0.01 * 100 = 30
    # Expected Received = 70
    
    if success and 69 < final_d < 71:
        print("SUCCESS: Routing logic verified. Multi-hop transfer successful.")
        return True
    else:
        print(f"FAIL: Unexpected result. D Energy: {final_d}")
        return False

if __name__ == "__main__":
    run_simulation()