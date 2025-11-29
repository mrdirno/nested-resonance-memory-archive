"""
Cycle 2595: The Swarm (Gate 60.2)
Goal: Massive Scaling. Run 10 concurrent Shards.
"""

import sys
import os
import time
import multiprocessing
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.shard import Shard

def run_experiment():
    print("--- Cycle 2595: The Swarm (Massive Scaling) ---")
    
    SHARD_COUNT = 10
    shards = []
    cmd_queues = []
    tel_queues = []
    
    # Initialize 10 Shards
    for i in range(SHARD_COUNT):
        shard_id = f"Shard-{i+1:02d}"
        cmd_q = multiprocessing.Queue()
        tel_q = multiprocessing.Queue()
        
        # Vary capacity slightly
        capacity = random.randint(15, 25)
        
        shard = Shard(shard_id, cmd_q, tel_q, capacity=capacity)
        shards.append(shard)
        cmd_queues.append(cmd_q)
        tel_queues.append(tel_q)
        
    print(f"Launching {SHARD_COUNT} Shards...")
    for s in shards:
        s.start()
        
    # Monitor Loop
    print("\n[Monitoring Swarm]")
    start_time = time.time()
    
    # Tracking
    active_shards = set(range(SHARD_COUNT))
    
    while time.time() - start_time < 10: # Run for 10 seconds
        
        total_pop = 0
        reporting_count = 0
        
        for i in range(SHARD_COUNT):
            q = tel_queues[i]
            last_data = None
            
            # Drain queue to get latest
            while not q.empty():
                msg = q.get()
                if msg.get('type') == 'TELEMETRY':
                    last_data = msg['data']
            
            if last_data:
                total_pop += last_data['population']
                reporting_count += 1
                # Print sample from Shard 1 and 10
                if i == 0 or i == 9:
                    print(f"{last_data['shard_id']} | Tick: {last_data['tick']} | Pop: {last_data['population']}")
                    
        print(f">> SWARM STATUS: {reporting_count}/{SHARD_COUNT} Online | Total Pop: {total_pop}")
        time.sleep(1.0)
        
    # Shutdown
    print("\n[Shutting Down Swarm]")
    for q in cmd_queues:
        q.put({'type': 'STOP'})
        
    for s in shards:
        s.join()
        
    print("Swarm Terminated.")
    
    if reporting_count == SHARD_COUNT:
        print("SUCCESS: All shards reported in.")
    else:
        print(f"WARNING: Only {reporting_count} shards reported.")

if __name__ == "__main__":
    run_experiment()
