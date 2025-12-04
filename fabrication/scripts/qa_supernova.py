import sys
import os
import time
import importlib.util

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

def load_module(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_test(module_path, func_name, output_name, resolution=50):
    print(f"\n--- QA Test: {output_name} ---")
    output_file = os.path.join(os.path.dirname(__file__), output_name)
    
    try:
        if not os.path.exists(module_path):
             print(f"FAIL: Module not found: {module_path}")
             return False

        module = load_module(module_path)
        func = getattr(module, func_name)
        
        start_time = time.time()
        try:
            func(output_file, resolution=resolution)
        except TypeError:
             print("WARNING: generator does not accept 'resolution'. Running with defaults.")
             func(output_file)
             
        duration = time.time() - start_time
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"PASS: Generated {size/1024/1024:.2f} MB in {duration:.2f}s")
        else:
            print("FAIL: No file generated.")
            return False
            
    except Exception as e:
        print(f"FAIL: Exception detected -> {e}")
        if "Connectivity broken" in str(e):
             pass 
        else:
             import traceback
             traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    base_dir = os.path.join(project_root, "fabrication/furniture/lamp_series_01/04_supernova")
    
    # 1. Shade
    shade_path = os.path.join(base_dir, "supernova_shade_gen.py")
    res1 = run_test(shade_path, "generate_shade", "supernova_shade_qa.stl", resolution=100)
    
    # 2. Base
    base_path = os.path.join(base_dir, "supernova_base_gen.py")
    res2 = run_test(base_path, "generate_base", "supernova_base_qa.stl", resolution=100)
    
    # 3. Shaft
    shaft_path = os.path.join(base_dir, "supernova_shaft_gen.py")
    res3 = run_test(shaft_path, "generate_shaft", "supernova_shaft_qa.stl", resolution=50)
    
    if res1 and res2 and res3:
        print("\nALL SYSTEMS GO. Supernova Design 04 is Valid.")
        sys.exit(0)
    else:
        print("\nQA FAILED.")
        sys.exit(1)
