import random
import json
import heapq

# -----------------------------------------------------------------------------
# CYCLE 3225: TELECOM NETWORK OPTIMIZATION BCP
# -----------------------------------------------------------------------------
# Domain: Telecommunications
# Goal: Optimize packet routing to minimize latency/drop rate.
# Hypothesis: BCP (predictive congestion avoidance) outperforms Static Shortest Path.
# -----------------------------------------------------------------------------

class Node:
    def __init__(self, id):
        self.id = id
        self.queue = []
        self.capacity = 10 # Max packets per tick
        
    def receive(self, packet):
        if len(self.queue) < self.capacity:
            self.queue.append(packet)
            return True
        return False # Dropped
        
    def process(self):
        # Process/Forward packets
        processed = []
        while self.queue and len(processed) < 5: # Throughput limit
            processed.append(self.queue.pop(0))
        return processed

class Packet:
    def __init__(self, id, src, dst, creation_time):
        self.id = id
        self.src = src
        self.dst = dst
        self.creation_time = creation_time
        self.path = []
        self.hops = 0

class Network:
    def __init__(self):
        self.nodes = {}
        self.edges = {} # (u, v) -> weight (latency)
        self.congestion_history = {} # (u, v) -> avg_queue_len
        
    def add_node(self, id):
        self.nodes[id] = Node(id)
        
    def add_edge(self, u, v, weight=1):
        if u not in self.edges: self.edges[u] = {}
        if v not in self.edges: self.edges[v] = {}
        self.edges[u][v] = weight
        self.edges[v][u] = weight # Undirected
        self.congestion_history[(u,v)] = 0
        self.congestion_history[(v,u)] = 0

    def get_cost(self, u, v, mode='static'):
        base_cost = self.edges[u][v]
        if mode == 'static':
            return base_cost
        elif mode == 'bcp':
            # Metabolic Cost = Distance + Lambda * Congestion
            # Congestion is estimated queue length at V
            congestion = len(self.nodes[v].queue)
            lambda_val = 2.0 # Sensitivity to congestion
            return base_cost + (lambda_val * congestion)
            
    def find_path(self, src, dst, mode='static'):
        # Dijkstra
        pq = [(0, src, [])]
        visited = set()
        
        while pq:
            cost, u, path = heapq.heappop(pq)
            
            if u in visited: continue
            visited.add(u)
            
            path = path + [u]
            if u == dst:
                return path
                
            if u in self.edges:
                for v in self.edges[u]:
                    if v not in visited:
                        edge_cost = self.get_cost(u, v, mode)
                        heapq.heappush(pq, (cost + edge_cost, v, path))
        return []

def run_simulation(routing_mode, packets_per_tick=5, steps=100):
    net = Network()
    for i in range(10): net.add_node(i)
    
    # Simple Mesh
    edges = [
        (0,1), (0,2), (1,3), (2,3), (3,4), (3,5), 
        (4,6), (5,6), (6,7), (6,8), (7,9), (8,9),
        (1,4), (2,5) # Cross links
    ]
    for u,v in edges: net.add_edge(u,v)
    
    packets = []
    active_packets = []
    delivered_count = 0
    dropped_count = 0
    total_latency = 0
    
    for t in range(steps):
        # Spawn
        for _ in range(packets_per_tick):
            src = 0
            dst = 9
            p = Packet(len(packets), src, dst, t)
            p.path = net.find_path(src, dst, routing_mode)
            if len(p.path) > 1:
                # Queue at first hop (after src)
                next_hop = p.path[1]
                if net.nodes[next_hop].receive(p):
                    active_packets.append(p)
                    p.current_node = next_hop
                    p.path_index = 1
                else:
                    dropped_count += 1
        
        # Process
        for node in net.nodes.values():
            processed = node.process()
            for p in processed:
                # Move to next hop
                if p.path_index < len(p.path) - 1:
                    next_node_id = p.path[p.path_index + 1]
                    if net.nodes[next_node_id].receive(p):
                        p.current_node = next_node_id
                        p.path_index += 1
                    else:
                        dropped_count += 1
                        if p in active_packets: active_packets.remove(p)
                else:
                    # Delivered
                    delivered_count += 1
                    total_latency += (t - p.creation_time)
                    if p in active_packets: active_packets.remove(p)
                    
    avg_latency = total_latency / delivered_count if delivered_count > 0 else 0
    return delivered_count, dropped_count, avg_latency

def main():
    print("======================================================================")
    print("CYCLE 3225: TELECOM NETWORK OPTIMIZATION BCP")
    print("======================================================================")
    
    # High Load Test
    print("Running High Load Test (10 packets/tick)...")
    
    # Static
    s_del, s_drop, s_lat = run_simulation('static', packets_per_tick=10, steps=200)
    print(f"Static: Delivered={s_del}, Dropped={s_drop}, Latency={s_lat:.2f}")
    
    # BCP
    b_del, b_drop, b_lat = run_simulation('bcp', packets_per_tick=10, steps=200)
    print(f"BCP:    Delivered={b_del}, Dropped={b_drop}, Latency={b_lat:.2f}")
    
    print("-" * 60)
    
    # Improvement
    drop_imp = ((s_drop - b_drop) / s_drop) * 100 if s_drop > 0 else 0
    
    print(f"Drop Rate Improvement: {drop_imp:.2f}%")
    
    if b_drop < s_drop:
        print("RESULT: SUCCESS. BCP Congestion Routing reduced packet loss.")
    else:
        print("RESULT: FAILURE. BCP did not outperform Static.")
        
    print("======================================================================")
    
    with open("results/cycle3225_telecom_opt.json", "w") as f:
        json.dump({
            "static": {"delivered": s_del, "dropped": s_drop, "latency": s_lat},
            "bcp": {"delivered": b_del, "dropped": b_drop, "latency": b_lat},
            "improvement": drop_imp
        }, f, indent=2)

if __name__ == "__main__":
    main()
