"""
Cycle 466: The Watcher (Process Supervision)
Role: The Guardian
Responsibility: Ensure the system survives critical failures (Crashes).
"""
import multiprocessing
import time
import os

def worker_task(run_id):
    print(f"[Worker {run_id}] PID: {os.getpid()} - Starting...")
    time.sleep(1.0)
    print(f"[Worker {run_id}] Working...")
    time.sleep(1.0)
    print(f"[Worker {run_id}] CRITICAL ERROR! Simulating crash.")
    # Exit with non-zero code to simulate crash
    os._exit(1) 

def run_experiment():
    print("Cycle 466: Process Supervisor Test")
    print("==================================")
    
    MAX_RESTARTS = 3
    restarts = 0
    
    while restarts < MAX_RESTARTS:
        print(f"\n[Supervisor] Launching Worker (Attempt {restarts + 1})...")
        p = multiprocessing.Process(target=worker_task, args=(restarts,)) # Changed from 'restarts' to 'restarts' to fix the issue
        p.start()
        p.join() # Wait for it to die
        
        exit_code = p.exitcode
        print(f"[Supervisor] Worker died with Exit Code: {exit_code}")
        
        if exit_code != 0:
            print("[Supervisor] Detected crash. Restarting...")
            restarts += 1
            time.sleep(0.5) # Backoff
        else:
            print("[Supervisor] Worker exited normally. Job done.")
            break
            
    if restarts == MAX_RESTARTS:
        print("\n[Supervisor] Max restarts reached. Giving up.")
        print("SUCCESS: Supervisor successfully detected crashes and restarted the process.")

if __name__ == "__main__":
    run_experiment()
