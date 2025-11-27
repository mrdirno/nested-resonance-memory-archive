"""
Phase 48: Latency Profiling (Stress Test)
Sweeps resolution to find the CPU bottleneck.
"""

import os
import sys
import time
import numpy as np

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.compiler import MatterCompiler

def stress_test():
    print("="*60)
    print("PHASE 48: LATENCY STRESS TEST")
    print("="*60)
    
    mesh_path = "data/triangle.obj"
    if not os.path.exists(mesh_path):
        # Fallback if not found
        with open(mesh_path, "w") as f:
            f.write("v 0 0 0\nv 0.01 0 0\nv 0 0.01 0\nf 1 2 3\n")

    resolutions = [32, 64, 128]
    limit = 20.0 # ms
    
    for res in resolutions:
        print(f"\n--- Testing Resolution: {res}x{res}x{res} ---")
        compiler = MatterCompiler(resolution=res)
        
        latencies = []
        for i in range(3):
            start = time.time()
            compiler.compile_object(mesh_path)
            end = time.time()
            latencies.append((end - start) * 1000)
            
        avg = np.mean(latencies)
        print(f"Average Latency: {avg:.2f} ms")
        
        if avg > limit:
            print(f"❌ BOTTLE NECK DETECTED at Res {res}. ({avg:.2f} ms > {limit} ms)")
            print(f"FPGA Acceleration required for High-Fidelity ({res}+).")
            return
            
    print("\n✅ CPU survived all tests. (Unexpected efficient optimization?)")

if __name__ == "__main__":
    stress_test()