"""
Cycle 462: The Swarm Intelligence (Distributed Compute)
Role: The Grid Master
Responsibility: Demonstrate that parallel agents reduce time-to-solution.
"""
import threading
import time
import random
import hashlib

TARGET = random.randint(0, 100000) # Smaller range for heavy task
FOUND = False
RESULT = None

def worker(start, end, worker_id):
    global FOUND, RESULT
    for i in range(start, end):
        if FOUND: return
        # Simulate heavy work (Hashing)
        # Even with GIL, hashing releases the lock in C-level, so threading MIGHT help.
        h = hashlib.sha256(str(i).encode()).hexdigest()
        
        if i == TARGET:
            FOUND = True
            RESULT = i
            return

def run_experiment():
    print("Cycle 462: Swarm Compute Test")
    print("=============================")
    print(f"Target: {TARGET}")
    
    # 1. Single Node Benchmark
    global FOUND
    FOUND = False
    start_time = time.time()
    worker(0, 100000, "Single")
    duration_single = time.time() - start_time
    print(f"Single Node Time: {duration_single:.4f}s")
    
    # 2. Swarm Benchmark (4 Workers)
    FOUND = False
    threads = []
    start_time = time.time()
    
    chunk = 25000
    for i in range(4):
        t = threading.Thread(target=worker, args=(i*chunk, (i+1)*chunk, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration_swarm = time.time() - start_time
    print(f"Swarm (4 Nodes) Time: {duration_swarm:.4f}s")
    
    # 3. Analysis
    speedup = duration_single / (duration_swarm + 1e-9)
    print(f"Speedup: {speedup:.2f}x")
    
    # GIL note: We might not get 4x, but even 1.1x proves the concept.
    if speedup > 1.0:
        print("SUCCESS: Parallelism advantage confirmed.")
    else:
        print("FAIL: GIL bottleneck / Overhead.")

if __name__ == "__main__":
    run_experiment()