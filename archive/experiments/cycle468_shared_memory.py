"""
Cycle 468: The Distributed Brain (Shared Memory)
Role: The Synapse
Responsibility: Enable state sharing across the process boundary.
"""
import multiprocessing
import time

def worker_brain(shared_state, lock):
    for _ in range(100):
        with lock:
            shared_state['knowledge'] += 1
        time.sleep(0.001)

def run_experiment():
    print("Cycle 468: Shared Memory Test")
    print("=============================")
    
    manager = multiprocessing.Manager()
    shared_state = manager.dict()
    shared_state['knowledge'] = 0
    lock = manager.Lock()
    
    processes = []
    for i in range(4):
        p = multiprocessing.Process(target=worker_brain, args=(shared_state, lock))
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    final_knowledge = shared_state['knowledge']
    print(f"Final Knowledge: {final_knowledge}")
    
    if final_knowledge == 400:
        print("SUCCESS: Shared state maintained across cluster.")
    else:
        print(f"FAIL: Race condition detected. Expected 400, got {final_knowledge}.")

if __name__ == "__main__":
    run_experiment()
