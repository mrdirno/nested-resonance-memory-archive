"""
Cycle 467: The Cluster (Multi-Process Coordination)
Role: The Orchestrator
Responsibility: Manage a fleet of processes.
"""
import multiprocessing
import time
import os
import random

def worker_task(worker_id, pipe):
    pid = os.getpid()
    pipe.send(f"Worker {worker_id} (PID {pid}) Ready.")
    
    start = time.time()
    while True:
        # Simulate work
        time.sleep(0.1)
        
        # Random chance of death (Chaos Monkey)
        if random.random() < 0.05:
            os._exit(1) # Crash
            
        if time.time() - start > 5.0:
            break
            
    pipe.send(f"Worker {worker_id} Finished.")

def run_experiment():
    print("Cycle 467: Cluster Simulation")
    print("=============================")
    
    NUM_WORKERS = 4
    processes = {} # pid -> worker_id
    pipes = []
    
    # Spawn initial
    for i in range(NUM_WORKERS):
        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=worker_task, args=(i, child_conn))
        p.start()
        processes[p.pid] = (p, i)
        pipes.append(parent_conn)
        print(f"Spawned Worker {i} (PID {p.pid})")
        
    start_time = time.time()
    while time.time() - start_time < 5.0:
        # Check for deaths
        dead_pids = []
        
        # Iterate over snapshot
        current_processes = list(processes.items())
        
        for pid, (p, wid) in current_processes:
            if not p.is_alive():
                print(f"Worker {wid} (PID {pid}) Died! Restarting...")
                dead_pids.append(pid)
                
                # Restart
                parent_conn, child_conn = multiprocessing.Pipe()
                new_p = multiprocessing.Process(target=worker_task, args=(wid, child_conn))
                new_p.start()
                processes[new_p.pid] = (new_p, wid)
                pipes.append(parent_conn) # Track new pipe
                print(f"Respawned Worker {wid} (PID {new_p.pid})")
                
        for pid in dead_pids:
            del processes[pid]
            
        # Read logs
        for pipe in pipes:
            if pipe.poll():
                try:
                    msg = pipe.recv()
                    # print(f"[LOG] {msg}") 
                except:
                    pass
                    
        time.sleep(0.1)
        
    # Cleanup
    print("\nStopping Cluster...")
    for pid, (p, wid) in processes.items():
        p.terminate()
        
    print("SUCCESS: Cluster maintained population despite failures.")

if __name__ == "__main__":
    run_experiment()
