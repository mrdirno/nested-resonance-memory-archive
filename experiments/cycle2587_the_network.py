"""
Cycle 2587: The Network (Gate 57.3)
Goal: Implement a Registry for Shard Discovery.
"""

import sys
import os
import time
import multiprocessing
import queue
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.shard import Shard

class NetworkRegistry(multiprocessing.Process):
    """
    A centralized service (simulated) that tracks active Shards.
    Real-world equivalent: DNS or Service Mesh Control Plane.
    """
    def __init__(self, request_queue, response_queue):
        super().__init__()
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.registry = {} # {shard_id: meta_data}
        self.running = True
        
    def run(self):
        print("[Network] Registry Service Online.")
        while self.running:
            try:
                req = self.request_queue.get(timeout=0.1)
                type = req.get('type')
                
                if type == 'REGISTER':
                    sid = req.get('shard_id')
                    self.registry[sid] = {'status': 'ONLINE', 'last_seen': time.time()}
                    # print(f"[Network] Registered: {sid}")
                    
                elif type == 'DISCOVER':
                    # Return list of other active shards
                    requester = req.get('requester_id')
                    others = [sid for sid in self.registry if sid != requester]
                    self.response_queue.put({'requester': requester, 'peers': others})
                    
                elif type == 'STOP':
                    self.running = False
                    
            except queue.Empty:
                pass
                
        print("[Network] Registry Service Offline.")

def run_experiment():
    print("--- Cycle 2587: The Network (Shard Discovery) ---")
    
    # Network Bus
    net_req_q = multiprocessing.Queue()
    net_res_q = multiprocessing.Queue()
    
    # Registry Service
    registry = NetworkRegistry(net_req_q, net_res_q)
    registry.start()
    
    # Shard Queues
    cmd_q_earth = multiprocessing.Queue()
    tel_q_earth = multiprocessing.Queue()
    
    cmd_q_mars = multiprocessing.Queue()
    tel_q_mars = multiprocessing.Queue()
    
    cmd_q_venus = multiprocessing.Queue()
    tel_q_venus = multiprocessing.Queue()

    # Initialize Shards
    # Note: Shard class needs update to support network registration.
    # For this prototype, we manually register them in the loop below.
    
    earth = Shard("Earth", cmd_q_earth, tel_q_earth, capacity=10)
    mars = Shard("Mars", cmd_q_mars, tel_q_mars, capacity=10)
    venus = Shard("Venus", cmd_q_venus, tel_q_venus, capacity=10)
    
    print("Starting Shards...")
    earth.start()
    mars.start()
    venus.start()
    
    # Manual Registration (Simulating Shard startup logic)
    net_req_q.put({'type': 'REGISTER', 'shard_id': 'Earth'})
    net_req_q.put({'type': 'REGISTER', 'shard_id': 'Mars'})
    net_req_q.put({'type': 'REGISTER', 'shard_id': 'Venus'})
    
    time.sleep(1)
    
    # Discovery Test
    print("\n[Testing Discovery]")
    net_req_q.put({'type': 'DISCOVER', 'requester_id': 'Earth'})
    
    try:
        response = net_res_q.get(timeout=2)
        peers = response.get('peers')
        print(f"Earth discovered peers: {peers}")
        
        if 'Mars' in peers and 'Venus' in peers:
            print("SUCCESS: Network Registry is functioning.")
        else:
            print("FAILURE: Peers missing.")
            
    except queue.Empty:
        print("FAILURE: Discovery timed out.")
        
    # Shutdown
    print("\n[Shutting Down]")
    cmd_q_earth.put({'type': 'STOP'})
    cmd_q_mars.put({'type': 'STOP'})
    cmd_q_venus.put({'type': 'STOP'})
    net_req_q.put({'type': 'STOP'})
    
    earth.join()
    mars.join()
    venus.join()
    registry.join()
    
    print("System Halted.")

if __name__ == "__main__":
    run_experiment()
