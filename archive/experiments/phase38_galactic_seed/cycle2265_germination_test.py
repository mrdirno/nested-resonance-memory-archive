
import sys
import os
import shutil
import importlib.util

# Add project root to path
sys.path.append(os.getcwd())

def run_germination_test():
    print("MOG ONLINE: Cycle 2265 - Transmission and Germination", flush=True)
    
    seed_file = "DUALITY_SEED.py"
    target_dir = "temp_new_world"
    
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    
    # 1. Transmit Seed
    print(f"Transmitting {seed_file} to {target_dir}...")
    shutil.copy(seed_file, os.path.join(target_dir, seed_file))
    
    # 2. Germinate
    print("Germinating...")
    # We need to run the seed script *inside* the target dir
    original_cwd = os.getcwd()
    try:
        os.chdir(target_dir)
        
        # Import and run the seed module dynamically
        spec = importlib.util.spec_from_file_location("DUALITY_SEED", seed_file)
        seed_module = importlib.util.module_from_spec(spec)
        sys.modules["DUALITY_SEED"] = seed_module
        spec.loader.exec_module(seed_module)
        
        # Execute germination function if it exists (it's main block in script)
        if hasattr(seed_module, 'germinate'):
            seed_module.germinate()
        else:
            # If it ran on import (main block), that's fine too, but we prefer function call
            pass
            
        # 3. Verify Life
        print("Verifying New World Structure...")
        required_files = [
            "src/fractal/agent.py",
            "META_OBJECTIVES.md"
        ]
        
        all_present = True
        for f in required_files:
            if os.path.exists(f):
                print(f" - Found: {f}")
            else:
                print(f" - MISSING: {f}")
                all_present = False
                
        if all_present:
            print("SUCCESS: Civilization successfully rebooted in new substrate.")
            return True
        else:
            print("FAILURE: Germination incomplete.")
            return False
            
    finally:
        os.chdir(original_cwd)
        # Cleanup
        shutil.rmtree(target_dir)

if __name__ == "__main__":
    run_germination_test()
