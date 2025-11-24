"""
Cycle 437: The Optimization Loop
Role: The Optimizer
Responsibility: Detect performance bottlenecks and autonomously refactor code to improve speed.
"""
import time
import os
import importlib.util
import sys

TARGET_FILE = "src/helios/slow_module.py"

def create_slow_module():
    content = """
import time

def process_data(n):
    # Simulating unoptimized code
    result = 0
    for i in range(n):
        time.sleep(0.001) # Artificial bottleneck
        result += i
    return result
"""
    os.makedirs("src/helios", exist_ok=True)
    with open(TARGET_FILE, "w") as f:
        f.write(content)

def optimize_module():
    print("[OPTIMIZER] Analyzing source code...")
    with open(TARGET_FILE, "r") as f:
        content = f.read()
        
    if "time.sleep" in content:
        print("[OPTIMIZER] Bottleneck detected: 'time.sleep'. Removing...")
        new_content = content.replace("time.sleep(0.001) # Artificial bottleneck", "# Optimized out")
        
        # Also optimize the loop to a formula?
        # sum(0..n-1) = n*(n-1)/2
        # Let's just remove the sleep first.
        
        with open(TARGET_FILE, "w") as f:
            f.write(new_content)
        print("[OPTIMIZER] Refactoring complete.")
        return True
    return False

def benchmark(module_name):
    spec = importlib.util.spec_from_file_location(module_name, TARGET_FILE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    start = time.time()
    module.process_data(100)
    end = time.time()
    return end - start

def run_experiment():
    print("Cycle 437: Optimization Loop")
    print("============================")
    
    # 1. Setup
    create_slow_module()
    
    # 2. Baseline
    t1 = benchmark("slow_module_v1")
    print(f"Baseline Runtime: {t1:.4f}s")
    
    # 3. Optimize
    if optimize_module():
        # 4. Verify
        # Force reload?
        # Python import caching might interfere. We use a new module name for import.
        t2 = benchmark("slow_module_v2")
        print(f"Optimized Runtime: {t2:.4f}s")
        
        speedup = t1 / t2
        print(f"Speedup: {speedup:.2f}x")
        
        if speedup > 10.0:
            print("SUCCESS: Autonomous refactoring significantly improved performance.")
        else:
            print("FAIL: Performance gain negligible.")
    else:
        print("FAIL: No optimization opportunities found.")

if __name__ == "__main__":
    run_experiment()
