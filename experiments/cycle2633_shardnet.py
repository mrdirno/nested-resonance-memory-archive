#!/usr/bin/env python3
"""
Experiment: Cycle 2633 - The Shard-Net
Goal: Simulate distributed communication between two separate Hive shards.
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

class MockNetwork:
    """
    Simulates a network bus between shards.
    """
    def __init__(self):
        self.channels = {} # shard_id -> queue

    def register(self, shard_id):
        self.channels[shard_id] = queue.Queue()
        print(f"[NET] Shard {shard_id} registered.")

    def send(self, sender_id, target_id, message):
        if target_id in self.channels:
            # Simulate latency
            time.sleep(0.01)
            self.channels[target_id].put((sender_id, message))
            # print(f"[NET] {sender_id} -> {target_id}: {message}")
        else:
            print(f"[NET] Error: Target {target_id} not found.")

    def receive(self, shard_id):
        try:
            return self.channels[shard_id].get_nowait()
        except queue.Empty:
            return None

class Shard:
    """
    A standalone simulation instance.
    """
    def __init__(self, shard_id, network):
        self.id = shard_id
        self.network = network
        self.network.register(self.id)
        self.local_state = {"active_agents": 5}

    def run_step(self):
        # Check inbox
        msg_data = self.network.receive(self.id)
        if msg_data:
            sender, content = msg_data
            print(f"[{self.id}] Received from {sender}: {content}")
            
            if content == "PING":
                self.network.send(self.id, sender, "PONG")
            elif content == "STATUS_REQ":
                self.network.send(self.id, sender, json.dumps(self.local_state))

    def ping_remote(self, target_id):
        print(f"[{self.id}] Pinging {target_id}...")
        self.network.send(self.id, target_id, "PING")

def run_shardnet_test():
    print("Cycle 2633: The Shard-Net - Distributed Simulation")
    
    net = MockNetwork()
    shard_a = Shard("Shard-A", net)
    shard_b = Shard("Shard-B", net)
    
    print("\n--- Phase 1: Ping-Pong ---")
    shard_a.ping_remote("Shard-B")
    
    # Simulate concurrent steps
    for _ in range(5):
        shard_a.run_step()
        shard_b.run_step()
        time.sleep(0.05)
        
    print("\n--- Phase 2: State Query ---")
    shard_b.network.send("Shard-B", "Shard-A", "STATUS_REQ")
    
    for _ in range(5):
        shard_a.run_step()
        shard_b.run_step()
        time.sleep(0.05)
        
    print("\nSUCCESS: Inter-shard communication established.")

if __name__ == "__main__":
    run_shardnet_test()
