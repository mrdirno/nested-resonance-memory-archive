"""
Cycle 461: The Network (P2P Discovery)
Role: The Network Engineer
Responsibility: Enable multi-node coordination.
"""
import threading
import time
import queue

class Node:
    def __init__(self, name, network):
        self.name = name
        self.network = network
        self.peers = set()
        
    def broadcast(self, message):
        print(f"[{self.name}] Broadcasting: {message}")
        self.network.put((self.name, message))
        
    def listen(self):
        try:
            sender, msg = self.network.get(timeout=1.0)
            if sender != self.name:
                print(f"[{self.name}] Received from {sender}: {msg}")
                if msg == "HELLO":
                    self.peers.add(sender)
                    self.broadcast(f"ACK to {sender}")
                elif "ACK" in msg:
                    self.peers.add(sender)
        except queue.Empty:
            pass

def run_experiment():
    print("Cycle 461: P2P Discovery Simulation")
    print("===================================")
    
    # Mock Network (Shared Queue)
    network = queue.Queue()
    
    node_a = Node("Node_A", network)
    node_b = Node("Node_B", network)
    
    # Simulation Loop
    # 1. A Broadcasts Hello
    node_a.broadcast("HELLO")
    
    # 2. B Listens and Responds
    node_b.listen()
    
    # 3. A Listens for Ack
    node_a.listen()
    
    # Check Connectivity
    print("\n--- Connectivity Check ---")
    print(f"Node A Peers: {node_a.peers}")
    print(f"Node B Peers: {node_b.peers}")
    
    if "Node_B" in node_a.peers and "Node_A" in node_b.peers:
        print("SUCCESS: Mutual Discovery confirmed.")
    else:
        print("FAIL: Network isolation.")

if __name__ == "__main__":
    run_experiment()
