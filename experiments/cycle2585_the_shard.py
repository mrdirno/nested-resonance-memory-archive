"""
Cycle 2585: The Shard (Gate 57.1)
Goal: Verify that we can run multiple Ecosystem instances in parallel processes.
"""

import sys
import os
import time
import multiprocessing

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.shard import Shard

def run_experiment():
    print("--- Cycle 2585: The Shard (Distributed Execution) ---")
    
    # Create Queues
    cmd_q_earth = multiprocessing.Queue()
    tel_q_earth = multiprocessing.Queue()
    
    cmd_q_mars = multiprocessing.Queue()
    tel_q_mars = multiprocessing.Queue()
    
    # Initialize Shards
    earth = Shard("Earth", cmd_q_earth, tel_q_earth, capacity=20)
    mars = Shard("Mars", cmd_q_mars, tel_q_mars, capacity=20)
    
    print("Starting Shards...")
    earth.start()
    mars.start()
    
    # Monitor Loop
    print("\n[Monitoring Telemetry]")
    
    active_shards = {'Earth', 'Mars'}
    shard_ticks = {'Earth': 0, 'Mars': 0}
    
    start_time = time.time()
    while time.time() - start_time < 5: # Run for 5 seconds
        # Check Earth
        while not tel_q_earth.empty():
            data = tel_q_earth.get()
            shard_ticks['Earth'] = data['tick']
            print(f"EARTH | Tick: {data['tick']} | Pop: {data['population']}")
            
        # Check Mars
        while not tel_q_mars.empty():
            data = tel_q_mars.get()
            shard_ticks['Mars'] = data['tick']
            print(f"MARS  | Tick: {data['tick']} | Pop: {data['population']}")
            
        time.sleep(0.5)
        
        if shard_ticks['Earth'] >= 5 and shard_ticks['Mars'] >= 5:
            print("\nBoth Shards reached 5 ticks.")
            break
            
    # Shutdown
    print("\n[Shutting Down]")
    cmd_q_earth.put({'type': 'STOP'})
    cmd_q_mars.put({'type': 'STOP'})
    
    earth.join()
    mars.join()
    
    print("Shards terminated.")
    
    if shard_ticks['Earth'] > 0 and shard_ticks['Mars'] > 0:
        print("SUCCESS: Both shards executed independently.")
    else:
        print("FAILURE: One or more shards failed to report.")

if __name__ == "__main__":
    run_experiment()
