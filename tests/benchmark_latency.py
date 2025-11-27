
import time
import numpy as np
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from src.helios.solver import InverseSolver

def benchmark_solver():
    print("Benchmarking InverseSolver Latency...")
    
    # Setup 32^3 grid (standard)
    res = 2.0 # mm
    shape = (32, 32, 32)
    target_field = np.zeros(shape)
    
    # Create a sparse target (e.g. a ring)
    center = 16
    radius = 10
    for x in range(32):
        for y in range(32):
            for z in range(32):
                dist = np.sqrt((x-center)**2 + (y-center)**2 + (z-center)**2)
                if abs(dist - radius) < 1.5:
                    target_field[z,y,x] = 1.0
                    
    emitters = [[x/8.0, y/8.0, 0.0] for x in range(8) for y in range(8)]
    config = {"c": 343, "rho": 1.2}
    
    solver = InverseSolver(target_field, emitters, config, resolution=res)
    
    # Warmup
    print("Warmup...")
    solver.evolve()
    
    # Benchmark
    print("Running 5 iterations...")
    times = []
    for i in range(5):
        start = time.time()
        solver.evolve()
        dt = time.time() - start
        times.append(dt)
        print(f"Iter {i}: {dt*1000:.2f} ms")
        
    avg_latency = np.mean(times) * 1000
    print(f"Average Latency: {avg_latency:.2f} ms")
    
    if avg_latency < 200:
        print("PASS: Latency < 200ms")
    else:
        print("FAIL: Latency > 200ms")

    # Benchmark Propagation Only (Real-Time Feedback)
    print("\nBenchmarking Field Propagation (get_field)...")
    phases = np.random.uniform(0, 2*np.pi, 64)
    
    times = []
    for i in range(10):
        start = time.time()
        _ = solver.get_field(phases)
        dt = time.time() - start
        times.append(dt)
        print(f"Prop Iter {i}: {dt*1000:.2f} ms")
        
    avg_prop = np.mean(times) * 1000
    print(f"Average Propagation Latency: {avg_prop:.2f} ms")
    
    if avg_prop < 50: # Strict target for 20fps+
        print("PASS: Propagation < 50ms")
        return True
    else:
        print("FAIL: Propagation > 50ms")
        return False

if __name__ == "__main__":
    benchmark_solver()
