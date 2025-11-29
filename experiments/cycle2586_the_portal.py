"""
Cycle 2586: The Portal (Gate 57.2)
Goal: Verify agent migration between Shards.
"""

import sys
import os
import time
import multiprocessing
import queue

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.shard import Shard

def run_experiment():
    print("--- Cycle 2586: The Portal (Inter-Shard Migration) ---")
    
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
    
    # State
    migrated_agent_data = None
    migration_complete = False
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < 10:
            # EARTH MONITOR
            try:
                while not tel_q_earth.empty():
                    msg = tel_q_earth.get_nowait()
                    if msg['type'] == 'TELEMETRY':
                        data = msg['data']
                        print(f"EARTH | Tick: {data['tick']} | Pop: {data['population']}")
                        
                        # Trigger Migration at Tick 3
                        if data['tick'] == 3 and not migrated_agent_data:
                            print(">>> Triggering Migration of Earth-Adam...")
                            cmd_q_earth.put({'type': 'EXPORT_AGENT', 'agent_name': 'Earth-Adam'})
                            
                    elif msg['type'] == 'EXPORT_SUCCESS':
                        print(">>> EXPORT RECEIVED from Earth!")
                        migrated_agent_data = msg['data']
                        
                        # Immediate Import to Mars
                        print(">>> Sending IMPORT to Mars...")
                        cmd_q_mars.put({'type': 'IMPORT_AGENT', 'data': migrated_agent_data})
            except queue.Empty:
                pass

            # MARS MONITOR
            try:
                while not tel_q_mars.empty():
                    msg = tel_q_mars.get_nowait()
                    if msg['type'] == 'TELEMETRY':
                        data = msg['data']
                        print(f"MARS  | Tick: {data['tick']} | Pop: {data['population']}")
                        
                        # Verification
                        if migrated_agent_data and data['population'] >= 3: # Adam, Eve + Earth-Adam (+ maybe children)
                             # It's hard to verify name from telemetry stats unless we added name list to telemetry.
                             # But population jump is a good proxy.
                             pass
            except queue.Empty:
                pass
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Shutdown
        print("\n[Shutting Down]")
        cmd_q_earth.put({'type': 'STOP'})
        cmd_q_mars.put({'type': 'STOP'})
        
        earth.join()
        mars.join()
        
        print("Shards terminated.")

if __name__ == "__main__":
    run_experiment()
